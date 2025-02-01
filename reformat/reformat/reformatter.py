"""
Main reformatter class for applying expert rules to prompts.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from .rules import (
    SeparatorRule,
    CasingRule,
    ItemFormattingRule,
    EnumerationRule,
)


@dataclass
class PromptReformatter:
    separator_rules: List[SeparatorRule] = field(default_factory=list)
    casing_rules: List[CasingRule] = field(default_factory=list)
    item_formatting_rules: List[ItemFormattingRule] = field(default_factory=list)
    enumeration_rules: List[EnumerationRule] = field(default_factory=list)

    def __post_init__(self):
        if not self.separator_rules:
            self.separator_rules = SeparatorRule.get_default_rules()
        if not self.casing_rules:
            self.casing_rules = CasingRule.get_default_rules()
        if not self.item_formatting_rules:
            self.item_formatting_rules = ItemFormattingRule.get_default_rules()
        if not self.enumeration_rules:
            self.enumeration_rules = EnumerationRule.get_default_rules()

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        return {
            "length": len(prompt),
            "has_enumeration": any(str(i) in prompt for i in range(1, 10)),
            "has_fields": ":" in prompt,
            "sections": prompt.count("\n") + 1,
        }

    def format(self, prompt: str) -> str:
        # apply separator rule
        prompt = self.separator_rules[0].apply(prompt)

        # apply casing rule
        prompt = self.casing_rules[0].apply(prompt)

        # apply item formatting if needed
        if any(str(i) in prompt for i in range(1, 10)):
            prompt = self.item_formatting_rules[0].apply(prompt)
            prompt = self.enumeration_rules[0].apply(prompt)

        return prompt

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
