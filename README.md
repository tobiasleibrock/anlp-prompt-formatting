# NLP Lab Course: Prompt Formatting

This project was developed as part of a Masters Seminar at the Technical University of Munich (TUM) focused on exploring and optimizing prompt formatting for large language models. With ever increasing context lengths and prompts, formatting correctly to ensure the model is able to work with them is crucial.

The project report and poster can be found inside the `bin/` directory as PDF files.

## Project Overview

This project consists of two main components:

1. **Prompt Format Exploration**: Scripts in the root directory for discovering and testing optimal prompt formatting approaches using the Natural Instructions dataset. The exploration uses random search over various formatting classes to find the best performing combinations for different models.

2. **Reformat Package**: A Python package in the `reformat/` directory that provides tools for improving prompts using:
   - Expert rules-based formatting with predefined templates
   - LLM-driven format improvement through random search and response quality evaluation with predefined templates
   - Synonym replacement optimization based on empirical performance data

## Reformat Package

The `reformat/` directory contains a Python package that can be used to improve prompts in two ways:

### Expert Rules Mode

- Uses predefined formatting rules optimized for specific models
- Applies templates with consistent formatting patterns
- Supports multiple models including GPT-4, Llama, Mixtral, and Gemma

### LLM-Driven Improvement

- Uses an LLM to evaluate and rank different format variations
- Performs random search over formatting options
- Optimizes based on response quality metrics

### Synonym Optimization

Both modes can utilize the synonym replacement module that:

- Maintains a database of empirically discovered better-performing alternatives
- Replaces words with synonyms that have shown better performance
- Preserves semantic similarity during replacements

## Installation

Installation and usage instructions can be found in the [Reformat Package README](reformat/README.md).

## Models

The package includes optimized formatting rules for:

- GPT-4 Optimized (gpt-4o)
- GPT-4 Mini Optimized (gpt-4o-mini)
- Llama 3.3 70B (llama-3.3-70b-versatile)
- Llama 3.1 8B (llama-3.1-8b-instant)
- Mixtral 8x7B (mixtral-8x7b-32768)
- Gemma 2 9B (gemma2-9b-it)

## License

This project is part of academic research at TUM. Please contact the authors for usage rights.
