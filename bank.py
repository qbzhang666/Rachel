import csv
import io
import math
import random
from collections import Counter
from datetime import datetime

import streamlit as st


# Every question in this bank comes from Rachel's own handwritten revision notebook
# (the photographed pages in bank/). Nothing has been invented that is not on one of
# those pages, and nothing on those pages has been left out.
#
#   Number facts -> power tables for 2 to 10, squares 11 to 26, the fraction and
#                   percentage table, factorials
#   Formulas     -> BODMAS, discount and final price, profit and loss, percentage
#                   profit, consecutive integers, probability, polygon angles,
#                   ratio sharing, sum of a sequence, heads and legs, average speed
#   Geometry     -> triangle types and area, Heron, Pythagoras, 2D areas, 3D volumes,
#                   unit conversion and scaling, compass directions, distance formula
#   Algebra      -> the quadratic formula, rearranging equations, gradient,
#                   average word problems
#   Data         -> mean, median, mode and range
#
# Easy / Medium / Hard follow the three dots Rachel drew beside her own squares table.

EASY = "Easy"
MEDIUM = "Medium"
HARD = "Hard"

# Notebook pages "Power of 2" through "Power of 10": base -> highest exponent written.
POWER_TABLE = {2: 15, 3: 7, 4: 7, 5: 7, 6: 7, 7: 7, 8: 7, 9: 7, 10: 7}

# Notebook page "Squares": the dot Rachel circled under each square.
SQUARE_DOTS = {
    11: EASY,
    12: EASY,
    13: EASY,
    14: EASY,
    15: EASY,
    16: MEDIUM,
    17: MEDIUM,
    18: MEDIUM,
    19: MEDIUM,
    20: EASY,
    21: HARD,
    22: HARD,
    23: HARD,
    24: HARD,
    25: MEDIUM,
    26: HARD,
}

# Notebook page "Percentage".
PERCENT_FACTS = [
    (1, 1, "100%", EASY),
    (1, 2, "50%", EASY),
    (1, 4, "25%", EASY),
    (1, 5, "20%", EASY),
    (1, 10, "10%", EASY),
    (1, 20, "5%", MEDIUM),
    (1, 25, "4%", MEDIUM),
    (1, 50, "2%", MEDIUM),
    (1, 100, "1%", EASY),
    (1, 8, "12.5%", MEDIUM),
    (1, 3, "33.33%", HARD),
    (1, 6, "16.67%", HARD),
    (1, 9, "11.11%", HARD),
]


def number_choices(answer, distractors, suffix=""):
    values = []
    for value in [answer, *distractors]:
        if value not in values:
            values.append(value)
    probe = 1
    while len(values) < 4:
        candidate = answer + probe
        if candidate not in values:
            values.append(candidate)
        probe += 1
    return [f"{value}{suffix}" for value in values[:4]]


def money_choices(answer, distractors):
    values = []
    for value in [answer, *distractors]:
        rounded = round(value, 2)
        if rounded not in values:
            values.append(rounded)
    probe = 5
    while len(values) < 4:
        candidate = round(answer + probe, 2)
        if candidate not in values:
            values.append(candidate)
        probe += 5
    return [f"${value:g}" for value in values[:4]]


def decimal_choices(answer, distractors, suffix="", places=1):
    values = []
    for value in [answer, *distractors]:
        rounded = round(value, places)
        if rounded not in values:
            values.append(rounded)
    step = 10 ** -places
    probe = 1
    while len(values) < 4:
        candidate = round(answer + probe * step * 7, places)
        if candidate not in values:
            values.append(candidate)
        probe += 1
    return [f"{value:.{places}f}{suffix}" for value in values[:4]]


def decimal_answer(value, suffix="", places=1):
    return f"{round(value, places):.{places}f}{suffix}"


def text_choices(answer, distractors):
    values = [answer]
    for value in distractors:
        if value not in values:
            values.append(value)
    return values[:4]


def fraction_text(numerator, denominator):
    divisor = math.gcd(numerator, denominator)
    return f"{numerator // divisor}/{denominator // divisor}"


def quadratic_text(square_coefficient, linear_coefficient, constant):
    lead = "" if square_coefficient == 1 else f"{square_coefficient}"
    middle = "x" if abs(linear_coefficient) == 1 else f"{abs(linear_coefficient)}x"
    return (
        f"{lead}x^2 {'+' if linear_coefficient >= 0 else '-'} {middle} "
        f"{'+' if constant >= 0 else '-'} {abs(constant)}"
    )


def escape_dollars(text):
    """Streamlit reads a pair of dollar signs as LaTeX, so money needs escaping."""
    return str(text).replace("$", "\\$")


def unique_choices(choices, answer):
    cleaned = []
    for choice in [*choices, answer]:
        if choice not in cleaned:
            cleaned.append(choice)
    fillers = ["None of these.", "Cannot be worked out.", "Not enough information.", "Both of the above."]
    for filler in fillers:
        if len(cleaned) >= 4:
            break
        if filler not in cleaned and filler != answer:
            cleaned.append(filler)
    return cleaned[:4]


def build_power_questions():
    """Notebook pages: Power of 2, 3, 4, 5, 6, 7, 8, 9 and 10."""
    questions = []
    for base, top in POWER_TABLE.items():
        for exponent in range(0, top + 1):
            value = base ** exponent
            if exponent <= 3:
                level = EASY
            elif exponent <= 5:
                level = MEDIUM
            else:
                level = HARD
            if exponent == 0:
                distractors = [0, base, base * base]
                solution = f"Any non-zero number to the power of 0 equals 1, so {base}^0 = 1."
                trap = "The base makes no difference. Every number to the power of 0 is 1, never 0."
            elif exponent == 1:
                distractors = [1, base * base, base + base]
                solution = f"A power of 1 leaves the base unchanged, so {base}^1 = {value}."
                trap = "Power 1 is not the same as power 0. Power 1 gives the base itself."
            else:
                distractors = [base * exponent, base ** (exponent - 1), base ** (exponent + 1)]
                repeated = " x ".join([str(base)] * exponent)
                solution = f"{base}^{exponent} means {base} multiplied by itself {exponent} times: {repeated} = {value}."
                trap = f"{base} x {exponent} = {base * exponent} is multiplying, not raising to a power."
            questions.append(
                {
                    "id": f"pow_{base}_{exponent}",
                    "domain": "Number facts",
                    "topic": "Power tables",
                    "difficulty": level,
                    "prompt": f"What is {base}^{exponent}?",
                    "choices": number_choices(value, distractors),
                    "answer": f"{value}",
                    "solution": solution,
                    "trap": trap,
                }
            )

    for base in [2, 3, 4, 5, 10]:
        for exponent in range(4, POWER_TABLE[base] + 1):
            value = base ** exponent
            questions.append(
                {
                    "id": f"powrev_{base}_{exponent}",
                    "domain": "Number facts",
                    "topic": "Power tables",
                    "difficulty": MEDIUM if exponent <= 5 else HARD,
                    "prompt": f"{value} is which power of {base}?",
                    "choices": text_choices(
                        f"{base}^{exponent}",
                        [f"{base}^{exponent - 1}", f"{base}^{exponent + 1}", f"{base}^{exponent + 2}"],
                    ),
                    "answer": f"{base}^{exponent}",
                    "solution": f"Reading the power table backwards, {base}^{exponent} = {value}.",
                    "trap": "Count the multiplications carefully. One step out gives a very different number.",
                }
            )

    # Rows of the notebook that land on exactly the same number.
    links = [
        (4, 5, 2, 10, 1024),
        (8, 5, 2, 15, 32768),
        (9, 3, 3, 6, 729),
        (4, 3, 2, 6, 64),
        (8, 2, 2, 6, 64),
        (9, 2, 3, 4, 81),
    ]
    for left_base, left_exp, right_base, right_exp, value in links:
        questions.append(
            {
                "id": f"powlink_{left_base}{left_exp}_{right_base}{right_exp}",
                "domain": "Number facts",
                "topic": "Power tables",
                "difficulty": HARD,
                "prompt": f"Which is larger, {left_base}^{left_exp} or {right_base}^{right_exp}?",
                "choices": text_choices(
                    "They are equal.",
                    [
                        f"{left_base}^{left_exp} is larger.",
                        f"{right_base}^{right_exp} is larger.",
                        "It depends on the order of operations.",
                    ],
                ),
                "answer": "They are equal.",
                "solution": (
                    f"{left_base}^{left_exp} = {value} and {right_base}^{right_exp} = {value}, "
                    "so those two rows of the power table meet at the same number."
                ),
                "trap": "A bigger base does not always mean a bigger answer. The index matters just as much.",
            }
        )

    index_laws = [
        (2, 5, 3, "x"),
        (2, 9, 4, "/"),
        (3, 4, 3, "x"),
        (3, 7, 4, "/"),
        (5, 3, 2, "x"),
        (10, 6, 3, "/"),
        (7, 3, 2, "x"),
        (9, 5, 3, "/"),
    ]
    for base, first, second, operation in index_laws:
        if operation == "x":
            exponent = first + second
            tag = "m"
            prompt = f"Using the power table, what is {base}^{first} x {base}^{second}?"
            solution = (
                f"Multiplying powers of the same base adds the indices: {first} + {second} = {exponent}, "
                f"so the answer is {base}^{exponent} = {base ** exponent}."
            )
            trap = "Add the indices when multiplying. Never multiply them."
        else:
            exponent = first - second
            tag = "d"
            prompt = f"Using the power table, what is {base}^{first} divided by {base}^{second}?"
            solution = (
                f"Dividing powers of the same base subtracts the indices: {first} - {second} = {exponent}, "
                f"so the answer is {base}^{exponent} = {base ** exponent}."
            )
            trap = "Subtract the indices when dividing. Never divide them."
        value = base ** exponent
        questions.append(
            {
                "id": f"powlaw_{base}_{first}_{second}_{tag}",
                "domain": "Number facts",
                "topic": "Power tables",
                "difficulty": HARD,
                "prompt": prompt,
                "choices": number_choices(
                    value,
                    [base ** (exponent + 1), base ** max(1, exponent - 1), base * exponent],
                ),
                "answer": f"{value}",
                "solution": solution,
                "trap": trap,
            }
        )
    return questions


