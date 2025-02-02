"""
Minimal example of using the formatter functionality with model-specific rules.
"""

from reformat import PromptReformatter
from reformat.templates import Example
from reformat.models import get_model_rules


def main():
    # Choose a model to get its specific formatting rules
    model = "llama-3.3-70b-versatile"  # or "gpt-4o", "mixtral-8x7b-32768", etc.

    # Get model-specific formatting rules
    rules = get_model_rules(model)

    # Create reformatter with model-specific rules
    reformatter = PromptReformatter(
        separator_rules=rules["separator_rules"],
        casing_rules=rules["casing_rules"],
        item_formatting_rules=rules["item_formatting_rules"],
        enumeration_rules=rules["enumeration_rules"],
    )

    # Set the template
    reformatter.set_template("general")

    # Create example field values
    field_values = {
        "Task": "Solve this math equation",
        "Examples": [
            Example(input="2+3", output="5"),
            Example(input="4*2", output="8"),
        ],
        "Input": "3*4",
    }

    # Format the prompt
    original_prompt, formatted_prompt, formatting_summary = reformatter.format(
        field_values
    )

    # Print results
    print(f"Using formatting rules for model: {model}")
    print("\nOriginal Prompt:")
    print("=" * 40)
    print(original_prompt)
    print("\nFormatted Prompt:")
    print("=" * 40)
    print(formatted_prompt)
    print("\nFormatting Rules Used:")
    print("=" * 40)
    for rule_type, rule_name in formatting_summary.items():
        print(f"{rule_type}: {rule_name}")


if __name__ == "__main__":
    main()
