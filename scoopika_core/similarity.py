from typing import List
import torch.nn.functional as F
import numpy as np
from .models import similarity_tokenizer, similarity_model
from .pools import average_pool


def similarity(source, targets: List, minimum_score):
    inputs = [str(source)] + targets

    batch_dict = similarity_tokenizer(
        inputs, max_length=512, padding=True, truncation=True, return_tensors="pt"
    )

    outputs = similarity_model(**batch_dict)
    embeddings = average_pool(outputs.last_hidden_state, batch_dict["attention_mask"])
    embeddings = F.normalize(embeddings, p=2, dim=1)
    scores = (embeddings[:1] @ embeddings[1:].T) * 100
    scores = scores.detach().numpy()
    print(scores[0])
    scores = [list(score for score in scores[0] if score >= minimum_score)]

    sorted_indices = np.argsort(scores)[0][::-1]
    sorted_values = [targets[i] for i in sorted_indices]

    return sorted_indices
