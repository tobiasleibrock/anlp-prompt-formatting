# Reformat

A Python package for intelligent prompt reformatting and improvement using expert rules and LLM evaluation.

## Installation

```bash
pip install reformat
```

## Features

- **Expert Rule-Based Formatting**: Apply predefined formatting rules optimized for different LLM models
- **Response-Driven Format Improvement**: Use LLM evaluation to find formats that produce better responses
- **Model-Specific Optimization**: Support for various LLM models with customized formatting rules
- **Random Search Optimization**: Explore different format combinations to find the best performing ones

## Usage

### As a Python Package

#### 1. Basic Prompt Formatting

Use predefined expert rules to format prompts:

```python
from reformat import PromptReformatter

# Create a reformatter with default rules
reformatter = PromptReformatter()

# Format a prompt
formatted_prompt = reformatter.format("Your prompt here")

# Use model-specific rules
reformatter = PromptReformatter(
    separator_rules=[...],  # Custom separator rules
    casing_rules=[...],     # Custom casing rules
    item_formatting_rules=[...],  # Custom item formatting rules
    enumeration_rules=[...],      # Custom enumeration rules
)
```

#### 2. Response-Driven Format Improvement

Use LLM evaluation to find formats that produce better responses:

```python
from reformat import PromptImprover

improver = PromptImprover(
    model="llama-3.3-70b-versatile",  # Model to use for responses
    api_key="your-api-key"            # Groq API key
)

result = improver.improve(
    "Your prompt here",
    num_candidates=10,  # Number of formats to try per iteration
    num_iterations=3,   # Number of search iterations
    temperature=0.1     # Temperature for exploration
)
```

### Command Line Interface

The package provides two main commands:

#### 1. Format Command

Format a prompt using expert rules for a specific model:

```bash
reformat format "Your prompt text" -m llama-3.3-70b-versatile

echo "Your prompt" | reformat format -m llama-3.1-8b-instant -o output.txt

reformat format "Your prompt" -m general -v
```

Available options for format:

- `-m, --model`: Target model (choices: general, gpt-4o, gpt-4o-mini, llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768, gemma2-9b-it)
- `-o, --output`: Output file (default: stdout)
- `-v, --verbose`: Print additional information about applied rules

#### 2. Improve Command

Improve prompt format by evaluating response quality:

```bash
# Improve a prompt's format
reformat improve "Your prompt text" -k your-api-key

# Customize search parameters
reformat improve "Your prompt" -n 20 -i 5 -t 0.2 -k your-api-key

# Get verbose output with improvement details
reformat improve "Your prompt" -k your-api-key -v
```

Available options for improve:

- `-k, --api-key`: Groq API key (required unless set as GROQ_API_KEY env variable)
- `-n, --num-candidates`: Number of format candidates to try per iteration (default: 10)
- `-i, --iterations`: Number of search iterations (default: 3)
- `-t, --temperature`: Temperature for exploration (0 = greedy, 1 = random)
- `-o, --output`: Output file (default: stdout)
- `-v, --verbose`: Print additional information about improvement process

## Supported Models

The package supports the following models with optimized formatting rules:

- GPT-4o (gpt-4o)
- GPT-4o-mini (gpt-4o-mini)
- Llama 3.3 70B (llama-3.3-70b-versatile)
- Llama 3.1 8B (llama-3.1-8b-instant)
- Mixtral 8x7B (mixtral-8x7b-32768)
- Gemma 2 9B (gemma2-9b-it)
- General (default rules)

## Format Evaluation

The improver evaluates format quality by comparing responses based on:

1. Accuracy and correctness of information
2. Completeness of the answer
3. Relevance to the query
4. Clarity and coherence of the response

The evaluation is done by the Llama 70B model, which compares responses from different formats and assigns scores between 0 and 1, where:

- 0 = New response is worse or equal to original
- 1 = New response is significantly better than original

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
