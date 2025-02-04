from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Example:
    input: str
    output: str

    def format(self) -> str:
        return f"Input: {self.input}\nOutput: {self.output}"


@dataclass
class PromptTemplate:
    name: str
    description: str
    fields: List[str]
    required_fields: List[str]
    separator: str = "\n\n"

    def format(self, field_values: Dict[str, Any]) -> str:
        missing_fields = [f for f in self.required_fields if f not in field_values]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        formatted_sections = []
        for field in self.fields:
            if field in field_values:
                # Apply casing rule to field name
                formatted_field = field
                if hasattr(self, "reformatter") and self.reformatter.casing_rules:
                    formatted_field = self.reformatter.casing_rules[0].apply(field)

                # Get separator between field name and value
                field_separator = "\n"  # Default to newline
                if hasattr(self, "reformatter") and self.reformatter.separator_rules:
                    field_separator = self.reformatter.separator_rules[0].separator

                if field == "Examples" and isinstance(field_values[field], list):
                    examples = field_values[field]
                    formatted_examples = []
                    for i, example in enumerate(examples, 1):
                        if isinstance(example, Example):
                            # Apply item formatting and enumeration rules to example number
                            example_num = str(i)
                            if hasattr(self, "reformatter"):
                                if self.reformatter.enumeration_rules:
                                    example_num = self.reformatter.enumeration_rules[
                                        0
                                    ].apply(example_num)
                                if self.reformatter.item_formatting_rules:
                                    example_num = (
                                        self.reformatter.item_formatting_rules[
                                            0
                                        ].format_str.format(example_num)
                                    )

                            # Apply casing to "Example", "Input", and "Output" labels
                            example_label = "Example"
                            input_label = "Input"
                            output_label = "Output"
                            if (
                                hasattr(self, "reformatter")
                                and self.reformatter.casing_rules
                            ):
                                example_label = self.reformatter.casing_rules[0].apply(
                                    example_label
                                )
                                input_label = self.reformatter.casing_rules[0].apply(
                                    input_label
                                )
                                output_label = self.reformatter.casing_rules[0].apply(
                                    output_label
                                )

                            formatted_examples.append(
                                f"{example_label} {example_num}{field_separator}"
                                f"{input_label}: {example.input}{field_separator}"
                                f"{output_label}: {example.output}"
                            )
                    if formatted_examples:
                        formatted_sections.append(
                            f"{formatted_field}{field_separator}"
                            + "\n\n".join(formatted_examples)
                        )
                elif field == "Options" and isinstance(field_values[field], list):
                    # Format options specially
                    options = field_values[field]
                    formatted_options = []
                    for i, opt in enumerate(options, 1):
                        # Apply item formatting and enumeration rules to option number
                        option_num = str(i)
                        if hasattr(self, "reformatter"):
                            if self.reformatter.enumeration_rules:
                                option_num = self.reformatter.enumeration_rules[
                                    0
                                ].apply(option_num)
                            if self.reformatter.item_formatting_rules:
                                option_num = self.reformatter.item_formatting_rules[
                                    0
                                ].format_str.format(option_num)

                            formatted_options.append(
                                f"{option_num}{field_separator}{opt}"
                            )

                    # Join options with appropriate separator
                    options_separator = "\n"  # Default to newline
                    if (
                        hasattr(self, "reformatter")
                        and self.reformatter.separator_rules
                    ):
                        options_separator = " -- "

                    formatted_sections.append(
                        f"{formatted_field}{field_separator}"
                        + options_separator.join(formatted_options)
                    )
                else:
                    formatted_sections.append(
                        f"{formatted_field}{field_separator}{field_values[field]}"
                    )

        # Always use double newline between major sections
        return "\n\n".join(formatted_sections)

    def extract_fields(self, text: str) -> Dict[str, Any]:
        field_values = {}
        sections = text.split(self.separator)

        for section in sections:
            section = section.strip()
            for field in self.fields:
                if section.startswith(f"{field}:"):
                    value = section[len(f"{field}:") :].strip()
                    if field == "Examples":
                        examples = []
                        example_sections = value.split("\n\n")
                        for example_section in example_sections:
                            if (
                                "Input:" in example_section
                                and "Output:" in example_section
                            ):
                                input_text = (
                                    example_section.split("Output:")[0]
                                    .replace("Input:", "")
                                    .strip()
                                )
                                output_text = example_section.split("Output:")[
                                    1
                                ].strip()
                                examples.append(
                                    Example(input=input_text, output=output_text)
                                )
                        if examples:
                            field_values[field] = examples
                    elif field == "Options":
                        options = []
                        for line in value.split("\n"):
                            if line.strip() and ". " in line:
                                options.append(line.split(". ", 1)[1].strip())
                        if options:
                            field_values[field] = options
                    else:
                        field_values[field] = value
                    break

        return field_values


GENERAL_TEMPLATE = PromptTemplate(
    name="general",
    description="A template for few-shot learning with task description and input-output examples",
    fields=["Task", "Examples", "Input"],
    required_fields=["Task", "Input"],
)

MULTIPLE_CHOICE_TEMPLATE = PromptTemplate(
    name="multiple_choice",
    description="A template for multiple choice questions with examples",
    fields=["Task", "Examples", "Question", "Options"],
    required_fields=["Task", "Question", "Options"],
)

DEFAULT_TEMPLATES = {
    "general": GENERAL_TEMPLATE,
    "multiple_choice": MULTIPLE_CHOICE_TEMPLATE,
}
