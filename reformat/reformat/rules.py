"""
Expert rules for prompt formatting.
"""

from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class BaseRule(ABC):
    """Base class for all formatting rules."""

    name: str
    description: str

    @abstractmethod
    def apply(self, prompt: str) -> str:
        """Apply the rule to the prompt."""
        pass

    @classmethod
    @abstractmethod
    def get_default_rules(cls) -> List["BaseRule"]:
        """Get the default set of expert rules."""
        pass


@dataclass
class SeparatorRule(BaseRule):
    """Rules for selecting optimal separators between prompt sections."""

    separator: str

    def apply(self, prompt: str) -> str:
        # Apply separator between sections
        sections = prompt.split("\n")
        return self.separator.join(section.strip() for section in sections)

    @classmethod
    def get_default_rules(cls) -> List["SeparatorRule"]:
        return [
            cls("Newline", "Use newline separator", "\n"),
            cls("Space", "Use space separator", " "),
            cls("Dash", "Use dash separator", " - "),
            cls("Double Colon", "Use double colon separator", " :: "),
        ]


@dataclass
class CasingRule(BaseRule):
    """Rules for determining optimal casing in prompts."""

    def apply(self, prompt: str) -> str:
        # Implement casing transformation
        if self.name == "Title":
            return prompt.title()
        elif self.name == "Lower":
            return prompt.lower()
        elif self.name == "Upper":
            return prompt.upper()
        return prompt

    @classmethod
    def get_default_rules(cls) -> List["CasingRule"]:
        return [
            cls("No Change", "Keep original casing"),
            cls("Title", "Use title case"),
            cls("Lower", "Use lowercase"),
            cls("Upper", "Use uppercase"),
        ]


@dataclass
class ItemFormattingRule(BaseRule):
    """Rules for formatting individual items in prompts."""

    format_str: str

    def apply(self, prompt: str) -> str:
        # Apply formatting to enumerated items
        for i in range(1, 10):
            if str(i) in prompt:
                prompt = prompt.replace(str(i), self.format_str.format(i))
        return prompt

    @classmethod
    def get_default_rules(cls) -> List["ItemFormattingRule"]:
        return [
            cls("Parentheses", "Use parentheses", "({})"),
            cls("Brackets", "Use brackets", "[{}]"),
            cls("Dot Suffix", "Use dot suffix", "{}."),
            cls("Angle Brackets", "Use angle brackets", "<{}>"),
        ]


@dataclass
class EnumerationRule(BaseRule):
    """Rules for handling enumerations in prompts."""

    enum_format: str

    def apply(self, prompt: str) -> str:
        if self.enum_format == "roman":
            # Convert numeric to roman numerals
            roman_map = {
                1: "I",
                2: "II",
                3: "III",
                4: "IV",
                5: "V",
                6: "VI",
                7: "VII",
                8: "VIII",
                9: "IX",
                10: "X",
            }
            for num, roman in roman_map.items():
                prompt = prompt.replace(str(num), roman)
        return prompt

    @classmethod
    def get_default_rules(cls) -> List["EnumerationRule"]:
        return [
            cls("Numeric", "Use numeric enumeration", "numeric"),
            cls("Roman", "Use roman numerals", "roman"),
            cls("Alpha", "Use alphabetic enumeration", "alpha"),
        ]
