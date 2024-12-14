import os
import random
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
import aisuite as ai
from task_formatters import get_task_formatter, load_task
from formatters import S1, S2, C, Fcasing, Fitem1, Fitem2


def setup_logging(task_id: str):
    """Set up logging configuration for a task."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = f"{log_dir}/task{task_id}_{timestamp}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


load_dotenv()

client = ai.Client({"groq": {"api_key": os.getenv("GROQ_API_KEY")}})
MODEL = "groq:llama-3.1-8b-instant"


def format_params_to_str(params: Tuple) -> str:
    """Convert format parameters to a readable string."""
    return (
        f"separator: '{params[0]}', "
        f"space: '{params[1]}', "
        f"casing: {params[2].__name__ if hasattr(params[2], '__name__') else str(params[2])}, "
        f"field_separator: '{params[3]}', "
        f"item_formatter: {params[4].__name__ if hasattr(params[4], '__name__') else str(params[4])}, "
        f"enumerator_format: {params[5].__name__ if hasattr(params[5], '__name__') else str(params[5])}"
    )


def sample_format_params() -> Tuple[str, str, callable, str, callable, callable]:
    """Sample random formatting parameters."""
    params = (
        random.choice(S1),  # separator
        random.choice(S2),  # space
        random.choice(Fcasing),  # casing
        random.choice(C),  # field_separator
        random.choice(Fitem1),  # item_formatter
        random.choice(Fitem2),  # enumerator_format
    )
    logging.info(f"Sampled format parameters: {format_params_to_str(params)}")
    return params


def evaluate_format(
    task_id: str,
    instances: List[Dict[str, Any]],
    format_params: Tuple[str, str, callable, str, callable, callable],
    num_samples: int = 10,
) -> float:
    """Evaluate a specific format on a task."""
    formatter = get_task_formatter(task_id)
    correct = 0
    total = 0

    random.seed(42)  # Use fixed seed for reproducibility
    eval_instances = random.sample(instances, min(num_samples, len(instances)))
    random.seed()
    logging.info(f"Evaluating format on {len(eval_instances)} instances")

    for i, instance in enumerate(eval_instances, 1):
        try:
            prompt = formatter(instance, *format_params)
            logging.debug(f"Formatted prompt for instance {i}:\n{prompt}")

            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ]

            # response = client.chat.completions.create(
            #     model=MODEL, messages=messages, temperature=0.0
            # )
            # prediction = response.choices[0].message.content.strip()
            # ground_truth = instance["output"][0]

            # # Log prediction details
            # is_correct = prediction == ground_truth
            # correct += int(is_correct)
            # total += 1

            # logging.info(
            #     f"Instance {i}/{len(eval_instances)} - "
            #     f"Prediction: {prediction}, "
            #     f"Ground Truth: {ground_truth}, "
            #     f"Correct: {is_correct}"
            # )

        except Exception as e:
            logging.error(f"Error evaluating instance {i}: {str(e)}", exc_info=True)
            continue

    accuracy = correct / total if total > 0 else 0.0
    logging.info(
        f"Format evaluation complete - Accuracy: {accuracy:.3f} ({correct}/{total} correct)"
    )
    return accuracy


def evaluate_task(task_id: str, num_formats: int = 10, samples_per_format: int = 1):
    """Evaluate multiple formats on a task."""
    logger = setup_logging(task_id)
    logger.info(f"Starting evaluation of task {task_id}")
    logger.info(
        f"Parameters: num_formats={num_formats}, samples_per_format={samples_per_format}"
    )

    task_data = load_task(task_id)
    logger.info(f"Loaded task data with {len(task_data['Instances'])} instances")
    instances = task_data["Instances"]

    logger.info(f"Task Definition: {task_data.get('Definition', ['No definition'])[0]}")

    results = []
    for format_idx in range(num_formats):
        logger.info(f"\nEvaluating format {format_idx + 1}/{num_formats}")
        format_params = sample_format_params()
        accuracy = evaluate_format(
            task_id, instances, format_params, samples_per_format
        )

        format_result = {
            "format_id": format_idx + 1,
            "params": {
                "separator": str(format_params[0]),
                "space": str(format_params[1]),
                "casing": str(format_params[2]),
                "field_separator": str(format_params[3]),
                "item_formatter": str(format_params[4]),
                "enumerator_format": str(format_params[5]),
            },
            "accuracy": accuracy,
        }
        results.append(format_result)

        accuracies = [r["accuracy"] for r in results]
        current_spread = max(accuracies) - min(accuracies)
        logger.info(
            f"Current statistics after {format_idx + 1} formats:\n"
            f"  Spread: {current_spread:.3f}\n"
            f"  Min accuracy: {min(accuracies):.3f}\n"
            f"  Max accuracy: {max(accuracies):.3f}\n"
            f"  Avg accuracy: {sum(accuracies)/len(accuracies):.3f}"
        )

    accuracies = [r["accuracy"] for r in results]
    spread = max(accuracies) - min(accuracies)

    final_results = {
        "task_id": task_id,
        "num_formats": num_formats,
        "samples_per_format": samples_per_format,
        "spread": spread,
        "min_accuracy": min(accuracies),
        "max_accuracy": max(accuracies),
        "avg_accuracy": sum(accuracies) / len(accuracies),
        "results": results,
    }

    logger.info(f"\nTask {task_id} evaluation complete")
    logger.info(f"Final spread: {spread:.3f}")
    logger.info(f"Final accuracy range: [{min(accuracies):.3f}, {max(accuracies):.3f}]")
    logger.info(f"Average accuracy: {sum(accuracies)/len(accuracies):.3f}")

    return final_results


def main():
    tasks = ["069"]

    all_results = {}
    for task_id in tasks:
        print(f"\nEvaluating task {task_id}...")
        results = evaluate_task(task_id)
        all_results[task_id] = results

        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"{results_dir}/results_task{task_id}_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {results_file}")


if __name__ == "__main__":
    main()
