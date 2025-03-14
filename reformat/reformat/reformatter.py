import os
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from .rules import (
    SeparatorRule,
    CasingRule,
    ItemFormattingRule,
    EnumerationRule,
)
from .templates import PromptTemplate, DEFAULT_TEMPLATES
from .synonym_rules import apply_synonym_rules


@dataclass
class PromptReformatter:
    separator_rules: List[SeparatorRule] = field(default_factory=list)
    casing_rules: List[CasingRule] = field(default_factory=list)
    item_formatting_rules: List[ItemFormattingRule] = field(default_factory=list)
    enumeration_rules: List[EnumerationRule] = field(default_factory=list)
    template: Optional[PromptTemplate] = None
    model_name: str = "general"

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
        if self.casing_rules:
            return self.casing_rules[0].apply(field_name)
        return field_name

    def format_number(self, number: int) -> str:
        num_str = str(number)
        if self.enumeration_rules:
            num_str = self.enumeration_rules[0].apply(num_str)
        if self.item_formatting_rules:
            num_str = self.item_formatting_rules[0].apply(num_str)
        return num_str

    def get_formatting_summary(self) -> Dict[str, str]:
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
        # Store original input for later
        original_prompt = (
            input_data
            if isinstance(input_data, str)
            else self.template.format(input_data)
        )

        if isinstance(input_data, str):
            field_values = self.template.extract_fields(input_data)
            if not field_values and self.template.required_fields:
                field_values = {self.template.required_fields[0]: input_data}
        else:
            field_values = input_data

        # Pass the reformatter to the template so it can access the formatting rules
        self.template.reformatter = self

        formatted_prompt = self.template.format(field_values)

        # Apply synonym rules if available
        model_name = self.model_name.replace(".", "_")
        synonym_rules_path = f"models/{model_name}_synonym_rules.json"
        if os.path.exists(synonym_rules_path):
            formatted_prompt = apply_synonym_rules(
                formatted_prompt, synonym_rules_path, 0.99
            )

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
        if template_name not in DEFAULT_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")
        self.template = DEFAULT_TEMPLATES[template_name]
