# Select arguments to pass to a tool to execute

from typing import List, Dict, Callable, Any
from torch import no_grad
from rich import print_json
import time
from kor.extraction import create_extraction_chain
from kor.nodes import Object
from .logger import logger
from . import kor_schema, similarity
from .pre_processing import join_user_actions, build_context
from .nlp import nlp
from .pre_processing import setup_parameters_schema
from .llm_output import process_llm_json_output, apply_type
from .helpers import is_allowed, is_notallowed
from .types import ParameterSchema


class ArgumentsSelection:

    layer = "arguments-selection"
    errors: List[str] = []
    logs: List[str] = []
    raw_model_output = None
    args = {}
    waiting_args = []
    start = time.time()
    why_invalid = {}

    def __init__(
        self,
        tool: Dict,
        context: str | None = None,
        verbose: bool = True,
        logger: Callable = logger,
        history=[],
        parameters_ready: bool = False,
    ):
        self.verbose = verbose
        self.logger = logger

        if "parameters" not in tool:
            tool["parameters"] = {}

        self.tool = tool
        if parameters_ready is False:
            self.parameters = setup_parameters_schema(tool["parameters"])
            self.parameters = {
                key: ParameterSchema(**self.parameters[key]).dict()
                for key in self.parameters.keys()
            }
        else:
            self.parameters = tool["parameters"]

        self.context = context
        self.build_kor_schema()

        self.validation_steps = [self.match_context, self.important, self.accept]

    # ----- Build a Kor schema from the tool's parameters config
    def build_kor_schema(self):
        self.kor_schema = kor_schema.build(self.tool)

        self.extraction_chain = create_extraction_chain(
            self.llm, Object.parse_obj(self.kor_schema), encoder_or_encoder_class="json"
        )

    # ----- Process all arguments
    def selection(self):
        self.start = time.time()
        extracted = self.extract_args()

        if extracted["success"] is False:
            return extracted

        self.logger(self, f"Extraction finished in {(time.time() - self.start):.4f}s")
        extracted = self.remove_nulls(extracted["data"])

        validated = self.validate(extracted)
        self.layer = "arguments-selection"
        self.logger(
            self,
            f"Arguments validation finished with {len(self.errors)} errors in {(time.time() - self.start):.4f}s",
            "error" if len(self.errors) > 0 else "info",
        )
        validated.update({"errors": self.errors})
        validated.update({"why_invalid": self.why_invalid})

        return validated

    def remove_nulls(self, data: Dict):
        valid = {}
        for key in data.keys():
            if isinstance(data[key], dict):
                valid.update(self.remove_nulls(data[key]))
            elif data[key] is not None:
                if isinstance(data[key], str) and len(data[key]) == 0:
                    continue
                elif isinstance(data[key], list) and len(data[key]) == 0:
                    continue
                valid.update({key: data[key]})

        return valid

    # ----- Extract arguments using the extraction chain
    def extract_args(self):
        self.logger(self, "Extracting arguments")
        extraction = self.extraction_chain.invoke(self.context)
        errors = extraction["text"]["errors"]
        self.raw_model_output = extraction["text"]["raw"]

        raw_data = extraction["text"]["raw"].strip()
        if raw_data.startswith("<json>"):
            raw_data += "</json>"

        json_llm_output = process_llm_json_output(raw_data)
        if json_llm_output["success"] is True:
            return {"success": True, "data": json_llm_output["value"]}

        errors = ["Invalid LLM output"] + errors
        list(self.new_error(err) for err in errors)
        return {"success": False, "errors": errors}

    def validate(self, data: Dict):
        self.logger(self, "Validating arguments")
        if not isinstance(data, dict):
            return {"success": False, "action": "ignore"}

        if self.tool["name"] in data:
            data = data[self.tool["name"]]

        # Get valid arguments that exist in the parameters schema
        wanted_args = list(
            [key, data[key]] for key in data.keys() if key in self.parameters.keys()
        )

        default_args = list(
            [key, self.resolve_default_arg_value(self.parameters[key], "missing")]
            for key in self.parameters.keys()
            if key not in data.keys() or data[key] is None
        )

        default_args_keys = list(
            key for key, value in default_args if value["success"] is True
        )

        missing_args = [
            ids
            for default in default_args
            if default[1]["success"] is False and default[1]["action"] == "stop"
            for ids in default[1]["ids"]
        ]

        validated_values = list(
            [key, self.validated_arg_value(self.parameters[key], value)]
            for key, value in wanted_args
        )

        validated_values += list(
            [key, value] for key, value in default_args if value["success"] is True
        )

        invalid_args = list(
            ids
            for key, value in validated_values
            if is_notallowed(value, "success") is True
            and value["action"] == "stop"
            and self.resolve_default_arg_value(self.parameters[key], "invalid")["why"]
            == "invalid"
            and is_allowed(self.parameters[key], "required") is True
            for ids in value["ids"]
        )

        valid_values = list(
            [key, value["value"]]
            for key, value in validated_values
            if is_allowed(value, "success") is True
        )

        invalid_has_default = list(
            [key, self.resolve_default_arg_value(self.parameters[key], "invalid")]
            for key, value in validated_values
            if is_notallowed(value, "success") is True
        )

        invalid_has_default = list(
            [key, value]
            for key, value in invalid_has_default
            if is_allowed(value, "success") is True
        )

        valid_values += invalid_has_default

        return {
            "valid": valid_values,
            "missing": missing_args,
            "invalid": invalid_args,
        }

    def resolve_default_arg_value(self, param_options: Dict, state: str):
        self.update_layer(param_options["id"])
        default_fallback = is_notallowed(param_options, f"{state}_default_fallback")

        if default_fallback is True:
            return {
                "success": False,
                "action": "stop" if is_allowed(param_options, "required") else "ignore",
                "why": state,
                "ids": [param_options["id"]],
            }

        if "default" in param_options and param_options["default"] is not None:
            self.logger(self, f"Falling back to default value")
            return {"success": True, "value": param_options["default"], "why": "done"}

        param_type = param_options["type"]

        if (
            param_type["root"].lower() in ["object", "json", "dict"]
            and "properties" in param_options
            and len(param_options["properties"].keys()) > 0
        ):
            default_values = list(
                [
                    key,
                    self.resolve_default_arg_value(
                        param_options["properties"][key], state
                    ),
                ]
                for key in param_options["properties"].keys()
            )

            are_all_default = (
                True
                if len(
                    [
                        default_value
                        for default_value in default_values
                        if default_value[1]["success"] is True
                        or default_value[1]["action"] == "ignore"
                    ]
                )
                == len(default_values)
                else False
            )

            object_value = {
                key: value["value"]
                for key, value in default_values
                if value["success"] is True
            }

            self.update_layer(param_options["id"])

            if are_all_default:
                self.logger(self, f"Falling back to default value")
                return {"success": True, "value": object_value, "why": "done"}

            no_default = [
                ids
                for value in default_values
                if value[1]["success"] is False and value[1]["action"] == "stop"
                for ids in value[1]["ids"]
            ]

            return {
                "success": False,
                "action": (
                    "stop"
                    if is_allowed(param_options, "required") is True
                    else "ignore"
                ),
                "why": "N",
                "ids": no_default,
            }

        return {
            "success": False,
            "action": (
                "stop" if is_allowed(param_options, "required") is True else "ignore"
            ),
            "why": "N",
            "ids": [param_options["id"]],
        }

    def validated_arg_value(self, param_options: Dict, value: Any):
        self.update_layer(param_options["id"])
        param_type = param_options["type"]
        required = is_allowed(param_options, "required")

        typed = apply_type(param_type, value)
        if typed["success"] is False:
            self.why_invalid[param_options["id"]] = "Can't validate invalid data type"
            self.logger(self, typed["error"], "error")
            return {
                "success": False,
                "action": "stop" if required is True else "ignore",
            }

        value = typed["value"]

        if param_type["root"].lower() in ["dict", "object", "json"]:
            arg_value = self.validated_object(param_options, value)
            is_whole_success = is_allowed(arg_value, "success")
            is_whole_failed = is_notallowed(arg_value, "success")

            if (
                not is_whole_success and not is_whole_failed
            ):  # the object is not as_whole
                errors_ids = [
                    f"{param_options['id']}.{key}"
                    for key in arg_value.keys()
                    if not is_allowed(arg_value[key], "success")
                    and arg_value[key]["action"] == "stop"
                ]

                if len(errors_ids) > 0:
                    return {"success": False, "action": "stop", "ids": errors_ids}

                key_values = {
                    key: arg_value[key]["value"]
                    for key in arg_value
                    if "value" in arg_value[key]
                }

                return {"success": True, "value": key_values}

            return arg_value

        if param_type["root"].lower() in ["list", "array"] and isinstance(value, list):
            arg_value = self.validated_array(param_options, value)
            if isinstance(arg_value, dict):  # the arg is a whole
                return arg_value

            validated_items = [
                item["value"] for item in arg_value if item["success"] is True
            ]
            if len(validated_items) < 1 and is_allowed(param_options, "required"):
                return {
                    "success": False,
                    "action": "stop",
                    "ids": [param_options["id"]],
                }

            return {"success": True, "value": validated_items}

        validated = self.validated_item(param_options, value)
        if validated["success"] is False:
            validated.update({"ids": [param_options["id"]]})

        return validated

    def validated_array(self, param_options: Dict, value: List):
        required = is_allowed(param_options, "required")

        if is_allowed(param_options, "as_whole") is True:
            return self.validated_item(param_options, value)

        return [self.validated_item(param_options, item) for item in value]

    def validated_object(self, param_options: Dict, value: Dict):
        required = is_allowed(param_options, "required")

        if is_allowed(param_options, "as_whole") is True:
            return self.validated_item(param_options, value)

        if "properties" not in param_options:
            self.logger(
                self, f"Invalid parameter schema (object has no properties)", "warning"
            )
            return {
                "success": False,
                "action": "stop" if required is True else "ignore",
            }

        validated_value = {
            key: self.validated_arg_value(param_options["properties"][key], value[key])
            for key in value.keys()
            if key in param_options["properties"]
        }

        return validated_value

    def run_validation_step(self, param_options: Dict, value: Any, step: Callable):
        validated_value = step(param_options, value)
        has_default = True if "default" in param_options.keys() else False
        default_fallback = is_notallowed(param_options, "invalid_default_fallback")
        logged_success = False

        if (
            validated_value["success"] is False
            and has_default is True
            and default_fallback is False
        ):
            self.logger(
                self,
                f"Validation failed. falling back to default value. (step: {step.__name__})",
                "warning",
            )
            logged_success = True
            validated_value = {"success": True, "value": param_options["default"]}

        if validated_value["success"] is False:
            self.logger(self, f"Validation failed. (step: {step.__name__})", "error")

        if (
            validated_value["success"] is True
            and logged_success is False
            and "no" not in validated_value.keys()
        ):
            self.logger(
                self, f"Validation succeeded. (step: {step.__name__})", "success"
            )

        return validated_value

    def validated_item(self, param_options: Dict, value: List):
        validated_value = {"success": True, "value": value}
        for step in self.validation_steps:
            if validated_value["success"] is False:
                break
            validated_value = self.run_validation_step(
                param_options, validated_value["value"], step
            )

        return validated_value

    def match_context(self, param_options: Dict, value: Any):
        if not is_allowed(param_options, "match_context"):
            return {"success": True, "value": value, "no": True}

        if "match_tokens" in param_options.keys():
            match_tokens = param_options["match_tokens"]
        else:
            match_tokens = ["VERB", "NOUN", "ADJ"]

        if is_allowed(param_options, "only_latest"):
            context_doc = nlp(str(self.inputs["input"]))
        else:
            context_doc = nlp(str(self.context))

        required = is_allowed(param_options, "required")
        value_doc = nlp(str(value))
        is_valid = True

        context_tokens = []
        context_tokens_lemma = []

        [
            context_tokens.append(str(token).lower())
            and context_tokens_lemma.append(str(token.lemma_).lower())
            for token in context_doc
            if token.pos_ in match_tokens
        ]

        valid_tokens = [
            token
            for token in value_doc
            if token.pos_ in match_tokens
            if str(token).lower() in context_tokens
            or str(token.lemma_).lower() in context_tokens_lemma
        ]

        if len(valid_tokens) < 1:
            self.why_invalid[param_options["id"]] = (
                "Had a problem understanding what the provided value is"
            )
            return {
                "success": False,
                "action": "stop" if required is True else "ignore",
            }

        return {"success": True, "value": value}

    def important(self, param_options: Dict, value: Any):
        if not is_allowed(param_options, "important"):
            return {"success": True, "value": value, "no": True}

        if is_allowed(param_options, "only_latest"):
            context = str(self.context)
        else:
            context = str(self.inputs["input"])

        required = is_allowed(param_options, "required")

        if is_allowed(param_options, "case_sensetive"):
            if isinstance(value, str):
                value = value.lower()
            context = context.lower()

        if value not in context:
            self.why_invalid[param_options["id"]] = (
                "Had a problem understanding what the provided value is"
            )
            return {
                "success": False,
                "action": "stop" if required is True else "ignore",
            }

        return {"success": True, "value": value}

    def accept(self, param_options: Dict, value: Any):
        if not isinstance(param_options["accept"], List):
            return {"success": True, "value": value, "no": True}

        required = is_allowed(param_options, "required")
        accepted_values = param_options["accept"]
        accepted_values_str = list(
            str(accepted_value).lower() for accepted_value in accepted_values
        )
        minimum_score = param_options["minimum_score"]

        if len(accepted_values) < 1:
            return {"success": True, "value": value, "no": True}

        if str(value).lower() in accepted_values_str:
            return {
                "success": True,
                "value": accepted_values[accepted_values_str.index(str(value).lower())],
            }

        joined_accepted_values = ", ".join(
            f"'{accepted_value}'" for accepted_value in accepted_values_str
        )
        why_error = (
            f"(expect one of {joined_accepted_values}) but instead got {str(value)}"
        )

        if is_allowed(param_options, "similar_values") is False:
            self.why_invalid[param_options["id"]] = why_error
            return {
                "success": False,
                "action": "stop" if required is True else "ignore",
            }

        sorted_values = similarity.similarity(str(value), accepted_values_str)

        if len(sorted_values) < 1:
            self.why_invalid[param_options["id"]] = why_error
            return {
                "success": False,
                "action": "stop" if required is True else "ignore",
            }

        wanted_index = sorted_values[0]
        return {"success": True, "value": accepted_values[wanted_index]}

    # ----- Log a new error and add it to the list of errors
    def new_error(self, err: str) -> None:
        self.logger(self, err, "error")
        self.errors.append(err)

    def is_exist(self, dict_value: Dict, key: str) -> bool:
        return True if key in dict_value.keys() else False

    def update_layer(self, key: str):
        self.layer = f"arguments-selection ({key})"
