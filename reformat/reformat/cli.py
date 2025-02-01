"""
Command-line interface for the reformat package.
"""

import argparse
import sys
from typing import Optional
from .reformatter import PromptReformatter
from .models import get_model_rules
from .improver import PromptImprover


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
        "input",
        nargs="?",
        type=str,
        help="Input prompt text. If not provided, reads from stdin",
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
        "input",
        nargs="?",
        type=str,
        help="Input prompt text. If not provided, reads from stdin",
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
        "-t",
        "--temperature",
        type=float,
        default=0.1,
        help="Temperature for exploration (0 = greedy, 1 = random)",
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


def format_command(args: argparse.Namespace) -> None:
    """Handle the format command."""
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


def improve_command(args: argparse.Namespace) -> None:
    """Handle the improve command."""
    # Read input
    prompt = read_input(args.input)

    # Create improver
    improver = PromptImprover(api_key=args.api_key)

    # Improve the prompt
    result = improver.improve(
        prompt,
        num_candidates=args.num_candidates,
        num_iterations=args.iterations,
        temperature=args.temperature,
    )

    # Handle verbose output
    if args.verbose:
        print("Improvement results:", file=sys.stderr)
        print(
            f"  Candidates evaluated: {result['num_candidates_evaluated']}",
            file=sys.stderr,
        )
        print(f"  Best score: {result['improvement_score']:.3f}", file=sys.stderr)
        print(f"  Best format:", file=sys.stderr)
        for k, v in result["best_format"].items():
            print(f"    {k}: {v}", file=sys.stderr)
        print("---", file=sys.stderr)

    # Write improved prompt
    write_output(result["improved_prompt"], args.output)


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
