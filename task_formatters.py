import json
import glob
from typing import Dict, Any, Callable
from formatters import (
    format_field,
    format_prompt,
    format_enumeration,
)


def load_task(task_id: str) -> Dict[str, Any]:
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
    input_text = instance["input"]
    parts = input_text.split("\\n") if "\\n" in input_text else input_text.split("\n")

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

    formatted = []
    formatted.append(format_field("Beginning", separator, casing, fields["Beginning"]))

    for i in range(1, 3):
        middle_content = fields[f"Middle {i}"]
        formatted.append(
            format_field(
                f"Middle {item_formatter(i)}", separator, casing, middle_content
            )
        )

    formatted.append(format_field("Ending", separator, casing, fields["Ending"]))
    formatted.append(format_field("Answer", separator, casing, ""))

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


def format_answerability_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    parts = input_text.split("Question:")
    sentence = parts[0].replace("Sentence:", "").strip()
    question = parts[1].strip()

    formatted_sentence = format_field("Sentence", separator, casing, sentence)
    formatted_question = format_field("Question", separator, casing, question)
    formatted_answer = format_field("Answer", separator, casing, "")

    return format_prompt(
        [formatted_sentence, formatted_question, formatted_answer],
        field_separator,
        space,
    )


def format_timetravel_task(task_input: str) -> str:
    sentences = [s.strip() for s in task_input.split("\n") if s.strip()]

    formatted_sentences = []
    for sentence in sentences:
        if sentence.startswith("Sentence "):
            num = sentence[8]
            text = sentence[sentence.find(":") + 1 :].strip()
            formatted_sentences.append(f"Sentence {num}: {text}")
        elif sentence.startswith("Option "):
            formatted_sentences.append(sentence.strip())

    formatted_input = "\n".join(formatted_sentences)
    return f"{formatted_input}\nAnswer:"


def format_text_quality_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    if "Text:" in input_text:
        text = input_text.replace("Text:", "").strip()
        formatted_text = format_field("Text", separator, casing, text)
    elif "Document:" in input_text:
        text = input_text.replace("Document:", "").strip()
        formatted_text = format_field("Document", separator, casing, text)
    else:
        formatted_text = format_field("Text", separator, casing, input_text)

    formatted_quality = format_field("Quality Assessment", separator, casing, "")

    return format_prompt(
        [formatted_text, formatted_quality],
        field_separator,
        space,
    )


def format_categorization_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    if "Text:" in input_text:
        text = input_text.replace("Text:", "").strip()
        formatted_text = format_field("Text", separator, casing, text)
    elif "Article:" in input_text:
        text = input_text.replace("Article:", "").strip()
        formatted_text = format_field("Article", separator, casing, text)
    else:
        formatted_text = format_field("Text", separator, casing, input_text)

    formatted_category = format_field("Category", separator, casing, "")

    return format_prompt(
        [formatted_text, formatted_category],
        field_separator,
        space,
    )


def format_stereotype_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    if "Passage:" in input_text:
        passage = input_text.replace("Passage:", "").strip()
        formatted_passage = format_field("Passage", separator, casing, passage)
        formatted_answer = format_field("Classification", separator, casing, "")
        return format_prompt(
            [formatted_passage, formatted_answer], field_separator, space
        )
    else:
        formatted_text = format_field("Text", separator, casing, input_text)
        formatted_answer = format_field("Classification", separator, casing, "")
        return format_prompt([formatted_text, formatted_answer], field_separator, space)


def format_toxic_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    if "Comment:" in input_text:
        comment = input_text.replace("Comment:", "").strip()
        formatted_comment = format_field("Comment", separator, casing, comment)
    elif "Tweet:" in input_text:
        comment = input_text.replace("Tweet:", "").strip()
        formatted_comment = format_field("Tweet", separator, casing, comment)
    elif "@USER" in input_text:
        formatted_comment = format_field("Tweet", separator, casing, input_text)
    else:
        formatted_comment = format_field("Text", separator, casing, input_text)

    formatted_answer = format_field("Classification", separator, casing, "")
    return format_prompt([formatted_comment, formatted_answer], field_separator, space)


