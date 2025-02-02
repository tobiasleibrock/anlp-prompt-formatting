"""
Command-line interface for the reformat package.
"""

import argparse
import sys
import os.path
import json
from typing import Optional, List, Dict, Any
from .reformatter import PromptReformatter
from .models import get_model_rules
from .improver import PromptImprover
from synonym_rules import apply_synonym_rules
from .templates import DEFAULT_TEMPLATES, Example, PromptTemplate


def get_multiline_input(prompt: str) -> str:
    """Get multiline input from user. Empty line ends input."""
    print(f"{prompt} (Enter empty line to finish):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


def get_examples_input() -> List[Example]:
    """Interactively get examples from user."""
    examples = []
    print("\nEnter examples (empty line to finish)")

    while True:
        if examples:
            print(f"\nExample {len(examples) + 1}:")
        else:
            print("\nExample 1:")

        print("Input (empty line to finish examples):")
        input_text = get_multiline_input("Enter input")
        if not input_text:
            break

        print("Output:")
        output_text = get_multiline_input("Enter output")
        if not output_text:
            break

        examples.append(Example(input=input_text, output=output_text))

        print("\nAdd another example? (y/N)")
        if input().lower() != "y":
            break

    return examples


def get_options_input() -> List[str]:
    """Interactively get options from user."""
    options = []
    while True:
        print(f"\nEnter option {len(options) + 1} (or empty line to finish):")
        option = input().strip()
        if not option:
            break
        options.append(option)

        if len(options) >= 2:  # Need at least 2 options
            print("Add another option? (y/N)")
            if input().lower() != "y":
                break

    return options


def get_field_values(template: PromptTemplate) -> Dict[str, Any]:
    """Interactively get values for template fields."""
    field_values = {}

    print(f"\nTemplate: {template.name}")
    print(f"Description: {template.description}")
    print(f"Required fields: {template.required_fields}")
    print(
        f"Optional fields: {[f for f in template.fields if f not in template.required_fields]}"
    )

    for field in template.fields:
        is_required = field in template.required_fields
        field_prompt = f"\n{field}" + (
            " (required)" if is_required else " (optional - press enter to skip)"
        )

        if field == "Examples":
            print(f"\n{field_prompt}")
            examples = get_examples_input()
            if examples:
                field_values[field] = examples
        elif field == "Options":
            print(f"\n{field_prompt}")
            options = get_options_input()
            if options:
                field_values[field] = options
        else:
            print(f"\n{field_prompt}")
            value = get_multiline_input("Enter value")
            if value or is_required:
                field_values[field] = value

    return field_values


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Reformat prompts using expert rules for different LLM models."
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Format command
    format_parser = subparsers.add_parser(
        "format", help="Format a prompt using expert rules"
    )
    format_parser.add_argument(
        "-t",
        "--template",
        type=str,
        required=True,
        choices=list(DEFAULT_TEMPLATES.keys()),
        help="Template to use for formatting",
    )
    format_parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="general",
        choices=[
            "general",
            "gpt-4o",
            "gpt-4o-mini",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        help="Target model for formatting rules (default: general)",
    )
    format_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file (default: stdout)",
    )
    format_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print additional information about applied rules",
    )

    # Improve command
    improve_parser = subparsers.add_parser(
        "improve", help="Improve prompt format using LLM judge"
    )
    improve_parser.add_argument(
        "-t",
        "--template",
        type=str,
        required=True,
        choices=list(DEFAULT_TEMPLATES.keys()),
        help="Template to use for formatting",
    )
    improve_parser.add_argument(
        "-k",
        "--api-key",
        type=str,
        help="API key for LLM service",
    )
    improve_parser.add_argument(
        "-n",
        "--num-candidates",
        type=int,
        default=10,
        help="Number of format candidates to try per iteration",
    )
    improve_parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=3,
        help="Number of search iterations",
    )
    improve_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file (default: stdout)",
    )
    improve_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print additional information about improvement process",
    )

    return parser.parse_args()


def write_output(text: str, output_file: Optional[str] = None) -> None:
    """Write output to file or stdout."""
    if output_file:
        with open(output_file, "w") as f:
            f.write(text)
    else:
        print(text)


