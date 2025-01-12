import torch
from transformers import BertTokenizer, BertForMaskedLM
from sentence_transformers import SentenceTransformer, util
import itertools

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

def rephrase(prompt, target_words, top_k=5, similarity_threshold=0.95):
    results = []
    
    # Generate synonyms for each target word
    synonyms_list = [
        generate_synonyms(prompt, target_word.lower(), top_k) 
        for target_word in target_words
    ]

    # Generate all combinations of synonyms (Cartesian product)
    for synonym_combination in itertools.product(*synonyms_list):
        rephrased_prompt = prompt
        for target_word, synonym in zip(target_words, synonym_combination):
            rephrased_prompt = rephrased_prompt.replace(target_word, synonym)

        # Check semantic similarity
        similarity = semantic_similarity(prompt, rephrased_prompt)

        # Reject prompts that are semantically dissimilar
        if similarity < similarity_threshold:
            continue

        results.append({
            "prompt": prompt,
            "rephrased_prompt": rephrased_prompt,
            "target_words": target_words,
            "synonyms": synonym_combination,
            "similarity": similarity
        })

    return results
