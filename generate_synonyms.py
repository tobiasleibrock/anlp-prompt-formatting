import torch
from transformers import BertTokenizer, BertForMaskedLM
from sentence_transformers import SentenceTransformer, util

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_synonyms(text, target_word, top_k=5):
    tokens = tokenizer.tokenize(text)
    tokenized = tokenizer(text, return_tensors="pt")
    mask_index = tokens.index(target_word) + 1 # Offset 1 because [CLS] is first token
    tokenized['input_ids'][0, mask_index] = tokenizer.mask_token_id

    with torch.no_grad():
        outputs = model(**tokenized)
        logits = outputs.logits
        mask_token_logits = logits[0, mask_index]
        top_tokens = torch.topk(mask_token_logits, top_k).indices.tolist()

    return [tokenizer.decode([token]).strip() for token in top_tokens]


def semantic_similarity(original, rephrased):
    embeddings = semantic_model.encode([original, rephrased], convert_to_tensor=True)
    return util.cos_sim(embeddings[0], embeddings[1]).item()


def rephrase(prompt, target_word, top_k=5):
    results = []

    synonyms = generate_synonyms(prompt, target_word.lower(), top_k)
    for synonym in synonyms:
        rephrased_prompt = prompt.replace(target_word, synonym)
        similarity = semantic_similarity(prompt, rephrased_prompt)

        # Reject prompts that are semantically dissimilar
        if similarity < 0.90:
            continue

        results.append({
            "prompt": prompt,
            "rephrased_prompt": rephrased_prompt,
            "synonym": synonym,
            "similarity": similarity
        })

    return results
