"""
Main reformatter class for applying expert rules to prompts.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from .rules import (
    SeparatorRule,
    CasingRule,
    ItemFormattingRule,
    EnumerationRule,
)
from .templates import PromptTemplate, DEFAULT_TEMPLATES, Example


@dataclass
class PromptReformatter:
    separator_rules: List[SeparatorRule] = field(default_factory=list)
    casing_rules: List[CasingRule] = field(default_factory=list)
    item_formatting_rules: List[ItemFormattingRule] = field(default_factory=list)
    enumeration_rules: List[EnumerationRule] = field(default_factory=list)
    template: Optional[PromptTemplate] = None

    def __post_init__(self):
        if not self.separator_rules:
            self.separator_rules = SeparatorRule.get_default_rules()
        if not self.casing_rules:
            self.casing_rules = CasingRule.get_default_rules()
        if not self.item_formatting_rules:
            self.item_formatting_rules = ItemFormattingRule.get_default_rules()
        if not self.enumeration_rules:
            self.enumeration_rules = EnumerationRule.get_default_rules()
        if not self.template:
            self.template = DEFAULT_TEMPLATES["general"]

    def format_field_name(self, field_name: str) -> str:
        """Format only the field name using casing rules."""
        if self.casing_rules:
            return self.casing_rules[0].apply(field_name)
        return field_name

    def format_number(self, number: int) -> str:
        """Format a number using item formatting and enumeration rules."""
        num_str = str(number)
        if self.enumeration_rules:
            num_str = self.enumeration_rules[0].apply(num_str)
        if self.item_formatting_rules:
            num_str = self.item_formatting_rules[0].apply(num_str)
        return num_str

    def get_formatting_summary(self) -> Dict[str, str]:
        """Get a summary of the formatting rules being used."""
        return {
            "separator": self.separator_rules[0].name
            if self.separator_rules
            else "None",
            "casing": self.casing_rules[0].name if self.casing_rules else "None",
            "item_formatting": self.item_formatting_rules[0].name
            if self.item_formatting_rules
            else "None",
            "enumeration": self.enumeration_rules[0].name
            if self.enumeration_rules
            else "None",
        }

    def format(
        self, input_data: Union[str, Dict[str, Any]]
    ) -> Tuple[str, str, Dict[str, str]]:
        """Format the prompt using the current template and rules.
        Returns: (original_prompt, formatted_prompt, formatting_summary)
        """
        # Store original input for later
        original_prompt = (
            input_data
            if isinstance(input_data, str)
            else self.template.format(input_data)
        )

        # If input is a string, try to extract fields
        if isinstance(input_data, str):
            field_values = self.template.extract_fields(input_data)
            # If no fields were extracted, treat the entire input as the first required field
            if not field_values and self.template.required_fields:
                field_values = {self.template.required_fields[0]: input_data}
        else:
            field_values = input_data

        # Pass the reformatter to the template so it can access the formatting rules
        self.template.reformatter = self

        # Format the prompt with all rules
        formatted_prompt = self.template.format(field_values)

        # Get formatting summary
        formatting_summary = self.get_formatting_summary()

        return original_prompt, formatted_prompt, formatting_summary

    def add_rule(self, rule_type: str, rule: Any) -> None:
        if rule_type == "separator":
            self.separator_rules.insert(0, rule)
        elif rule_type == "casing":
            self.casing_rules.insert(0, rule)
        elif rule_type == "item_formatting":
            self.item_formatting_rules.insert(0, rule)
        elif rule_type == "enumeration":
            self.enumeration_rules.insert(0, rule)
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")

    def set_template(self, template_name: str) -> None:
        """Set the template to use for formatting."""
        if template_name not in DEFAULT_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")
        self.template = DEFAULT_TEMPLATES[template_name]