def format_command(args: argparse.Namespace) -> None:
    """Handle the format command."""
    # Get model-specific rules
    rules = get_model_rules(args.model)

    # Create reformatter with model-specific rules and template
    reformatter = PromptReformatter(**rules)
    reformatter.set_template(args.template)
    template = reformatter.template

    # Get field values interactively
    field_values = get_field_values(template)

    # Apply synonym rules
    model_name = args.model.replace(".", "_")
    synonym_rules_path = f"models/{model_name}_synonym_rules.json"

    try:
        # Format the prompt
        original_prompt, formatted_prompt, formatting_summary = reformatter.format(
            field_values
        )

        if os.path.exists(synonym_rules_path):
            formatted_prompt = apply_synonym_rules(
                formatted_prompt, synonym_rules_path, 0.99
            )

        # Print formatting information
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

        # Handle verbose output
        if args.verbose:
            print("\nTemplate Information:", file=sys.stderr)
            print(f"Model: {args.model}", file=sys.stderr)
            print(f"Template: {args.template}", file=sys.stderr)
            print("Template fields:", file=sys.stderr)
            print(f"  Required: {template.required_fields}", file=sys.stderr)
            print(
                f"  Optional: {[f for f in template.fields if f not in template.required_fields]}",
                file=sys.stderr,
            )
            print("Provided fields:", file=sys.stderr)
            for field, value in field_values.items():
                if isinstance(value, list):
                    print(f"  {field}: {len(value)} items", file=sys.stderr)
                else:
                    print(f"  {field}: {len(str(value))} chars", file=sys.stderr)

        # Write to output file if specified
        if args.output:
            with open(args.output, "w") as f:
                f.write("Original Prompt:\n")
                f.write("=" * 40 + "\n")
                f.write(original_prompt + "\n\n")
                f.write("Formatted Prompt:\n")
                f.write("=" * 40 + "\n")
                f.write(formatted_prompt + "\n\n")
                f.write("Formatting Rules Used:\n")
                f.write("=" * 40 + "\n")
                for rule_type, rule_name in formatting_summary.items():
                    f.write(f"{rule_type}: {rule_name}\n")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def improve_command(args: argparse.Namespace) -> None:
    """Handle the improve command."""
    # Create improver
    improver = PromptImprover(api_key=args.api_key)

    # Get template and field values interactively
    reformatter = PromptReformatter()
    reformatter.set_template(args.template)  # Use the specified template
    field_values = get_field_values(reformatter.template)

    print(f"\nImproving prompt with template: {args.template}")
    print(
        f"Running {args.iterations} iterations with {args.num_candidates} candidates each..."
    )

    # Improve the prompt format
    result = improver.improve(
        field_values=field_values,
        num_candidates=args.num_candidates,
        num_iterations=args.iterations,
    )

    # Print results
    print("\nOriginal Prompt:")
    print("=" * 40)
    print(result["original_prompt"])

    print("\nImproved Prompt:")
    print("=" * 40)
    print(result["improved_prompt"])

    print("\nOriginal Response:")
    print("=" * 40)
    print(result["original_response"])

    print("\nImproved Response:")
    print("=" * 40)
    print(result["improved_response"])

    print("\nBest Format Found:")
    print("=" * 40)
    if result["best_format"]:
        for rule_type, rule_name in result["best_format"].items():
            print(f"{rule_type}: {rule_name}")
    else:
        print("No improvement found")

    print(f"\nImprovement Score: {result['improvement_score']:.3f}")

    # Handle verbose output
    if args.verbose:
        print("\nImprovement Details:", file=sys.stderr)
        print(
            f"Candidates evaluated: {result['num_candidates_evaluated']}",
            file=sys.stderr,
        )
        print("Score distribution:", file=sys.stderr)
        scores = result["all_scores"]
        if scores:
            print(f"  Min: {min(scores):.3f}", file=sys.stderr)
            print(f"  Max: {max(scores):.3f}", file=sys.stderr)
            print(f"  Avg: {sum(scores) / len(scores):.3f}", file=sys.stderr)

    # Write to output file if specified
    if args.output:
        with open(args.output, "w") as f:
            f.write("Original Prompt:\n")
            f.write("=" * 40 + "\n")
            f.write(result["original_prompt"] + "\n\n")
            f.write("Improved Prompt:\n")
            f.write("=" * 40 + "\n")
            f.write(result["improved_prompt"] + "\n\n")
            f.write("Original Response:\n")
            f.write("=" * 40 + "\n")
            f.write(result["original_response"] + "\n\n")
            f.write("Improved Response:\n")
            f.write("=" * 40 + "\n")
            f.write(result["improved_response"] + "\n\n")
            f.write("Best Format Found:\n")
            f.write("=" * 40 + "\n")
            if result["best_format"]:
                for rule_type, rule_name in result["best_format"].items():
                    f.write(f"{rule_type}: {rule_name}\n")
            else:
                f.write("No improvement found\n")
            f.write(f"\nImprovement Score: {result['improvement_score']:.3f}\n")


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    if args.command == "format":
        format_command(args)
    elif args.command == "improve":
        improve_command(args)
    else:
        print("Error: No command specified. Use --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
