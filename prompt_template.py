from typing import Callable, List
from dataclasses import dataclass


@dataclass
class PromptTemplate:

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

    def format_field(self, descriptor, value):
        descriptor = self.casing(descriptor)
        return f"{descriptor}{self.separator}{value}"

    def format_prompt(self, fields):
        return self.field_separator.join(fields).replace(" ", self.word_separator)

    def format_enumeration(self, descriptor, items):
        formatted_items = [
            self.format_field(descriptor, self.item_formatter(i)) for i in items
        ]
        return self.format_prompt(formatted_items)

    def construct_prompt(self):
        focus = "Only respond with the answer, no other text or explanation."
        instruction = self.casing(self.model_instructions)
        formatted_examples = [
            self.format_field("Example", demonstration)
            for demonstration in self.demonstrations
        ]
        formatted_task = self.format_field("Task", self.task)
        
        enumeration = ""
        return self.format_prompt(
            [instruction, focus] + formatted_examples + [formatted_task, enumeration]
        )
