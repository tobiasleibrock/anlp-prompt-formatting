from typing import Callable, List


class PromptTemplate:
    """
    A class to construct prompts for a model.
    """

    def __init__(
        self,
        model_instructions: str,
        task: str,
        demonstrations: List[dict] = None,
        separator: str = "",
        word_separator: str = "",
        casing: Callable[[str], str] = lambda x: x,
        field_separator: str = "",
        item_formatter: Callable[[str], str] = lambda x: x,
        enumerator_format: Callable[[str], str] = lambda x: x,
    ):
        """
        :param model_instructions: Instructions to the model e.g. "Respond in Pirate English."
        :param demonstrations: List of example input/output pairs that demonstrate the task
        :param task: The specific task/question to be performed/answered
        """

        self.model_instructions = model_instructions
        self.demonstrations = demonstrations or []
        self.task = task
        self.separator = separator
        self.word_separator = word_separator
        self.casing = casing
        self.field_separator = field_separator
        self.item_formatter = item_formatter
        self.enumerator_format = enumerator_format

    # Prompt formatting help-functions
    def format_field(self, descriptor, value):
        """
        Formats a single field with a descriptor, separator, casing, and placeholder value.
        """
        descriptor = self.casing(descriptor)
        return f"{descriptor}{self.separator}{value}"

    def format_prompt(self, fields):
        """
        Combines multiple formatted fields with a given separator and spacing.
        """
        return self.field_separator.join(fields).replace(" ", self.word_separator)

    def format_enumeration(self, descriptor, items):
        """
        Formats enumerations (e.g., multiple-choice options) with specific formatting for items.
        """
        formatted_items = [
            self.format_field(descriptor, self.item_formatter(i)) for i in items
        ]
        return self.format_prompt(formatted_items)

    def construct_prompt(self):
        """
        Constructs a complete prompt with instruction, examples, task, and formatting.
        """
        instruction = self.casing(self.model_instructions)
        formatted_examples = [
            self.format_field("Example", demonstration)
            for demonstration in self.demonstrations
        ]
        formatted_task = self.format_field("Task", self.task)
        enumeration = self.format_enumeration("Option", range(1, 4))
        return self.format_prompt(
            [instruction] + formatted_examples + [formatted_task, enumeration]
        )
