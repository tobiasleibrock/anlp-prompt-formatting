from dotenv import load_dotenv
from reformat import PromptImprover
from reformat.templates import Example


def main():
    load_dotenv()

    improver = PromptImprover()

    field_values = {
        "Task": "Solve this math equation",
        "Examples": [
            Example(input="2+3", output="5"),
            Example(input="4*2", output="8"),
        ],
        "Input": "3*4",
    }

    print("Improving prompt format...")
    print("Running 2 iterations with 2 candidates each...")

    result = improver.improve(
        field_values=field_values,
        num_candidates=2,
        num_iterations=2,
    )

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

    print("\nImprovement Details:")
    print(f"Candidates evaluated: {result['num_candidates_evaluated']}")
    print("Score distribution:")
    scores = result["all_scores"]
    if scores:
        print(f"  Min: {min(scores):.3f}")
        print(f"  Max: {max(scores):.3f}")
        print(f"  Avg: {sum(scores) / len(scores):.3f}")


if __name__ == "__main__":
    main()
