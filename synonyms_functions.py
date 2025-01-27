import torch
from transformers import BertTokenizer, BertForMaskedLM
from sentence_transformers import SentenceTransformer, util
import itertools
import json
from prompt_template import PromptTemplate
from collections import defaultdict

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

def save_progress_to_json(filename, data):
    hierarchical_data = {}
    for (word, synonym), value in data.items():
        if word not in hierarchical_data:
            hierarchical_data[word] = {}
        hierarchical_data[word][synonym] = value
    
    with open(filename, "w") as f:
        json.dump(hierarchical_data, f, indent=4)

def load_progress_from_json(filename):
    try:
        with open(filename, "r") as f:
            hierarchical_data = json.load(f)
        # Convert hierarchical structure back to the original format
        flat_data = {}
        for word, synonyms in hierarchical_data.items():
            for synonym, value in synonyms.items():
                flat_data[(word, synonym)] = value
        return flat_data
    except FileNotFoundError:
        return {}

def temp(client, fname, tasks, target_words, Fcasing, S1, Fitem2, Fitem1, tasks_path="natural-instructions/tasks/"):
    # Load previous progress if available
    fname = "word_synonym_performance.json"
    loaded_data = load_progress_from_json(fname)

    # Dictionary to store scores for each word-synonym pair
    word_synonym_performance = defaultdict(lambda: {"total": 0, "correct": 0}, loaded_data)

    # Iterate through all tasks and instances
    for task in tasks:
        print(f"Processing task: {task}")

        with open(tasks_path + task, "r") as f:
            data = json.load(f)

        template = PromptTemplate(model_instructions=data["Definition"][0], 
                                task="", 
                                fields=" ", 
                                demonstrations=data["Positive Examples"][0] + data["Negative Examples"][0], 
                                separator=": ", 
                                word_separator=" ", 
                                casing=Fcasing[0], 
                                field_separator=S1[2], 
                                item_formatter=Fitem2[4], 
                                enumerator_format=Fitem1[0]
                                )
        formatted_prompt = template.construct_prompt()
        modified_templates = rephrase(prompt=formatted_prompt, target_words=target_words, top_k=3, similarity_threshold=0.8)

        for i in range(len(data["Instances"])):  # Iterate over all instances
            input = data["Instances"][i]["input"]
            output = data["Instances"][i]["output"][0]

            # Evaluate the original prompt
            messages = [
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": input},
            ]
            response = client.chat.completions.create(model=model, messages=messages, temperature=0.75)
            original_agreement = output == response.choices[0].message.content

            key = (target_words[0], target_words[0])
            word_synonym_performance[key]["total"] += 1
            if original_agreement:
                word_synonym_performance[key]["correct"] += 1

            # Evaluate each modified prompt
            for modified_template in modified_templates:
                target_words = modified_template['target_words']
                synonyms = modified_template['synonyms']

                messages = [
                    {"role": "system", "content": modified_template['rephrased_prompt']},
                    {"role": "user", "content": input},
                ]
                response = client.chat.completions.create(model=model, messages=messages, temperature=0.75)
                agreement = output == response.choices[0].message.content

                # Update the performance tracking
                for word, synonym in zip(target_words, synonyms):
                    key = (word, synonym)
                    word_synonym_performance[key]["total"] += 1
                    if agreement:
                        word_synonym_performance[key]["correct"] += 1

            # Save progress every 100 instances
            if (i + 1) % 100 == 0:
                print(f"Saving progress after {i + 1} instances...")
                save_progress_to_json(fname, word_synonym_performance)

    # Save the final performance scores
    save_progress_to_json(fname, word_synonym_performance)

def augment_text_with_synonyms(input_text, json_path, similarity_threshold=0.95):

    # Load performance data from JSON
    with open(json_path, "r") as f:
        performance_data = json.load(f)

    words = input_text.split()  # Split the input text into words
    augmented_text = words[:]   # Create a copy of the text to modify

    for idx, word in enumerate(words):
        if word in performance_data:  # Check if the word is in the JSON file
            synonyms = performance_data[word]
            
            # Collect synonyms that performed better than the original word
            better_synonyms = []
            for synonym, stats in synonyms.items():
                if synonym != word and stats["correct"] > synonyms[word]["correct"]:
                    better_synonyms.append((synonym, stats["correct"]))

            # Sort better synonyms by performance (highest to lowest)
            better_synonyms.sort(key=lambda x: x[1], reverse=True)

            for synonym, _ in better_synonyms:
                # Replace the word with the synonym
                temp_text = " ".join(augmented_text[:idx] + [synonym] + augmented_text[idx+1:])

                # Check semantic similarity
                if semantic_similarity(" ".join(words), temp_text) >= similarity_threshold:
                    augmented_text[idx] = synonym
                    break  # Stop once a valid synonym is found

    return " ".join(augmented_text)