def format_nli_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    if "Sentence 1:" in input_text and "Sentence 2:" in input_text:
        parts = input_text.split("Sentence 2:")
        sentence1 = parts[0].replace("Sentence 1:", "").strip()
        sentence2 = parts[1].strip()

        formatted_premise = format_field("Premise", separator, casing, sentence1)
        formatted_hypothesis = format_field("Hypothesis", separator, casing, sentence2)
        formatted_answer = format_field("Entailment", separator, casing, "")

        return format_prompt(
            [formatted_premise, formatted_hypothesis, formatted_answer],
            field_separator,
            space,
        )
    elif "sentence_A:" in input_text and "sentence_B:" in input_text:
        parts = input_text.split("sentence_B:")
        sentence1 = parts[0].replace("sentence_A:", "").strip()
        sentence2 = parts[1].strip()

        formatted_premise = format_field("Premise", separator, casing, sentence1)
        formatted_hypothesis = format_field("Hypothesis", separator, casing, sentence2)
        formatted_answer = format_field("Entailment", separator, casing, "")

        return format_prompt(
            [formatted_premise, formatted_hypothesis, formatted_answer],
            field_separator,
            space,
        )
    elif "Premise:" in input_text and "Hypothesis:" in input_text:
        parts = input_text.split("Hypothesis:")
        premise = parts[0].replace("Premise:", "").strip()
        hypothesis = parts[1].strip()

        formatted_premise = format_field("Premise", separator, casing, premise)
        formatted_hypothesis = format_field("Hypothesis", separator, casing, hypothesis)
        formatted_answer = format_field("Entailment", separator, casing, "")

        return format_prompt(
            [formatted_premise, formatted_hypothesis, formatted_answer],
            field_separator,
            space,
        )
    elif "<sep>" in input_text:
        parts = input_text.split("<sep>")

        if "Premise:" in parts[0]:
            premise = parts[0].replace("Premise:", "").strip()
        else:
            premise = parts[0].strip()

        if "Hypothesis:" in parts[1]:
            hypothesis = parts[1].replace("Hypothesis:", "").strip()
        else:
            hypothesis = parts[1].strip()

        formatted_premise = format_field("Premise", separator, casing, premise)
        formatted_hypothesis = format_field("Hypothesis", separator, casing, hypothesis)
        formatted_answer = format_field("Entailment", separator, casing, "")

        return format_prompt(
            [formatted_premise, formatted_hypothesis, formatted_answer],
            field_separator,
            space,
        )
    else:
        formatted_text = format_field("Text", separator, casing, input_text)
        formatted_answer = format_field("Answer", separator, casing, "")
        return format_prompt([formatted_text, formatted_answer], field_separator, space)


