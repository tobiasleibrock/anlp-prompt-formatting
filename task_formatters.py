import json
import glob
from typing import List, Dict, Any, Tuple
from formatters import (
    S1,
    S2,
    C,
    Fcasing,
    Fitem1,
    Fitem2,
    format_field,
    format_prompt,
    format_enumeration,
)


def load_task(task_id: str) -> Dict[str, Any]:
    """Load a task from the natural-instructions dataset."""
    task_files = glob.glob(f"natural-instructions/tasks/task{task_id}_*.json")
    if not task_files:
        raise FileNotFoundError(f"No task file found for task ID {task_id}")

    task_file = task_files[0]
    with open(task_file, "r") as f:
        return json.load(f)


def format_abductive_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    """Format an abductive reasoning task (069, 070)."""
    input_text = instance["input"]
    parts = input_text.split("\\n") if "\\n" in input_text else input_text.split("\n")

    # Extract fields from input
    fields = {
        "Beginning": "",
        "Middle 1": "",
        "Middle 2": "",
        "Ending": "",
    }

    for part in parts:
        part = part.strip()
        for field in fields:
            if f"{field}:" in part:
                fields[field] = part.split(f"{field}:", 1)[1].strip()
                break

    # Format all fields in sequence
    formatted = []

    # Beginning
    formatted.append(format_field("Beginning", separator, casing, fields["Beginning"]))

    # Middle 1 & 2
    for i in range(1, 3):
        middle_content = fields[f"Middle {i}"]
        formatted.append(
            format_field(
                f"Middle {item_formatter(i)}", separator, casing, middle_content
            )
        )

    # Ending and Answer
    formatted.append(format_field("Ending", separator, casing, fields["Ending"]))
    formatted.append(format_field("Answer", separator, casing, ""))

    # Join with field separator and apply spacing
    return format_prompt(formatted, field_separator, space)


def format_qasc_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    """Format a QASC question answering task (1297)."""
    input_text = instance["input"]
    parts = [p.strip() for p in input_text.split(",")]

    fact1 = parts[0].replace("Fact1: ", "")
    fact2 = parts[1].replace("Fact2: ", "")
    question_part = parts[2].replace("Question: ", "")

    q_parts = question_part.split("(")
    question = q_parts[0].strip()

    choices = []
    for choice in q_parts[1:]:
        choice = choice.strip(") ")
        choices.append(choice)

    formatted_fact1 = format_field("Fact 1", separator, casing, fact1)
    formatted_fact2 = format_field("Fact 2", separator, casing, fact2)
    formatted_question = format_field("Question", separator, casing, question)
    formatted_choices = format_enumeration(
        "Choice", choices, separator, space, casing, item_formatter
    )

    return format_prompt(
        [formatted_fact1, formatted_fact2, formatted_question, formatted_choices],
        field_separator,
        space,
    )


def get_task_formatter(task_id: str):
    """Get the appropriate formatter function for a task."""
    if task_id in ["069", "070"]:
        return format_abductive_task
    elif task_id == "1297":
        return format_qasc_task
    else:
        raise ValueError(f"Unknown task ID: {task_id}")
