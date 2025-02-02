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
            # S₁ separators
            cls("Empty", "No separator", ""),
            cls("Space", "Single space", " "),
            cls("Double Space", "Double space", "  "),
            cls("Newline", "Single newline", "\n"),
            cls("Double Newline", "Double newline", "\n\n"),
            cls("Double Dash", "Double dash", " -- "),
            cls("Semicolon", "Semicolon", " ; "),
            cls("Pipe", "Double pipe", " || "),
            cls("Sep", "Special separator", " <sep> "),
            cls("Comma", "Comma", ", "),
            cls("Period", "Period", ". "),
            # C connectors
            cls("Double Colon", "Double colon", ":: "),
            cls("Single Colon", "Single colon", ": "),
            cls("Tab", "Tab", "\t"),
            cls("Newline Tab", "Newline with tab", "\n\t"),
            cls("Triple Period", "Triple period", "..."),
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
        """This method is deprecated in favor of using format_str directly."""
        # Apply formatting to enumerated items
        for i in range(1, 10):
            if str(i) in prompt:
                prompt = prompt.replace(str(i), self.format_str.format(i))
        return prompt

    @classmethod
    def get_default_rules(cls) -> List["ItemFormattingRule"]:
        return [
            # Fitem1 formats
            cls("Parentheses", "Use parentheses", "({})"),
            cls("Dot", "Use dot suffix", "{}."),
            cls("Paren", "Use right parenthesis", "{})"),
            cls("Underscore", "Use underscore suffix", "{}_"),
            cls("Brackets", "Use square brackets", "[{}]"),
            cls("Angle", "Use angle brackets", "<{}>"),
            # Combined with Fitem2 variations
            cls("Roman Lower", "Use lowercase roman numerals with parentheses", "({})"),
            cls("Roman Upper", "Use uppercase roman numerals with parentheses", "({})"),
            cls("Alpha Lower", "Use lowercase letters with parentheses", "({})"),
            cls("Alpha Upper", "Use uppercase letters with parentheses", "({})"),
            cls("Numeric", "Use numeric with parentheses", "({})"),
        ]


@dataclass
class EnumerationRule(BaseRule):
    """Rules for handling enumerations in prompts."""

    enum_format: str

    def apply(self, prompt: str) -> str:
        if self.enum_format == "roman_lower":
            return self._convert_roman(prompt, upper=False)
        elif self.enum_format == "roman_upper":
            return self._convert_roman(prompt, upper=True)
        elif self.enum_format == "alpha_lower":
            return self._convert_alpha(prompt, upper=False)
        elif self.enum_format == "alpha_upper":
            return self._convert_alpha(prompt, upper=True)
        return prompt

    def _convert_roman(self, prompt: str, upper: bool = True) -> str:
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
            if not upper:
                roman = roman.lower()
            prompt = prompt.replace(str(num), roman)
        return prompt

    def _convert_alpha(self, prompt: str, upper: bool = True) -> str:
        alpha_map = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
            7: "G",
            8: "H",
            9: "I",
            10: "J",
        }
        for num, letter in alpha_map.items():
            if not upper:
                letter = letter.lower()
            prompt = prompt.replace(str(num), letter)
        return prompt

    @classmethod
    def get_default_rules(cls) -> List["EnumerationRule"]:
        return [
            cls("Numeric", "Use numeric enumeration", "numeric"),
            cls("Roman Upper", "Use uppercase roman numerals", "roman_upper"),
            cls("Roman Lower", "Use lowercase roman numerals", "roman_lower"),
            cls("Alpha Upper", "Use uppercase letters", "alpha_upper"),
            cls("Alpha Lower", "Use lowercase letters", "alpha_lower"),
        ]
