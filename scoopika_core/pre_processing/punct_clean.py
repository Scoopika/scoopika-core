from ..nlp import nlp


def punct_clean(text: str, joiner: str = "") -> str:
    doc = nlp(text)

    clean_tokens = list(str(token) for token in doc if token.pos_ != "PUNCT")
    clean_text = joiner.join(clean_tokens)

    return clean_text