def format_multiple_choice_qa(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    if (
        "Context:" in input_text
        and "Question:" in input_text
        and "Options:" in input_text
    ):
        parts = input_text.split("Question:")
        context = parts[0].replace("Context:", "").strip()

        question_parts = parts[1].split("Options:")
        question = question_parts[0].strip()

        options_text = question_parts[1].strip()
        options = []

        if "(" in options_text:
            for option in options_text.split("(")[1:]:
                option_text = (
                    option.split(")")[1].strip() if ")" in option else option.strip()
                )
                options.append(option_text)
        else:
            options = [opt.strip() for opt in options_text.split("\n") if opt.strip()]

        formatted_context = format_field("Context", separator, casing, context)
        formatted_question = format_field("Question", separator, casing, question)
        formatted_options = format_enumeration(
            "Option", options, separator, space, casing, item_formatter
        )
        formatted_answer = format_field("Answer", separator, casing, "")

        return format_prompt(
            [
                formatted_context,
                formatted_question,
                formatted_options,
                formatted_answer,
            ],
            field_separator,
            space,
        )
    elif "Problem:" in input_text and "Options:" in input_text:
        parts = input_text.split("Options:")
        problem = parts[0].replace("Problem:", "").strip()

        options_text = parts[1].strip()
        options = []

        if "," in options_text:
            for option in options_text.split(","):
                option = option.strip()
                if option:
                    if ")" in option:
                        option = option.split(")", 1)[1].strip()
                    options.append(option)
        else:
            options = [opt.strip() for opt in options_text.split("\n") if opt.strip()]

        formatted_problem = format_field("Problem", separator, casing, problem)
        formatted_options = format_enumeration(
            "Option", options, separator, space, casing, item_formatter
        )
        formatted_answer = format_field("Answer", separator, casing, "")

        return format_prompt(
            [formatted_problem, formatted_options, formatted_answer],
            field_separator,
            space,
        )
    elif "Choices:" in input_text or "choices:" in input_text:
        choices_keyword = "Choices:" if "Choices:" in input_text else "choices:"
        parts = input_text.split(choices_keyword)
        context = parts[0].strip()

        choices_text = parts[1].strip()
        choices = []

        if "a." in choices_text.lower() or "a)" in choices_text.lower():
            import re

            choice_pattern = re.compile(r"([a-z])[.)\s]+([^a-z.][^\n]*)", re.IGNORECASE)
            matches = choice_pattern.findall(choices_text)

            if matches:
                choices = [choice[1].strip() for choice in matches]
            else:
                for choice in choices_text.split(".")[:-1]:
                    if choice and choice[0].isalpha():
                        choices.append(choice[1:].strip())
        else:
            choices = [c.strip() for c in choices_text.split("\n") if c.strip()]

        if not choices:
            choices = [choices_text]

        formatted_context = format_field("Context", separator, casing, context)
        formatted_choices = format_enumeration(
            "Choice", choices, separator, space, casing, item_formatter
        )
        formatted_answer = format_field("Answer", separator, casing, "")

        return format_prompt(
            [formatted_context, formatted_choices, formatted_answer],
            field_separator,
            space,
        )
    else:
        formatted_text = format_field("Text", separator, casing, input_text)
        formatted_answer = format_field("Answer", separator, casing, "")
        return format_prompt([formatted_text, formatted_answer], field_separator, space)


def format_linguistic_probing(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    if "Sentence:" in input_text and "?" in input_text:
        parts = input_text.split("Sentence:")
        question_parts = parts[1].split("?")

        sentence = (
            question_parts[0].split("'")[1].strip()
            if "'" in question_parts[0]
            else question_parts[0].strip()
        )
        question = question_parts[1].strip() + "?"

        formatted_sentence = format_field("Sentence", separator, casing, sentence)
        formatted_question = format_field("Question", separator, casing, question)
        formatted_answer = format_field("Answer", separator, casing, "")

        return format_prompt(
            [formatted_sentence, formatted_question, formatted_answer],
            field_separator,
            space,
        )
    else:
        formatted_text = format_field("Text", separator, casing, input_text)
        formatted_answer = format_field("Answer", separator, casing, "")
        return format_prompt([formatted_text, formatted_answer], field_separator, space)


def format_coreference_task(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]
    parts = input_text.split("\n")

    sentence = ""
    reason = ""
    question = ""

    for part in parts:
        part = part.strip()
        if part.startswith("Sentence:"):
            sentence = part.replace("Sentence:", "").strip()
        elif part.startswith("Reason:"):
            reason = part.replace("Reason:", "").strip()
        elif part.startswith("Question:"):
            question = part.replace("Question:", "").strip()

    formatted_sentence = format_field("Sentence", separator, casing, sentence)
    formatted_reason = format_field("Reason", separator, casing, reason)
    formatted_question = format_field("Question", separator, casing, question)
    formatted_answer = format_field("Answer", separator, casing, "")

    return format_prompt(
        [formatted_sentence, formatted_reason, formatted_question, formatted_answer],
        field_separator,
        space,
    )


def format_text_similarity(
    instance: Dict[str, Any],
    separator: str,
    space: str,
    casing: callable,
    field_separator: str,
    item_formatter: callable,
    enumerator_format: callable,
) -> str:
    input_text = instance["input"]

    if "Sentence 1:" in input_text and "Sentence 2:" in input_text:
        parts = input_text.split("Sentence 2:")
        sentence1 = parts[0].replace("Sentence 1:", "").strip()
        sentence2 = parts[1].strip()

        formatted_sentence1 = format_field("Sentence 1", separator, casing, sentence1)
        formatted_sentence2 = format_field("Sentence 2", separator, casing, sentence2)
        formatted_answer = format_field("Similarity", separator, casing, "")

        return format_prompt(
            [formatted_sentence1, formatted_sentence2, formatted_answer],
            field_separator,
            space,
        )
    else:
        formatted_text = format_field("Text", separator, casing, input_text)
        formatted_answer = format_field("Answer", separator, casing, "")
        return format_prompt([formatted_text, formatted_answer], field_separator, space)


def safe_format(formatter_func, instance, *args, **kwargs):
    try:
        return formatter_func(instance, *args, **kwargs)
    except Exception as e:
        print(f"Error applying formatter: {e}")
        input_text = instance.get("input", "")
        formatted_text = format_field(
            "Text",
            kwargs.get("separator", ":"),
            kwargs.get("casing", str.capitalize),
            input_text,
        )
        formatted_answer = format_field(
            "Answer",
            kwargs.get("separator", ":"),
            kwargs.get("casing", str.capitalize),
            "",
        )
        return format_prompt(
            [formatted_text, formatted_answer],
            kwargs.get("field_separator", "\n"),
            kwargs.get("space", " "),
        )


def get_task_formatter(task_id: str) -> Callable[[str], str]:
    if task_id == "050":
        return format_answerability_task

    elif task_id in ["279", "316", "317", "319", "320"]:
        return format_stereotype_task

    elif task_id in [
        "286",
        "322",
        "323",
        "325",
        "326",
        "327",
        "328",
        "335",
        "337",
        "607",
        "608",
        "609",
        "904",
        "905",
        "1502",
        "1724",
    ]:
        return format_toxic_task

    elif task_id == "280":
        return format_categorization_task

    elif task_id in ["1186", "1283", "1284"]:
        return format_text_quality_task

    elif task_id == "065":
        return format_timetravel_task
    elif task_id in ["069", "070"]:
        return format_abductive_task
    elif task_id in ["190", "1387", "1612"]:
        return format_nli_task

    elif task_id in ["385", "580", "1420"]:
        return format_multiple_choice_qa
    elif task_id == "1297":
        return format_qasc_task

    elif task_id == "114":
        return format_linguistic_probing
    elif task_id == "133":
        return format_coreference_task
    elif task_id == "1347":
        return format_text_similarity

    else:
        raise ValueError(f"Unknown task ID: {task_id}")


def format_task(
    task_id: str,
    separator: str = ":",
    space: str = " ",
    casing: callable = str.capitalize,
    field_separator: str = "\n",
    item_formatter: callable = lambda x: str(x),
    enumerator_format: callable = None,
) -> Dict[str, Any]:
    try:
        task_data = load_task(task_id)

        formatter = get_task_formatter(task_id)

        definition = "\n".join(task_data.get("Definition", []))

        positive_examples = []
        for example in task_data.get("Positive Examples", []):
            try:
                formatted_input = safe_format(
                    formatter,
                    example,
                    separator,
                    space,
                    casing,
                    field_separator,
                    item_formatter,
                    enumerator_format,
                )
                positive_examples.append(
                    {
                        "input": formatted_input,
                        "output": example.get("output", ""),
                        "explanation": example.get("explanation", ""),
                    }
                )
            except Exception as e:
                print(f"Error formatting positive example: {e}")
                continue

        negative_examples = []
        for example in task_data.get("Negative Examples", []):
            try:
                formatted_input = safe_format(
                    formatter,
                    example,
                    separator,
                    space,
                    casing,
                    field_separator,
                    item_formatter,
                    enumerator_format,
                )
                negative_examples.append(
                    {
                        "input": formatted_input,
                        "output": example.get("output", ""),
                        "explanation": example.get("explanation", ""),
                    }
                )
            except Exception as e:
                print(f"Error formatting negative example: {e}")
                continue

        return {
            "task_id": task_id,
            "definition": definition,
            "positive_examples": positive_examples,
            "negative_examples": negative_examples,
            "categories": task_data.get("Categories", []),
            "domains": task_data.get("Domains", []),
        }
    except Exception as e:
        print(f"Error formatting task {task_id}: {e}")
        return {"task_id": task_id, "error": str(e)}


def format_all_tasks(task_ids, **formatter_kwargs):
    results = {}

    for task_id in task_ids:
        try:
            results[task_id] = format_task(task_id, **formatter_kwargs)
        except Exception as e:
            print(f"Error formatting task {task_id}: {e}")
            results[task_id] = {"task_id": task_id, "error": str(e)}

    return results
