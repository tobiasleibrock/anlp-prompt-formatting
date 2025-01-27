import os
import json
from collections import Counter
import re

def read_json_files(directory):
    texts = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if "Definition" in data:
                    texts.append(data["Definition"][0])
    return texts

def tokenize(text):
    # Use regex to tokenize text into words
    return re.findall(r'\b\w+\b', text.lower())

def count_word_frequencies(texts):
    counter = Counter()
    for text in texts:
        words = tokenize(text)
        counter.update(words)
    return counter