# formats from paper "How I learned to start worrying about prompt formatting"


# Utility for Roman numeral conversion
def to_roman(num):
    roman_dict = {
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
    return roman_dict.get(num, str(num))


def to_lower_roman(num):
    return to_roman(num).lower()


# Format classes
S1 = ["", " ", "\n", " -- ", "; \n", " || ", "< sep >", " - ", "\n "]
S2 = ["", " ", "  ", "\t"]  # No space, single, double, tab
C = ["", " ::: ", " :: ", " : ", "\n\t", "\n ", ": ", " - ", "\t"]
Fcasing = [lambda x: x, lambda x: x.title(), lambda x: x.upper(), lambda x: x.lower()]
Fitem1 = [
    lambda x: f"({x})",
    lambda x: f"{x}.",
    lambda x: f"{x})",
    lambda x: f"{x} )",
    lambda x: f"[{x}]",
    lambda x: f"<{x}>",
]
Fitem2 = [
    lambda x: x + 1,
    lambda x: f"A{x}",
    lambda x: f"a{x}",
    lambda x: f"{0x215F + x}",
    to_roman,
    to_lower_roman,
]


# Prompt formatting functions
def format_field(descriptor, separator, casing, value):
    """
    Formats a single field with a descriptor, separator, casing, and placeholder value.
    """
    descriptor = casing(descriptor)
    return f"{descriptor}{separator}{value}"


def format_prompt(fields, field_separator, space):
    """
    Combines multiple formatted fields with a given separator and spacing.
    """
    return field_separator.join(fields).replace(" ", space)


def format_enumeration(descriptor, items, separator, space, casing, item_formatter):
    """
    Formats enumerations (e.g., multiple-choice options) with specific formatting for items.
    """
    formatted_items = [
        format_field(descriptor, separator, casing, item_formatter(i)) for i in items
    ]
    return format_prompt(formatted_items, field_separator=space, space=" ")
