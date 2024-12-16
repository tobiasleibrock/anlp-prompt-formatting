from typing import Callable, List
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """
    A class to construct prompts for a model.
    """

    model_instructions: str
    task: str
    fields: List[str]
    demonstrations: List[dict] = None
    separator: str = ""
    word_separator: str = ""
    casing: Callable[[str], str] = lambda x: x
    field_separator: str = ""
    item_formatter: Callable[[str], str] = lambda x: x
    enumerator_format: Callable[[str], str] = lambda x: x

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
        focus = "Only respond with the answer, no other text or explanation."
        instruction = self.casing(self.model_instructions)
        formatted_examples = [
            self.format_field("Example", demonstration)
            for demonstration in self.demonstrations
        ]
        formatted_task = self.format_field("Task", self.task)
        # enumeration = self.format_enumeration("Option", range(1, 4))
        enumeration = ""
        return self.format_prompt(
            [instruction, focus] + formatted_examples + [formatted_task, enumeration]
        )
