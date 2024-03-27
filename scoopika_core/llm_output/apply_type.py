import json

def apply_json(value):
	if isinstance(value, dict):
		return value

	return json.loads(value)


def apply_list(value):
	if isinstance(value, list):
		value

	return [value]

types_funcs = [
	["string", str],
	["str", str],
	["int", int],
	["number", int],
	["float", float],
	["object", dict],
	["dict", dict],
	["json", apply_json],
	["array", apply_list],
	["list", apply_list]
]

types = {key.casefold(): func for key, func in types_funcs}

def apply_type(arg_type, value):
	if arg_type["root"] not in types.keys():
		return {"success": True, "value": value}

	type_func = types[arg_type["root"]]

	if arg_type not in ["array", "list"]:
		try:
			return {"success": True, "value": type_func(value)}
		except:
			return {"success": False, "error": f"Can't apply a type {arg_type['root']} to the value {str(value)}"}

	list_value = type_func(value)

	list_items = list(apply_type({"root": arg_type["items"]}, item) for item in list_value)
	valid_items = [item["value"] for item in list_items if item["success"] is True]

	if len(valid_items) == 0 and len(list_value) != 0:
		return {"success": False, "error": f"List items types are not valid"}

	return {"success": True, "value": valid_items}