from sentence_transformers import SentenceTransformer, util
import json

def semantic_similarity(original, rephrased):
    embeddings = SentenceTransformer("all-MiniLM-L6-v2").encode([original, rephrased], convert_to_tensor=True)
    return util.cos_sim(embeddings[0], embeddings[1]).item()

def apply_synonym_rules(input_text, json_path, similarity_threshold=0.95):

    # Load performance data from JSON
    with open(json_path, "r") as f:
        synonyms_data = json.load(f)

    # Build a reverse lookup dictionary mapping each synonym to its category (original key)
    synonym_to_category = {}
    for category, synonyms in synonyms_data.items():
        for synonym in synonyms.keys():
            synonym_to_category[synonym] = category

    words = input_text.split()  # Split the input text into words
    augmented_text = words[:]   # Create a copy of the text to modify

    for idx, word in enumerate(words):
        # Identify the category for this word
        if word in synonyms_data:
            category = word  # The word is an original key
        elif word in synonym_to_category:
            category = synonym_to_category[word]  # The word is a synonym
        else:
            continue  # Word is not in the JSON, move to the next word

        synonyms = synonyms_data[category]  # Get all words in the category

        # Collect better-performing synonyms
        better_synonyms = []
        for synonym, stats in synonyms.items():
            if synonym != word and (stats["correct"] / stats["total"]) > (synonyms[word]["correct"] / synonyms[word]["total"]):
                better_synonyms.append((synonym, (stats["correct"] / stats["total"])))

        # Sort synonyms by performance (highest to lowest)
        better_synonyms.sort(key=lambda x: x[1], reverse=True)

        for synonym, _ in better_synonyms:
            # Replace the word with the synonym
            temp_text = " ".join(augmented_text[:idx] + [synonym] + augmented_text[idx+1:])

            # Check semantic similarity
            if semantic_similarity(" ".join(words), temp_text) >= similarity_threshold:
                augmented_text[idx] = synonym
                break  # Stop once a valid synonym is found

    return " ".join(augmented_text)