def build_square_questions():
    """Notebook page: Squares, 11 x 11 through 26 x 26, using Rachel's own difficulty dots."""
    questions = []
    for number, level in SQUARE_DOTS.items():
        value = number * number
        questions.append(
            {
                "id": f"sq_{number}",
                "domain": "Number facts",
                "topic": "Squares 11 to 26",
                "difficulty": level,
                "prompt": f"What is {number} x {number}?",
                "choices": number_choices(value, [(number - 1) ** 2, (number + 1) ** 2, value + 20]),
                "answer": f"{value}",
                "solution": (
                    f"{number}^2 = {number} x {number} = {value}. Splitting also works: "
                    f"{number} x {number - 1} + {number} = {number * (number - 1)} + {number} = {value}."
                ),
                "trap": "Neighbouring squares look alike. Check the last digit before choosing.",
            }
        )
        questions.append(
            {
                "id": f"sqrt_{number}",
                "domain": "Number facts",
                "topic": "Squares 11 to 26",
                "difficulty": level,
                "prompt": f"What is the square root of {value}?",
                "choices": number_choices(number, [number - 1, number + 1, value // 2]),
                "answer": f"{number}",
                "solution": f"Because {number} x {number} = {value}, the square root of {value} is {number}.",
                "trap": "A square root is not half the number. Look for what multiplies by itself.",
            }
        )
    return questions


def build_percentage_fact_questions():
    """Notebook page: Percentage."""
    questions = []
    for numerator, denominator, label, level in PERCENT_FACTS:
        fraction = fraction_text(numerator, denominator)
        shown = "1 whole" if denominator == 1 else fraction
        recurring = denominator in (3, 6, 9)
        note = " The decimal recurs forever, so it is written with a bar or rounded." if recurring else ""
        percent_value = float(label.rstrip("%"))
        wrong_labels = [
            f"{denominator}%",
            f"{100 - percent_value:g}%",
            f"{percent_value / 10:g}%",
            f"{percent_value * 2:g}%",
            f"{percent_value + 10:g}%",
        ]
        questions.append(
            {
                "id": f"pctfact_{denominator}",
                "domain": "Number facts",
                "topic": "Fraction and percentage table",
                "difficulty": level,
                "prompt": f"Write {shown} as a percentage.",
                "choices": text_choices(label, wrong_labels),
                "answer": label,
                "solution": f"{shown} means {numerator} divided by {denominator}, which is {label}.{note}",
                "trap": "Per cent means out of 100, so divide first and then multiply by 100.",
            }
        )
        if denominator > 1:
            questions.append(
                {
                    "id": f"pctrev_{denominator}",
                    "domain": "Number facts",
                    "topic": "Fraction and percentage table",
                    "difficulty": level,
                    "prompt": f"Which fraction equals {label}?",
                    "choices": text_choices(
                        fraction,
                        [
                            fraction_text(1, denominator * 2),
                            fraction_text(1, max(2, denominator // 2)),
                            fraction_text(2, denominator),
                            fraction_text(1, denominator + 1),
                            fraction_text(denominator, 100),
                        ],
                    ),
                    "answer": fraction,
                    "solution": f"{label} of a whole is one part out of {denominator}, which is {fraction}.",
                    "trap": "A smaller percentage needs a larger denominator, not a smaller one.",
                }
            )

    applied = [
        (2, 84, MEDIUM),
        (4, 96, EASY),
        (5, 130, EASY),
        (8, 240, MEDIUM),
        (10, 470, EASY),
        (20, 300, MEDIUM),
        (25, 400, MEDIUM),
        (3, 240, HARD),
        (6, 360, HARD),
        (9, 540, HARD),
        (50, 850, MEDIUM),
        (100, 6200, EASY),
    ]
    for denominator, total, level in applied:
        label = next(item[2] for item in PERCENT_FACTS if item[1] == denominator)
        value = total // denominator
        questions.append(
            {
                "id": f"pctapply_{denominator}_{total}",
                "domain": "Number facts",
                "topic": "Fraction and percentage table",
                "difficulty": level,
                "prompt": f"What is {label} of {total}?",
                "choices": number_choices(
                    value,
                    [value * 2, max(1, value // 2), total - value],
                ),
                "answer": f"{value}",
                "solution": (
                    f"{label} is the same as {fraction_text(1, denominator)}, so divide: "
                    f"{total} / {denominator} = {value}."
                ),
                "trap": "Turn the percentage into its fraction first. Dividing is faster than long multiplication.",
            }
        )
    return questions


def build_factorial_questions():
    """Notebook page: Factorials."""
    questions = []
    for number in range(3, 9):
        value = math.factorial(number)
        expansion = " x ".join(str(item) for item in range(number, 0, -1))
        questions.append(
            {
                "id": f"fact_{number}",
                "domain": "Number facts",
                "topic": "Factorials",
                "difficulty": EASY if number <= 4 else (MEDIUM if number <= 6 else HARD),
                "prompt": f"What is {number}!?",
                "choices": number_choices(
                    value,
                    [math.factorial(number - 1), math.factorial(number + 1), sum(range(1, number + 1))],
                ),
                "answer": f"{value}",
                "solution": f"{number}! = {expansion} = {value}.",
                "trap": "A factorial multiplies every number down to 1. It does not add them.",
            }
        )
    for number in [6, 7, 8]:
        lower = number - 1
        value = math.factorial(number)
        questions.append(
            {
                "id": f"factshort_{number}",
                "domain": "Number facts",
                "topic": "Factorials",
                "difficulty": HARD,
                "prompt": f"Given that {lower}! = {math.factorial(lower)}, use the short cut rule to find {number}!.",
                "choices": number_choices(
                    value,
                    [math.factorial(lower) + number, math.factorial(lower) * lower, math.factorial(number + 1)],
                ),
                "answer": f"{value}",
                "solution": (
                    f"The short cut rule is n! = n x (n - 1)!, so {number}! = {number} x {lower}! = "
                    f"{number} x {math.factorial(lower)} = {value}."
                ),
                "trap": "Multiply by the new number. Adding it gives a far smaller answer.",
            }
        )
        questions.append(
            {
                "id": f"factdiv_{number}",
                "domain": "Number facts",
                "topic": "Factorials",
                "difficulty": HARD,
                "prompt": f"What is {number}! divided by {lower}!?",
                "choices": number_choices(number, [1, lower, math.factorial(number) // 2]),
                "answer": f"{number}",
                "solution": f"{number}! = {number} x {lower}!, so dividing by {lower}! leaves just {number}.",
                "trap": "Cancel the shared part of the factorial before reaching for a calculator.",
            }
        )
    return questions


def build_bodmas_questions():
    """Notebook page: Formulas, BODMAS."""
    questions = []
    patterns = [
        (7, 6, 3, 5, EASY),
        (12, 4, 5, 9, EASY),
        (20, 3, 7, 6, MEDIUM),
        (9, 8, 2, 11, MEDIUM),
        (30, 5, 4, 18, HARD),
    ]
    for a, b, c, d, level in patterns:
        plain = a + b * c - d
        questions.append(
            {
                "id": f"bodmas_plain_{a}_{b}_{c}_{d}",
                "domain": "Formulas",
                "topic": "BODMAS",
                "difficulty": level,
                "prompt": f"Work out {a} + {b} x {c} - {d}.",
                "choices": number_choices(plain, [(a + b) * c - d, a + b * (c - d), plain + d]),
                "answer": f"{plain}",
                "solution": (
                    f"Multiplication comes before addition and subtraction: {b} x {c} = {b * c}. "
                    f"Then {a} + {b * c} - {d} = {plain}."
                ),
                "trap": "Do not work straight from left to right. Multiplication happens first.",
            }
        )
        bracketed = (a + b) * c - d
        questions.append(
            {
                "id": f"bodmas_bracket_{a}_{b}_{c}_{d}",
                "domain": "Formulas",
                "topic": "BODMAS",
                "difficulty": level,
                "prompt": f"Work out ({a} + {b}) x {c} - {d}.",
                "choices": number_choices(bracketed, [a + b * c - d, (a + b) * (c - d), bracketed + d]),
                "answer": f"{bracketed}",
                "solution": (
                    f"Brackets first: {a} + {b} = {a + b}. Then {a + b} x {c} = {(a + b) * c}, "
                    f"and finally subtract {d} to get {bracketed}."
                ),
                "trap": "The bracket changes everything. Clear it before you multiply.",
            }
        )

    divisions = [
        (24, 6, 2, 5, MEDIUM),
        (36, 9, 3, 7, MEDIUM),
        (48, 8, 4, 11, HARD),
    ]
    for a, b, c, d, level in divisions:
        value = a / b * c + d
        questions.append(
            {
                "id": f"bodmas_div_{a}_{b}_{c}_{d}",
                "domain": "Formulas",
                "topic": "BODMAS",
                "difficulty": level,
                "prompt": f"Work out {a} / {b} x {c} + {d}.",
                "choices": number_choices(
                    int(value),
                    [int(a / (b * c) + d), int(a / b * (c + d)), int(value) + c],
                ),
                "answer": f"{int(value)}",
                "solution": (
                    f"Division and multiplication have the same rank, so work left to right: "
                    f"{a} / {b} = {int(a / b)}, then {int(a / b)} x {c} = {int(a / b * c)}, then add {d} = {int(value)}."
                ),
                "trap": (
                    "The D before the M in BODMAS does not mean divide first. Multiplication and division "
                    "rank equally and are done left to right."
                ),
            }
        )

    questions.append(
        {
            "id": "bodmas_rank_rule",
            "domain": "Formulas",
            "topic": "BODMAS",
            "difficulty": HARD,
            "prompt": "In 40 / 5 x 2, which operation is carried out first?",
            "choices": text_choices(
                "The division, because multiplication and division are worked left to right.",
                [
                    "The multiplication, because BODMAS puts D before M.",
                    "Either one, because the answer is the same.",
                    "The multiplication, because it is closer to the end.",
                ],
            ),
            "answer": "The division, because multiplication and division are worked left to right.",
            "solution": (
                "40 / 5 x 2 = 8 x 2 = 16. Doing the multiplication first would give 40 / 10 = 4, which is wrong. "
                "Multiplication and division sit at the same level, so they run left to right. Addition and "
                "subtraction work the same way."
            ),
            "trap": "BODMAS is a memory aid, not a strict order for the last four letters.",
        }
    )
    return questions


def build_profit_questions():
    """Notebook pages: Profit / discount and Percentage Profit."""
    questions = []
    discounts = [(200, 15, EASY), (450, 20, EASY), (80, 25, MEDIUM), (640, 35, MEDIUM), (1250, 12, HARD)]
    for selling, percent, level in discounts:
        discount = selling * percent / 100
        final = selling - discount
        questions.append(
            {
                "id": f"disc_{selling}_{percent}",
                "domain": "Formulas",
                "topic": "Profit, loss and discount",
                "difficulty": level,
                "prompt": f"A jacket has a selling price of ${selling:g} with a {percent}% discount. How much is the discount?",
                "choices": money_choices(discount, [final, selling + discount, discount * 2]),
                "answer": f"${discount:g}",
                "solution": (
                    f"Discount = percentage x selling price = {percent}% x ${selling:g} = "
                    f"{percent / 100:g} x {selling:g} = ${discount:g}."
                ),
                "trap": "The discount is the amount taken off, not the price you pay.",
            }
        )
        questions.append(
            {
                "id": f"final_{selling}_{percent}",
                "domain": "Formulas",
                "topic": "Profit, loss and discount",
                "difficulty": level,
                "prompt": f"A ${selling:g} item is discounted by {percent}%. What is the final price?",
                "choices": money_choices(final, [discount, selling, final - discount]),
                "answer": f"${final:g}",
                "solution": (
                    f"Discount = {percent}% x ${selling:g} = ${discount:g}. "
                    f"Final price = selling price - discount = ${selling:g} - ${discount:g} = ${final:g}."
                ),
                "trap": "Two steps are needed. Finding the discount is only half the question.",
            }
        )

    trades = [(60, 84, EASY), (250, 310, MEDIUM), (400, 340, MEDIUM), (125, 200, HARD), (90, 72, HARD)]
    for cost, final, level in trades:
        if final >= cost:
            profit = final - cost
            questions.append(
                {
                    "id": f"profit_{cost}_{final}",
                    "domain": "Formulas",
                    "topic": "Profit, loss and discount",
                    "difficulty": level,
                    "prompt": f"An item costs ${cost:g} and sells for ${final:g}. What is the profit?",
                    "choices": money_choices(profit, [cost + final, final, cost - final if cost > final else profit + 10]),
                    "answer": f"${profit:g}",
                    "solution": f"Profit = final price - cost price = ${final:g} - ${cost:g} = ${profit:g}.",
                    "trap": "Profit subtracts the cost price from the selling price, in that order.",
                }
            )
            percent = profit / cost * 100
            questions.append(
                {
                    "id": f"pctprofit_{cost}_{final}",
                    "domain": "Formulas",
                    "topic": "Percentage profit",
                    "difficulty": HARD,
                    "prompt": f"An item costs ${cost:g} and sells for ${final:g}. What is the percentage profit?",
                    "choices": decimal_choices(percent, [profit / final * 100, percent / 2, percent * 2], suffix="%", places=1),
                    "answer": decimal_answer(percent, suffix="%", places=1),
                    "solution": (
                        f"Profit = ${final:g} - ${cost:g} = ${profit:g}. "
                        f"Percentage profit = profit / cost price x 100% = {profit:g} / {cost:g} x 100% = "
                        f"{decimal_answer(percent, suffix='%', places=1)}."
                    ),
                    "trap": "Percentage profit divides by the COST price, never by the selling price.",
                }
            )
        else:
            loss = cost - final
            questions.append(
                {
                    "id": f"loss_{cost}_{final}",
                    "domain": "Formulas",
                    "topic": "Profit, loss and discount",
                    "difficulty": level,
                    "prompt": f"An item costs ${cost:g} but only sells for ${final:g}. What is the loss?",
                    "choices": money_choices(loss, [cost + final, final, loss * 2]),
                    "answer": f"${loss:g}",
                    "solution": f"Loss = cost price - final price = ${cost:g} - ${final:g} = ${loss:g}.",
                    "trap": "For a loss the cost price comes first. Swapping them gives a negative answer.",
                }
            )
    return questions


def build_consecutive_questions():
    """Notebook page: Formulas, consecutive integers and even or odd numbers."""
    questions = []
    for total in [84, 96, 141, 216, 60]:
        smallest = (total - 3) // 3
        if smallest * 3 + 3 != total:
            continue
        questions.append(
            {
                "id": f"consec_{total}",
                "domain": "Formulas",
                "topic": "Consecutive integers",
                "difficulty": MEDIUM,
                "prompt": f"Three consecutive integers add to {total}. What is the smallest one?",
                "choices": number_choices(smallest, [smallest + 1, smallest + 2, total // 3]),
                "answer": f"{smallest}",
                "solution": (
                    f"Write them as x + (x + 1) + (x + 2) = 3x + 3 = {total}. "
                    f"So 3x = {total - 3} and x = {smallest}. The numbers are {smallest}, {smallest + 1}, {smallest + 2}."
                ),
                "trap": "The +1 and +2 add an extra 3 to the total. Take that off before dividing.",
            }
        )
    for total, kind in [(96, "even"), (141, "odd"), (72, "even"), (105, "odd")]:
        smallest = (total - 6) // 3
        if smallest * 3 + 6 != total:
            continue
        questions.append(
            {
                "id": f"consecstep_{kind}_{total}",
                "domain": "Formulas",
                "topic": "Consecutive integers",
                "difficulty": HARD,
                "prompt": f"Three consecutive {kind} numbers add to {total}. What is the smallest one?",
                "choices": number_choices(smallest, [smallest + 2, smallest + 4, total // 3]),
                "answer": f"{smallest}",
                "solution": (
                    f"Consecutive {kind} numbers step by 2: x + (x + 2) + (x + 4) = 3x + 6 = {total}. "
                    f"So 3x = {total - 6} and x = {smallest}. The numbers are {smallest}, {smallest + 2}, {smallest + 4}."
                ),
                "trap": f"{kind.title()} numbers jump by 2, so the extra total is 6, not 3.",
            }
        )
    return questions


def build_probability_questions():
    """Notebook page: Formulas, Probability."""
    questions = []
    bags = [
        (5, 3, 4, "blue", MEDIUM),
        (6, 2, 4, "red", EASY),
        (8, 7, 5, "green", HARD),
        (4, 4, 4, "red", EASY),
    ]
    for red, blue, green, wanted, level in bags:
        counts = {"red": red, "blue": blue, "green": green}
        total = red + blue + green
        favourable = counts[wanted]
        answer = fraction_text(favourable, total)
        questions.append(
            {
                "id": f"prob_bag_{red}{blue}{green}_{wanted}",
                "domain": "Data and chance",
                "topic": "Probability",
                "difficulty": level,
                "prompt": (
                    f"A bag holds {red} red, {blue} blue and {green} green counters. "
                    f"What is the probability of drawing a {wanted} counter?"
                ),
                "choices": text_choices(
                    answer,
                    [
                        fraction_text(total - favourable, total),
                        fraction_text(favourable, total - favourable),
                        fraction_text(favourable + 1, total),
                        f"{favourable}/{favourable + 1}",
                        fraction_text(favourable, total + 1),
                    ],
                ),
                "answer": answer,
                "solution": (
                    f"Probability = number of favourable outcomes / total outcomes = {favourable} / {total} = {answer}."
                ),
                "trap": "The denominator is every counter in the bag, not just the other colours.",
            }
        )
    dice = [
        ("a number greater than 4", 2, EASY),
        ("an even number", 3, EASY),
        ("a factor of 6", 4, HARD),
    ]
    for description, favourable, level in dice:
        answer = fraction_text(favourable, 6)
        questions.append(
            {
                "id": f"prob_dice_{favourable}",
                "domain": "Data and chance",
                "topic": "Probability",
                "difficulty": level,
                "prompt": f"A fair six-sided die is rolled. What is the probability of {description}?",
                "choices": text_choices(
                    answer,
                    [
                        fraction_text(6 - favourable, 6),
                        fraction_text(favourable, 12),
                        fraction_text(favourable + 1, 6),
                        f"{favourable}/{favourable + 1}",
                        f"{favourable}/1",
                    ],
                ),
                "answer": answer,
                "solution": (
                    f"There are {favourable} favourable outcomes out of 6 equally likely results, "
                    f"so the probability is {favourable}/6 = {answer}."
                ),
                "trap": "Count the favourable faces carefully, then simplify the fraction.",
            }
        )
    return questions


def build_polygon_questions():
    """Notebook page: Polygon angles."""
    questions = []
    for sides in [5, 6, 8, 9, 10, 12]:
        total = (sides - 2) * 180
        level = EASY if sides <= 6 else (MEDIUM if sides <= 9 else HARD)
        questions.append(
            {
                "id": f"polyfwd_{sides}",
                "domain": "Formulas",
                "topic": "Polygon angles",
                "difficulty": level,
                "prompt": f"What do the interior angles of a polygon with {sides} sides add to?",
                "choices": number_choices(total, [sides * 180, total + 180, total - 180], suffix=" degrees"),
                "answer": f"{total} degrees",
                "solution": f"Sum = (n - 2) x 180 = ({sides} - 2) x 180 = {sides - 2} x 180 = {total} degrees.",
                "trap": "Subtract 2 from the number of sides before multiplying by 180.",
            }
        )
        questions.append(
            {
                "id": f"polyrev_{sides}",
                "domain": "Formulas",
                "topic": "Polygon angles",
                "difficulty": level,
                "prompt": f"The interior angles of a polygon add to {total} degrees. How many sides does it have?",
                "choices": number_choices(sides, [sides - 2, sides + 2, total // 180]),
                "answer": f"{sides}",
                "solution": (
                    f"Given sum / 180 = x, so {total} / 180 = {sides - 2}. "
                    f"Then x + 2 = number of sides = {sides - 2} + 2 = {sides}."
                ),
                "trap": "Dividing by 180 gives n - 2. Remember to add the 2 back on.",
            }
        )
    return questions


def build_ratio_questions():
    """Notebook page: Ratio."""
    questions = []
    two_part = [(240, 3, 5, EASY), (420, 2, 5, MEDIUM), (960, 7, 5, HARD)]
    for total, a, b, level in two_part:
        parts = a + b
        unit = total // parts
        larger = max(a, b) * unit
        smaller = min(a, b) * unit
        questions.append(
            {
                "id": f"ratio2_{total}_{a}_{b}",
                "domain": "Formulas",
                "topic": "Ratio sharing",
                "difficulty": level,
                "prompt": f"${total} is shared in the ratio {a}:{b}. What is the larger share?",
                "choices": money_choices(larger, [smaller, unit, total - unit]),
                "answer": f"${larger:g}",
                "solution": (
                    f"Total parts = {a} + {b} = {parts}. One part = {total} / {parts} = {unit}. "
                    f"The larger share is {max(a, b)} x {unit} = ${larger}."
                ),
                "trap": "Find the value of one part first, then multiply by that share's number of parts.",
            }
        )
    three_part = [(450, 2, 3, 4, MEDIUM), (960, 4, 5, 7, HARD), (360, 1, 2, 3, EASY)]
    for total, a, b, c, level in three_part:
        parts = a + b + c
        unit = total // parts
        middle = b * unit
        questions.append(
            {
                "id": f"ratio3_{total}_{a}{b}{c}",
                "domain": "Formulas",
                "topic": "Ratio sharing",
                "difficulty": level,
                "prompt": f"${total} is shared in the ratio {a}:{b}:{c}. What is the middle share?",
                "choices": money_choices(middle, [a * unit, c * unit, unit]),
                "answer": f"${middle:g}",
                "solution": (
                    f"Total parts = {a} + {b} + {c} = {parts}. One part = {total} / {parts} = {unit}. "
                    f"The middle share is {b} x {unit} = ${middle}."
                ),
                "trap": "Divide by the TOTAL number of parts, not by the number of people.",
            }
        )
    questions.append(
        {
            "id": "ratio_difference",
            "domain": "Formulas",
            "topic": "Ratio sharing",
            "difficulty": HARD,
            "prompt": "Prize money is shared in the ratio 4:5:7. The largest share is $180 more than the smallest. What is the total?",
            "choices": money_choices(960, [720, 540, 1080]),
            "answer": "$960",
            "solution": (
                "The difference is 7 - 4 = 3 parts, so 3 parts = $180 and one part = $60. "
                "The total is 4 + 5 + 7 = 16 parts, which is 16 x $60 = $960."
            ),
            "trap": "Use the difference in parts to find one part before scaling to the total.",
        }
    )
    return questions


def build_sequence_questions():
    """Notebook page: Sum of a sequence."""
    questions = []
    sums = [
        (2, 40, 2, MEDIUM),
        (1, 100, 1, EASY),
        (1, 39, 2, MEDIUM),
        (5, 50, 5, HARD),
        (3, 60, 3, HARD),
    ]
    for first, last, step, level in sums:
        terms = (last - first) // step + 1
        total = terms * (first + last) // 2
        questions.append(
            {
                "id": f"seqsum_{first}_{last}_{step}",
                "domain": "Formulas",
                "topic": "Sum of a sequence",
                "difficulty": level,
                "prompt": f"Find the sum of {first}, {first + step}, {first + 2 * step}, ... , {last}.",
                "choices": number_choices(total, [total // 2, total + last, terms * last]),
                "answer": f"{total}",
                "solution": (
                    f"Number of terms n = ({last} - {first}) / {step} + 1 = {terms}. "
                    f"Then S = n(f + l) / 2 = {terms} x ({first} + {last}) / 2 = {terms} x {first + last} / 2 = {total}."
                ),
                "trap": "Count the terms first. Forgetting the +1 loses one whole term.",
            }
        )
        questions.append(
            {
                "id": f"seqterms_{first}_{last}_{step}",
                "domain": "Formulas",
                "topic": "Sum of a sequence",
                "difficulty": level,
                "prompt": f"How many terms are in the sequence {first}, {first + step}, {first + 2 * step}, ... , {last}?",
                "choices": number_choices(terms, [terms - 1, terms + 1, last // step]),
                "answer": f"{terms}",
                "solution": (
                    f"n = (last - first) / step + 1 = ({last} - {first}) / {step} + 1 = "
                    f"{(last - first) // step} + 1 = {terms}."
                ),
                "trap": "Always add 1 at the end. Subtracting alone counts the gaps, not the terms.",
            }
        )
    return questions


def build_heads_legs_questions():
    """Notebook page: Heads and legs."""
    questions = []
    farms = [(30, 84, EASY), (25, 78, MEDIUM), (40, 116, MEDIUM), (52, 150, HARD)]
    for heads, legs, level in farms:
        cows = (legs - 2 * heads) // 2
        chickens = heads - cows
        questions.append(
            {
                "id": f"heads_{heads}_{legs}",
                "domain": "Formulas",
                "topic": "Heads and legs",
                "difficulty": level,
                "prompt": f"A farm has {heads} cows and chickens altogether, with {legs} legs in total. How many cows are there?",
                "choices": number_choices(cows, [chickens, heads - cows + 2, legs // 4]),
                "answer": f"{cows}",
                "solution": (
                    f"Heads: c + h = {heads}. Legs: 4c + 2h = {legs}. "
                    f"Using c = (total legs - 2 x total heads) / 2 = ({legs} - {2 * heads}) / 2 = {cows} cows. "
                    f"That leaves {chickens} chickens, and {cows} x 4 + {chickens} x 2 = {legs} legs. Correct."
                ),
                "trap": "Cows have 4 legs and chickens 2. Check the legs add back to the total.",
            }
        )
        questions.append(
            {
                "id": f"headschick_{heads}_{legs}",
                "domain": "Formulas",
                "topic": "Heads and legs",
                "difficulty": level,
                "prompt": f"A farm has {heads} cows and chickens altogether, with {legs} legs in total. How many chickens are there?",
                "choices": number_choices(chickens, [cows, heads, legs // 2]),
                "answer": f"{chickens}",
                "solution": (
                    f"c = ({legs} - 2 x {heads}) / 2 = {cows} cows, so h = {heads} - {cows} = {chickens} chickens."
                ),
                "trap": "Find the cows first, then take them off the head count.",
            }
        )
    return questions


def build_speed_questions():
    """Notebook page: Average speed when distances are equal."""
    questions = []
    trips = [(30, 60, EASY), (40, 60, MEDIUM), (20, 30, MEDIUM), (50, 75, HARD), (12, 24, HARD)]
    for out_speed, back_speed, level in trips:
        average = 2 * out_speed * back_speed / (out_speed + back_speed)
        questions.append(
            {
                "id": f"speed_{out_speed}_{back_speed}",
                "domain": "Formulas",
                "topic": "Average speed",
                "difficulty": level,
                "prompt": (
                    f"A car drives to a town at {out_speed} km/h and returns along the same road at "
                    f"{back_speed} km/h. What is the average speed for the whole trip?"
                ),
                "choices": number_choices(
                    int(average),
                    [(out_speed + back_speed) // 2, out_speed + back_speed, int(average) + 5],
                    suffix=" km/h",
                ),
                "answer": f"{int(average)} km/h",
                "solution": (
                    f"With equal distances, average speed = 2ab / (a + b) = "
                    f"2 x {out_speed} x {back_speed} / ({out_speed} + {back_speed}) = "
                    f"{2 * out_speed * back_speed} / {out_speed + back_speed} = {int(average)} km/h."
                ),
                "trap": (
                    f"The plain average ({(out_speed + back_speed) / 2:g} km/h) is wrong. More time is spent "
                    "at the slower speed, so the answer is always lower."
                ),
            }
        )
    questions.append(
        {
            "id": "speed_time_step",
            "domain": "Formulas",
            "topic": "Average speed",
            "difficulty": HARD,
            "prompt": (
                "A cyclist rides 60 km out at 20 km/h and 60 km back at 30 km/h. "
                "How long does the whole 120 km trip take?"
            ),
            "choices": number_choices(5, [4, 6, 3], suffix=" hours"),
            "answer": "5 hours",
            "solution": (
                "Average speed = 2ab / (a + b) = 2 x 20 x 30 / 50 = 1200 / 50 = 24 km/h. "
                "Then time = distance / speed = 120 / 24 = 5 hours."
            ),
            "trap": "Find the average speed first, then divide the given total distance by it.",
        }
    )
    return questions


def build_triangle_questions():
    """Notebook pages: Types of Triangles and Area, Obtuse and Acute Triangle."""
    questions = []
    half_base = [
        ("right-angled", 12, 9, EASY),
        ("isosceles", 10, 14, EASY),
        ("obtuse", 16, 7, MEDIUM),
        ("acute", 18, 11, MEDIUM),
        ("right-angled", 25, 14, HARD),
    ]
    for kind, base, height, level in half_base:
        area = base * height / 2
        article = "An" if kind[0] in "aeiou" else "A"
        questions.append(
            {
                "id": f"tri_{kind}_{base}_{height}",
                "domain": "Geometry",
                "topic": "Triangles and area",
                "difficulty": level,
                "prompt": (
                    f"{article} {kind} triangle has base {base} cm and perpendicular height {height} cm. "
                    "What is its area?"
                ),
                "choices": number_choices(
                    int(area),
                    [base * height, int(area) + base, base + height],
                    suffix=" square cm",
                ),
                "answer": f"{int(area)} square cm",
                "solution": (
                    f"Every one of these triangle types uses A = 1/2 x b x h. "
                    f"A = 1/2 x {base} x {height} = {int(area)} square cm."
                ),
                "trap": "Halve the answer. Base x height alone gives the surrounding rectangle.",
            }
        )

    for side in [6, 8, 10, 12]:
        area = math.sqrt(3) / 4 * side * side
        questions.append(
            {
                "id": f"trieq_{side}",
                "domain": "Geometry",
                "topic": "Triangles and area",
                "difficulty": HARD,
                "prompt": f"An equilateral triangle has side length {side} cm. What is its area, to 2 decimal places?",
                "choices": decimal_choices(
                    area,
                    [side * side / 2, side * side, area * 2],
                    suffix=" square cm",
                    places=2,
                ),
                "answer": decimal_answer(area, suffix=" square cm", places=2),
                "solution": (
                    f"A = (sqrt(3) / 4) x a^2. Here a^2 = {side * side}, and sqrt(3) / 4 = 1.732 / 4 = 0.433, "
                    f"so A = 0.433 x {side * side} = {decimal_answer(area, places=2)} square cm."
                ),
                "trap": "An equilateral triangle needs the sqrt(3)/4 rule, not 1/2 x b x h with the side as height.",
            }
        )

    herons = [(3, 4, 5, 6, EASY), (13, 14, 15, 84, HARD), (6, 8, 10, 24, MEDIUM), (9, 10, 17, 36, HARD), (7, 15, 20, 42, HARD)]
    for a, b, c, area, level in herons:
        s = (a + b + c) / 2
        questions.append(
            {
                "id": f"heron_{a}_{b}_{c}",
                "domain": "Geometry",
                "topic": "Triangles and area",
                "difficulty": level,
                "prompt": f"A scalene triangle has sides {a} cm, {b} cm and {c} cm. Use Heron's formula to find its area.",
                "choices": number_choices(area, [int(s), a * b // 2, area * 2], suffix=" square cm"),
                "answer": f"{area} square cm",
                "solution": (
                    f"s = (a + b + c) / 2 = ({a} + {b} + {c}) / 2 = {s:g}. "
                    f"A = sqrt(s(s - a)(s - b)(s - c)) = sqrt({s:g} x {s - a:g} x {s - b:g} x {s - c:g}) = "
                    f"sqrt({int(s * (s - a) * (s - b) * (s - c))}) = {area} square cm."
                ),
                "trap": "s is HALF the perimeter. Using the full perimeter makes the area far too large.",
            }
        )

    questions.append(
        {
            "id": "tri_obtuse_def",
            "domain": "Geometry",
            "topic": "Triangles and area",
            "difficulty": EASY,
            "prompt": "What makes a triangle obtuse?",
            "choices": text_choices(
                "One angle is greater than 90 degrees.",
                [
                    "All three angles are less than 90 degrees.",
                    "One angle is exactly 90 degrees.",
                    "All three sides are the same length.",
                ],
            ),
            "answer": "One angle is greater than 90 degrees.",
            "solution": "An obtuse triangle has exactly one angle bigger than 90 degrees. Its area still uses 1/2 x b x h.",
            "trap": "Only one angle can be obtuse, because the three angles must total 180 degrees.",
        }
    )
    questions.append(
        {
            "id": "tri_acute_def",
            "domain": "Geometry",
            "topic": "Triangles and area",
            "difficulty": EASY,
            "prompt": "What makes a triangle acute?",
            "choices": text_choices(
                "All three angles are less than 90 degrees.",
                [
                    "One angle is greater than 90 degrees.",
                    "One angle is exactly 90 degrees.",
                    "Two sides are equal in length.",
                ],
            ),
            "answer": "All three angles are less than 90 degrees.",
            "solution": "In an acute triangle every angle is under 90 degrees.",
            "trap": "Equal sides make a triangle isosceles or equilateral, which is about sides, not angles.",
        }
    )
    return questions


def build_pythagoras_questions():
    """Notebook pages: Pythagorean Theorem and Pythagoras' Theorem."""
    questions = []
    triples = [(3, 4, 5, EASY), (6, 8, 10, EASY), (5, 12, 13, MEDIUM), (9, 12, 15, MEDIUM), (8, 15, 17, HARD), (7, 24, 25, HARD), (9, 40, 41, HARD), (20, 21, 29, HARD)]
    for a, b, c, level in triples:
        questions.append(
            {
                "id": f"pyth_hyp_{a}_{b}",
                "domain": "Geometry",
                "topic": "Pythagoras",
                "difficulty": level,
                "prompt": f"A right-angled triangle has legs of {a} cm and {b} cm. How long is the hypotenuse?",
                "choices": number_choices(c, [a + b, c - 1, c + 1], suffix=" cm"),
                "answer": f"{c} cm",
                "solution": (
                    f"c^2 = a^2 + b^2 = {a}^2 + {b}^2 = {a * a} + {b * b} = {c * c}. "
                    f"So c = sqrt({c * c}) = {c} cm."
                ),
                "trap": f"Do not add the legs. {a} + {b} = {a + b} is always too big.",
            }
        )
        questions.append(
            {
                "id": f"pyth_leg_{a}_{b}",
                "domain": "Geometry",
                "topic": "Pythagoras",
                "difficulty": HARD,
                "prompt": f"A right-angled triangle has a hypotenuse of {c} cm and one leg of {b} cm. How long is the other leg?",
                "choices": number_choices(a, [c - b, c + b, a + 2], suffix=" cm"),
                "answer": f"{a} cm",
                "solution": (
                    f"Rearrange c^2 = a^2 + b^2 to a^2 = c^2 - b^2 = {c * c} - {b * b} = {a * a}. "
                    f"So a = sqrt({a * a}) = {a} cm."
                ),
                "trap": "When a leg is missing you SUBTRACT the squares. Adding them finds a hypotenuse.",
            }
        )
    questions.append(
        {
            "id": "pyth_hyp_def",
            "domain": "Geometry",
            "topic": "Pythagoras",
            "difficulty": EASY,
            "prompt": "Where is the hypotenuse of a right-angled triangle?",
            "choices": text_choices(
                "It is the longest side, always opposite the 90 degree angle.",
                [
                    "It is the shortest side, next to the 90 degree angle.",
                    "It is whichever side sits along the bottom.",
                    "It is the side marked with the height.",
                ],
            ),
            "answer": "It is the longest side, always opposite the 90 degree angle.",
            "solution": "The hypotenuse faces the right angle and is the longest side, so c is always the largest number in c^2 = a^2 + b^2.",
            "trap": "If the answer for a hypotenuse is smaller than a leg, something has gone wrong.",
        }
    )
    return questions


def build_area_questions():
    """Notebook pages: Rectangle, Parallelogram, Triangle, Rhombus, Kite, Trapezium, Circle, Sector, Diamond, Square area."""
    questions = []
    rectangles = [(12, 7, EASY), (25, 8, MEDIUM), (14, 13, HARD)]
    for length, width, level in rectangles:
        area = length * width
        perimeter = 2 * (length + width)
        questions.append(
            {
                "id": f"arearect_{length}_{width}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": level,
                "prompt": f"A rectangle is {length} cm long and {width} cm wide. What is its area?",
                "choices": number_choices(area, [perimeter, length + width, area * 2], suffix=" square cm"),
                "answer": f"{area} square cm",
                "solution": f"A = l x w = {length} x {width} = {area} square cm.",
                "trap": "Area multiplies. Perimeter adds. Check which one the question wants.",
            }
        )
        questions.append(
            {
                "id": f"perimrect_{length}_{width}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": level,
                "prompt": f"A rectangle is {length} cm long and {width} cm wide. What is its perimeter?",
                "choices": number_choices(perimeter, [area, length + width, perimeter * 2], suffix=" cm"),
                "answer": f"{perimeter} cm",
                "solution": f"P = 2(l + w) = 2 x ({length} + {width}) = 2 x {length + width} = {perimeter} cm.",
                "trap": "Double the sum of the two sides. Adding them once only covers half the way round.",
            }
        )

    for side, level in [(9, EASY), (14, MEDIUM), (21, HARD)]:
        questions.append(
            {
                "id": f"areasq_{side}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": level,
                "prompt": f"What is the area of a square with side length {side} cm?",
                "choices": number_choices(side * side, [side * 4, side * 2, side * side + 10], suffix=" square cm"),
                "answer": f"{side * side} square cm",
                "solution": f"A = l x l = {side} x {side} = {side * side} square cm.",
                "trap": "Four sides of length l give the perimeter, not the area.",
            }
        )

    for base, height, level in [(11, 6, EASY), (18, 9, MEDIUM), (23, 14, HARD)]:
        questions.append(
            {
                "id": f"areapara_{base}_{height}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": level,
                "prompt": f"A parallelogram has base {base} cm and perpendicular height {height} cm. What is its area?",
                "choices": number_choices(
                    base * height,
                    [base * height // 2, base + height, 2 * (base + height)],
                    suffix=" square cm",
                ),
                "answer": f"{base * height} square cm",
                "solution": f"A = b x h = {base} x {height} = {base * height} square cm.",
                "trap": "A parallelogram is NOT halved. Only the triangle version uses the 1/2.",
            }
        )

    for x, y, level in [(10, 8, EASY), (14, 9, MEDIUM), (17, 12, HARD)]:
        area = x * y / 2
        for shape in ["rhombus", "kite"]:
            questions.append(
                {
                    "id": f"area{shape}_{x}_{y}",
                    "domain": "Geometry",
                    "topic": "Areas of 2D shapes",
                    "difficulty": level,
                    "prompt": f"A {shape} has diagonals of {x} cm and {y} cm. What is its area?",
                    "choices": number_choices(int(area), [x * y, x + y, int(area) + x], suffix=" square cm"),
                    "answer": f"{int(area)} square cm",
                    "solution": (
                        f"A = 1/2 x (x x y) = 1/2 x {x} x {y} = {x * y} / 2 = {int(area)} square cm."
                    ),
                    "trap": "Multiply the two diagonals, then halve. The same rule covers the diamond.",
                }
            )

    for a, b, height, level in [(14, 8, 6, MEDIUM), (20, 12, 9, MEDIUM), (25, 15, 11, HARD)]:
        area = (a + b) * height / 2
        questions.append(
            {
                "id": f"areatrap_{a}_{b}_{height}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": level,
                "prompt": (
                    f"A trapezium has parallel sides of {a} cm and {b} cm, and a perpendicular height of {height} cm. "
                    "What is its area?"
                ),
                "choices": number_choices(int(area), [(a + b) * height, a * b // 2, int(area) + height], suffix=" square cm"),
                "answer": f"{int(area)} square cm",
                "solution": (
                    f"A = 1/2 x (a + b) x h = 1/2 x ({a} + {b}) x {height} = 1/2 x {a + b} x {height} = "
                    f"{int(area)} square cm."
                ),
                "trap": "Add the two parallel sides FIRST, then multiply by the height and halve.",
            }
        )

    for radius, level in [(5, EASY), (7, MEDIUM), (12, HARD)]:
        area = math.pi * radius * radius
        questions.append(
            {
                "id": f"areacircle_{radius}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": level,
                "prompt": f"What is the area of a circle with radius {radius} cm, to 1 decimal place?",
                "choices": decimal_choices(
                    area,
                    [2 * math.pi * radius, math.pi * radius * 2, area / 2],
                    suffix=" square cm",
                    places=1,
                ),
                "answer": decimal_answer(area, suffix=" square cm", places=1),
                "solution": (
                    f"A = pi x r^2 = pi x {radius}^2 = pi x {radius * radius} = "
                    f"{decimal_answer(area, places=1)} square cm."
                ),
                "trap": "Square the radius before multiplying by pi. 2 x pi x r is the circumference.",
            }
        )

    for radius, angle, level in [(6, 90, MEDIUM), (10, 60, HARD), (8, 45, HARD)]:
        area = angle / 360 * math.pi * radius * radius
        questions.append(
            {
                "id": f"areasector_{radius}_{angle}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": level,
                "prompt": (
                    f"A sector has radius {radius} cm and an angle of {angle} degrees. "
                    "What is its area, to 1 decimal place?"
                ),
                "choices": decimal_choices(
                    area,
                    [math.pi * radius * radius, area * 2, area / 2],
                    suffix=" square cm",
                    places=1,
                ),
                "answer": decimal_answer(area, suffix=" square cm", places=1),
                "solution": (
                    f"A = (angle / 360) x (pi x r^2) = ({angle} / 360) x pi x {radius * radius} = "
                    f"{decimal_answer(area, places=1)} square cm."
                ),
                "trap": "A sector is a fraction of the whole circle, so the angle over 360 comes first.",
            }
        )
    return questions


def build_volume_questions():
    """Notebook pages: Cube, Rectangular Prism, Sphere, Cylinder, Cone, Pyramid, Tetrahedron, Prism."""
    questions = []
    for side, level in [(4, EASY), (7, MEDIUM), (11, HARD)]:
        questions.append(
            {
                "id": f"volcube_{side}",
                "domain": "Geometry",
                "topic": "Volumes of 3D solids",
                "difficulty": level,
                "prompt": f"What is the volume of a cube with edge length {side} cm?",
                "choices": number_choices(
                    side ** 3,
                    [side * side, side * 6, side ** 3 + side],
                    suffix=" cubic cm",
                ),
                "answer": f"{side ** 3} cubic cm",
                "solution": f"V = a x a x a = a^3 = {side}^3 = {side ** 3} cubic cm.",
                "trap": "Volume uses three dimensions, so cube the edge rather than squaring it.",
            }
        )

    for length, width, height, level in [(8, 5, 3, EASY), (12, 7, 4, MEDIUM), (15, 9, 6, HARD)]:
        volume = length * width * height
        questions.append(
            {
                "id": f"volprism_{length}_{width}_{height}",
                "domain": "Geometry",
                "topic": "Volumes of 3D solids",
                "difficulty": level,
                "prompt": (
                    f"A rectangular prism is {length} cm long, {width} cm wide and {height} cm high. "
                    "What is its volume?"
                ),
                "choices": number_choices(
                    volume,
                    [length * width, 2 * (length * width + length * height + width * height), volume // 2],
                    suffix=" cubic cm",
                ),
                "answer": f"{volume} cubic cm",
                "solution": f"V = l x w x h = {length} x {width} x {height} = {volume} cubic cm.",
                "trap": "All three measurements are multiplied. Two of them only give a face area.",
            }
        )

    for radius, level in [(3, MEDIUM), (6, HARD)]:
        volume = 4 / 3 * math.pi * radius ** 3
        questions.append(
            {
                "id": f"volsphere_{radius}",
                "domain": "Geometry",
                "topic": "Volumes of 3D solids",
                "difficulty": level,
                "prompt": f"What is the volume of a sphere with radius {radius} cm, to 1 decimal place?",
                "choices": decimal_choices(
                    volume,
                    [math.pi * radius ** 3, volume * 3 / 4, 4 * math.pi * radius * radius],
                    suffix=" cubic cm",
                    places=1,
                ),
                "answer": decimal_answer(volume, suffix=" cubic cm", places=1),
                "solution": (
                    f"V = 4/3 x pi x r^3 = 4/3 x pi x {radius}^3 = 4/3 x pi x {radius ** 3} = "
                    f"{decimal_answer(volume, places=1)} cubic cm."
                ),
                "trap": "Cube the radius, not square it, and keep the 4/3 in front.",
            }
        )

    for radius, height, level in [(4, 10, MEDIUM), (7, 12, HARD)]:
        cylinder = math.pi * radius * radius * height
        cone = cylinder / 3
        questions.append(
            {
                "id": f"volcyl_{radius}_{height}",
                "domain": "Geometry",
                "topic": "Volumes of 3D solids",
                "difficulty": level,
                "prompt": (
                    f"A cylinder has radius {radius} cm and height {height} cm. "
                    "What is its volume, to 1 decimal place?"
                ),
                "choices": decimal_choices(
                    cylinder,
                    [cone, math.pi * radius * height, cylinder * 2],
                    suffix=" cubic cm",
                    places=1,
                ),
                "answer": decimal_answer(cylinder, suffix=" cubic cm", places=1),
                "solution": (
                    f"V = pi x r^2 x h = pi x {radius * radius} x {height} = "
                    f"{decimal_answer(cylinder, places=1)} cubic cm."
                ),
                "trap": "Find the circular base area first, then multiply by the height.",
            }
        )
        questions.append(
            {
                "id": f"volcone_{radius}_{height}",
                "domain": "Geometry",
                "topic": "Volumes of 3D solids",
                "difficulty": HARD,
                "prompt": (
                    f"A cone has radius {radius} cm and height {height} cm. "
                    "What is its volume, to 1 decimal place?"
                ),
                "choices": decimal_choices(
                    cone,
                    [cylinder, cone * 2, cylinder / 2],
                    suffix=" cubic cm",
                    places=1,
                ),
                "answer": decimal_answer(cone, suffix=" cubic cm", places=1),
                "solution": (
                    f"V = 1/3 x pi x r^2 x h = 1/3 x pi x {radius * radius} x {height} = "
                    f"{decimal_answer(cone, places=1)} cubic cm. That is exactly a third of the matching cylinder."
                ),
                "trap": "A cone is one third of the cylinder with the same base and height.",
            }
        )

    for base_area, height, level in [(30, 9, MEDIUM), (48, 15, HARD)]:
        pyramid = base_area * height / 3
        questions.append(
            {
                "id": f"volpyr_{base_area}_{height}",
                "domain": "Geometry",
                "topic": "Volumes of 3D solids",
                "difficulty": level,
                "prompt": (
                    f"A pyramid has a base area of {base_area} square cm and a height of {height} cm. "
                    "What is its volume?"
                ),
                "choices": number_choices(
                    int(pyramid),
                    [base_area * height, int(pyramid) * 2, base_area + height],
                    suffix=" cubic cm",
                ),
                "answer": f"{int(pyramid)} cubic cm",
                "solution": (
                    f"V = 1/3 x A base x h = 1/3 x {base_area} x {height} = {int(pyramid)} cubic cm. "
                    "The height is the distance from the apex straight down to the base."
                ),
                "trap": "A prism with the same base and height would be three times bigger.",
            }
        )
        prism = base_area * height
        questions.append(
            {
                "id": f"volprismbase_{base_area}_{height}",
                "domain": "Geometry",
                "topic": "Volumes of 3D solids",
                "difficulty": level,
                "prompt": (
                    f"A prism has a base area of {base_area} square cm and a height of {height} cm. "
                    "What is its volume?"
                ),
                "choices": number_choices(
                    prism,
                    [int(pyramid), base_area + height, prism * 2],
                    suffix=" cubic cm",
                ),
                "answer": f"{prism} cubic cm",
                "solution": f"V = A base x h = {base_area} x {height} = {prism} cubic cm. No third is involved.",
                "trap": "Only pyramids, cones and tetrahedrons lose the third. A prism keeps its full volume.",
            }
        )

    for edge in [6, 12]:
        volume = edge ** 3 / (6 * math.sqrt(2))
        questions.append(
            {
                "id": f"voltetra_{edge}",
                "domain": "Geometry",
                "topic": "Volumes of 3D solids",
                "difficulty": HARD,
                "prompt": (
                    f"A regular tetrahedron has edge length {edge} cm. "
                    "What is its volume, to 2 decimal places?"
                ),
                "choices": decimal_choices(
                    volume,
                    [edge ** 3 / 6, edge ** 3 / 3, volume * 2],
                    suffix=" cubic cm",
                    places=2,
                ),
                "answer": decimal_answer(volume, suffix=" cubic cm", places=2),
                "solution": (
                    f"V = a^3 / (6 x sqrt(2)) = {edge ** 3} / (6 x 1.414) = {edge ** 3} / "
                    f"{6 * math.sqrt(2):.3f} = {decimal_answer(volume, places=2)} cubic cm."
                ),
                "trap": "sqrt(2) is about 1.414, so the denominator is roughly 8.49, not 6.",
            }
        )
    return questions


def build_conversion_questions():
    """Notebook pages: Volume Rules, Liters and volume, Scaling rule, Summary."""
    questions = []
    length_items = [(3, 300, "cm", EASY), (4.5, 450, "cm", MEDIUM), (2, 2000, "mm", MEDIUM)]
    for metres, value, unit, level in length_items:
        questions.append(
            {
                "id": f"convlen_{str(metres).replace('.', '')}_{unit}",
                "domain": "Geometry",
                "topic": "Unit conversion and scaling",
                "difficulty": level,
                "prompt": f"Convert {metres:g} m into {unit}.",
                "choices": number_choices(value, [value * 10, value // 10, value * 100], suffix=f" {unit}"),
                "answer": f"{value} {unit}",
                "solution": (
                    f"1 m = 100 cm = 1000 mm, so length multiplies by 100 to reach cm and by 1000 to reach mm. "
                    f"{metres:g} m = {value} {unit}."
                ),
                "trap": "Length scales by 100, area by 100^2 and volume by 100^3. Keep them apart.",
            }
        )

    questions.append(
        {
            "id": "convarea_1m2",
            "domain": "Geometry",
            "topic": "Unit conversion and scaling",
            "difficulty": MEDIUM,
            "prompt": "How many square centimetres are in 1 square metre?",
            "choices": number_choices(10000, [100, 1000, 1000000], suffix=" square cm"),
            "answer": "10000 square cm",
            "solution": "Area scales by 100^2, so 1 square m = 100 x 100 = 10 000 square cm.",
            "trap": "Area uses the length factor SQUARED. 100 square cm would only be a 10 cm by 10 cm tile.",
        }
    )
    questions.append(
        {
            "id": "convarea_3m2",
            "domain": "Geometry",
            "topic": "Unit conversion and scaling",
            "difficulty": HARD,
            "prompt": "Convert 3 square metres into square centimetres.",
            "choices": number_choices(30000, [300, 3000, 3000000], suffix=" square cm"),
            "answer": "30000 square cm",
            "solution": "1 square m = 10 000 square cm, so 3 square m = 3 x 10 000 = 30 000 square cm.",
            "trap": "Convert one unit first, then scale up by the number given.",
        }
    )
    questions.append(
        {
            "id": "convvol_1m3",
            "domain": "Geometry",
            "topic": "Unit conversion and scaling",
            "difficulty": MEDIUM,
            "prompt": "How many cubic centimetres are in 1 cubic metre?",
            "choices": number_choices(1000000, [1000, 10000, 100000], suffix=" cubic cm"),
            "answer": "1000000 cubic cm",
            "solution": "Volume scales by 100^3, so 1 cubic m = 100 x 100 x 100 = 1 000 000 cubic cm.",
            "trap": "Three dimensions means three factors of 100.",
        }
    )

    litre_items = [
        ("How many litres are in 1 cubic metre?", 1000, " L", "1 cubic m = 1000 L.", EASY),
        ("How many millilitres are in 1 litre?", 1000, " mL", "1 L = 1000 mL.", EASY),
        ("How many millilitres does 1 cubic centimetre hold?", 1, " mL", "1 cubic cm = 1 mL exactly.", MEDIUM),
        ("How many litres are in 2.5 cubic metres?", 2500, " L", "1 cubic m = 1000 L, so 2.5 cubic m = 2500 L.", HARD),
    ]
    for index, (prompt, value, suffix, explanation, level) in enumerate(litre_items):
        questions.append(
            {
                "id": f"convlitre_{index}",
                "domain": "Geometry",
                "topic": "Unit conversion and scaling",
                "difficulty": level,
                "prompt": prompt,
                "choices": number_choices(value, [value * 10, max(1, value // 10), value * 100], suffix=suffix),
                "answer": f"{value}{suffix}",
                "solution": explanation,
                "trap": "Litres link to cubic centimetres, which is why 1 cubic cm is exactly 1 mL.",
            }
        )

    for volume, level in [(250, EASY), (1500, MEDIUM)]:
        questions.append(
            {
                "id": f"density_{volume}",
                "domain": "Geometry",
                "topic": "Unit conversion and scaling",
                "difficulty": level,
                "prompt": f"What is the mass of {volume} cubic cm of water?",
                "choices": number_choices(volume, [volume * 10, volume // 10, volume * 1000], suffix=" g"),
                "answer": f"{volume} g",
                "solution": (
                    f"Mass = density x volume. Water has a density of 1 g per cubic cm, "
                    f"so mass = 1 x {volume} = {volume} g."
                ),
                "trap": "1 g per cubic cm is the same as 1000 kg per cubic metre. Match the units before multiplying.",
            }
        )

    scaling = [
        ("double", 2, 8, "volume", HARD),
        ("triple", 3, 27, "volume", HARD),
        ("double", 2, 4, "area", MEDIUM),
        ("triple", 3, 9, "area", MEDIUM),
    ]
    for word, factor, result, measure, level in scaling:
        power = 3 if measure == "volume" else 2
        questions.append(
            {
                "id": f"scale_{word}_{measure}",
                "domain": "Geometry",
                "topic": "Unit conversion and scaling",
                "difficulty": level,
                "prompt": f"If you {word} every length of a solid, how many times bigger does the {measure} become?",
                "choices": number_choices(result, [factor, factor * power, result * 2], suffix=" times"),
                "answer": f"{result} times",
                "solution": (
                    f"{measure.title()} uses {power} dimensions, so the scale factor is raised to the power {power}: "
                    f"{factor}^{power} = {result} times bigger."
                ),
                "trap": f"{word[:-1].title()}ing the length does NOT just {word} the {measure}.",
            }
        )
    return questions


def build_direction_questions():
    """Notebook pages: North, East, South, West, Movement Formula, Distance from start, Turning angles."""
    questions = []
    walks = [(6, 3, 8, 4, EASY), (12, 4, 15, 9, MEDIUM), (9, 1, 12, 6, HARD)]
    for east, west, north, south, level in walks:
        net_east = east - west
        net_north = north - south
        distance = math.sqrt(net_east ** 2 + net_north ** 2)
        questions.append(
            {
                "id": f"nesw_net_{east}{west}{north}{south}",
                "domain": "Geometry",
                "topic": "Compass directions",
                "difficulty": level,
                "prompt": (
                    f"A walker goes {east} km east, {west} km west, {north} km north and {south} km south. "
                    "What is the net east-west movement?"
                ),
                "choices": number_choices(net_east, [east + west, net_north, east], suffix=" km east"),
                "answer": f"{net_east} km east",
                "solution": f"Net east - west = {east} - {west} = {net_east} km east.",
                "trap": "Opposite directions cancel. Add them only if they point the same way.",
            }
        )
        questions.append(
            {
                "id": f"nesw_dist_{east}{west}{north}{south}",
                "domain": "Geometry",
                "topic": "Compass directions",
                "difficulty": HARD,
                "prompt": (
                    f"A walker goes {east} km east, {west} km west, {north} km north and {south} km south. "
                    "How far is the walker from the starting point, to 1 decimal place?"
                ),
                "choices": decimal_choices(
                    distance,
                    [net_east + net_north, east + west + north + south, distance * 2],
                    suffix=" km",
                    places=1,
                ),
                "answer": decimal_answer(distance, suffix=" km", places=1),
                "solution": (
                    f"Net east - west = {net_east} km and net north - south = {net_north} km. "
                    f"Distance = sqrt(({net_east})^2 + ({net_north})^2) = sqrt({net_east ** 2 + net_north ** 2}) = "
                    f"{decimal_answer(distance, places=1)} km. This uses Pythagoras."
                ),
                "trap": f"Adding the two net distances gives {net_east + net_north} km, which is the walking path, not the direct line.",
            }
        )

    turns = [(70, "right", 50, 120, EASY), (40, "left", 90, 310, HARD), (200, "right", 85, 285, MEDIUM), (30, "left", 45, 345, HARD)]
    for start, direction, angle, result, level in turns:
        questions.append(
            {
                "id": f"turn_{start}_{direction}_{angle}",
                "domain": "Geometry",
                "topic": "Compass directions",
                "difficulty": level,
                "prompt": f"A hiker faces a bearing of {start:03d} degrees and turns {direction} by {angle} degrees. What is the new bearing?",
                "choices": number_choices(
                    result,
                    [
                        (start - angle) % 360 if direction == "right" else (start + angle) % 360,
                        (start + 180) % 360,
                        angle,
                    ],
                    suffix=" degrees",
                ),
                "answer": f"{result} degrees",
                "solution": (
                    f"Turning {direction} means new direction = current {'+' if direction == 'right' else '-'} angle = "
                    f"{start} {'+' if direction == 'right' else '-'} {angle} = "
                    f"{start + angle if direction == 'right' else start - angle}, "
                    f"which is {result} degrees once it is written between 0 and 360."
                ),
                "trap": "Right adds and left subtracts. If the answer goes below 0, add 360 to bring it back.",
            }
        )
    return questions


def build_distance_questions():
    """Notebook page: Distance Formula (coordinates)."""
    questions = []
    pairs = [((0, 0), (3, 4), EASY), ((-3, 2), (5, -4), MEDIUM), ((1, 1), (7, 9), MEDIUM), ((2, -1), (-2, 2), HARD)]
    for (x1, y1), (x2, y2), level in pairs:
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        questions.append(
            {
                "id": f"dist_{x1}{y1}_{x2}{y2}",
                "domain": "Geometry",
                "topic": "Distance formula",
                "difficulty": level,
                "prompt": f"What is the distance between ({x1}, {y1}) and ({x2}, {y2})?",
                "choices": number_choices(
                    int(distance),
                    [abs(x2 - x1) + abs(y2 - y1), int(distance) + 2, abs(x2 - x1) * abs(y2 - y1)],
                    suffix=" units",
                ),
                "answer": f"{int(distance)} units",
                "solution": (
                    f"d = sqrt((x2 - x1)^2 + (y2 - y1)^2) = sqrt(({x2} - {x1})^2 + ({y2} - {y1})^2) = "
                    f"sqrt({(x2 - x1) ** 2} + {(y2 - y1) ** 2}) = sqrt({(x2 - x1) ** 2 + (y2 - y1) ** 2}) = "
                    f"{int(distance)} units."
                ),
                "trap": "Squaring removes any minus signs, so a negative step never makes the distance negative.",
            }
        )
    questions.append(
        {
            "id": "dist_notebook_example",
            "domain": "Geometry",
            "topic": "Distance formula",
            "difficulty": MEDIUM,
            "prompt": "What is the distance between (2, 3) and (6, 7), to 2 decimal places?",
            "choices": decimal_choices(math.sqrt(32), [8, 4, 16], suffix=" units", places=2),
            "answer": decimal_answer(math.sqrt(32), suffix=" units", places=2),
            "solution": (
                "d = sqrt((6 - 2)^2 + (7 - 3)^2) = sqrt(4^2 + 4^2) = sqrt(16 + 16) = sqrt(32) = 4 x sqrt(2), "
                "which is about 5.66 units."
            ),
            "trap": "sqrt(32) does not simplify to 8. Split it as sqrt(16) x sqrt(2) = 4 sqrt(2).",
        }
    )
    return questions


def build_gradient_questions():
    """Notebook page: Gradient formula."""
    questions = []
    pairs = [((2, 3), (6, 11), 2, EASY), ((1, 2), (4, 11), 3, EASY), ((-2, 5), (2, -3), -2, HARD), ((0, 4), (5, 19), 3, MEDIUM), ((3, 7), (8, 2), -1, MEDIUM)]
    for (x1, y1), (x2, y2), gradient, level in pairs:
        questions.append(
            {
                "id": f"grad_{x1}{y1}_{x2}{y2}",
                "domain": "Algebra",
                "topic": "Gradient",
                "difficulty": level,
                "prompt": f"Find the gradient of the line joining ({x1}, {y1}) and ({x2}, {y2}).",
                "choices": number_choices(gradient, [-gradient, gradient + 1, x2 - x1]),
                "answer": f"{gradient}",
                "solution": (
                    f"m = (y2 - y1) / (x2 - x1) = ({y2} - {y1}) / ({x2} - {x1}) = "
                    f"{y2 - y1} / {x2 - x1} = {gradient}."
                ),
                "trap": "Top is the y values and bottom is the x values, subtracted in the SAME order.",
            }
        )
    questions.append(
        {
            "id": "grad_order_rule",
            "domain": "Algebra",
            "topic": "Gradient",
            "difficulty": MEDIUM,
            "prompt": "In the gradient formula, which values go on the top of the fraction?",
            "choices": text_choices(
                "The y values, subtracted in the same order as the x values below.",
                [
                    "The x values, because they come first in a coordinate.",
                    "Whichever pair gives a positive answer.",
                    "The smaller value of each pair.",
                ],
            ),
            "answer": "The y values, subtracted in the same order as the x values below.",
            "solution": "m = (y2 - y1) / (x2 - x1). Top is the y values, bottom is the x values, and the equation is y = kx.",
            "trap": "Flipping only one of the two subtractions reverses the sign of the gradient.",
        }
    )
    return questions


def build_quadratic_questions():
    """Notebook page: Quadratic Symbol, completing the square to the quadratic formula."""
    questions = []
    quadratics = [(1, -5, 6, 2, 3, EASY), (1, -7, 12, 3, 4, MEDIUM), (1, 1, -6, -3, 2, MEDIUM), (2, -7, 3, 0.5, 3, HARD)]
    for a, b, c, root_one, root_two, level in quadratics:
        discriminant = b * b - 4 * a * c
        smaller = min(root_one, root_two)
        larger = max(root_one, root_two)
        answer = f"x = {smaller:g} and x = {larger:g}"
        questions.append(
            {
                "id": f"quad_solve_{a}_{b}_{c}",
                "domain": "Algebra",
                "topic": "Quadratic formula",
                "difficulty": level,
                "prompt": f"Solve {quadratic_text(a, b, c)} = 0.",
                "choices": text_choices(
                    answer,
                    [
                        f"x = {-smaller:g} and x = {-larger:g}",
                        f"x = {smaller:g} and x = {-larger:g}",
                        f"x = {a:g} and x = {abs(c):g}",
                    ],
                ),
                "answer": answer,
                "solution": (
                    f"a = {a}, b = {b}, c = {c}. The discriminant is b^2 - 4ac = {b * b} - {4 * a * c} = {discriminant}, "
                    f"and sqrt({discriminant}) = {math.sqrt(discriminant):g}. "
                    f"x = (-b +/- sqrt(b^2 - 4ac)) / 2a = ({-b} +/- {math.sqrt(discriminant):g}) / {2 * a}, "
                    f"which gives x = {smaller:g} and x = {larger:g}."
                ),
                "trap": "The formula starts with MINUS b. Forgetting that sign flips both answers.",
            }
        )
        questions.append(
            {
                "id": f"quad_disc_{a}_{b}_{c}",
                "domain": "Algebra",
                "topic": "Quadratic formula",
                "difficulty": level,
                "prompt": f"What is the value of b^2 - 4ac for {quadratic_text(a, b, c)} = 0?",
                "choices": number_choices(discriminant, [b * b + 4 * a * c, -discriminant, b * b]),
                "answer": f"{discriminant}",
                "solution": (
                    f"b^2 - 4ac = ({b})^2 - 4 x {a} x {c} = {b * b} - {4 * a * c} = {discriminant}."
                ),
                "trap": "Square b before doing anything else, and watch the sign of c when it is negative.",
            }
        )
    questions.append(
        {
            "id": "quad_formula_recall",
            "domain": "Algebra",
            "topic": "Quadratic formula",
            "difficulty": HARD,
            "prompt": "Completing the square on ax^2 + bx + c = 0 leads to which formula?",
            "choices": text_choices(
                "x = (-b +/- sqrt(b^2 - 4ac)) / 2a",
                [
                    "x = (b +/- sqrt(b^2 - 4ac)) / 2a",
                    "x = (-b +/- sqrt(b^2 + 4ac)) / 2a",
                    "x = (-b +/- sqrt(b^2 - 4ac)) / 2",
                ],
            ),
            "answer": "x = (-b +/- sqrt(b^2 - 4ac)) / 2a",
            "solution": (
                "Divide by a, move c across, add (b/2a)^2 to both sides, factorise the left as (x + b/2a)^2, "
                "then square root both sides. The result is x = (-b +/- sqrt(b^2 - 4ac)) / 2a."
            ),
            "trap": "The whole numerator sits over 2a, not just over 2. The +/- means solve it twice.",
        }
    )
    return questions


def build_rearranging_questions():
    """Notebook page: Algebraic equations, x up and x down."""
    questions = []
    up = [(5, 7, 42, MEDIUM), (3, 11, 35, EASY), (8, -6, 42, HARD), (4, 9, 41, EASY)]
    for a, b, c, level in up:
        value = (c - b) / a
        shown_b = f"{b}" if b >= 0 else f"({b})"
        questions.append(
            {
                "id": f"solveup_{a}_{b}_{c}",
                "domain": "Algebra",
                "topic": "Rearranging equations",
                "difficulty": level,
                "prompt": f"Solve {a}x {'+' if b >= 0 else '-'} {abs(b)} = {c}.",
                "choices": number_choices(int(value), [int((c + b) / a), c - b, int(value) + 1]),
                "answer": f"{int(value)}",
                "solution": (
                    f"With x up the rule is ax + b = c, so ax = c - b and x = (c - b) / a. "
                    f"Here x = ({c} - {shown_b}) / {a} = {c - b} / {a} = {int(value)}."
                ),
                "trap": "Undo the addition first, then the multiplication. Reverse order to how it was built.",
            }
        )
    down = [(12, 3, 7, MEDIUM), (20, 2, 6, MEDIUM), (36, 5, 14, HARD), (30, 4, 9, HARD)]
    for a, b, c, level in down:
        value = a / (c - b)
        questions.append(
            {
                "id": f"solvedown_{a}_{b}_{c}",
                "domain": "Algebra",
                "topic": "Rearranging equations",
                "difficulty": level,
                "prompt": f"Solve {a}/x + {b} = {c}.",
                "choices": number_choices(int(value), [a - c + b, c - b, int(value) + 2]),
                "answer": f"{int(value)}",
                "solution": (
                    f"With x down the rule is a/x + b = c, so a/x = c - b and x = a / (c - b). "
                    f"Here x = {a} / ({c} - {b}) = {a} / {c - b} = {int(value)}."
                ),
                "trap": "When x is on the bottom the answer is a / (c - b), not (c - b) / a. The fraction flips.",
            }
        )
    return questions


def build_average_questions():
    """Notebook page: Algebra Word Problem (Average + Relationships)."""
    questions = []
    totals = [(20, 3, EASY), (14, 5, EASY), (72, 4, MEDIUM), (8.5, 6, HARD)]
    for average, count, level in totals:
        total = average * count
        questions.append(
            {
                "id": f"avgtotal_{str(average).replace('.', '')}_{count}",
                "domain": "Algebra",
                "topic": "Average word problems",
                "difficulty": level,
                "prompt": f"The average of {count} numbers is {average:g}. What do the numbers add to?",
                "choices": number_choices(
                    int(total) if float(total).is_integer() else total,
                    [average, count, total * 2],
                ),
                "answer": f"{int(total) if float(total).is_integer() else total:g}",
                "solution": (
                    f"Total = average x number of values = {average:g} x {count} = {total:g}."
                ),
                "trap": "Multiply, do not divide. Dividing would take you back to the average.",
            }
        )

    questions.append(
        {
            "id": "avgrel_tom",
            "domain": "Algebra",
            "topic": "Average word problems",
            "difficulty": MEDIUM,
            "prompt": (
                "Tom is 5 years older than Sam, and Jake is 2 years younger than Sam. "
                "Their average age is 21. How old is Tom?"
            ),
            "choices": number_choices(25, [20, 21, 23]),
            "answer": "25",
            "solution": (
                "Let Sam = S, so Tom = S + 5 and Jake = S - 2. "
                "Total = average x number of values = 21 x 3 = 63. "
                "Then (S + 5) + (S - 2) + S = 63, so 3S + 3 = 63, 3S = 60 and S = 20. Tom = 20 + 5 = 25."
            ),
            "trap": "Turn the average into a TOTAL first. Everything else follows from that one line.",
        }
    )
    questions.append(
        {
            "id": "avgrel_mia",
            "domain": "Algebra",
            "topic": "Average word problems",
            "difficulty": HARD,
            "prompt": (
                "Mia scored 8 more than Ben, and Zoe scored 5 less than Ben. "
                "Their average score is 16. What did Mia score?"
            ),
            "choices": number_choices(23, [15, 16, 20]),
            "answer": "23",
            "solution": (
                "Let Ben = B, so Mia = B + 8 and Zoe = B - 5. Total = 16 x 3 = 48. "
                "Then (B + 8) + (B - 5) + B = 48, so 3B + 3 = 48, 3B = 45 and B = 15. Mia = 15 + 8 = 23."
            ),
            "trap": "Write every person in terms of the same letter before adding them up.",
        }
    )
    questions.append(
        {
            "id": "avgrel_notebook",
            "domain": "Algebra",
            "topic": "Average word problems",
            "difficulty": HARD,
            "prompt": (
                "Tom is 5 years older than Sam, and Jake is 3 years younger than Sam. "
                "Their average age is 20. How old is Tom, to the nearest year?"
            ),
            "choices": number_choices(24, [20, 22, 25]),
            "answer": "24",
            "solution": (
                "Let Sam = S, so Tom = S + 5 and Jake = S - 3. Total = 20 x 3 = 60. "
                "Then (S + 5) + (S - 3) + S = 60, so 3S + 2 = 60, 3S = 58 and S = 19.33. "
                "Tom = 19.33 + 5 = 24.33, which rounds to 24 years."
            ),
            "trap": (
                "The notebook wrote 3S + 2 = 20 here. The 20 is the AVERAGE, so the total must be 20 x 3 = 60 first."
            ),
        }
    )
    return questions


def build_data_questions():
    """Notebook page: Mean, median, range and mode."""
    questions = []
    data_sets = [
        ([4, 8, 6, 10, 7], EASY),
        ([12, 15, 11, 15, 9, 14], MEDIUM),
        ([23, 19, 23, 30, 25], MEDIUM),
        ([5, 9, 9, 12, 14, 20, 21], HARD),
    ]
    for values, level in data_sets:
        label = ", ".join(str(item) for item in values)
        ordered = sorted(values)
        key = "".join(str(item) for item in values)
        total = sum(values)
        mean = total / len(values)
        middle = len(ordered) // 2
        median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
        counts = Counter(values)
        mode_value, mode_count = counts.most_common(1)[0]
        data_range = max(values) - min(values)

        questions.append(
            {
                "id": f"mean_{key}",
                "domain": "Data and chance",
                "topic": "Mean, median, mode and range",
                "difficulty": level,
                "prompt": f"Find the mean of {label}.",
                "choices": decimal_choices(mean, [median, data_range, total], places=1)
                if not float(mean).is_integer()
                else number_choices(int(mean), [int(median), data_range, total]),
                "answer": decimal_answer(mean, places=1) if not float(mean).is_integer() else f"{int(mean)}",
                "solution": (
                    f"Add every number: {total}. There are {len(values)} numbers, "
                    f"so the mean is {total} / {len(values)} = {mean:g}."
                ),
                "trap": "Divide by how many numbers there are, not by the largest one.",
            }
        )
        questions.append(
            {
                "id": f"median_{key}",
                "domain": "Data and chance",
                "topic": "Mean, median, mode and range",
                "difficulty": level,
                "prompt": f"Find the median of {label}.",
                "choices": decimal_choices(median, [mean, data_range, ordered[0]], places=1)
                if not float(median).is_integer()
                else number_choices(int(median), [int(mean) if float(mean).is_integer() else ordered[0], data_range, ordered[-1]]),
                "answer": decimal_answer(median, places=1) if not float(median).is_integer() else f"{int(median)}",
                "solution": (
                    f"Put them in order: {', '.join(str(item) for item in ordered)}. "
                    + (
                        f"The middle number is {median:g}."
                        if len(ordered) % 2
                        else f"There are two middle numbers, {ordered[middle - 1]} and {ordered[middle]}, "
                        f"so the median is ({ordered[middle - 1]} + {ordered[middle]}) / 2 = {median:g}."
                    )
                ),
                "trap": "Order the list FIRST. The middle of the unsorted list means nothing.",
            }
        )
        if mode_count > 1:
            questions.append(
                {
                    "id": f"mode_{key}",
                    "domain": "Data and chance",
                    "topic": "Mean, median, mode and range",
                    "difficulty": level,
                    "prompt": f"Find the mode of {label}.",
                    "choices": number_choices(mode_value, [max(values), min(values), data_range]),
                    "answer": f"{mode_value}",
                    "solution": f"{mode_value} appears {mode_count} times, more often than any other value, so it is the mode.",
                    "trap": "The mode is the most common VALUE, not how many times it appears.",
                }
            )
        questions.append(
            {
                "id": f"range_{key}",
                "domain": "Data and chance",
                "topic": "Mean, median, mode and range",
                "difficulty": level,
                "prompt": f"Find the range of {label}.",
                "choices": number_choices(data_range, [max(values), min(values), max(values) + min(values)]),
                "answer": f"{data_range}",
                "solution": f"Range = highest - lowest = {max(values)} - {min(values)} = {data_range}.",
                "trap": "Range is a single number, the gap between the extremes, not the two values themselves.",
            }
        )
    return questions


def build_recall_questions():
    """Straight recall of the rules written on the notebook pages."""
    recalls = [
        (
            "bodmas_letters",
            "Formulas",
            "BODMAS",
            EASY,
            "What does the B in BODMAS stand for, and what is done first?",
            "Brackets, and they are always cleared first.",
            ["Base numbers, cleared last.", "Both sides, cleared together.", "Bottom of the fraction, cleared first."],
            "BODMAS is Brackets, Operations, Divisions, Multiplication, Addition, Subtraction. Brackets always come first.",
            "Anything inside a bracket is finished before it meets the rest of the sum.",
        ),
        (
            "discount_rule",
            "Formulas",
            "Profit, loss and discount",
            EASY,
            "Which rule gives the discount on an item?",
            "Discount = percentage x selling price",
            ["Discount = selling price - cost price", "Discount = percentage x cost price", "Discount = selling price / percentage"],
            "Discount = percentage x selling price. Then final price = selling price - discount.",
            "The discount is worked out on the SELLING price, not the cost price.",
        ),
        (
            "profit_rule",
            "Formulas",
            "Profit, loss and discount",
            EASY,
            "Which rule gives the profit on a sale?",
            "Profit = final price - cost price",
            ["Profit = cost price - final price", "Profit = final price + cost price", "Profit = final price / cost price"],
            "Profit = final price - cost price. A loss is the other way round: loss = cost price - final price.",
            "Getting the order wrong turns a profit into a loss.",
        ),
        (
            "pctprofit_rule",
            "Formulas",
            "Percentage profit",
            MEDIUM,
            "Which rule gives the percentage profit?",
            "Percentage profit = profit / cost price x 100%",
            [
                "Percentage profit = profit / selling price x 100%",
                "Percentage profit = profit x cost price / 100",
                "Percentage profit = cost price / profit x 100%",
            ],
            "First find profit = selling price - cost price, then divide by the COST price and multiply by 100%.",
            "Dividing by the selling price is the single most common slip here.",
        ),
        (
            "consecutive_rule",
            "Formulas",
            "Consecutive integers",
            MEDIUM,
            "How do you write three consecutive even numbers in algebra?",
            "x + (x + 2) + (x + 4)",
            ["x + (x + 1) + (x + 2)", "x + 2x + 4x", "x + (x + 2) + (x + 3)"],
            "Consecutive integers step by 1: x + (x + 1) + (x + 2). Consecutive even or odd numbers step by 2: x + (x + 2) + (x + 4).",
            "Even and odd numbers both step by 2, so the same expression covers them both.",
        ),
        (
            "probability_rule",
            "Data and chance",
            "Probability",
            EASY,
            "Which rule gives a probability?",
            "Probability = number of favourable outcomes / total outcomes",
            [
                "Probability = total outcomes / number of favourable outcomes",
                "Probability = favourable outcomes x total outcomes",
                "Probability = favourable outcomes / unfavourable outcomes",
            ],
            "Probability = number of favourable outcomes divided by total outcomes.",
            "The denominator is EVERY possible outcome, not just the ones you do not want.",
        ),
        (
            "polygon_rule",
            "Formulas",
            "Polygon angles",
            MEDIUM,
            "Which rule gives the sum of the interior angles of a polygon?",
            "(n - 2) x 180",
            ["n x 180", "(n + 2) x 180", "360 / n"],
            "Sum = (n - 2) x 180. To go backwards: given sum / 180 = x, then x + 2 = the number of sides.",
            "The minus 2 is there because a polygon splits into n - 2 triangles.",
        ),
        (
            "sequence_rule",
            "Formulas",
            "Sum of a sequence",
            MEDIUM,
            "Which rule gives the sum of an evenly spaced sequence?",
            "S = n(f + l) / 2",
            ["S = n(f - l) / 2", "S = (f + l) / 2n", "S = n x f x l"],
            "S = n(f + l) / 2, where n is the number of terms, f is the first number and l is the last.",
            "n is the number of TERMS, not the last number in the list.",
        ),
        (
            "heads_rule",
            "Formulas",
            "Heads and legs",
            MEDIUM,
            "In a heads and legs problem with cows and chickens, what are the two core equations?",
            "c + h = total heads and 4c + 2h = total legs",
            [
                "c + h = total legs and 4c + 2h = total heads",
                "c + h = total heads and 2c + 4h = total legs",
                "c x h = total heads and c + h = total legs",
            ],
            "Cows have 4 legs and chickens have 2, so c + h = total heads and 4c + 2h = total legs. Rearranged, c = (total legs - 2 x total heads) / 2.",
            "Match the animal to its number of legs before writing the second equation.",
        ),
        (
            "speed_rule",
            "Formulas",
            "Average speed",
            MEDIUM,
            "Which rule gives the average speed when the two distances are equal?",
            "Average speed = 2ab / (a + b)",
            ["Average speed = (a + b) / 2", "Average speed = ab / 2", "Average speed = (a + b) / 2ab"],
            "For equal distances, average speed = 2ab / (a + b). Simplify the fraction if it divides.",
            "The plain average of the two speeds is always too high.",
        ),
        (
            "nesw_distance_rule",
            "Geometry",
            "Compass directions",
            MEDIUM,
            "How do you find the distance from the starting point after moving in two directions?",
            "Distance = sqrt((East - West)^2 + (North - South)^2)",
            [
                "Distance = (East - West) + (North - South)",
                "Distance = (East - West) x (North - South)",
                "Distance = sqrt(East + West + North + South)",
            ],
            "Find the net east-west and net north-south movement, then use Pythagoras: distance = sqrt((E - W)^2 + (N - S)^2).",
            "The straight-line distance is shorter than the total distance walked.",
        ),
        (
            "turn_rule",
            "Geometry",
            "Compass directions",
            EASY,
            "How does a bearing change when you turn left?",
            "New direction = current direction - angle",
            [
                "New direction = current direction + angle",
                "New direction = 360 - angle",
                "New direction = angle - current direction",
            ],
            "Turning right adds the angle and turning left subtracts it. If the answer drops below 0, add 360.",
            "Bearings run clockwise, which is why a left turn subtracts.",
        ),
        (
            "tetra_rule",
            "Geometry",
            "Volumes of 3D solids",
            MEDIUM,
            "What is a tetrahedron?",
            "A pyramid with a triangular base.",
            ["A pyramid with a square base.", "A prism with a triangular base.", "A cube cut in half."],
            "A tetrahedron is a pyramid with a triangular base. Its volume is V = a^3 / (6 x sqrt(2)), where a is one edge.",
            "sqrt(2) is irrational and about 1.414, so the answer never comes out exact.",
        ),
        (
            "mean_rule",
            "Data and chance",
            "Mean, median, mode and range",
            EASY,
            "How do you find the median of a list with an even number of values?",
            "Order the list, then average the two middle numbers.",
            [
                "Order the list, then take the larger middle number.",
                "Add every number and divide by how many there are.",
                "Subtract the smallest from the largest.",
            ],
            "Arrange smallest to largest. With two middle numbers, add them and divide by 2.",
            "Adding all the numbers and dividing gives the MEAN, not the median.",
        ),
        (
            "mode_rule",
            "Data and chance",
            "Mean, median, mode and range",
            EASY,
            "What is the mode of a data set?",
            "The number that appears most often.",
            [
                "The number in the middle once the list is ordered.",
                "The difference between the highest and lowest number.",
                "The total divided by how many numbers there are.",
            ],
            "The mode is the most frequent value. The median is the middle one, the range is the spread and the mean is the average.",
            "Mode and median both start with M. Mode is most often, median is middle.",
        ),
        (
            "volume_scale_rule",
            "Geometry",
            "Unit conversion and scaling",
            MEDIUM,
            "When converting between metres and centimetres, what happens to an area?",
            "It is multiplied by 100^2, which is 10 000.",
            [
                "It is multiplied by 100.",
                "It is multiplied by 100^3, which is 1 000 000.",
                "It stays the same, because only lengths change.",
            ],
            "Length multiplies by 100, area by 100^2 = 10 000 and volume by 100^3 = 1 000 000.",
            "The power matches the number of dimensions: 1 for length, 2 for area, 3 for volume.",
        ),
        (
            "square_diagonal_rule",
            "Geometry",
            "Areas of 2D shapes",
            HARD,
            "A square has side length a. How long is its diagonal?",
            "b = sqrt(2) x a",
            ["b = 2a", "b = a^2", "b = a / sqrt(2)"],
            "The diagonal splits the square into two right-angled triangles, so a^2 + a^2 = b^2, giving 2a^2 = b^2 and b = sqrt(2) x a.",
            "The diagonal is about 1.414 times the side, never double it.",
        ),
        (
            "diamond_rule",
            "Geometry",
            "Areas of 2D shapes",
            MEDIUM,
            "A diamond has diagonals a and b. What is its area?",
            "Area = (a x b) / 2",
            ["Area = a x b", "Area = 2 x a x b", "Area = (a + b) / 2"],
            "Area = (a x b) / 2. The rhombus and the kite use exactly the same rule.",
            "Multiply the diagonals and halve. Adding them measures nothing useful.",
        ),
    ]
    questions = []
    for question_id, domain, topic, level, prompt, answer, distractors, solution, trap in recalls:
        questions.append(
            {
                "id": f"recall_{question_id}",
                "domain": domain,
                "topic": topic,
                "difficulty": level,
                "prompt": prompt,
                "choices": text_choices(answer, distractors),
                "answer": answer,
                "solution": solution,
                "trap": trap,
            }
        )
    return questions


def build_notebook_example_questions():
    """The worked examples Rachel wrote out in full, kept in her own numbers."""
    questions = []
    for side in [5, 8, 10]:
        value = side * math.sqrt(2)
        questions.append(
            {
                "id": f"sqdiag_{side}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": HARD,
                "prompt": f"A square has side length {side} cm. How long is its diagonal, to 2 decimal places?",
                "choices": decimal_choices(value, [side * 2, side, side * side], suffix=" cm", places=2),
                "answer": decimal_answer(value, suffix=" cm", places=2),
                "solution": (
                    f"a^2 + a^2 = b^2, so 2 x {side}^2 = b^2 and b = sqrt(2) x {side} = 1.414 x {side} = "
                    f"{decimal_answer(value, places=2)} cm."
                ),
                "trap": "sqrt(2) is about 1.414. Doubling the side is far too long.",
            }
        )
    for x, y in [(12, 9), (20, 14)]:
        area = x * y / 2
        questions.append(
            {
                "id": f"diamond_{x}_{y}",
                "domain": "Geometry",
                "topic": "Areas of 2D shapes",
                "difficulty": MEDIUM,
                "prompt": f"A diamond has diagonals of {x} cm and {y} cm. What is its area?",
                "choices": number_choices(int(area), [x * y, x + y, int(area) + x], suffix=" square cm"),
                "answer": f"{int(area)} square cm",
                "solution": f"Area = (a x b) / 2 = ({x} x {y}) / 2 = {x * y} / 2 = {int(area)} square cm.",
                "trap": "The diamond, the rhombus and the kite all share this rule.",
            }
        )
    return questions


BANK_BUILDERS = [
    build_power_questions,
    build_square_questions,
    build_percentage_fact_questions,
    build_factorial_questions,
    build_bodmas_questions,
    build_profit_questions,
    build_consecutive_questions,
    build_probability_questions,
    build_polygon_questions,
    build_ratio_questions,
    build_sequence_questions,
    build_heads_legs_questions,
    build_speed_questions,
    build_triangle_questions,
    build_pythagoras_questions,
    build_area_questions,
    build_volume_questions,
    build_conversion_questions,
    build_direction_questions,
    build_distance_questions,
    build_gradient_questions,
    build_quadratic_questions,
    build_rearranging_questions,
    build_average_questions,
    build_data_questions,
    build_recall_questions,
    build_notebook_example_questions,
]

QUESTIONS = []
for builder in BANK_BUILDERS:
    QUESTIONS.extend(builder())

for question in QUESTIONS:
    question["choices"] = unique_choices(question["choices"], question["answer"])

QUESTION_LOOKUP = {question["id"]: question for question in QUESTIONS}
DOMAIN_ORDER = ["Number facts", "Formulas", "Geometry", "Algebra", "Data and chance"]
DIFFICULTY_ORDER = [EASY, MEDIUM, HARD]
DIFFICULTY_LABELS = {
    EASY: "Easy (one dot)",
    MEDIUM: "Medium (two dots)",
    HARD: "Hard (three dots)",
}

# Fast recall topics: the tables Rachel wrote out to learn by heart.
DRILL_TOPICS = ["Power tables", "Squares 11 to 26", "Fraction and percentage table", "Factorials"]


# The notebook typed out, page by page, in the order Rachel wrote it.
FORMULA_SHEET = [
    (
        "Power tables",
        [
            "2^0 to 2^15: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768",
            "3^0 to 3^7: 1, 3, 9, 27, 81, 243, 729, 2187",
            "4^0 to 4^7: 1, 4, 16, 64, 256, 1024, 4096, 16384",
            "5^0 to 5^7: 1, 5, 25, 125, 625, 3125, 15625, 78125",
            "6^0 to 6^7: 1, 6, 36, 216, 1296, 7776, 46656, 279936",
            "7^0 to 7^7: 1, 7, 49, 343, 2401, 16807, 117649, 823543",
            "8^0 to 8^7: 1, 8, 64, 512, 4096, 32768, 262144, 2097152",
            "9^0 to 9^7: 1, 9, 81, 729, 6561, 59049, 531441, 4782969",
            "10^0 to 10^7: 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000",
        ],
    ),
    (
        "Squares 11 to 26",
        [
            "121, 144, 169, 196, 225, 256, 289, 324, 361, 400",
            "441, 484, 529, 576, 625, 676",
            "One dot = easy, two dots = medium, three dots = hard.",
        ],
    ),
    (
        "Percentage",
        [
            "1 = 100%, 1/2 = 50%, 1/4 = 25%, 1/5 = 20%, 1/10 = 10%",
            "1/20 = 5%, 1/25 = 4%, 1/50 = 2%, 1/100 = 1%",
            "1/8 = 12.5%, 1/3 = 33.33% recurring, 1/6 = 16.67% recurring, 1/9 = 11.11% recurring",
        ],
    ),
    (
        "BODMAS",
        [
            "Brackets, Operations, Divisions, Multiplication, Addition, Subtraction",
            "Multiplication and division rank equally, so work them left to right.",
            "Addition and subtraction rank equally too.",
        ],
    ),
    (
        "Profit, discount and loss",
        [
            "Discount = percentage x selling price",
            "Final price = selling price - discount",
            "Profit = final price - cost price",
            "Loss = cost price - final price",
            "Percentage profit = profit / cost price x 100%",
        ],
    ),
    (
        "Consecutive numbers and probability",
        [
            "Consecutive integers: x + (x + 1) + (x + 2)",
            "Consecutive even or odd integers: x + (x + 2) + (x + 4)",
            "Probability = number of favourable outcomes / total outcomes",
        ],
    ),
    (
        "Polygon angles and ratio",
        [
            "(n - 2) x 180 = sum of interior angles",
            "Backwards: given sum / 180 = x, then x + 2 = number of sides",
            "Ratio a:b:c: total / total parts gives one part, then multiply each share",
        ],
    ),
    (
        "Sum of a sequence",
        [
            "S = n(f + l) / 2, with n terms, first number f and last number l",
            "Example: 2, 4, 6, ... , 40 has 20 terms, so S = 20 x 42 / 2 = 420",
            "Number of terms for odd numbers: n = (l - f) / 2 + 1",
        ],
    ),
    (
        "Heads and legs",
        [
            "c = number of cows, h = number of chickens",
            "Heads: c + h = total heads",
            "Legs: 4c + 2h = total legs",
            "Short cut: c = (total legs - 2 x total heads) / 2",
        ],
    ),
    (
        "Average speed and directions",
        [
            "Equal distances: average speed = 2ab / (a + b)",
            "Then time = distance / speed",
            "Net east - west = East - West, net north - south = North - South",
            "Distance from start = sqrt((East - West)^2 + (North - South)^2)",
            "Turning right: new direction = current + angle. Turning left: current - angle",
        ],
    ),
    (
        "Quadratic formula",
        [
            "Start with ax^2 + bx + c = 0, divide by a, move c across",
            "Complete the square by adding (b / 2a)^2 to both sides",
            "The left becomes (x + b / 2a)^2",
            "x = (-b +/- sqrt(b^2 - 4ac)) / 2a, where +/- means solve it twice",
        ],
    ),
    (
        "Triangles and area",
        [
            "Right-angled, isosceles, obtuse and acute: A = 1/2 x b x h",
            "Equilateral: A = (sqrt(3) / 4) x a^2, and sqrt(3) / 4 is about 0.433",
            "Scalene (Heron): A = sqrt(s(s - a)(s - b)(s - c)) with s = (a + b + c) / 2",
            "Obtuse: one angle over 90 degrees. Acute: all three under 90 degrees.",
            "Pythagoras: c^2 = a^2 + b^2, where c is the hypotenuse opposite the right angle",
        ],
    ),
    (
        "Areas of 2D shapes",
        [
            "Square: A = l x l. Rectangle: A = l x w, P = 2(l + w)",
            "Parallelogram: A = b x h. Triangle: A = 1/2 x b x h",
            "Rhombus, kite and diamond: A = 1/2 x (x x y) using the diagonals",
            "Trapezium: A = 1/2 x (a + b) x h",
            "Circle: A = pi x r^2. Sector: A = (angle / 360) x pi x r^2",
            "Square diagonal: 2a^2 = b^2, so b = sqrt(2) x a",
        ],
    ),
    (
        "Volumes of 3D solids",
        [
            "Cube: V = a^3. Rectangular prism: V = l x w x h",
            "Sphere: V = 4/3 x pi x r^3. Cylinder: V = pi x r^2 x h",
            "Cone: V = 1/3 x pi x r^2 x h. Pyramid: V = 1/3 x A base x h",
            "Tetrahedron (a pyramid with a triangular base): V = a^3 / (6 x sqrt(2))",
            "Prism: V = A base x h",
        ],
    ),
    (
        "Unit conversion and scaling",
        [
            "Length: 1 m = 100 cm = 1000 mm",
            "Area: 1 square m = 10 000 square cm",
            "Volume: 1 cubic m = 1 000 000 cubic cm",
            "Length x 100, area x 100^2, volume x 100^3",
            "1 cubic m = 1000 L, 1 L = 1000 mL, 1 cubic cm = 1 mL",
            "Mass = density x volume. Water is 1 g per cubic cm = 1000 kg per cubic m",
            "Double every length and the volume becomes 2^3 = 8 times bigger. Triple it and it is 3^3 = 27 times bigger.",
        ],
    ),
    (
        "Coordinates and algebra",
        [
            "Distance: d = sqrt((x2 - x1)^2 + (y2 - y1)^2)",
            "Gradient: m = (y2 - y1) / (x2 - x1). Top is the y values, bottom is the x values, equation y = kx",
            "Total = average x number of values",
            "Factorials: n! = n x (n - 1) x (n - 2) x ... x 2 x 1, and the short cut n! = n x (n - 1)!",
            "x up: ax + b = c, so x = (c - b) / a",
            "x down: a/x + b = c, so x = a / (c - b)",
        ],
    ),
    (
        "Mean, median, mode and range",
        [
            "Mean: add every number, then divide by how many there are",
            "Median: order the numbers and take the middle one. With two middles, average them",
            "Mode: the number that appears most often",
            "Range: highest number - lowest number",
        ],
    ),
]


# Slips found while typing up the notebook. Worth fixing on the page itself.
NOTEBOOK_FIXES = [
    ("Power of 4", "4^6 = 4176", "4^6 = 4096", "4^5 = 1024, and 1024 x 4 = 4096."),
    ("Power of 4", "4^7 = 16704", "4^7 = 16384", "4096 x 4 = 16384. It also matches 2^14 in the power of 2 table."),
    ("Power of 6", "6^5 = 61776", "6^5 = 7776", "1296 x 6 = 7776."),
    ("Power of 6", "6^6 = 370656", "6^6 = 46656", "7776 x 6 = 46656."),
    ("Power of 6", "6^7 = 2799366", "6^7 = 279936", "46656 x 6 = 279936. The digits were right but one was repeated."),
    ("Power of 9", "9^2 = 91", "9^2 = 81", "9 x 9 = 81. The rest of the power of 9 row is correct."),
    ("Volume Rules", "1 square m = 100 square cm", "1 square m = 10 000 square cm", "Area scales by 100^2. The summary further down the page already says x 10 000."),
    ("BODMAS", "Divisions before Multiplication", "Divisions and Multiplication rank equally", "Work them left to right. 40 / 5 x 2 = 16, not 4."),
    ("Algebra Word Problem", "3S + 2 = 20", "3S + 2 = 60", "20 is the AVERAGE. Total = average x number of values = 20 x 3 = 60."),
]


def css():
    st.markdown(
        """
        <style>
        :root {
            --navy: #1b2a4a;
            --teal: #1f7a8c;
            --red: #c33f31;
            --gold: #f0b429;
            --paper: #fffaf1;
            --ink: #242938;
            --line: #d9e1ec;
        }
        .stApp { background: linear-gradient(180deg, #f6fbfb 0%, #fffaf1 100%); color: var(--ink); }
        .block-container { padding-top: 1.4rem; max-width: 1180px; }
        .bank-hero {
            background: linear-gradient(135deg, var(--navy), var(--teal));
            color: white;
            padding: 24px 28px;
            border-radius: 8px;
            border-bottom: 6px solid var(--gold);
            box-shadow: 0 16px 40px rgba(27, 42, 74, 0.18);
        }
        .bank-hero h1 { margin: 0 0 8px; font-size: 2.2rem; }
        .bank-hero p { margin: 0; font-size: 1.03rem; opacity: 0.94; }
        .notice {
            background: #ffffff;
            border: 1px solid var(--line);
            border-left: 5px solid var(--teal);
            padding: 14px 16px;
            border-radius: 8px;
            margin: 16px 0;
        }
        .sheet-card {
            background: white;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
            min-height: 120px;
        }
        .sheet-card code { background: #f2f6fb; padding: 1px 4px; border-radius: 4px; }
        div.stButton > button[kind="primary"] {
            background: var(--red);
            border-color: var(--red);
            font-weight: 800;
        }
        div.stButton > button[kind="primary"]:hover {
            background: #a92f24;
            border-color: #a92f24;
        }
        @media (max-width: 700px) {
            .bank-hero h1 { font-size: 1.65rem; }
            .block-container { padding: 0.8rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    defaults = {
        "bank_test_ids": [],
        "bank_test_orders": {},
        "bank_test_submitted": False,
        "bank_test_confirming": False,
        "bank_practice_ids": [],
        "bank_practice_orders": {},
        "bank_practice_submitted": False,
        "bank_drill_ids": [],
        "bank_drill_orders": {},
        "bank_drill_submitted": False,
        "bank_history": [],
        "bank_seen_ids": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if not st.session_state["bank_test_ids"]:
        new_test()
    if not st.session_state["bank_practice_ids"]:
        new_practice("All", "All topics", "All levels", 8)
    if not st.session_state["bank_drill_ids"]:
        new_drill(15)


def choose_questions(pool, count, seen_key=None):
    count = min(count, len(pool))
    if count <= 0:
        return []
    seen = set(st.session_state.get(seen_key, [])) if seen_key else set()
    fresh = [question for question in pool if question["id"] not in seen]
    if len(fresh) < count:
        fresh = pool
        if seen_key:
            st.session_state[seen_key] = []
    selected = random.sample(fresh, count)
    if seen_key:
        st.session_state[seen_key] = list(
            dict.fromkeys(st.session_state.get(seen_key, []) + [question["id"] for question in selected])
        )
    return selected


def shuffle_orders(questions):
    return {question["id"]: random.sample(question["choices"], len(question["choices"])) for question in questions}


def clear_answers(prefix):
    for question_id in QUESTION_LOOKUP:
        st.session_state.pop(f"{prefix}{question_id}", None)


def new_test():
    selected = []
    for domain in DOMAIN_ORDER:
        pool = [question for question in QUESTIONS if question["domain"] == domain]
        selected.extend(choose_questions(pool, 4, "bank_seen_ids"))
    random.shuffle(selected)
    st.session_state["bank_test_ids"] = [question["id"] for question in selected]
    st.session_state["bank_test_orders"] = shuffle_orders(selected)
    st.session_state["bank_test_submitted"] = False
    st.session_state["bank_test_confirming"] = False
    clear_answers("bank_test_answer_")


def new_practice(domain, topic, difficulty, count):
    pool = list(QUESTIONS)
    if domain != "All":
        pool = [question for question in pool if question["domain"] == domain]
    if topic != "All topics":
        pool = [question for question in pool if question["topic"] == topic]
    if difficulty != "All levels":
        pool = [question for question in pool if question["difficulty"] == difficulty]
    selected = choose_questions(pool, count, "bank_seen_ids")
    st.session_state["bank_practice_ids"] = [question["id"] for question in selected]
    st.session_state["bank_practice_orders"] = shuffle_orders(selected)
    st.session_state["bank_practice_submitted"] = False
    clear_answers("bank_practice_answer_")


def new_drill(count, topic="All tables"):
    pool = [question for question in QUESTIONS if question["topic"] in DRILL_TOPICS]
    if topic != "All tables":
        pool = [question for question in pool if question["topic"] == topic]
    selected = choose_questions(pool, count, "bank_seen_ids")
    st.session_state["bank_drill_ids"] = [question["id"] for question in selected]
    st.session_state["bank_drill_orders"] = shuffle_orders(selected)
    st.session_state["bank_drill_submitted"] = False
    clear_answers("bank_drill_answer_")


def mark(question_ids, prefix):
    results = []
    for question_id in question_ids:
        question = QUESTION_LOOKUP[question_id]
        selected = st.session_state.get(f"{prefix}{question_id}")
        results.append(
            {
                "question": question,
                "selected": selected or "",
                "correct": selected == question["answer"],
            }
        )
    return results


def score_band(score, total):
    if not total:
        return "No result yet."
    percent = score / total
    if percent >= 0.9:
        return "Notebook secure: these facts and formulas are ready to use under time pressure."
    if percent >= 0.75:
        return "Nearly there: re-read the pages behind the missed questions, then retry the same topic."
    if percent >= 0.5:
        return "Getting there: work through the formula sheet for the weak topics before the next set."
    return "Back to the notebook: read the worked solutions below and copy the method out by hand."


def results_to_csv(results):
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["Question", "Section", "Topic", "Level", "Your answer", "Correct answer", "Result", "Worked solution"],
    )
    writer.writeheader()
    for index, result in enumerate(results, start=1):
        question = result["question"]
        writer.writerow(
            {
                "Question": index,
                "Section": question["domain"],
                "Topic": question["topic"],
                "Level": question["difficulty"],
                "Your answer": result["selected"] or "Not answered",
                "Correct answer": question["answer"],
                "Result": "Correct" if result["correct"] else "Review",
                "Worked solution": question["solution"],
            }
        )
    return output.getvalue()


def history_to_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Date", "Mode", "Score", "Total", "Accuracy", "Focus"])
    writer.writeheader()
    for item in st.session_state["bank_history"]:
        writer.writerow(item)
    return output.getvalue()


def record_results(mode, results):
    score = sum(1 for result in results if result["correct"])
    total = len(results)
    focus = Counter(result["question"]["topic"] for result in results if not result["correct"])
    st.session_state["bank_history"].append(
        {
            "Date": datetime.now().astimezone().isoformat(timespec="seconds"),
            "Mode": mode,
            "Score": score,
            "Total": total,
            "Accuracy": f"{round(score / total * 100)}%" if total else "0%",
            "Focus": ", ".join(topic for topic, _ in focus.most_common(3)) or "Keep the accuracy up",
        }
    )


def render_mcq(question_ids, orders, prefix, submitted):
    for index, question_id in enumerate(question_ids, start=1):
        question = QUESTION_LOOKUP[question_id]
        with st.container(border=True):
            st.markdown(f"**Question {index}. {escape_dollars(question['prompt'])}**")
            level = question["difficulty"]
            st.caption(f"{question['domain']} | {question['topic']} | {DIFFICULTY_LABELS.get(level, level)}")
            st.radio(
                "Choose one answer",
                orders.get(question_id, question["choices"]),
                index=None,
                key=f"{prefix}{question_id}",
                horizontal=True,
                disabled=submitted,
                label_visibility="collapsed",
                format_func=escape_dollars,
            )
            if submitted:
                selected = st.session_state.get(f"{prefix}{question_id}")
                if selected == question["answer"]:
                    st.success("Correct.")
                else:
                    st.error(f"Correct answer: {escape_dollars(question['answer'])}")
                st.write(f"**Worked solution:** {escape_dollars(question['solution'])}")
                if question.get("trap"):
                    st.caption(f"Watch out: {escape_dollars(question['trap'])}")


def render_results(results, key):
    score = sum(1 for result in results if result["correct"])
    total = len(results)
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{score}/{total}")
    c2.metric("Accuracy", f"{round(score / total * 100)}%" if total else "0%")
    c3.metric("Standing", score_band(score, total).split(":")[0])
    st.info(score_band(score, total))
    topic_rows = []
    for topic, count in Counter(
        result["question"]["topic"] for result in results if not result["correct"]
    ).most_common():
        topic_rows.append({"Notebook page": topic, "Missed": count})
    if topic_rows:
        st.warning("Re-read these pages first: " + ", ".join(row["Notebook page"] for row in topic_rows[:3]))
        st.dataframe(topic_rows, hide_index=True, width="stretch")
    rows = []
    for index, result in enumerate(results, start=1):
        question = result["question"]
        rows.append(
            {
                "Q": index,
                "Section": question["domain"],
                "Topic": question["topic"],
                "Your answer": result["selected"] or "Not answered",
                "Correct answer": question["answer"],
                "Result": "Correct" if result["correct"] else "Review",
                "Steps": question["solution"],
            }
        )
    st.subheader("Solution table")
    st.dataframe(rows, hide_index=True, width="stretch")
    st.download_button(
        "Export this result (CSV)",
        data=results_to_csv(results),
        file_name=f"bank_{key}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        width="stretch",
    )


def render_header():
    st.markdown(
        f"""
        <div class="bank-hero">
            <h1>Rachel's Notebook Practice Bank</h1>
            <p>{len(QUESTIONS)} questions built only from the revision notebook: the power tables, squares,
            percentages, formulas, geometry, algebra and data pages.</p>
        </div>
        <div class="notice">
            Easy, Medium and Hard follow the same one, two and three dot code used on the squares page.
            Every worked solution repeats the rule exactly as it is written in the notebook.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_test_tab():
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Full notebook test")
        st.caption(
            "Twenty questions, four from each section of the notebook. "
            "Answers start blank and submitting asks for confirmation."
        )
    with right:
        st.button("New test", type="primary", width="stretch", on_click=new_test)

    question_ids = st.session_state["bank_test_ids"]
    render_mcq(question_ids, st.session_state["bank_test_orders"], "bank_test_answer_", st.session_state["bank_test_submitted"])

    unanswered = [qid for qid in question_ids if st.session_state.get(f"bank_test_answer_{qid}") is None]
    st.divider()
    if not st.session_state["bank_test_submitted"]:
        if st.session_state["bank_test_confirming"]:
            if unanswered:
                st.warning(f"{len(unanswered)} question(s) are unanswered. Submit anyway?")
            else:
                st.warning("Ready to submit and see the worked solutions?")
            c1, c2 = st.columns(2)
            if c1.button("Yes, submit the test", type="primary", width="stretch"):
                results = mark(question_ids, "bank_test_answer_")
                record_results("Full test", results)
                st.session_state["bank_test_submitted"] = True
                st.session_state["bank_test_confirming"] = False
                st.rerun()
            if c2.button("Keep working", width="stretch"):
                st.session_state["bank_test_confirming"] = False
                st.rerun()
        else:
            if st.button("Submit test", type="primary", width="stretch"):
                st.session_state["bank_test_confirming"] = True
                st.rerun()

    if st.session_state["bank_test_submitted"]:
        render_results(mark(question_ids, "bank_test_answer_"), "test")


def render_drill_tab():
    st.subheader("Memory drill")
    st.caption(
        "Fast recall of the tables written out to learn by heart: powers of 2 to 10, "
        "squares 11 to 26, the fraction and percentage table, and factorials."
    )
    buttons = st.columns(4)
    if buttons[0].button("Powers", type="primary", width="stretch"):
        new_drill(15, "Power tables")
        st.rerun()
    if buttons[1].button("Squares", type="primary", width="stretch"):
        new_drill(15, "Squares 11 to 26")
        st.rerun()
    if buttons[2].button("Percentages", type="primary", width="stretch"):
        new_drill(15, "Fraction and percentage table")
        st.rerun()
    if buttons[3].button("Factorials", type="primary", width="stretch"):
        new_drill(12, "Factorials")
        st.rerun()
    if st.button("Mixed drill from all four tables", width="stretch"):
        new_drill(20)
        st.rerun()

    question_ids = st.session_state["bank_drill_ids"]
    render_mcq(question_ids, st.session_state["bank_drill_orders"], "bank_drill_answer_", st.session_state["bank_drill_submitted"])
    st.divider()
    if not st.session_state["bank_drill_submitted"]:
        if st.button("Submit drill", type="primary", width="stretch"):
            st.session_state["bank_drill_submitted"] = True
            record_results("Memory drill", mark(question_ids, "bank_drill_answer_"))
            st.rerun()
    else:
        render_results(mark(question_ids, "bank_drill_answer_"), "drill")


def render_practice_tab():
    st.subheader("Topic practice")
    st.caption("Pick a notebook page, or use the quick buttons for the topics with the most working out.")

    st.markdown("**Formula pages**")
    formula_buttons = st.columns(4)
    if formula_buttons[0].button("Profit and discount", width="stretch"):
        new_practice("Formulas", "Profit, loss and discount", "All levels", 10)
        st.rerun()
    if formula_buttons[1].button("Ratio sharing", width="stretch"):
        new_practice("Formulas", "Ratio sharing", "All levels", 8)
        st.rerun()
    if formula_buttons[2].button("Sequence sums", width="stretch"):
        new_practice("Formulas", "Sum of a sequence", "All levels", 10)
        st.rerun()
    if formula_buttons[3].button("Heads and legs", width="stretch"):
        new_practice("Formulas", "Heads and legs", "All levels", 8)
        st.rerun()

    st.markdown("**Geometry pages**")
    geometry_buttons = st.columns(4)
    if geometry_buttons[0].button("Triangles and area", width="stretch"):
        new_practice("Geometry", "Triangles and area", "All levels", 10)
        st.rerun()
    if geometry_buttons[1].button("Areas of 2D shapes", width="stretch"):
        new_practice("Geometry", "Areas of 2D shapes", "All levels", 12)
        st.rerun()
    if geometry_buttons[2].button("Volumes of 3D solids", width="stretch"):
        new_practice("Geometry", "Volumes of 3D solids", "All levels", 12)
        st.rerun()
    if geometry_buttons[3].button("Unit conversion", width="stretch"):
        new_practice("Geometry", "Unit conversion and scaling", "All levels", 10)
        st.rerun()

    st.markdown("**Algebra and data pages**")
    algebra_buttons = st.columns(4)
    if algebra_buttons[0].button("Quadratic formula", width="stretch"):
        new_practice("Algebra", "Quadratic formula", "All levels", 8)
        st.rerun()
    if algebra_buttons[1].button("Rearranging equations", width="stretch"):
        new_practice("Algebra", "Rearranging equations", "All levels", 8)
        st.rerun()
    if algebra_buttons[2].button("Gradient", width="stretch"):
        new_practice("Algebra", "Gradient", "All levels", 6)
        st.rerun()
    if algebra_buttons[3].button("Mean, median, mode", width="stretch"):
        new_practice("Data and chance", "Mean, median, mode and range", "All levels", 10)
        st.rerun()

    st.markdown("**Hardest questions only**")
    hard_buttons = st.columns(3)
    if hard_buttons[0].button("Hard number facts", width="stretch"):
        new_practice("Number facts", "All topics", HARD, 12)
        st.rerun()
    if hard_buttons[1].button("Hard geometry", width="stretch"):
        new_practice("Geometry", "All topics", HARD, 12)
        st.rerun()
    if hard_buttons[2].button("Hard formulas", width="stretch"):
        new_practice("Formulas", "All topics", HARD, 12)
        st.rerun()

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        domain = st.selectbox("Section", ["All"] + DOMAIN_ORDER, key="bank_domain")
    topic_pool = QUESTIONS if domain == "All" else [q for q in QUESTIONS if q["domain"] == domain]
    topic_options = ["All topics"] + sorted({question["topic"] for question in topic_pool})
    with c2:
        topic = st.selectbox("Notebook page", topic_options, key="bank_topic")
    difficulty_pool = topic_pool if topic == "All topics" else [q for q in topic_pool if q["topic"] == topic]
    available = {question["difficulty"] for question in difficulty_pool}
    difficulty_options = ["All levels"] + [level for level in DIFFICULTY_ORDER if level in available]
    with c3:
        difficulty = st.selectbox(
            "Level",
            difficulty_options,
            key="bank_difficulty",
            format_func=lambda level: DIFFICULTY_LABELS.get(level, level),
        )
    count_pool = (
        difficulty_pool
        if difficulty == "All levels"
        else [q for q in difficulty_pool if q["difficulty"] == difficulty]
    )
    with c4:
        count = st.number_input(
            "Questions",
            min_value=1,
            max_value=max(1, min(25, len(count_pool))),
            value=min(8, max(1, len(count_pool))),
            step=1,
        )
    if st.button("Start topic practice", type="primary", width="stretch"):
        new_practice(domain, topic, difficulty, int(count))
        st.rerun()

    question_ids = st.session_state["bank_practice_ids"]
    render_mcq(
        question_ids,
        st.session_state["bank_practice_orders"],
        "bank_practice_answer_",
        st.session_state["bank_practice_submitted"],
    )
    st.divider()
    if not st.session_state["bank_practice_submitted"]:
        if st.button("Submit practice answers", type="primary", width="stretch"):
            st.session_state["bank_practice_submitted"] = True
            record_results("Topic practice", mark(question_ids, "bank_practice_answer_"))
            st.rerun()
    else:
        render_results(mark(question_ids, "bank_practice_answer_"), "practice")


def render_sheet_tab():
    st.subheader("Formula sheet")
    st.caption("The notebook typed out page by page, in the order it was written.")
    for title, lines in FORMULA_SHEET:
        with st.expander(title, expanded=False):
            for line in lines:
                st.write(f"- {line}")

    st.divider()
    st.subheader("Corrections to copy back into the notebook")
    st.caption("Nine small slips found while typing the pages up. Everything else on them checked out.")
    st.dataframe(
        [
            {"Page": page, "Written": written, "Should be": correct, "Why": why}
            for page, written, correct, why in NOTEBOOK_FIXES
        ],
        hide_index=True,
        width="stretch",
    )

    st.divider()
    st.subheader("What is in the bank")
    counts = Counter(question["topic"] for question in QUESTIONS)
    domain_lookup = {question["topic"]: question["domain"] for question in QUESTIONS}
    rows = []
    for topic, count in sorted(counts.items(), key=lambda item: (DOMAIN_ORDER.index(domain_lookup[item[0]]), item[0])):
        levels = Counter(
            question["difficulty"] for question in QUESTIONS if question["topic"] == topic
        )
        rows.append(
            {
                "Section": domain_lookup[topic],
                "Notebook page": topic,
                "Questions": count,
                "Easy": levels.get(EASY, 0),
                "Medium": levels.get(MEDIUM, 0),
                "Hard": levels.get(HARD, 0),
            }
        )
    st.dataframe(rows, hide_index=True, width="stretch")


def render_record_tab():
    st.subheader("Practice record")
    if st.session_state["bank_history"]:
        st.dataframe(st.session_state["bank_history"], hide_index=True, width="stretch")
        st.download_button(
            "Export practice record (CSV)",
            data=history_to_csv(),
            file_name=f"bank_practice_record_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            width="stretch",
        )
        weak = Counter()
        for item in st.session_state["bank_history"]:
            for topic in [part.strip() for part in item["Focus"].split(",") if part.strip()]:
                weak[topic] += 1
        weak.pop("Keep the accuracy up", None)
        if weak:
            st.markdown("**Pages that keep coming up**")
            st.dataframe(
                [{"Notebook page": topic, "Times missed": count} for topic, count in weak.most_common(6)],
                hide_index=True,
                width="stretch",
            )
    else:
        st.info("Submit a test, a drill or a practice set to start the record.")


def main():
    st.set_page_config(page_title="Rachel's Notebook Practice Bank", layout="wide")
    css()
    init_state()
    render_header()
    tabs = st.tabs(["Full test", "Memory drill", "Topic practice", "Formula sheet", "Practice record"])
    with tabs[0]:
        render_test_tab()
    with tabs[1]:
        render_drill_tab()
    with tabs[2]:
        render_practice_tab()
    with tabs[3]:
        render_sheet_tab()
    with tabs[4]:
        render_record_tab()


if __name__ == "__main__":
    main()
