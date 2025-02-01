"""
Test notebook for the reformat package.
Copy each cell (separated by ###########) into a Jupyter notebook.
"""

############### [Cell 1] - Imports and Setup
import sys
from pathlib import Path
import random
import json
import os
from dotenv import load_dotenv

# Add the reformat package to path if needed
package_path = Path.cwd().parent
if str(package_path) not in sys.path:
    sys.path.append(str(package_path))

from reformat import PromptReformatter, PromptImprover
from reformat.rules import (
    SeparatorRule,
    CasingRule,
    ItemFormattingRule,
    EnumerationRule,
)

# Load environment variables (make sure you have GROQ_API_KEY set)
load_dotenv()

############### [Cell 2] - Test Data
# Sample prompts for testing
test_prompts = {
    "qa": """Write a detailed explanation of how photosynthesis works in plants. 
Include the main steps and components involved.""",
    "coding": """Write a Python function that implements binary search.
Include error handling and documentation.""",
    "analysis": """Analyze the following text for its main themes and literary devices:
"Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;"
""",
    "instruction": """Create a step-by-step guide for making a perfect omelette.
Include ingredients needed and common mistakes to avoid.""",
    "creative": """Write a short story about a time traveler who accidentally changes history.
Focus on the consequences of their actions.""",
}


############### [Cell 3] - Test Response Quality Improvement
def test_response_improvement(prompt: str, model: str = "llama-3.3-70b-versatile"):
    """Test how formatting affects response quality."""
    print("=== Testing Response Improvement ===")
    print("\nOriginal Prompt:")
    print(prompt)

    improver = PromptImprover(model=model)
    result = improver.improve(
        prompt,
        num_candidates=3,  # Small number for testing
        num_iterations=2,
    )

    print("\nOriginal Response:")
    print(result["original_response"])
    print("\nImproved Response:")
    print(result["improved_response"])
    print(f"\nImprovement Score: {result['improvement_score']:.3f}")
    print("\nBest Format Used:")
    print(json.dumps(result["best_format"], indent=2))

    return result


# Test with different prompts
for prompt_type, prompt in list(test_prompts.items())[:2]:  # Test first two prompts
    print(f"\n\n{'=' * 50}")
    print(f"Testing {prompt_type} prompt")
    print("=" * 50)
    result = test_response_improvement(prompt)


############### [Cell 4] - Compare Models
def compare_models(prompt: str):
    """Compare response quality improvement across different models."""
    models = [
        "llama-3.3-70b-versatile",  # High quality
        "llama-3.1-8b-instant",  # Fast
    ]

    results = {}
    for model in models:
        print(f"\n=== Testing {model} ===")
        improver = PromptImprover(model=model)
        result = improver.improve(prompt, num_candidates=3, num_iterations=1)
        results[model] = result

        print(f"\nImprovement Score: {result['improvement_score']:.3f}")
        print("\nOriginal Response:")
        print(
            result["original_response"][:200] + "..."
            if len(result["original_response"]) > 200
            else result["original_response"]
        )
        print("\nImproved Response:")
        print(
            result["improved_response"][:200] + "..."
            if len(result["improved_response"]) > 200
            else result["improved_response"]
        )

    return results


# Test model comparison
test_prompt = test_prompts["analysis"]
print("\nComparing models on analysis prompt:")
model_results = compare_models(test_prompt)


############### [Cell 5] - Format Impact Analysis
def analyze_format_impact(prompt: str, num_trials: int = 5):
    """Analyze how different formatting rules impact response quality."""
    improver = PromptImprover()
    results = []

    # Test each separator type
    separator_rules = SeparatorRule.get_default_rules()
    original_response = improver.get_model_response(prompt)

    for separator in separator_rules:
        candidate = improver.sample_candidate()
        candidate.separator_rule = separator

        formatted = improver.format_prompt(prompt, candidate)
        response = improver.get_model_response(formatted)
        score = improver.evaluate_format(original_response, response)

        results.append(
            {
                "type": "separator",
                "name": separator.name,
                "score": score,
                "response": response,
            }
        )

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    print("Top performing formats and their responses:")
    for i, result in enumerate(results[:2], 1):
        print(f"\n{i}. {result['type'].title()}: {result['name']}")
        print(f"Score: {result['score']:.3f}")
        print("Response excerpt:")
        print(
            result["response"][:200] + "..."
            if len(result["response"]) > 200
            else result["response"]
        )


# Test format impact
print("\nAnalyzing format impact on coding prompt:")
analyze_format_impact(test_prompts["coding"])


############### [Cell 6] - Interactive Testing
def interactive_improve(
    prompt: str,
    model: str = "llama-3.3-70b-versatile",
    num_candidates: int = 3,
    num_iterations: int = 2,
):
    """Interactive function to test response improvement."""
    improver = PromptImprover(model=model)

    print("Starting response quality improvement...")
    result = improver.improve(
        prompt, num_candidates=num_candidates, num_iterations=num_iterations
    )

    print("\nOriginal Response:")
    print(result["original_response"])
    print("\nImproved Response:")
    print(result["improved_response"])
    print(f"\nImprovement Score: {result['improvement_score']:.3f}")
    print("\nBest Format Used:")
    print(json.dumps(result["best_format"], indent=2))

    return result


# Test interactive improvement
test_prompt = """Explain the concept of recursion in programming.
Provide a simple example and explain how it works step by step."""

result = interactive_improve(test_prompt, num_candidates=3, num_iterations=2)
