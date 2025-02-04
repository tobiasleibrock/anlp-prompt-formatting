# formats from paper "How I learned to start worrying about prompt formatting"

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


# Casing functions
def no_change(x):
    return x


def to_title(x):
    return x.title()


def to_upper(x):
    return x.upper()


def to_lower(x):
    return x.lower()


# Item formatting functions - Type 1
def parentheses(x):
    return f"({x})"


def dot_suffix(x):
    return f"{x}."


def paren_suffix(x):
    return f"{x})"


def paren_space_suffix(x):
    return f"{x} )"


def square_brackets(x):
    return f"[{x}]"


def angle_brackets(x):
    return f"<{x}>"


# Item formatting functions - Type 2
def increment(x):
    return x + 1


def prefix_upper_a(x):
    return f"A{x}"


def prefix_lower_a(x):
    return f"a{x}"


def to_unicode_fraction(x):
    return f"{0x215F + x}"


# Format classes
S1 = ["", " ", "\n", " -- ", "; \n", " || ", "< sep >", " - ", "\n "]
S2 = ["", " ", "  ", "\t"]
C = ["", " ::: ", " :: ", " : ", "\n\t", "\n ", ": ", " - ", "\t"]
Fcasing = [no_change, to_title, to_upper, to_lower]
Fitem1 = [
    parentheses,
    dot_suffix,
    paren_suffix,
    paren_space_suffix,
    square_brackets,
    angle_brackets,
]
Fitem2 = [
    increment,
    prefix_upper_a,
    prefix_lower_a,
    to_unicode_fraction,
    to_roman,
    to_lower_roman,
]


def format_field(descriptor, separator, casing, value):
    descriptor = casing(descriptor)
    return f"{descriptor}{separator}{value}"


def format_prompt(fields, field_separator, space):
    return field_separator.join(fields).replace(" ", space)


def format_enumeration(descriptor, items, separator, space, casing, item_formatter):
    formatted_items = [
        format_field(descriptor, separator, casing, item_formatter(i)) for i in items
    ]
    return format_prompt(formatted_items, field_separator=space, space=" ")
