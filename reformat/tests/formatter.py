from reformat import PromptReformatter
from reformat.templates import Example
from reformat.models import get_model_rules


def main():
    model = "llama-3.3-70b-versatile"
    rules = get_model_rules(model)

    reformatter = PromptReformatter(
        separator_rules=rules["separator_rules"],
        casing_rules=rules["casing_rules"],
        item_formatting_rules=rules["item_formatting_rules"],
        enumeration_rules=rules["enumeration_rules"],
    )

    reformatter.set_template("general")

    field_values = {
        "Task": "Solve this math equation",
        "Examples": [
            Example(input="2+3", output="5"),
            Example(input="4*2", output="8"),
        ],
        "Input": "3*4",
    }

    original_prompt, formatted_prompt, formatting_summary = reformatter.format(
        field_values
    )

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
