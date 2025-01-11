from typing import Dict, List, Any
from .rules import (
    SeparatorRule,
    CasingRule,
    ItemFormattingRule,
    EnumerationRule,
)


def get_gpt4o_rules() -> Dict[str, List[Any]]:
    """
    Get formatting rules optimized for GPT-4 Optimized models.
    """

    return {
        "separator_rules": SeparatorRule.get_default_rules(),
        "casing_rules": CasingRule.get_default_rules(),
        "item_formatting_rules": ItemFormattingRule.get_default_rules(),
        "enumeration_rules": EnumerationRule.get_default_rules(),
    }


def get_gpt4o_mini_rules() -> Dict[str, List[Any]]:
    """
    Get formatting rules optimized for GPT-4 Mini Optimized models.
    """

    return {
        "separator_rules": SeparatorRule.get_default_rules(),
        "casing_rules": CasingRule.get_default_rules(),
        "item_formatting_rules": ItemFormattingRule.get_default_rules(),
        "enumeration_rules": EnumerationRule.get_default_rules(),
    }


def get_llama_70b_rules() -> Dict[str, List[Any]]:
    """
    Get formatting rules optimized for Llama-3 70B Versatile model.
    """

    return {
        "separator_rules": SeparatorRule.get_default_rules(),
        "casing_rules": CasingRule.get_default_rules(),
        "item_formatting_rules": ItemFormattingRule.get_default_rules(),
        "enumeration_rules": EnumerationRule.get_default_rules(),
    }


def get_llama_8b_rules() -> Dict[str, List[Any]]:
    """
    Get formatting rules optimized for Llama3 8B model.
    """

    return {
        "separator_rules": SeparatorRule.get_default_rules(),
        "casing_rules": [CasingRule("upper", "Uppercase")],
        "item_formatting_rules": ItemFormattingRule.get_default_rules(),
        "enumeration_rules": EnumerationRule.get_default_rules(),
    }


def get_mixtral_rules() -> Dict[str, List[Any]]:
    """
    Get formatting rules optimized for Mixtral 8x7B model.
    """
    return {
        "separator_rules": SeparatorRule.get_default_rules(),
        "casing_rules": CasingRule.get_default_rules(),
        "item_formatting_rules": ItemFormattingRule.get_default_rules(),
        "enumeration_rules": EnumerationRule.get_default_rules(),
    }


def get_gemma_rules() -> Dict[str, List[Any]]:
    """
    Get formatting rules optimized for Gemma 2 9B model.
    """

    return {
        "separator_rules": SeparatorRule.get_default_rules(),
        "casing_rules": CasingRule.get_default_rules(),
        "item_formatting_rules": ItemFormattingRule.get_default_rules(),
        "enumeration_rules": EnumerationRule.get_default_rules(),
    }


def get_general_rules() -> Dict[str, List[Any]]:
    """
    Get general-purpose formatting rules.
    """

    return {
        "separator_rules": SeparatorRule.get_default_rules(),
        "casing_rules": CasingRule.get_default_rules(),
        "item_formatting_rules": ItemFormattingRule.get_default_rules(),
        "enumeration_rules": EnumerationRule.get_default_rules(),
    }


def get_model_rules(model: str) -> Dict[str, List[Any]]:
    """Get formatting rules for a specific model."""

    rules_map = {
        "general": get_general_rules,
        "gpt-4o": get_gpt4o_rules,
        "gpt-4o-mini": get_gpt4o_mini_rules,
        "llama-3.1-70b-versatile": get_llama_70b_rules,
        "llama-3.1-8b-instant": get_llama_8b_rules,
        "mixtral-8x7b-32768": get_mixtral_rules,
        "gemma2-9b-it": get_gemma_rules,
    }

    if model not in rules_map:
        raise ValueError(
            f"Unknown model: {model}. Available models: {list(rules_map.keys())}"
        )

    return rules_map[model]()
