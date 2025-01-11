# Reformat

A Python package for intelligent prompt reformatting using expert rules.

## Installation

```bash
pip install reformat
```

## Usage

### As a Python Package

```python
from reformat import PromptReformatter

# Create a reformatter instance with model-specific rules
reformatter = PromptReformatter()

# Format a prompt with expert rules
formatted_prompt = reformatter.format("Your prompt here")
```

### Command Line Interface

The package can be used directly from the command line:

```bash
# Format a prompt for a specific model
reformat "Your prompt text" -m openai

# Read from stdin and write to a file
echo "Your prompt" | reformat -m anthropic -o output.txt

# Get verbose output with formatting details
reformat "Your prompt" -m llama -v
```

Available options:

- `-m, --model`: Target model (choices: general, openai, anthropic, llama, deepseek)
- `-o, --output`: Output file (default: stdout)
- `-v, --verbose`: Print additional information about applied rules

## Supported Models

- GPT-4o (gpt-4o)
- GPT-4o-mini (gpt-4o-mini)
- Llama 3.1 70B (llama-3.1-70b-versatile)
- Llama 3.1 8B (llama-3.1-8b-instant)
- Mixtral 8x7B (mixtral-8x7b-32768)
- Gemma 2 9B (gemma2-9b-it)
- General (default rules)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
