import os
import json
import random
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Callable
from dataclasses import dataclass
from dotenv import load_dotenv
import aisuite as ai
from task_formatters import get_task_formatter, load_task
from formatters import S1, S2, C, Fcasing, Fitem1, Fitem2


@dataclass
class FormatResults:
    rule_name: str
    rule_value: Any
    accuracies: List[float]

    @property
    def avg_accuracy(self) -> float:
        return sum(self.accuracies) / len(self.accuracies) if self.accuracies else 0.0


class FormatExplorer:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = ai.Client({"groq": {"api_key": self.api_key}})
        self.model = f"groq:{model_name}"

        self.s1_results: Dict[str, FormatResults] = {}
        self.s2_results: Dict[str, FormatResults] = {}
        self.c_results: Dict[str, FormatResults] = {}
        self.fcasing_results: Dict[str, FormatResults] = {}
        self.fitem1_results: Dict[str, FormatResults] = {}
        self.fitem2_results: Dict[str, FormatResults] = {}

        self.setup_logging()

    def setup_logging(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        log_file = f"{log_dir}/format_explorer_{timestamp}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

    def sample_format_params(
        self,
    ) -> Tuple[str, str, callable, str, callable, callable]:
        params = (
            random.choice(S1),
            random.choice(S2),
            random.choice(Fcasing),
            random.choice(C),
            random.choice(Fitem1),
            random.choice(Fitem2),
        )
        return params

    def evaluate_format(
        self,
        task_id: str,
        definition: str,
        instances: List[Dict[str, Any]],
        format_params: Tuple[str, str, callable, str, callable, callable],
        num_samples: int = 10,
    ) -> float:
        correct = 0
        total = 0

        logging.info(f"\nEvaluating with format parameters:")
        logging.info(f"  Separator: '{format_params[0]}'")
        logging.info(f"  Word Separator: '{format_params[1]}'")
        logging.info(f"  Casing: {format_params[2].__name__}")
        logging.info(f"  Field Separator: '{format_params[3]}'")
        logging.info(f"  Item Formatter: {format_params[4].__name__}")
        logging.info(f"  Enumerator: {format_params[5].__name__}")

        eval_instances = random.sample(instances, min(num_samples, len(instances)))

        for i, instance in enumerate(eval_instances, 1):
            try:
                formatter = get_task_formatter(task_id)
                formatted_prompt = formatter(instance, *format_params)

                logging.info(f"\nInstance {i}/10:")
                logging.info("Formatted Prompt:")
                logging.info("-" * 50)
                logging.info(formatted_prompt)
                logging.info("-" * 50)

                messages = [
                    {"role": "system", "content": definition},
                    {"role": "user", "content": formatted_prompt},
                ]

                response = self.client.chat.completions.create(
                    model=self.model, messages=messages, temperature=0.0
                )
                prediction = response.choices[0].message.content.strip()

                logging.info(f"Raw Response: {prediction}")

                if task_id == "069":
                    if "1" in prediction:
                        prediction = "1"
                    elif "2" in prediction:
                        prediction = "2"
                    else:
                        logging.warning(f"Invalid prediction format: {prediction}")
                        continue

                ground_truth = instance["output"][0]

                if task_id == "069":
                    is_correct = prediction == ground_truth
                else:
                    is_correct = prediction == ground_truth

                correct += int(is_correct)
                total += 1

                logging.info(
                    f"Prediction: {prediction}, "
                    f"Ground Truth: {ground_truth}, "
                    f"Correct: {is_correct}"
                )

            except Exception as e:
                logging.error(f"Error evaluating instance: {str(e)}", exc_info=True)
                continue

        accuracy = correct / total if total > 0 else 0.0
        logging.info(f"\nFormat accuracy: {accuracy:.3f}")
        return accuracy

    def update_rule_results(
        self, results_dict: Dict[str, FormatResults], rule_value: Any, accuracy: float
    ):
        rule_name = str(rule_value)
        if rule_name not in results_dict:
            results_dict[rule_name] = FormatResults(rule_name, rule_value, [])
        results_dict[rule_name].accuracies.append(accuracy)

    def explore_task(
        self, task_id: str, num_formats: int = 30, samples_per_format: int = 10
    ):
        logging.info(f"Starting format exploration for task {task_id}")

        task_data = load_task(task_id)
        definition = task_data.get("Definition", ["No definition"])[0]
        instances = task_data["Instances"]

        for i in range(num_formats):
            logging.info(f"Evaluating format combination {i + 1}/{num_formats}")

            format_params = self.sample_format_params()

            accuracy = self.evaluate_format(
                task_id, definition, instances, format_params, samples_per_format
            )

            self.update_rule_results(self.s1_results, format_params[0], accuracy)
            self.update_rule_results(self.s2_results, format_params[1], accuracy)
            self.update_rule_results(self.c_results, format_params[3], accuracy)
            self.update_rule_results(
                self.fcasing_results, format_params[2].__name__, accuracy
            )
            self.update_rule_results(
                self.fitem1_results, format_params[4].__name__, accuracy
            )
            self.update_rule_results(
                self.fitem2_results, format_params[5].__name__, accuracy
            )

    def get_best_rules(self) -> Dict[str, Tuple[str, float]]:
        best_rules = {}

        def find_best(results_dict: Dict[str, FormatResults]) -> Tuple[str, float]:
            if not results_dict:
                return ("none", 0.0)
            best_rule = max(results_dict.values(), key=lambda x: x.avg_accuracy)
            return (best_rule.rule_name, best_rule.avg_accuracy)

        best_rules["separator"] = find_best(self.s1_results)
        best_rules["word_separator"] = find_best(self.s2_results)
        best_rules["field_separator"] = find_best(self.c_results)
        best_rules["casing"] = find_best(self.fcasing_results)
        best_rules["item_formatter"] = find_best(self.fitem1_results)
        best_rules["enumerator"] = find_best(self.fitem2_results)

        return best_rules

    def save_results(self, output_dir: str = "results"):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        results = {
            "model": self.model,
            "best_rules": self.get_best_rules(),
            "detailed_results": {
                "s1": {
                    k: {"accuracies": v.accuracies, "avg": v.avg_accuracy}
                    for k, v in self.s1_results.items()
                },
                "s2": {
                    k: {"accuracies": v.accuracies, "avg": v.avg_accuracy}
                    for k, v in self.s2_results.items()
                },
                "c": {
                    k: {"accuracies": v.accuracies, "avg": v.avg_accuracy}
                    for k, v in self.c_results.items()
                },
                "fcasing": {
                    k: {"accuracies": v.accuracies, "avg": v.avg_accuracy}
                    for k, v in self.fcasing_results.items()
                },
                "fitem1": {
                    k: {"accuracies": v.accuracies, "avg": v.avg_accuracy}
                    for k, v in self.fitem1_results.items()
                },
                "fitem2": {
                    k: {"accuracies": v.accuracies, "avg": v.avg_accuracy}
                    for k, v in self.fitem2_results.items()
                },
            },
        }

        output_file = f"{output_dir}/format_exploration_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        logging.info(f"Results saved to {output_file}")


def main():
    explorer = FormatExplorer()

    tasks = [
        "050",
        "065",
        "069",
        "070",
        "1297",
    ]

    task_accuracies = {}

    for task_id in tasks:
        logging.info(f"\nExploring formats for task {task_id}")
        explorer.explore_task(task_id)

        task_best_rules = explorer.get_best_rules()
        task_accuracies[task_id] = {
            rule_type: accuracy
            for rule_type, (rule, accuracy) in task_best_rules.items()
        }

    rule_types = [
        "separator",
        "word_separator",
        "field_separator",
        "casing",
        "item_formatter",
        "enumerator",
    ]
    avg_accuracies = {}

    for rule_type in rule_types:
        accuracies = [task_accuracies[task_id][rule_type] for task_id in tasks]
        avg_accuracies[rule_type] = sum(accuracies) / len(accuracies)

    logging.info("\nAverage accuracies across all tasks:")
    for rule_type, avg_accuracy in avg_accuracies.items():
        logging.info(f"{rule_type}: {avg_accuracy:.3f}")

    explorer.save_results()


if __name__ == "__main__":
    main()
