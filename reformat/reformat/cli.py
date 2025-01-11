"""
Command-line interface for the reformat package.
"""

import argparse
import sys
from typing import Optional
from .reformatter import PromptReformatter
from .models import get_model_rules


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Reformat prompts using expert rules for different LLM models."
    )

    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        help="Input prompt text. If not provided, reads from stdin",
    )

    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="general",
        choices=[
            "general",
            "gpt-4o",
            "gpt-4o-mini",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        help="Target model for formatting rules (default: general)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file (default: stdout)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print additional information about applied rules",
    )

    return parser.parse_args()


def read_input(input_arg: Optional[str] = None) -> str:
    """Read input from argument or stdin."""
    if input_arg:
        return input_arg

    # Check if there's data in stdin
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()

    print(
        "Error: No input provided. Please provide input text or pipe it through stdin."
    )
    sys.exit(1)


def write_output(text: str, output_file: Optional[str] = None) -> None:
    """Write output to file or stdout."""
    if output_file:
        with open(output_file, "w") as f:
            f.write(text)
    else:
        print(text)


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    # Read input
    prompt = read_input(args.input)

    # Get model-specific rules
    rules = get_model_rules(args.model)

    # Create reformatter with model-specific rules
    reformatter = PromptReformatter(**rules)

    # Format the prompt
    formatted_prompt = reformatter.format(prompt)

    # Handle verbose output
    if args.verbose:
        print(f"Model: {args.model}", file=sys.stderr)
        print("Applied formatting:", file=sys.stderr)
        print(f"  Input length: {len(prompt)}", file=sys.stderr)
        print(f"  Output length: {len(formatted_prompt)}", file=sys.stderr)
        print("---", file=sys.stderr)

    # Write output
    write_output(formatted_prompt, args.output)


if __name__ == "__main__":
    main()
