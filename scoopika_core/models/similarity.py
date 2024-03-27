from transformers import AutoTokenizer, AutoModel
import os

try:
    model_id = os.environ.get("similarity_model")
except:
    model_id = "thenlper/gte-small"

if model_id is None:
    model_id = "thenlper/gte-small"

similarity_tokenizer = AutoTokenizer.from_pretrained(model_id)
similarity_model = AutoModel.from_pretrained(model_id)
