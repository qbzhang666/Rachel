import csv
import io
import json
import math
import random
from collections import Counter
from datetime import datetime

import streamlit as st


# Difficulty bands were rescaled after Rachel completed the Year 6-7 material.
#   Challenge -> Victorian Curriculum Year 8 standard
#   Extension -> Victorian Curriculum Year 9 standard
#   Advanced  -> beyond Year 9: multi-step, selective/competition-style reasoning
# Nothing at Year 6-7 "Core" level remains in the bank.

MATH_QUESTIONS = [
    {
        "id": "s_ind_01",
        "topic": "Indices and scientific notation",
        "difficulty": "Challenge",
        "prompt": "Simplify 3a^4 x 4a^3 divided by 6a^5.",
        "choices": ["2a^2", "2a^12", "12a^2", "7a^2"],
        "answer": "2a^2",
        "solution": "Multiply first: 3a^4 x 4a^3 = 12a^7. Then divide: 12a^7 / 6a^5 = 2a^(7-5) = 2a^2.",
        "trap": "Add indices when multiplying and subtract them when dividing. Never multiply the indices here.",
    },
    {
        "id": "s_ind_02",
        "topic": "Indices and scientific notation",
        "difficulty": "Extension",
        "prompt": "Evaluate 5^0 + 3^(-2) x 27.",
        "choices": ["4", "3", "28", "10"],
        "answer": "4",
        "solution": "5^0 = 1 and 3^(-2) = 1/9, so 3^(-2) x 27 = 27/9 = 3. The total is 1 + 3 = 4.",
        "trap": "Any non-zero number to the power of 0 is 1, not 0.",
    },
    {
        "id": "s_ind_03",
        "topic": "Indices and scientific notation",
        "difficulty": "Extension",
        "prompt": "Write (6 x 10^-3) x (4 x 10^7) in scientific notation.",
        "choices": ["2.4 x 10^5", "2.4 x 10^4", "2.4 x 10^-5", "24 x 10^-21"],
        "answer": "2.4 x 10^5",
        "solution": "Multiply the mantissas: 6 x 4 = 24. Add the indices: -3 + 7 = 4. So 24 x 10^4, which normalises to 2.4 x 10^5.",
        "trap": "Scientific notation needs a mantissa between 1 and 10, so 24 x 10^4 must be rewritten.",
    },
    {
        "id": "s_alg_04",
        "topic": "Algebraic manipulation",
        "difficulty": "Extension",
        "prompt": "Expand and simplify (3x - 4)(2x + 5).",
        "choices": ["6x^2 + 7x - 20", "6x^2 - 7x - 20", "6x^2 + 23x - 20", "6x^2 + 7x + 20"],
        "answer": "6x^2 + 7x - 20",
        "solution": "Expand every pair: 6x^2 + 15x - 8x - 20. Collect the middle terms: 6x^2 + 7x - 20.",
        "trap": "The middle terms have opposite signs, so subtract before deciding the sign of the x term.",
    },
    {
        "id": "s_alg_05",
        "topic": "Algebraic manipulation",
        "difficulty": "Extension",
        "prompt": "Factorise 49y^2 - 16.",
        "choices": ["(7y - 4)(7y + 4)", "(7y - 4)^2", "(49y - 16)(y + 1)", "(7y - 16)(7y + 1)"],
        "answer": "(7y - 4)(7y + 4)",
        "solution": "This is a difference of two squares: 49y^2 = (7y)^2 and 16 = 4^2, so 49y^2 - 16 = (7y - 4)(7y + 4).",
        "trap": "A difference of two squares never factorises to a perfect square bracket.",
    },
    {
        "id": "s_alg_06",
        "topic": "Algebraic manipulation",
        "difficulty": "Advanced",
        "prompt": "Factorise x^2 - x - 12.",
        "choices": ["(x - 4)(x + 3)", "(x + 4)(x - 3)", "(x - 6)(x + 2)", "(x - 12)(x + 1)"],
        "answer": "(x - 4)(x + 3)",
        "solution": "Find two numbers that multiply to -12 and add to -1. They are -4 and +3, so x^2 - x - 12 = (x - 4)(x + 3).",
        "trap": "Check the sum as well as the product, or the signs will be swapped.",
    },
    {
        "id": "s_eq_07",
        "topic": "Linear equations",
        "difficulty": "Extension",
        "prompt": "Solve (2x + 1)/3 = (x - 4)/2.",
        "choices": ["-14", "14", "-2", "-10"],
        "answer": "-14",
        "solution": "Cross-multiply: 2(2x + 1) = 3(x - 4), so 4x + 2 = 3x - 12. Then x = -14.",
        "trap": "Multiply every term by the denominator, not just the numerators you notice first.",
    },
    {
        "id": "s_eq_08",
        "topic": "Linear equations",
        "difficulty": "Challenge",
        "prompt": "Solve 5(2x - 3) = 3(x + 4) + 8.",
        "choices": ["5", "3", "7", "-5"],
        "answer": "5",
        "solution": "Expand both sides: 10x - 15 = 3x + 12 + 8 = 3x + 20. Then 7x = 35 and x = 5.",
        "trap": "Expand the brackets before collecting like terms.",
    },
    {
        "id": "s_lin_09",
        "topic": "Linear relationships",
        "difficulty": "Extension",
        "prompt": "A straight line passes through (-4, 9) and (2, -3). What is its equation?",
        "choices": ["y = -2x + 1", "y = -2x - 1", "y = 2x + 17", "y = -0.5x + 7"],
        "answer": "y = -2x + 1",
        "solution": "Gradient = (-3 - 9) / (2 - -4) = -12/6 = -2. Substitute (2, -3): -3 = -2(2) + c, so c = 1 and y = -2x + 1.",
        "trap": "Subtract the coordinates in the same order on the top and the bottom of the gradient fraction.",
    },
    {
        "id": "s_lin_10",
        "topic": "Linear relationships",
        "difficulty": "Advanced",
        "prompt": "What is the equation of the line perpendicular to y = (3/4)x - 2 that passes through (6, -1)?",
        "choices": ["y = (-4/3)x + 7", "y = (4/3)x - 9", "y = (-3/4)x + 3.5", "y = (-4/3)x - 7"],
        "answer": "y = (-4/3)x + 7",
        "solution": "Perpendicular gradients multiply to -1, so the new gradient is -4/3. Substitute (6, -1): -1 = (-4/3)(6) + c = -8 + c, so c = 7.",
        "trap": "A perpendicular gradient is the negative reciprocal, not just the negative.",
    },
    {
        "id": "s_lin_11",
        "topic": "Linear relationships",
        "difficulty": "Extension",
        "prompt": "What is the distance between the points (-3, 2) and (5, -4)?",
        "choices": ["10 units", "14 units", "8 units", "28 units"],
        "answer": "10 units",
        "solution": "The horizontal step is 8 and the vertical step is 6. Distance = sqrt(8^2 + 6^2) = sqrt(100) = 10 units.",
        "trap": "Distance uses Pythagoras, not the sum of the two steps.",
    },
    {
        "id": "s_sim_12",
        "topic": "Simultaneous equations",
        "difficulty": "Extension",
        "prompt": "Solve simultaneously: 4x + 3y = 29 and 2x - y = 7.",
        "choices": ["x = 5, y = 3", "x = 3, y = 5", "x = 5, y = -3", "x = 2, y = 7"],
        "answer": "x = 5, y = 3",
        "solution": "From the second equation, y = 2x - 7. Substitute: 4x + 3(2x - 7) = 29, so 10x = 50 and x = 5. Then y = 3.",
        "trap": "Always substitute back to check both equations, not just the one you rearranged.",
    },
    {
        "id": "s_pct_13",
        "topic": "Percentages and finance",
        "difficulty": "Challenge",
        "prompt": "After a 15% increase, a jacket costs $92. What was the original price?",
        "choices": ["$80", "$78.20", "$77", "$85"],
        "answer": "$80",
        "solution": "$92 represents 115% of the original. Original = 92 / 1.15 = $80.",
        "trap": "Do not take 15% off $92; the increase was applied to the smaller original price.",
    },
    {
        "id": "s_pct_14",
        "topic": "Percentages and finance",
        "difficulty": "Extension",
        "prompt": "A price rises by 25% and is later reduced by 20%. What is the overall change?",
        "choices": ["It returns to its original price.", "It is 5% higher.", "It is 5% lower.", "It is 45% higher."],
        "answer": "It returns to its original price.",
        "solution": "Multiply the factors: 1.25 x 0.80 = 1.00, so the final price equals the original price.",
        "trap": "Percentage changes multiply. They cannot simply be added and subtracted.",
    },
    {
        "id": "s_fin_15",
        "topic": "Percentages and finance",
        "difficulty": "Extension",
        "prompt": "$6000 is invested at 5% per annum compound interest, compounded annually. What is it worth after 3 years?",
        "choices": ["$6945.75", "$6900.00", "$6300.00", "$6961.50"],
        "answer": "$6945.75",
        "solution": "Value = 6000 x 1.05^3 = 6000 x 1.157625 = $6945.75.",
        "trap": "Simple interest would give $6900. Compound interest earns interest on interest.",
    },
    {
        "id": "s_rate_16",
        "topic": "Ratio, rates and proportion",
        "difficulty": "Challenge",
        "prompt": "A car uses 7.2 litres of fuel per 100 km. How much fuel does it use on a 375 km trip?",
        "choices": ["27 L", "24 L", "30.5 L", "19.2 L"],
        "answer": "27 L",
        "solution": "Fuel per km = 7.2 / 100 = 0.072 L. For 375 km: 0.072 x 375 = 27 L.",
        "trap": "Convert the rate to a per-kilometre figure before scaling up.",
    },
    {
        "id": "s_ratio_17",
        "topic": "Ratio, rates and proportion",
        "difficulty": "Extension",
        "prompt": "Prize money is shared in the ratio 4:5:7. The largest share is $180 more than the smallest. What is the total prize money?",
        "choices": ["$960", "$720", "$1080", "$540"],
        "answer": "$960",
        "solution": "The difference is 7 - 4 = 3 parts, so 3 parts = $180 and 1 part = $60. The total is 16 parts = 16 x $60 = $960.",
        "trap": "Find the value of one part from the difference before scaling to the total.",
    },
    {
        "id": "s_meas_18",
        "topic": "Measurement",
        "difficulty": "Extension",
        "prompt": "A circular garden of radius 7 m is surrounded by a path 1 m wide. What is the area of the path, to 1 decimal place?",
        "choices": ["47.1 square m", "50.3 square m", "44.0 square m", "6.3 square m"],
        "answer": "47.1 square m",
        "solution": "Outer area = pi x 8^2 = 201.1 square m. Inner area = pi x 7^2 = 153.9 square m. The path is 201.1 - 153.9 = 47.1 square m.",
        "trap": "Subtract the two circle areas. Do not multiply the radius difference by pi.",
    },
    {
        "id": "s_meas_19",
        "topic": "Measurement",
        "difficulty": "Extension",
        "prompt": "A closed cylinder has radius 4 cm and height 11 cm. What is its total surface area, to 1 decimal place?",
        "choices": ["377.0 square cm", "276.5 square cm", "552.9 square cm", "175.9 square cm"],
        "answer": "377.0 square cm",
        "solution": "Total surface area = 2 x pi x r x (r + h) = 2 x pi x 4 x 15 = 120 pi = 377.0 square cm.",
        "trap": "A closed cylinder has a curved surface plus two circular ends.",
    },
    {
        "id": "s_pyth_20",
        "topic": "Pythagoras and trigonometry",
        "difficulty": "Extension",
        "prompt": "A rectangular box measures 6 cm by 8 cm by 10 cm. What is the length of the longest straight rod that fits inside, to 1 decimal place?",
        "choices": ["14.1 cm", "12.8 cm", "10.0 cm", "24.0 cm"],
        "answer": "14.1 cm",
        "solution": "The space diagonal is sqrt(6^2 + 8^2 + 10^2) = sqrt(36 + 64 + 100) = sqrt(200) = 14.1 cm.",
        "trap": "Use Pythagoras twice, or the three-dimensional form, rather than only the base diagonal.",
    },
    {
        "id": "s_trig_21",
        "topic": "Pythagoras and trigonometry",
        "difficulty": "Extension",
        "prompt": "In a right-angled triangle the hypotenuse is 12 cm and one acute angle is 34 degrees. How long is the side opposite that angle, to 1 decimal place?",
        "choices": ["6.7 cm", "9.9 cm", "8.1 cm", "17.8 cm"],
        "answer": "6.7 cm",
        "solution": "Opposite = hypotenuse x sin(34 degrees) = 12 x 0.5592 = 6.7 cm.",
        "trap": "With the hypotenuse and an angle, sine gives the opposite side and cosine gives the adjacent side.",
    },
    {
        "id": "s_trig_22",
        "topic": "Pythagoras and trigonometry",
        "difficulty": "Extension",
        "prompt": "A ramp rises 9 m over a horizontal distance of 14 m. What is the angle of elevation, to 1 decimal place?",
        "choices": ["32.7 degrees", "40.0 degrees", "57.3 degrees", "50.0 degrees"],
        "answer": "32.7 degrees",
        "solution": "tan(angle) = opposite / adjacent = 9 / 14, so the angle is tan^-1(0.6429) = 32.7 degrees.",
        "trap": "Rise over horizontal run is a tangent ratio, not a sine ratio.",
    },
    {
        "id": "s_stat_23",
        "topic": "Statistics",
        "difficulty": "Extension",
        "prompt": "Find the interquartile range of 4, 7, 8, 11, 13, 15, 18, 21, 24.",
        "choices": ["12", "13", "20", "6.5"],
        "answer": "12",
        "solution": "The median is 13. The lower half is 4, 7, 8, 11 so Q1 = 7.5. The upper half is 15, 18, 21, 24 so Q3 = 19.5. IQR = 19.5 - 7.5 = 12.",
        "trap": "With an odd number of values, leave the median out of both halves.",
    },
    {
        "id": "s_prob_24",
        "topic": "Probability",
        "difficulty": "Extension",
        "prompt": "A bag holds 5 red and 4 blue counters. Two are drawn without replacement. What is the probability that both are red?",
        "choices": ["5/18", "25/81", "2/9", "5/12"],
        "answer": "5/18",
        "solution": "P(first red) = 5/9. After removing one red, P(second red) = 4/8. Multiply: 5/9 x 4/8 = 20/72 = 5/18.",
        "trap": "Without replacement, both the numerator and denominator change for the second draw.",
    },
    {
        "id": "s_num_25",
        "topic": "Number theory and counting",
        "difficulty": "Advanced",
        "prompt": "How many positive divisors of 360 are multiples of 6?",
        "choices": ["12", "18", "16", "24"],
        "answer": "12",
        "solution": "Each such divisor is 6k where k divides 360/6 = 60. Since 60 = 2^2 x 3 x 5, it has (2+1)(1+1)(1+1) = 12 divisors.",
        "trap": "Divide by 6 first, then count the divisors of the quotient.",
    },
    {
        "id": "s_num_26",
        "topic": "Number theory and counting",
        "difficulty": "Advanced",
        "prompt": "A path on a grid goes from one corner to the opposite corner using only 4 moves right and 3 moves down. How many different paths are there?",
        "choices": ["35", "12", "20", "60"],
        "answer": "35",
        "solution": "There are 7 moves in total. Choose which 3 of them are down moves: 7C3 = 35.",
        "trap": "Arrange the moves with a combination rather than trying to draw every path.",
    },
    {
        "id": "s_num_27",
        "topic": "Number theory and counting",
        "difficulty": "Advanced",
        "prompt": "What is the units digit of 3^2025?",
        "choices": ["3", "9", "7", "1"],
        "answer": "3",
        "solution": "Units digits of powers of 3 cycle 3, 9, 7, 1 with period 4. Since 2025 = 4 x 506 + 1, the units digit matches 3^1, which is 3.",
        "trap": "Find the cycle length first, then use the remainder when the index is divided by that length.",
    },
    {
        "id": "s_num_28",
        "topic": "Number theory and counting",
        "difficulty": "Advanced",
        "prompt": "A drawer holds 8 black, 6 white and 4 grey socks, mixed in the dark. What is the smallest number of socks that must be taken to guarantee a matching pair?",
        "choices": ["4", "3", "9", "7"],
        "answer": "4",
        "solution": "In the worst case the first three socks are one of each colour. The fourth sock must repeat a colour, so 4 socks guarantee a pair.",
        "trap": "A guarantee question asks for the worst case, not the likely case.",
    },
]


READING_TASKS = [
    {
        "title": "The Cost of Convenience",
        "passage": (
            "Every few months a new device promises to save us time. The advertisements are careful never to mention "
            "what that time is for. A phone that answers your messages before you have read them is not handing you an "
            "hour of freedom; it is quietly deciding which conversations deserve your attention. Manufacturers insist "
            "that users remain 'in complete control', yet the default settings - the ones almost nobody changes - are "
            "chosen in a boardroom, not a bedroom. This is not an argument against technology. It is an argument for "
            "noticing. Convenience is never free. It is simply billed in a currency we have not yet learned to count."
        ),
        "questions": [
            {
                "id": "rd01a",
                "skill": "Analysis of argument",
                "difficulty": "Extension",
                "prompt": "Which statement best expresses the writer's contention?",
                "choices": [
                    "Convenience involves hidden trade-offs that users should recognise.",
                    "Modern technology should be rejected by careful consumers.",
                    "Advertisements are the most reliable guide to a product's value.",
                    "Users already have complete control over their devices.",
                ],
                "answer": "Convenience involves hidden trade-offs that users should recognise.",
                "solution": "The writer explicitly refuses to argue against technology and instead argues 'for noticing' the unseen cost.",
            },
            {
                "id": "rd01b",
                "skill": "Figurative language",
                "difficulty": "Extension",
                "prompt": "The metaphor 'billed in a currency we have not yet learned to count' suggests that the cost of convenience is",
                "choices": [
                    "real but difficult to measure",
                    "printed clearly on every receipt",
                    "entirely imaginary",
                    "paid only by manufacturers",
                ],
                "answer": "real but difficult to measure",
                "solution": "A bill in an uncounted currency is still owed; the metaphor stresses a genuine cost we lack the tools to quantify.",
            },
            {
                "id": "rd01c",
                "skill": "Persuasive technique",
                "difficulty": "Extension",
                "prompt": "Why does the writer contrast 'a boardroom' with 'a bedroom'?",
                "choices": [
                    "To stress that decisions shaping private life are made by companies rather than users.",
                    "To argue that companies should be involved in designing bedrooms.",
                    "To show that the two spaces are equally private.",
                    "To suggest that people never use devices at home.",
                ],
                "answer": "To stress that decisions shaping private life are made by companies rather than users.",
                "solution": "The juxtaposition sets a corporate space against a private one to expose who really sets the defaults.",
            },
            {
                "id": "rd01d",
                "skill": "Authorial stance",
                "difficulty": "Advanced",
                "prompt": "The quotation marks around 'in complete control' mainly signal that the writer",
                "choices": [
                    "distances himself from a claim he doubts",
                    "is praising the honesty of manufacturers",
                    "is citing a legal definition word for word",
                    "is unsure how the phrase should be spelled",
                ],
                "answer": "distances himself from a claim he doubts",
                "solution": "Scare quotes attribute the phrase to someone else and imply scepticism about it.",
            },
        ],
    },
    {
        "title": "The Bridge at Ferry Point",
        "passage": (
            "Every summer my grandfather drove us to the bridge at Ferry Point, and every summer he stopped the car "
            "twenty metres short of it. He would open the door, look at the water, and say the light was wrong for "
            "photographs. We were children. We believed him. It was only after he died that my mother told me his "
            "brother had drowned there in 1961, on a day when, by every account, the light had been perfect. I have "
            "been back once. The bridge is unremarkable - grey, low, patched with newer concrete - and standing on it "
            "I understood that grief does not attach itself to remarkable places. It attaches itself to the places you "
            "cannot avoid driving past."
        ),
        "questions": [
            {
                "id": "rd02a",
                "skill": "Inference",
                "difficulty": "Extension",
                "prompt": "Why did the grandfather always stop short of the bridge?",
                "choices": [
                    "Crossing it would have forced him to face a painful memory.",
                    "The road surface was unsafe for his car.",
                    "He genuinely believed the light spoiled every photograph.",
                    "He wanted the children to walk the last stretch.",
                ],
                "answer": "Crossing it would have forced him to face a painful memory.",
                "solution": "The later revelation of his brother's drowning reframes the ritual stop as avoidance, not preference.",
            },
            {
                "id": "rd02b",
                "skill": "Irony",
                "difficulty": "Advanced",
                "prompt": "The detail that in 1961 'the light had been perfect' is significant because it",
                "choices": [
                    "exposes his stated reason as an excuse",
                    "proves that his photographs were technically excellent",
                    "shows that the weather in 1961 was unusual",
                    "explains why the family stopped visiting",
                ],
                "answer": "exposes his stated reason as an excuse",
                "solution": "The one day the light was perfect was the day of the drowning, so 'wrong light' was never the real reason.",
            },
            {
                "id": "rd02c",
                "skill": "Tone",
                "difficulty": "Extension",
                "prompt": "The tone of the final two sentences is best described as",
                "choices": ["reflective and understated", "bitter and accusing", "cheerful and nostalgic", "alarmed and urgent"],
                "answer": "reflective and understated",
                "solution": "The narrator states a hard-won insight plainly, without heightened emotion or blame.",
            },
            {
                "id": "rd02d",
                "skill": "Text structure",
                "difficulty": "Advanced",
                "prompt": "Withholding the drowning until the second half of the passage mainly allows the reader to",
                "choices": [
                    "share the children's innocence first and then reinterpret it",
                    "learn the family history in strict chronological order",
                    "predict the ending from the opening sentence",
                    "focus on the physical description of the bridge",
                ],
                "answer": "share the children's innocence first and then reinterpret it",
                "solution": "The delayed disclosure recreates the narrator's own late understanding in the reader.",
            },
        ],
    },
    {
        "title": "Reading the Ice",
        "passage": (
            "An ice core is a column of frozen time. Each winter's snowfall traps a thin layer of air, and when that "
            "snow is compressed into ice the bubbles are sealed. Drill deep enough and you can sample the atmosphere of "
            "the Bronze Age. What makes the method persuasive is not any single measurement but the agreement between "
            "independent ones: cores taken from Greenland and from Antarctica, separated by the width of the planet, "
            "record the same volcanic eruptions in the same years. A result that survives that kind of cross-checking is "
            "not merely plausible. It is difficult to explain away."
        ),
        "questions": [
            {
                "id": "rd03a",
                "skill": "Evaluating evidence",
                "difficulty": "Extension",
                "prompt": "According to the passage, what makes ice-core evidence convincing?",
                "choices": [
                    "Independent samples from distant places agree with one another.",
                    "A single deep core produces an unusually precise measurement.",
                    "The method has been used for longer than any other.",
                    "Volcanic eruptions are easy to date by other means.",
                ],
                "answer": "Independent samples from distant places agree with one another.",
                "solution": "The writer states that the persuasive element is agreement between independent measurements, not one result.",
            },
            {
                "id": "rd03b",
                "skill": "Vocabulary in context",
                "difficulty": "Extension",
                "prompt": "In this passage, 'plausible' most nearly means",
                "choices": ["believable", "proven beyond doubt", "extremely detailed", "recently discovered"],
                "answer": "believable",
                "solution": "The sentence contrasts merely believable with something stronger, so 'plausible' means credible but not yet confirmed.",
            },
            {
                "id": "rd03c",
                "skill": "Author purpose",
                "difficulty": "Extension",
                "prompt": "The phrase 'a column of frozen time' is used mainly to",
                "choices": [
                    "make an unfamiliar object easier for readers to picture",
                    "prove that ice cores are older than other records",
                    "criticise scientists for using technical language",
                    "introduce a counterargument about dating methods",
                ],
                "answer": "make an unfamiliar object easier for readers to picture",
                "solution": "The metaphor translates a technical object into an accessible image before the explanation begins.",
            },
            {
                "id": "rd03d",
                "skill": "Analysis of argument",
                "difficulty": "Advanced",
                "prompt": "'It is difficult to explain away' implies that the writer regards rival explanations as",
                "choices": [
                    "unlikely to account for the agreement between cores",
                    "impossible for any scientist to propose",
                    "already accepted by most researchers",
                    "irrelevant to the question of dating",
                ],
                "answer": "unlikely to account for the agreement between cores",
                "solution": "The phrase concedes that alternatives exist while implying they cannot survive the cross-checking described.",
            },
        ],
    },
    {
        "title": "The Understudy",
        "passage": (
            "Nadia had learned every line of a part she was not going to play. At rehearsals she stood in the wings "
            "mouthing the words, and the director, who noticed everything, noticed this and said nothing. On the "
            "Thursday, Priya's voice gave out. Nadia walked on stage without triumph. She had spent four weeks "
            "imagining this exact moment and had somehow forgotten to imagine how it would feel to be the reason "
            "someone else was sitting in the third row, silent, watching her."
        ),
        "questions": [
            {
                "id": "rd04a",
                "skill": "Inference",
                "difficulty": "Extension",
                "prompt": "What does 'noticed this and said nothing' suggest about the director?",
                "choices": [
                    "He was quietly assessing whether she was ready.",
                    "He had failed to see what she was doing.",
                    "He disapproved of understudies learning lines.",
                    "He had already promised the role to Priya's family.",
                ],
                "answer": "He was quietly assessing whether she was ready.",
                "solution": "The clause 'who noticed everything' rules out oversight, so the silence is deliberate observation.",
            },
            {
                "id": "rd04b",
                "skill": "Characterisation",
                "difficulty": "Extension",
                "prompt": "The phrase 'walked on stage without triumph' mainly conveys",
                "choices": [
                    "her awareness of what her opportunity had cost someone else",
                    "her lack of confidence in the lines she had learned",
                    "her disappointment at the size of the audience",
                    "her resentment towards the director",
                ],
                "answer": "her awareness of what her opportunity had cost someone else",
                "solution": "The final sentence explains the absence of triumph: her chance depends on Priya's loss.",
            },
            {
                "id": "rd04c",
                "skill": "Text structure",
                "difficulty": "Advanced",
                "prompt": "The repetition in 'imagining this exact moment ... forgotten to imagine' works to",
                "choices": [
                    "highlight the gap between practical and emotional preparation",
                    "show that Nadia had a poor memory for detail",
                    "suggest that the moment never actually happened",
                    "emphasise how long four weeks of rehearsal felt",
                ],
                "answer": "highlight the gap between practical and emotional preparation",
                "solution": "The same verb is used twice with opposite outcomes, exposing what her rehearsal never covered.",
            },
            {
                "id": "rd04d",
                "skill": "Theme",
                "difficulty": "Extension",
                "prompt": "Which theme does the passage most clearly develop?",
                "choices": [
                    "Success can arrive with a cost that preparation cannot anticipate.",
                    "Talent will always be recognised by those in authority.",
                    "Friendship matters more than professional ambition.",
                    "Hard work guarantees a fair outcome for everyone.",
                ],
                "answer": "Success can arrive with a cost that preparation cannot anticipate.",
                "solution": "Nadia is fully prepared yet unprepared, and the passage ends on the cost rather than the achievement.",
            },
        ],
    },
    {
        "title": "The Museum Label",
        "passage": (
            "The label beside the spear is forty-one words long. It records the material, the approximate date, the "
            "region, and the name of the expedition leader who 'collected' it in 1897. It does not record the name of "
            "the person who made it, the community it was taken from, or the circumstances of its removal. Museums are "
            "increasingly rewriting such labels. Critics call this politicising history. The reverse is closer to the "
            "truth: the original label was already an argument, made quietly, about whose names were worth keeping."
        ),
        "questions": [
            {
                "id": "rd05a",
                "skill": "Analysis of argument",
                "difficulty": "Advanced",
                "prompt": "What is the writer's central claim?",
                "choices": [
                    "The original label was never neutral, so rewriting it is not a new intrusion of politics.",
                    "Museums should remove all labels from contested objects.",
                    "Expedition leaders deserve more recognition than they receive.",
                    "The date and material of an object are the only reliable facts.",
                ],
                "answer": "The original label was never neutral, so rewriting it is not a new intrusion of politics.",
                "solution": "The final sentence reverses the critics' charge by arguing the old label already made a quiet argument.",
            },
            {
                "id": "rd05b",
                "skill": "Authorial stance",
                "difficulty": "Extension",
                "prompt": "The quotation marks around 'collected' invite the reader to",
                "choices": [
                    "question whether the object was acquired fairly",
                    "accept the term as the museum's official wording",
                    "notice an unusual spelling of a common word",
                    "assume the object was purchased at a market",
                ],
                "answer": "question whether the object was acquired fairly",
                "solution": "The scare quotes signal that the neutral-sounding verb may conceal a very different act.",
            },
            {
                "id": "rd05c",
                "skill": "Persuasive technique",
                "difficulty": "Advanced",
                "prompt": "'Critics call this politicising history. The reverse is closer to the truth' is an example of",
                "choices": [
                    "stating an opposing view and then turning it back on itself",
                    "conceding that the opposing view is correct",
                    "supporting the argument with statistical evidence",
                    "appealing to the reader's emotions through anecdote",
                ],
                "answer": "stating an opposing view and then turning it back on itself",
                "solution": "The writer names the objection and immediately inverts it, a rebuttal by reversal.",
            },
            {
                "id": "rd05d",
                "skill": "Inference",
                "difficulty": "Extension",
                "prompt": "The detail that the label is 'forty-one words long' is included to suggest that",
                "choices": [
                    "there was room to record more, and the omissions were choices",
                    "museum labels are usually far too long to read",
                    "the writer counted the words to check for spelling errors",
                    "shorter labels are always more accurate than longer ones",
                ],
                "answer": "there was room to record more, and the omissions were choices",
                "solution": "Precise length sets up the following list of what those forty-one words deliberately left out.",
            },
        ],
    },
    {
        "title": "Night Shift",
        "passage": (
            "At two in the morning the bakery is the warmest building on the street, and the loneliest. Flour hangs in "
            "the air like a rumour. The ovens breathe. Marek works to the radio's low murmur, shaping dough that will "
            "be bought at seven by people who will never learn his name, and he finds that he does not mind this. There "
            "is a kind of dignity in being the reason a thing is ready."
        ),
        "questions": [
            {
                "id": "rd06a",
                "skill": "Figurative language",
                "difficulty": "Extension",
                "prompt": "'Flour hangs in the air like a rumour' is a simile that suggests the flour is",
                "choices": [
                    "everywhere, suspended, and impossible to pin down",
                    "dangerous to breathe and quickly removed",
                    "spoken about often by the customers",
                    "arranged in neat and deliberate patterns",
                ],
                "answer": "everywhere, suspended, and impossible to pin down",
                "solution": "A rumour drifts and lingers without a fixed source, which is the quality transferred to the hanging flour.",
            },
            {
                "id": "rd06b",
                "skill": "Figurative language",
                "difficulty": "Extension",
                "prompt": "'The ovens breathe' is an example of",
                "choices": ["personification", "hyperbole", "simile", "onomatopoeia"],
                "answer": "personification",
                "solution": "A human action, breathing, is given to an inanimate object.",
            },
            {
                "id": "rd06c",
                "skill": "Mood",
                "difficulty": "Extension",
                "prompt": "The mood created in the passage is best described as",
                "choices": ["quietly companionable solitude", "frantic and pressured", "menacing and unsettled", "bitter and resentful"],
                "answer": "quietly companionable solitude",
                "solution": "Warmth, low murmur and breathing ovens soften the loneliness rather than sharpening it.",
            },
            {
                "id": "rd06d",
                "skill": "Inference",
                "difficulty": "Advanced",
                "prompt": "The last sentence implies that Marek values",
                "choices": [
                    "usefulness more than recognition",
                    "recognition more than payment",
                    "solitude more than competence",
                    "speed more than quality",
                ],
                "answer": "usefulness more than recognition",
                "solution": "He accepts anonymity and locates dignity in the readiness of the product, not in credit for it.",
            },
        ],
    },
    {
        "title": "The Statistics of Safety",
        "passage": (
            "A council media release announced that the new crossing had reduced accidents by fifty per cent. The figure "
            "was accurate. The crossing had recorded four accidents in the year before installation and two in the year "
            "after. Two fewer accidents is genuinely good news. 'Fifty per cent' makes it sound like a transformation. "
            "When the base number is small, a percentage behaves like a magnifying glass held over a fingerprint: "
            "technically faithful, wildly out of proportion."
        ),
        "questions": [
            {
                "id": "rd07a",
                "skill": "Evaluating evidence",
                "difficulty": "Advanced",
                "prompt": "What is the writer's main point about the council's statistic?",
                "choices": [
                    "It is accurate but presented in a way that overstates the change.",
                    "It is false and the council should retract it.",
                    "It proves that the crossing has made no difference.",
                    "It should have been expressed as a larger percentage.",
                ],
                "answer": "It is accurate but presented in a way that overstates the change.",
                "solution": "The writer concedes accuracy twice and objects only to the impression the percentage creates.",
            },
            {
                "id": "rd07b",
                "skill": "Figurative language",
                "difficulty": "Extension",
                "prompt": "The image of 'a magnifying glass held over a fingerprint' suggests that the percentage",
                "choices": [
                    "enlarges something small without distorting the underlying fact",
                    "conceals evidence that investigators need",
                    "is too small for readers to notice",
                    "was calculated using the wrong formula",
                ],
                "answer": "enlarges something small without distorting the underlying fact",
                "solution": "The passage glosses the image itself as 'technically faithful, wildly out of proportion'.",
            },
            {
                "id": "rd07c",
                "skill": "Authorial stance",
                "difficulty": "Extension",
                "prompt": "The writer's attitude towards the council is best described as",
                "choices": [
                    "critical of how the result was presented, not of the result itself",
                    "hostile to the crossing and the money spent on it",
                    "fully supportive of the media release as written",
                    "indifferent to whether accidents were reduced",
                ],
                "answer": "critical of how the result was presented, not of the result itself",
                "solution": "'Genuinely good news' separates approval of the outcome from criticism of the framing.",
            },
            {
                "id": "rd07d",
                "skill": "Evaluating evidence",
                "difficulty": "Advanced",
                "prompt": "Which additional information would most improve the reader's ability to judge the claim?",
                "choices": [
                    "Accident numbers at the crossing across several years before and after installation",
                    "The total cost of building the crossing",
                    "The number of council members who voted for the crossing",
                    "The wording used in media releases about other projects",
                ],
                "answer": "Accident numbers at the crossing across several years before and after installation",
                "solution": "A longer series would show whether the drop reflects a trend or ordinary year-to-year variation.",
            },
        ],
    },
    {
        "title": "Rewilding the Creek",
        "passage": (
            "Opponents of the creek restoration make one serious point: the works will close the walking track for "
            "eleven months. That is a real cost, and residents are entitled to resent it. But the objection measures "
            "the wrong thing. A track that floods four times every winter is already closed - just unpredictably, and "
            "without notice. The choice is not between access and inconvenience. It is between inconvenience we "
            "schedule and inconvenience we endure."
        ),
        "questions": [
            {
                "id": "rd08a",
                "skill": "Persuasive technique",
                "difficulty": "Extension",
                "prompt": "The opening two sentences are an example of",
                "choices": [
                    "concession, acknowledging a genuine strength in the opposing case",
                    "hyperbole, exaggerating the opponents' position",
                    "anecdote, describing a personal experience",
                    "repetition, restating the writer's contention",
                ],
                "answer": "concession, acknowledging a genuine strength in the opposing case",
                "solution": "The writer grants that the cost is real and the resentment reasonable before rebutting.",
            },
            {
                "id": "rd08b",
                "skill": "Analysis of argument",
                "difficulty": "Advanced",
                "prompt": "'The objection measures the wrong thing' means that opponents have",
                "choices": [
                    "compared the closure with an ideal that does not currently exist",
                    "used inaccurate figures for the length of the works",
                    "failed to consult the council before objecting",
                    "underestimated how much the restoration will cost",
                ],
                "answer": "compared the closure with an ideal that does not currently exist",
                "solution": "The writer argues the real comparison is with a track already closed unpredictably by flooding.",
            },
            {
                "id": "rd08c",
                "skill": "Persuasive technique",
                "difficulty": "Extension",
                "prompt": "The final sentence gains its force mainly through",
                "choices": [
                    "a balanced contrast between two kinds of inconvenience",
                    "a statistic that quantifies the flooding",
                    "an emotive appeal to residents' loyalty",
                    "a rhetorical question aimed at the council",
                ],
                "answer": "a balanced contrast between two kinds of inconvenience",
                "solution": "The parallel structure reframes the choice so that both options carry a cost.",
            },
            {
                "id": "rd08d",
                "skill": "Evaluating evidence",
                "difficulty": "Advanced",
                "prompt": "Which response would most weaken the writer's argument?",
                "choices": [
                    "Evidence that flood closures usually last only a few hours each time",
                    "Evidence that residents enjoy walking the track in summer",
                    "Evidence that the restoration has been approved by council",
                    "Evidence that the creek has flooded for many decades",
                ],
                "answer": "Evidence that flood closures usually last only a few hours each time",
                "solution": "The rebuttal depends on the two closures being comparable; brief flood closures break that equivalence.",
            },
        ],
    },
    {
        "title": "Words Change Sides",
        "passage": (
            "Words rarely retire; they change jobs. 'Nice' once meant ignorant, and travelled through fussy and precise "
            "before settling into its present vagueness. 'Awful' meant full of awe. Purists describe such drift as "
            "decay, as though English were a building losing bricks. A better comparison is a river: a river does not "
            "decay when it changes course. Still, drift has consequences. When a word such as 'literally' can carry its "
            "own opposite, speakers must work harder to be understood, and much of that work falls to the listener."
        ),
        "questions": [
            {
                "id": "rd09a",
                "skill": "Analysis of argument",
                "difficulty": "Extension",
                "prompt": "Which statement best summarises the writer's position?",
                "choices": [
                    "Language change is natural rather than harmful, though it does create difficulties.",
                    "Language change is a form of decay that should be resisted.",
                    "The meanings of words have remained stable for centuries.",
                    "Only careless speakers allow the meanings of words to shift.",
                ],
                "answer": "Language change is natural rather than harmful, though it does create difficulties.",
                "solution": "The river image rejects the decay claim, and 'Still, drift has consequences' qualifies without reversing it.",
            },
            {
                "id": "rd09b",
                "skill": "Figurative language",
                "difficulty": "Advanced",
                "prompt": "Why does the writer replace the building comparison with a river comparison?",
                "choices": [
                    "A river changes without losing anything, so the image removes the idea of loss.",
                    "A river is more familiar to most readers than a building.",
                    "Buildings are harder to describe in a short passage.",
                    "Rivers are mentioned in the dictionary definitions being discussed.",
                ],
                "answer": "A river changes without losing anything, so the image removes the idea of loss.",
                "solution": "Bricks falling implies damage; a change of course implies movement, which is the point being argued.",
            },
            {
                "id": "rd09c",
                "skill": "Vocabulary in context",
                "difficulty": "Extension",
                "prompt": "In this passage, 'drift' refers to",
                "choices": [
                    "gradual change in what a word means",
                    "the careless pronunciation of long words",
                    "the borrowing of words from other languages",
                    "the disappearance of words from a dictionary",
                ],
                "answer": "gradual change in what a word means",
                "solution": "The examples of 'nice' and 'awful' establish drift as slow movement in meaning.",
            },
            {
                "id": "rd09d",
                "skill": "Inference",
                "difficulty": "Advanced",
                "prompt": "'Much of that work falls to the listener' implies that ambiguity",
                "choices": [
                    "shifts the effort of interpretation onto the audience",
                    "makes conversation impossible in practice",
                    "is always the speaker's deliberate choice",
                    "affects written English but not spoken English",
                ],
                "answer": "shifts the effort of interpretation onto the audience",
                "solution": "If a word can mean its opposite, the listener must do the disambiguating, which is where the burden lands.",
            },
        ],
    },
    {
        "title": "Two Views: Phones in School",
        "passage": (
            "TEXT A (school newsletter): The evidence is unambiguous. Since the introduction of the phone ban, "
            "playground conversation has increased, reported incidents of online bullying during school hours have "
            "fallen to zero, and teachers report fewer disruptions. The policy must remain. Any relaxation would "
            "undo a year of progress.\n\n"
            "TEXT B (student submission): I supported the ban, and I still think it improved lunchtimes. But 'incidents "
            "during school hours' fell to zero partly because students now report them after school instead, where no "
            "teacher sees them. A ban can move a problem without solving it. If the school wants the credit, it should "
            "also collect the after-hours data."
        ),
        "questions": [
            {
                "id": "rd10a",
                "skill": "Comparing texts",
                "difficulty": "Advanced",
                "prompt": "The main difference between the two texts is that Text B",
                "choices": [
                    "questions how the evidence in Text A should be interpreted",
                    "rejects the phone ban entirely",
                    "provides different statistics from a separate study",
                    "argues that playground conversation has not increased",
                ],
                "answer": "questions how the evidence in Text A should be interpreted",
                "solution": "Text B accepts the ban's benefits but challenges what the 'zero incidents' figure actually measures.",
            },
            {
                "id": "rd10b",
                "skill": "Analysis of argument",
                "difficulty": "Advanced",
                "prompt": "Text A's use of 'The evidence is unambiguous' and 'must remain' shows",
                "choices": [
                    "high modality intended to close off debate",
                    "low modality intended to invite discussion",
                    "a concession to the opposing viewpoint",
                    "a reliance on personal anecdote",
                ],
                "answer": "high modality intended to close off debate",
                "solution": "Absolute wording and the obligation verb 'must' present the conclusion as beyond argument.",
            },
            {
                "id": "rd10c",
                "skill": "Persuasive technique",
                "difficulty": "Extension",
                "prompt": "Text B opens with 'I supported the ban, and I still think it improved lunchtimes' in order to",
                "choices": [
                    "establish credibility before raising an objection",
                    "signal that the writer has changed sides completely",
                    "avoid stating any position at all",
                    "criticise students who opposed the ban",
                ],
                "answer": "establish credibility before raising an objection",
                "solution": "Agreeing first positions the writer as fair-minded, making the following criticism harder to dismiss.",
            },
            {
                "id": "rd10d",
                "skill": "Evaluating evidence",
                "difficulty": "Advanced",
                "prompt": "Which flaw in Text A does Text B most directly identify?",
                "choices": [
                    "The measure used captures only part of the behaviour it claims to track.",
                    "The teachers surveyed were not chosen at random.",
                    "The figures were collected over too short a period.",
                    "The newsletter failed to define what a phone is.",
                ],
                "answer": "The measure used captures only part of the behaviour it claims to track.",
                "solution": "'During school hours' excludes the after-hours reports where the behaviour may have relocated.",
            },
        ],
    },
]


GRAMMAR_QUESTIONS = [
    {
        "id": "s_gram_01",
        "skill": "Punctuation",
        "difficulty": "Extension",
        "prompt": "Which sentence uses the semicolon correctly?",
        "choices": [
            "The first draft was competent; the second was persuasive.",
            "The first draft was competent; but the second was persuasive.",
            "The first draft was competent; which the second improved.",
            "Although the first draft was competent; the second was persuasive.",
        ],
        "answer": "The first draft was competent; the second was persuasive.",
        "solution": "A semicolon joins two independent clauses that are closely related, without a coordinating conjunction.",
    },
    {
        "id": "s_gram_02",
        "skill": "Punctuation",
        "difficulty": "Extension",
        "prompt": "Which sentence uses the colon correctly?",
        "choices": [
            "The report reached one conclusion: the data had been collected too narrowly.",
            "The report reached: one conclusion the data had been collected too narrowly.",
            "The report reached one conclusion, that the data: had been collected too narrowly.",
            "The report: reached one conclusion the data had been collected too narrowly.",
        ],
        "answer": "The report reached one conclusion: the data had been collected too narrowly.",
        "solution": "A colon follows a complete clause and introduces the explanation or list that fulfils it.",
    },
    {
        "id": "s_gram_03",
        "skill": "Punctuation",
        "difficulty": "Advanced",
        "prompt": "Which sentence punctuates the non-defining relative clause correctly?",
        "choices": [
            "The captain, who had trained all summer, was the obvious choice.",
            "The captain who had trained all summer, was the obvious choice.",
            "The captain, who had trained all summer was the obvious choice.",
            "The captain who, had trained all summer, was the obvious choice.",
        ],
        "answer": "The captain, who had trained all summer, was the obvious choice.",
        "solution": "A non-defining relative clause adds extra information and is enclosed by a pair of commas.",
    },
    {
        "id": "s_gram_04",
        "skill": "Register and tone",
        "difficulty": "Extension",
        "prompt": "Which sentence is most appropriate for a formal analytical essay?",
        "choices": [
            "The imagery in the final stanza reinforces the speaker's isolation.",
            "The imagery at the end is pretty cool and shows she is lonely.",
            "I reckon the last bit makes you feel sorry for her.",
            "The poem is about loneliness and stuff like that.",
        ],
        "answer": "The imagery in the final stanza reinforces the speaker's isolation.",
        "solution": "Formal analysis uses precise metalanguage and avoids colloquialism and vague filler.",
    },
    {
        "id": "s_gram_05",
        "skill": "Sentence structure",
        "difficulty": "Advanced",
        "prompt": "Which sentence avoids a dangling modifier?",
        "choices": [
            "Having checked the calculations, the student submitted the report.",
            "Having checked the calculations, the report was submitted.",
            "Having checked the calculations, submission of the report occurred.",
            "Having checked the calculations, it was submitted by the student.",
        ],
        "answer": "Having checked the calculations, the student submitted the report.",
        "solution": "The opening participle must describe the subject of the main clause; only the student can check calculations.",
    },
    {
        "id": "s_gram_06",
        "skill": "Sentence structure",
        "difficulty": "Extension",
        "prompt": "Which sentence maintains parallel structure?",
        "choices": [
            "The course teaches students to plan an argument, gather evidence and evaluate sources.",
            "The course teaches students to plan an argument, gathering evidence and evaluation of sources.",
            "The course teaches planning an argument, to gather evidence and evaluating sources.",
            "The course teaches students planning, to gather evidence, and that sources are evaluated.",
        ],
        "answer": "The course teaches students to plan an argument, gather evidence and evaluate sources.",
        "solution": "Items in a list must share the same grammatical form; here all three are infinitive verbs.",
    },
]


WRITING_PROMPTS = [
    {
        "type": "Analytical",
        "prompt": "'A writer's most persuasive move is the one the reader does not notice.' Discuss, using at least one text you have studied.",
        "success": ["clear thesis", "topic sentences", "embedded evidence", "analysis of technique", "sustained formal register"],
    },
    {
        "type": "Argumentative",
        "prompt": "Schools should judge students on the quality of their reasoning rather than the accuracy of their recall. Argue for or against.",
        "success": ["clear contention", "two developed arguments", "counterargument and rebuttal", "specific evidence", "decisive conclusion"],
    },
    {
        "type": "Comparative",
        "prompt": "Compare how two texts you have read present the idea of belonging. Which is more convincing, and why?",
        "success": ["comparative thesis", "point-by-point structure", "quotation from both texts", "evaluative judgement", "linked conclusion"],
    },
    {
        "type": "Discursive",
        "prompt": "Is it possible to be well informed and still be wrong? Explore the question without settling on a simple answer.",
        "success": ["exploratory opening", "multiple perspectives", "concrete example", "qualified reasoning", "reflective ending"],
    },
    {
        "type": "Creative",
        "prompt": "Write a narrative in which a character discovers that the version of an event they have told for years is not true.",
        "success": ["controlled opening", "subtext", "specific sensory detail", "turning point", "restrained resolution"],
    },
    {
        "type": "Persuasive speech",
        "prompt": "Write a three-minute speech arguing that your school should change one rule. Address the strongest objection directly.",
        "success": ["direct address", "clear contention", "rebuttal of strongest objection", "rhetorical technique", "call to action"],
    },
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
        if value not in values:
            values.append(value)
    probe = 5
    while len(values) < 4:
        candidate = answer + probe
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


def signed(value):
    return f"+ {value}" if value >= 0 else f"- {abs(value)}"


def linear_expression(coefficient, constant):
    if constant == 0:
        return f"{coefficient}x"
    return f"{coefficient}x {signed(constant)}"


def text_choices(answer, distractors):
    values = [answer]
    for value in distractors:
        if value not in values:
            values.append(value)
    return values[:4]


def fraction_text(numerator, denominator):
    divisor = math.gcd(numerator, denominator)
    return f"{numerator // divisor}/{denominator // divisor}"


def quadratic_expression(square_coefficient, linear_coefficient, constant):
    return f"{square_coefficient}x^2 {signed(linear_coefficient)}x {signed(constant)}"


def build_year8_math_questions():
    """Victorian Curriculum Year 8: indices, algebra, finance, measurement, geometry, statistics."""
    questions = []
    for v in range(1, 7):
        # --- Indices ---
        coef = 1 + v
        power = 2 + v
        exponent = 3 if v % 2 else 2
        questions.append(
            {
                "id": f"y8_index_power_{v}",
                "topic": "Indices and scientific notation",
                "difficulty": "Challenge",
                "prompt": f"Simplify ({coef}x^{power})^{exponent}.",
                "choices": [
                    f"{coef ** exponent}x^{power * exponent}",
                    f"{coef * exponent}x^{power * exponent}",
                    f"{coef ** exponent}x^{power + exponent}",
                    f"{coef}x^{power * exponent}",
                ],
                "answer": f"{coef ** exponent}x^{power * exponent}",
                "solution": f"Raise both parts to the outside power: {coef}^{exponent} = {coef ** exponent} and (x^{power})^{exponent} = x^{power * exponent}.",
                "trap": "The coefficient must be raised to the power too, and indices multiply when a power is raised to a power.",
            }
        )

        a1, a2 = 3 + v, 4 + v
        p1, p2, p3 = 5 + v, 2 + v, 3 + v
        questions.append(
            {
                "id": f"y8_index_laws_{v}",
                "topic": "Indices and scientific notation",
                "difficulty": "Challenge",
                "prompt": f"Simplify {a1}a^{p1} x {a2}a^{p2} divided by {a1}a^{p3}.",
                "choices": [
                    f"{a2}a^{p1 + p2 - p3}",
                    f"{a1 * a2}a^{p1 + p2 - p3}",
                    f"{a2}a^{p1 + p2 + p3}",
                    f"{a1 + a2}a^{p1 + p2 - p3}",
                ],
                "answer": f"{a2}a^{p1 + p2 - p3}",
                "solution": f"Multiply: {a1 * a2}a^{p1 + p2}. Divide by {a1}a^{p3}: coefficients give {a2} and indices give {p1} + {p2} - {p3} = {p1 + p2 - p3}.",
                "trap": "Divide the coefficients but subtract the indices.",
            }
        )

        # --- Algebra ---
        a, b, c = 2 + v, 3 + v, 4 + v
        d, e, f = 3, 2 + v, 5 + v
        x_coefficient = a * b - d * e
        constant = -a * c + d * f
        questions.append(
            {
                "id": f"y8_expand_{v}",
                "topic": "Algebraic manipulation",
                "difficulty": "Challenge",
                "prompt": f"Expand and simplify {a}({b}x - {c}) - {d}({e}x - {f}).",
                "choices": [
                    linear_expression(x_coefficient, constant),
                    linear_expression(x_coefficient, -a * c - d * f),
                    linear_expression(a * b + d * e, constant),
                    linear_expression(x_coefficient, a * c + d * f),
                ],
                "answer": linear_expression(x_coefficient, constant),
                "solution": f"{a}({b}x - {c}) = {a * b}x - {a * c} and -{d}({e}x - {f}) = -{d * e}x + {d * f}. Collecting gives {linear_expression(x_coefficient, constant)}.",
                "trap": "The minus sign in front of the second bracket changes the sign of both terms inside it.",
            }
        )

        root = 3 + v
        p, q, r = 2 + v, 3, 4 + v
        s = 1 + v
        t = p * (q * root - r) - s * root
        questions.append(
            {
                "id": f"y8_equation_brackets_{v}",
                "topic": "Linear equations",
                "difficulty": "Challenge",
                "prompt": f"Solve {p}({q}x - {r}) = {s}x {signed(t)}.",
                "choices": number_choices(root, [root - 2, root + 2, r]),
                "answer": str(root),
                "solution": f"Expand the left side: {p * q}x - {p * r} = {s}x {signed(t)}. Collect the x terms: {p * q - s}x = {t + p * r}, so x = {root}.",
                "trap": "Expand the bracket before moving any terms across the equals sign.",
            }
        )

        k = 2 + v
        big_root = 4 + v
        rhs = 2 + v
        subtracted = k * big_root - 3 * rhs
        questions.append(
            {
                "id": f"y8_equation_fraction_{v}",
                "topic": "Linear equations",
                "difficulty": "Extension",
                "prompt": f"Solve ({k}x - {subtracted})/3 = {rhs}.",
                "choices": number_choices(big_root, [big_root + 1, big_root + 3, subtracted]),
                "answer": str(big_root),
                "solution": f"Multiply both sides by 3: {k}x - {subtracted} = {3 * rhs}. Then {k}x = {3 * rhs + subtracted} and x = {big_root}.",
                "trap": "Multiply the whole side by the denominator, not just the first term.",
            }
        )

        # --- Percentages and finance ---
        original = 20 * (2 + v)
        rise = 5 * (1 + v % 4)
        after = int(original * (100 + rise) / 100)
        questions.append(
            {
                "id": f"y8_reverse_percent_{v}",
                "topic": "Percentages and finance",
                "difficulty": "Challenge",
                "prompt": f"After a {rise}% increase, an item costs ${after}. What was the price before the increase?",
                "choices": money_choices(original, [after - rise, int(after * (100 - rise) / 100), original + 10]),
                "answer": f"${original:g}",
                "solution": f"${after} represents {100 + rise}% of the original price, so the original price is {after} / {(100 + rise) / 100:g} = ${original}.",
                "trap": "Do not take the percentage off the new price. The increase was calculated from the smaller original.",
            }
        )

        base_price = 100 + 50 * v
        up = 10 + v
        down = 5 + v
        final = base_price * (100 + up) * (100 - down) / 10000
        questions.append(
            {
                "id": f"y8_successive_percent_{v}",
                "topic": "Percentages and finance",
                "difficulty": "Extension",
                "prompt": f"A ${base_price} item is increased by {up}% and then reduced by {down}%. What is the final price, to the nearest dollar?",
                "choices": money_choices(round(final), [base_price, round(base_price * (100 + up - down) / 100), round(final) + 5]),
                "answer": f"${round(final):g}",
                "solution": f"Multiply the factors: {base_price} x {(100 + up) / 100:g} x {(100 - down) / 100:g} = ${final:.2f}, which is about ${round(final)}.",
                "trap": "Percentage changes multiply. Adding {up}% and subtracting {down}% is not the same calculation.",
            }
        )

        principal = 500 * (1 + v)
        rate = 3 + v
        years = 2 + v % 3
        interest = int(principal * rate * years / 100)
        questions.append(
            {
                "id": f"y8_simple_interest_{v}",
                "topic": "Percentages and finance",
                "difficulty": "Challenge",
                "prompt": f"Find the simple interest earned on ${principal} invested at {rate}% per annum for {years} years.",
                "choices": money_choices(interest, [int(principal * rate / 100), interest + int(principal * rate / 100), int(principal * rate * years / 1000)]),
                "answer": f"${interest:g}",
                "solution": f"I = PRT/100 = {principal} x {rate} x {years} / 100 = ${interest}.",
                "trap": "Simple interest is calculated on the original principal every year.",
            }
        )

        hourly = 24 + 2 * v
        hours = 5
        pay = hourly * hours
        new_hours = 7 + v
        new_pay = hourly * new_hours
        questions.append(
            {
                "id": f"y8_rate_{v}",
                "topic": "Ratio, rates and proportion",
                "difficulty": "Challenge",
                "prompt": f"A casual worker is paid ${pay} for {hours} hours. At the same rate, what is the pay for {new_hours} hours?",
                "choices": money_choices(new_pay, [pay + hourly, new_pay - hourly, pay * 2]),
                "answer": f"${new_pay:g}",
                "solution": f"The unit rate is {pay} / {hours} = ${hourly} per hour, so {new_hours} hours earn {hourly} x {new_hours} = ${new_pay}.",
                "trap": "Find the unit rate first, then scale it.",
            }
        )

        # --- Measurement ---
        radius = 5 + v
        circle_area = math.pi * radius ** 2
        questions.append(
            {
                "id": f"y8_circle_area_{v}",
                "topic": "Measurement",
                "difficulty": "Challenge",
                "prompt": f"A circle has radius {radius} cm. What is its area, to 1 decimal place?",
                "choices": decimal_choices(circle_area, [2 * math.pi * radius, 2 * math.pi * radius ** 2, math.pi * radius], " square cm"),
                "answer": decimal_answer(circle_area, " square cm"),
                "solution": f"A = pi r^2 = pi x {radius}^2 = {circle_area:.1f} square cm.",
                "trap": "Square the radius before multiplying by pi; 2 pi r is the circumference.",
            }
        )

        cyl_r = 3 + v
        cyl_h = 8 + v
        cyl_volume = math.pi * cyl_r ** 2 * cyl_h
        questions.append(
            {
                "id": f"y8_cylinder_volume_{v}",
                "topic": "Measurement",
                "difficulty": "Extension",
                "prompt": f"A cylinder has radius {cyl_r} cm and height {cyl_h} cm. What is its volume, to 1 decimal place?",
                "choices": decimal_choices(cyl_volume, [2 * math.pi * cyl_r * cyl_h, math.pi * cyl_r * cyl_h, cyl_volume / 3], " cubic cm"),
                "answer": decimal_answer(cyl_volume, " cubic cm"),
                "solution": f"V = pi r^2 h = pi x {cyl_r}^2 x {cyl_h} = {cyl_volume:.1f} cubic cm.",
                "trap": "Volume needs the radius squared; 2 pi r h is only the curved surface area.",
            }
        )

        length, width, height = 6 + v, 4 + v, 3 + v
        surface = 2 * (length * width + length * height + width * height)
        questions.append(
            {
                "id": f"y8_prism_surface_{v}",
                "topic": "Measurement",
                "difficulty": "Challenge",
                "prompt": f"A rectangular prism measures {length} cm by {width} cm by {height} cm. What is its total surface area?",
                "choices": number_choices(surface, [length * width * height, surface // 2, 2 * (length + width + height)], " square cm"),
                "answer": f"{surface} square cm",
                "solution": f"SA = 2(lw + lh + wh) = 2({length * width} + {length * height} + {width * height}) = {surface} square cm.",
                "trap": "There are three pairs of identical faces, so double the sum of the three different faces.",
            }
        )

        # --- Geometric reasoning ---
        x_value = 10 + v
        first_constant = 60 - 2 * v
        second_constant = 70 - 3 * v
        questions.append(
            {
                "id": f"y8_parallel_angles_{v}",
                "topic": "Geometric reasoning",
                "difficulty": "Challenge",
                "prompt": f"Two parallel lines are cut by a transversal. A pair of co-interior angles measure (2x + {first_constant}) degrees and (3x + {second_constant}) degrees. What is the value of x?",
                "choices": number_choices(x_value, [x_value + 5, 180 - x_value, x_value - 3]),
                "answer": str(x_value),
                "solution": f"Co-interior angles are supplementary: (2x + {first_constant}) + (3x + {second_constant}) = 180, so 5x + {first_constant + second_constant} = 180 and x = {x_value}.",
                "trap": "Co-interior angles add to 180 degrees; alternate and corresponding angles are equal.",
            }
        )

        # --- Statistics and probability ---
        count = 8 + v
        mean_one = 10 + v
        mean_two = 9 + v
        removed = count * mean_one - (count - 1) * mean_two
        questions.append(
            {
                "id": f"y8_mean_removed_{v}",
                "topic": "Statistics",
                "difficulty": "Extension",
                "prompt": f"A set of {count} numbers has a mean of {mean_one}. When one number is removed, the mean of the remaining {count - 1} numbers is {mean_two}. What number was removed?",
                "choices": number_choices(removed, [mean_one, removed - 2, removed + 3]),
                "answer": str(removed),
                "solution": f"Total before = {count} x {mean_one} = {count * mean_one}. Total after = {count - 1} x {mean_two} = {(count - 1) * mean_two}. The removed number is the difference, {removed}.",
                "trap": "Convert both means into totals before comparing them.",
            }
        )

        red = 2 + v
        blue = 3 + v
        total_marbles = red + blue
        questions.append(
            {
                "id": f"y8_probability_replacement_{v}",
                "topic": "Probability",
                "difficulty": "Extension",
                "prompt": f"A bag holds {red} red and {blue} blue marbles. One is drawn, replaced, and another is drawn. What is the probability that both are red?",
                # Every option is reduced, so the correct one is not identifiable by form alone.
                "choices": [
                    fraction_text(red * red, total_marbles * total_marbles),
                    fraction_text(red, total_marbles),
                    fraction_text(red * red, total_marbles),
                    fraction_text(red * (red - 1), total_marbles * (total_marbles - 1)),
                ],
                "answer": fraction_text(red * red, total_marbles * total_marbles),
                "solution": f"With replacement the draws are independent: {red}/{total_marbles} x {red}/{total_marbles} = {red * red}/{total_marbles * total_marbles}.",
                "trap": "With replacement nothing changes between draws; without replacement both numbers would drop by one.",
            }
        )

    return questions


def build_year9_math_questions():
    """Victorian Curriculum Year 9: indices, linear graphs, trigonometry, similarity, statistics."""
    questions = []
    triples = [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (9, 12, 15), (7, 24, 25)]

    for v in range(1, 7):
        base = 2 + v % 3
        negative_index = 2 + v
        positive_index = 4 + 2 * v
        index_result = base ** (positive_index - negative_index)
        questions.append(
            {
                "id": f"y9_negative_index_{v}",
                "topic": "Indices and scientific notation",
                "difficulty": "Extension",
                "prompt": f"Evaluate {base}^(-{negative_index}) x {base}^{positive_index}.",
                "choices": number_choices(index_result, [base ** (positive_index + negative_index), base ** (positive_index - negative_index - 1), base * (positive_index - negative_index)]),
                "answer": str(index_result),
                "solution": f"Add the indices: -{negative_index} + {positive_index} = {positive_index - negative_index}, so the value is {base}^{positive_index - negative_index} = {index_result}.",
                "trap": "A negative index still follows the index laws; it does not make the answer negative.",
            }
        )

        mantissa_top = 8
        power_top = 3 + v
        mantissa_bottom = 2 if v % 2 else 4
        power_bottom = -(2 + v)
        quotient_mantissa = mantissa_top / mantissa_bottom
        quotient_power = power_top - power_bottom
        questions.append(
            {
                "id": f"y9_scientific_{v}",
                "topic": "Indices and scientific notation",
                "difficulty": "Extension",
                "prompt": f"Write ({mantissa_top} x 10^{power_top}) divided by ({mantissa_bottom} x 10^{power_bottom}) in scientific notation.",
                "choices": [
                    f"{quotient_mantissa:g} x 10^{quotient_power}",
                    f"{quotient_mantissa:g} x 10^{quotient_power - 2}",
                    f"{quotient_mantissa * 2:g} x 10^{quotient_power}",
                    f"{quotient_mantissa:g} x 10^{power_top + power_bottom}",
                ],
                "answer": f"{quotient_mantissa:g} x 10^{quotient_power}",
                "solution": f"Divide the mantissas: {mantissa_top} / {mantissa_bottom} = {quotient_mantissa:g}. Subtract the indices: {power_top} - ({power_bottom}) = {quotient_power}.",
                "trap": "Subtracting a negative index increases the power.",
            }
        )

        x1 = -(1 + v)
        y1 = 4 + 2 * v
        gradient = -(1 + v)
        run = (2 + v) - x1
        x2 = 2 + v
        y2 = y1 + gradient * run
        intercept = y1 - gradient * x1
        questions.append(
            {
                "id": f"y9_gradient_{v}",
                "topic": "Linear relationships",
                "difficulty": "Extension",
                "prompt": f"What is the gradient of the line through ({x1}, {y1}) and ({x2}, {y2})?",
                "choices": number_choices(gradient, [-gradient, gradient - 1, gradient + 2]),
                "answer": str(gradient),
                "solution": f"Gradient = (y2 - y1) / (x2 - x1) = ({y2} - {y1}) / ({x2} - ({x1})) = {y2 - y1}/{run} = {gradient}.",
                "trap": "Keep the coordinates in the same order on the numerator and denominator.",
            }
        )

        questions.append(
            {
                "id": f"y9_line_equation_{v}",
                "topic": "Linear relationships",
                "difficulty": "Extension",
                "prompt": f"What is the equation of the line through ({x1}, {y1}) and ({x2}, {y2})?",
                "choices": [
                    f"y = {gradient}x {signed(intercept)}",
                    f"y = {gradient}x {signed(-intercept)}",
                    f"y = {-gradient}x {signed(intercept)}",
                    f"y = {gradient}x {signed(intercept + 3)}",
                ],
                "answer": f"y = {gradient}x {signed(intercept)}",
                "solution": f"The gradient is {gradient}. Substituting ({x1}, {y1}) into y = mx + c gives c = {intercept}, so y = {gradient}x {signed(intercept)}.",
                "trap": "Substitute a known point to find c; do not assume the y-intercept is one of the given points.",
            }
        )

        leg_a, leg_b, hypotenuse = triples[v - 1]
        px1 = -(2 + v)
        py1 = 1 + v
        px2 = px1 + leg_a
        py2 = py1 + leg_b
        questions.append(
            {
                "id": f"y9_distance_{v}",
                "topic": "Linear relationships",
                "difficulty": "Extension",
                "prompt": f"What is the distance between ({px1}, {py1}) and ({px2}, {py2})?",
                "choices": number_choices(hypotenuse, [leg_a + leg_b, hypotenuse - 2, hypotenuse + 3], " units"),
                "answer": f"{hypotenuse} units",
                "solution": f"The horizontal step is {leg_a} and the vertical step is {leg_b}, so the distance is sqrt({leg_a}^2 + {leg_b}^2) = {hypotenuse} units.",
                "trap": "Distance uses Pythagoras, not the sum of the two steps.",
            }
        )

        mx1 = 2 * (1 + v)
        my1 = -2 * (2 + v)
        mx2 = mx1 + 2 * (3 + v)
        my2 = my1 + 2 * (1 + v)
        midpoint_x = mx1 + (3 + v)
        midpoint_y = my1 + (1 + v)
        questions.append(
            {
                "id": f"y9_midpoint_{v}",
                "topic": "Linear relationships",
                "difficulty": "Challenge",
                "prompt": f"What is the midpoint of the interval joining ({mx1}, {my1}) and ({mx2}, {my2})?",
                "choices": [
                    f"({midpoint_x}, {midpoint_y})",
                    f"({mx1 + mx2}, {my1 + my2})",
                    f"({midpoint_y}, {midpoint_x})",
                    f"({midpoint_x + 2}, {midpoint_y})",
                ],
                "answer": f"({midpoint_x}, {midpoint_y})",
                "solution": f"Average each coordinate: (({mx1} + {mx2})/2, ({my1} + {my2})/2) = ({midpoint_x}, {midpoint_y}).",
                "trap": "Average the coordinates; do not simply add them.",
            }
        )

        sx = 2 + v
        sy = 4 + v
        c1 = 3 * sx + 2 * sy
        c2 = 5 * sx - 2 * sy
        questions.append(
            {
                "id": f"y9_simultaneous_{v}",
                "topic": "Simultaneous equations",
                "difficulty": "Extension",
                "prompt": f"Solve simultaneously: 3x + 2y = {c1} and 5x - 2y = {c2}.",
                "choices": [
                    f"x = {sx}, y = {sy}",
                    f"x = {sy}, y = {sx}",
                    f"x = {sx}, y = {-sy}",
                    f"x = {sx + 1}, y = {sy - 1}",
                ],
                "answer": f"x = {sx}, y = {sy}",
                "solution": f"Add the equations to eliminate y: 8x = {c1 + c2}, so x = {sx}. Substituting back gives y = {sy}.",
                "trap": "Adding works when the y coefficients are opposites; otherwise scale one equation first.",
            }
        )

        ba, bb = 2 + v, -(2 + v)
        bc, bd = 1 + v, 4 + v
        middle = ba * bd + bb * bc
        questions.append(
            {
                "id": f"y9_binomial_{v}",
                "topic": "Algebraic manipulation",
                "difficulty": "Extension",
                "prompt": f"Expand and simplify ({ba}x - {abs(bb)})({bc}x + {bd}).",
                "choices": [
                    quadratic_expression(ba * bc, middle, bb * bd),
                    quadratic_expression(ba * bc, ba * bd - bb * bc, bb * bd),
                    quadratic_expression(ba * bc, middle, -bb * bd),
                    quadratic_expression(ba + bc, middle, bb * bd),
                ],
                "answer": quadratic_expression(ba * bc, middle, bb * bd),
                "solution": f"Multiply each pair: {ba * bc}x^2 {signed(ba * bd)}x {signed(bb * bc)}x {signed(bb * bd)}. Collecting the x terms gives {quadratic_expression(ba * bc, middle, bb * bd)}.",
                "trap": "Both middle terms must be collected, and a negative term keeps its sign.",
            }
        )

        da, db = 2 + v, 3 + v
        questions.append(
            {
                "id": f"y9_dots_{v}",
                "topic": "Algebraic manipulation",
                "difficulty": "Extension",
                "prompt": f"Factorise {da * da}x^2 - {db * db}.",
                "choices": [
                    f"({da}x - {db})({da}x + {db})",
                    f"({da}x - {db})^2",
                    f"({da * da}x - {db * db})(x + 1)",
                    f"({da}x - {db * db})({da}x + 1)",
                ],
                "answer": f"({da}x - {db})({da}x + {db})",
                "solution": f"{da * da}x^2 = ({da}x)^2 and {db * db} = {db}^2, so this is a difference of two squares: ({da}x - {db})({da}x + {db}).",
                "trap": "A difference of two squares gives two brackets with opposite signs.",
            }
        )

        small_area = 4 * (1 + v)
        scale_small, scale_large = 2, 2 + v
        large_area = (1 + v) * (2 + v) ** 2
        questions.append(
            {
                "id": f"y9_similar_area_{v}",
                "topic": "Geometric reasoning",
                "difficulty": "Extension",
                "prompt": f"Two similar triangles have corresponding sides in the ratio {scale_small}:{scale_large}. The smaller triangle has area {small_area} square cm. What is the area of the larger triangle?",
                "choices": number_choices(large_area, [small_area * scale_large // scale_small, small_area + scale_large, large_area + scale_large], " square cm"),
                "answer": f"{large_area} square cm",
                "solution": f"Areas scale by the square of the side ratio: ({scale_large}/{scale_small})^2 = {scale_large ** 2}/{scale_small ** 2}, so the larger area is {small_area} x {scale_large ** 2}/{scale_small ** 2} = {large_area} square cm.",
                "trap": "Area scale factor is the square of the length scale factor.",
            }
        )

        angle = 25 + 5 * v
        hypotenuse_length = 10 + 2 * v
        opposite = hypotenuse_length * math.sin(math.radians(angle))
        questions.append(
            {
                "id": f"y9_trig_side_{v}",
                "topic": "Pythagoras and trigonometry",
                "difficulty": "Extension",
                "prompt": f"In a right-angled triangle the hypotenuse is {hypotenuse_length} cm and one acute angle is {angle} degrees. Find the side opposite that angle, to 1 decimal place.",
                "choices": decimal_choices(
                    opposite,
                    [hypotenuse_length * math.cos(math.radians(angle)), hypotenuse_length * math.tan(math.radians(angle)), opposite + 2],
                    " cm",
                ),
                "answer": decimal_answer(opposite, " cm"),
                "solution": f"sin({angle}) = opposite / {hypotenuse_length}, so opposite = {hypotenuse_length} x sin({angle}) = {opposite:.1f} cm.",
                "trap": "With the hypotenuse and an angle, use sine for the opposite side and cosine for the adjacent side.",
            }
        )

        opposite_side = 5 + v
        adjacent_side = 9 + v
        found_angle = math.degrees(math.atan(opposite_side / adjacent_side))
        questions.append(
            {
                "id": f"y9_trig_angle_{v}",
                "topic": "Pythagoras and trigonometry",
                "difficulty": "Extension",
                "prompt": f"A ramp rises {opposite_side} m over a horizontal distance of {adjacent_side} m. What is the angle of elevation, to 1 decimal place?",
                "choices": decimal_choices(
                    found_angle,
                    [90 - found_angle, math.degrees(math.asin(opposite_side / adjacent_side)), found_angle + 5],
                    " degrees",
                ),
                "answer": decimal_answer(found_angle, " degrees"),
                "solution": f"tan(angle) = {opposite_side}/{adjacent_side}, so the angle = tan^-1({opposite_side / adjacent_side:.4f}) = {found_angle:.1f} degrees.",
                "trap": "Rise over horizontal run is the tangent ratio, not the sine ratio.",
            }
        )

        bl, bw, bh = 4 + v, 6 + v, 8 + v
        space_diagonal = math.sqrt(bl ** 2 + bw ** 2 + bh ** 2)
        questions.append(
            {
                "id": f"y9_pythagoras_3d_{v}",
                "topic": "Pythagoras and trigonometry",
                "difficulty": "Extension",
                "prompt": f"A rectangular box measures {bl} cm by {bw} cm by {bh} cm. What is the longest straight rod that fits inside, to 1 decimal place?",
                "choices": decimal_choices(space_diagonal, [math.sqrt(bl ** 2 + bw ** 2), bl + bw + bh, space_diagonal + 2], " cm"),
                "answer": decimal_answer(space_diagonal, " cm"),
                "solution": f"The space diagonal is sqrt({bl}^2 + {bw}^2 + {bh}^2) = sqrt({bl ** 2 + bw ** 2 + bh ** 2}) = {space_diagonal:.1f} cm.",
                "trap": "Apply Pythagoras twice: first across the base, then up to the opposite corner.",
            }
        )

        invest = 2000 * (1 + v)
        annual_rate = 3 + v
        amount = invest * (1 + annual_rate / 100) ** 3
        questions.append(
            {
                "id": f"y9_compound_{v}",
                "topic": "Percentages and finance",
                "difficulty": "Extension",
                "prompt": f"${invest} is invested at {annual_rate}% per annum compound interest, compounded annually. What is it worth after 3 years?",
                "choices": [
                    f"${amount:.2f}",
                    f"${invest * (1 + 3 * annual_rate / 100):.2f}",
                    f"${invest * (1 + annual_rate / 100) ** 2:.2f}",
                    f"${invest + invest * annual_rate / 100:.2f}",
                ],
                "answer": f"${amount:.2f}",
                "solution": f"A = P(1 + r)^n = {invest} x {1 + annual_rate / 100:g}^3 = ${amount:.2f}.",
                "trap": "Compound interest earns interest on interest, so it exceeds the simple interest total.",
            }
        )

        stat_base = 4 + v
        offsets = [0, 2, 4 + 2 * v, 6 + 2 * v, 9 + 2 * v, 12 + 3 * v, 15 + 3 * v, 17 + 3 * v, 20 + 4 * v]
        values = [stat_base + offset for offset in offsets]
        # Nine values: the median sits at index 4, so the quartiles are the medians
        # of values[0:4] and values[5:9].
        quartile_one = stat_base + (offsets[1] + offsets[2]) // 2
        quartile_three = stat_base + (offsets[6] + offsets[7]) // 2
        iqr = quartile_three - quartile_one
        questions.append(
            {
                "id": f"y9_iqr_{v}",
                "topic": "Statistics",
                "difficulty": "Extension",
                "prompt": "Find the interquartile range of " + ", ".join(str(value) for value in values) + ".",
                "choices": number_choices(iqr, [values[-1] - values[0], values[4], iqr + 3]),
                "answer": str(iqr),
                "solution": f"The median is {values[4]}. Q1 is the median of the lower four values ({quartile_one}) and Q3 is the median of the upper four values ({quartile_three}), so IQR = {quartile_three} - {quartile_one} = {iqr}.",
                "trap": "With nine values, leave the median out of both halves before finding the quartiles.",
            }
        )

        red_count = 4 + v
        blue_count = 3 + v
        total_count = red_count + blue_count
        questions.append(
            {
                "id": f"y9_probability_no_replacement_{v}",
                "topic": "Probability",
                "difficulty": "Extension",
                "prompt": f"A bag holds {red_count} red and {blue_count} blue counters. Two are drawn without replacement. What is the probability that both are red?",
                "choices": [
                    fraction_text(red_count * (red_count - 1), total_count * (total_count - 1)),
                    fraction_text(red_count * red_count, total_count * total_count),
                    fraction_text(red_count, total_count),
                    fraction_text(red_count - 1, total_count - 1),
                ],
                "answer": fraction_text(red_count * (red_count - 1), total_count * (total_count - 1)),
                "solution": f"P = {red_count}/{total_count} x {red_count - 1}/{total_count - 1} = {fraction_text(red_count * (red_count - 1), total_count * (total_count - 1))}.",
                "trap": "Without replacement both the numerator and the denominator fall by one on the second draw.",
            }
        )

    return questions


def build_advanced_math_questions():
    """Beyond Year 9: multi-step reasoning of the kind used in selective and scholarship papers."""
    questions = []
    surds = [(72, 6, 2), (98, 7, 2), (128, 8, 2), (75, 5, 3)]
    quadratics = [(5, -3), (6, -2), (7, -4), (8, -3)]
    percent_pairs = [(20, 25), (10, 20), (50, 40), (30, 50)]
    speed_pairs = [(60, 40), (30, 20), (24, 12), (45, 30)]
    words = [("LEVEL", 30), ("BANANA", 60), ("LETTER", 180), ("SUCCESS", 420)]

    for v in range(1, 5):
        number, outside, inside = surds[v - 1]
        questions.append(
            {
                "id": f"adv_surd_{v}",
                "topic": "Indices and scientific notation",
                "difficulty": "Advanced",
                "prompt": f"Simplify sqrt({number}).",
                "choices": [
                    f"{outside}sqrt({inside})",
                    f"{outside * inside}sqrt({inside})",
                    f"{inside}sqrt({outside})",
                    f"{outside}sqrt({outside})",
                ],
                "answer": f"{outside}sqrt({inside})",
                "solution": f"{number} = {outside ** 2} x {inside}, and sqrt({outside ** 2}) = {outside}, so sqrt({number}) = {outside}sqrt({inside}).",
                "trap": "Pull out the largest perfect square factor, not just any factor.",
            }
        )

        p, q = quadratics[v - 1]
        questions.append(
            {
                "id": f"adv_quadratic_{v}",
                "topic": "Algebraic manipulation",
                "difficulty": "Advanced",
                "prompt": f"Factorise x^2 {signed(-(p + q))}x {signed(p * q)}.",
                # Note: (x - a)(x + b) and (x + b)(x - a) are the same product, so every
                # distractor must differ in the numbers, not merely in bracket order.
                "choices": [
                    f"(x - {p})(x + {abs(q)})",
                    f"(x + {p})(x - {abs(q)})",
                    f"(x - {p + 1})(x + {abs(q) + 1})",
                    f"(x - {p})(x - {abs(q)})",
                ],
                "answer": f"(x - {p})(x + {abs(q)})",
                "solution": f"Two numbers multiply to {p * q} and add to {p + q}. They are {p} and {q}, so the factorisation is (x - {p})(x + {abs(q)}).",
                "trap": "Check the sum as well as the product, or the signs will end up reversed.",
            }
        )

        rise_percent, fall_percent = percent_pairs[v - 1]
        start_price = 2000 * (1 + v)
        end_price = round(start_price * (100 + rise_percent) * (100 - fall_percent) / 10000)
        questions.append(
            {
                "id": f"adv_percent_reverse_{v}",
                "topic": "Percentages and finance",
                "difficulty": "Advanced",
                "prompt": f"A price rose by {rise_percent}% and later fell by {fall_percent}%. It is now ${end_price}. What was the price before the rise?",
                "choices": money_choices(start_price, [end_price, round(end_price / (1 + (rise_percent - fall_percent) / 100)), start_price + 200]),
                "answer": f"${start_price:g}",
                "solution": f"The combined factor is {(100 + rise_percent) / 100:g} x {(100 - fall_percent) / 100:g} = {(100 + rise_percent) * (100 - fall_percent) / 10000:g}. Divide: {end_price} / {(100 + rise_percent) * (100 - fall_percent) / 10000:g} = ${start_price}.",
                "trap": "Reverse both changes as a single multiplying factor rather than adding the percentages.",
            }
        )

        speed_one, speed_two = speed_pairs[v - 1]
        average_speed = 2 * speed_one * speed_two // (speed_one + speed_two)
        questions.append(
            {
                "id": f"adv_average_speed_{v}",
                "topic": "Ratio, rates and proportion",
                "difficulty": "Advanced",
                "prompt": f"A cyclist rides to a town at {speed_one} km/h and returns along the same road at {speed_two} km/h. What is the average speed for the whole trip?",
                "choices": number_choices(average_speed, [(speed_one + speed_two) // 2, speed_one, speed_two], " km/h"),
                "answer": f"{average_speed} km/h",
                "solution": f"Average speed is total distance over total time. For equal distances it is 2 x {speed_one} x {speed_two} / ({speed_one} + {speed_two}) = {average_speed} km/h.",
                "trap": "Average speed is not the average of the two speeds because more time is spent at the slower speed.",
            }
        )

        word, arrangements = words[v - 1]
        questions.append(
            {
                "id": f"adv_arrangements_{v}",
                "topic": "Number theory and counting",
                "difficulty": "Advanced",
                "prompt": f"How many different arrangements can be made from all the letters of {word}?",
                "choices": number_choices(arrangements, [arrangements * 2, arrangements // 2, arrangements + 10]),
                "answer": str(arrangements),
                "solution": f"Divide the total arrangements of the letters by the factorial of each repeated letter count. For {word} this gives {arrangements}.",
                "trap": "Repeated letters must be divided out or identical arrangements are counted more than once.",
            }
        )

        share = 2 + v
        guarantee = 12 * (share - 1) + 1
        questions.append(
            {
                "id": f"adv_pigeonhole_{v}",
                "topic": "Number theory and counting",
                "difficulty": "Advanced",
                "prompt": f"What is the smallest number of students needed to guarantee that at least {share} of them share a birth month?",
                "choices": number_choices(guarantee, [12 * share, 12 * (share - 1), guarantee + 12]),
                "answer": str(guarantee),
                "solution": f"In the worst case each month holds {share - 1} students, which is {12 * (share - 1)}. One more student forces a month to reach {share}, so {guarantee} students are needed.",
                "trap": "Build the worst case first, then add one.",
            }
        )

        solve_x = 2 + v
        solve_y = -(1 + v)
        left_constant = 3 * solve_x + 4 * solve_y
        right_constant = 5 * solve_x - 3 * solve_y
        questions.append(
            {
                "id": f"adv_simultaneous_{v}",
                "topic": "Simultaneous equations",
                "difficulty": "Advanced",
                "prompt": f"Solve simultaneously: 3x + 4y = {left_constant} and 5x - 3y = {right_constant}.",
                "choices": [
                    f"x = {solve_x}, y = {solve_y}",
                    f"x = {solve_y}, y = {solve_x}",
                    f"x = {solve_x}, y = {-solve_y}",
                    f"x = {solve_x - 1}, y = {solve_y + 1}",
                ],
                "answer": f"x = {solve_x}, y = {solve_y}",
                "solution": f"Multiply the first equation by 3 and the second by 4, then add to eliminate y. This gives x = {solve_x}, and substituting back gives y = {solve_y}.",
                "trap": "Neither variable eliminates directly, so scale both equations before adding.",
            }
        )

        part_a, part_b, part_c = 2 + v, 3 + v, 5 + v
        one_part = 10 + v
        difference = 3 * one_part
        total_prize = (part_a + part_b + part_c) * one_part
        questions.append(
            {
                "id": f"adv_three_ratio_{v}",
                "topic": "Ratio, rates and proportion",
                "difficulty": "Advanced",
                "prompt": f"Three prizes are shared in the ratio {part_a}:{part_b}:{part_c}. The largest prize is ${difference} more than the smallest. What is the total prize money?",
                "choices": money_choices(total_prize, [difference, part_c * one_part, total_prize - difference]),
                "answer": f"${total_prize:g}",
                "solution": f"The difference is {part_c} - {part_a} = 3 parts, so one part is ${one_part}. The total is {part_a + part_b + part_c} parts = ${total_prize}.",
                "trap": "Use the difference in parts to find one part before scaling to the total.",
            }
        )

    return questions


def build_year8_grammar_questions():
    """Victorian Curriculum Year 8 language: modality, nominalisation, voice, clauses, punctuation, cohesion."""
    questions = []

    modality_items = [
        ("The council must act before winter.", "The council might act before winter.", "The council could act before winter.", "The council may act before winter."),
        ("Students will certainly benefit from the change.", "Students may benefit from the change.", "Students could possibly benefit from the change.", "Students might benefit from the change."),
        ("This evidence proves the claim beyond doubt.", "This evidence perhaps supports the claim.", "This evidence may support the claim.", "This evidence could support the claim."),
        ("Every school should adopt the policy immediately.", "Some schools might consider the policy.", "A school could look at the policy.", "Schools may perhaps review the policy."),
        ("The results demonstrate a clear pattern.", "The results seem to hint at a pattern.", "The results possibly show a pattern.", "The results may suggest a pattern."),
        ("We are obliged to report the finding.", "We might mention the finding.", "We could raise the finding later.", "We may possibly note the finding."),
        ("The rule always applies to Year 9 students.", "The rule sometimes applies to Year 9 students.", "The rule occasionally applies to Year 9 students.", "The rule rarely applies to Year 9 students."),
        ("The design is definitely the safest option.", "The design is arguably a safe option.", "The design is perhaps a safe option.", "The design may be a safe option."),
    ]
    for index, item in enumerate(modality_items, start=1):
        questions.append(
            {
                "id": f"y8_modality_{index:02d}",
                "skill": "Modality",
                "difficulty": "Challenge",
                "prompt": "Which sentence uses the highest modality?",
                "choices": list(item),
                "answer": item[0],
                "solution": "High modality words such as must, will, always and definitely express strong certainty or obligation.",
            }
        )

    nominalisation_items = [
        ("The introduction of the ban caused significant disruption.", "They introduced the ban and it disrupted a lot of things.", "After the ban came in, things got disrupted.", "The ban was introduced and then disruption happened."),
        ("The failure of the experiment prompted a review.", "The experiment failed so they reviewed it.", "Because the experiment failed, they had a look at it.", "They reviewed it after the experiment did not work."),
        ("The expansion of the program improved attendance.", "They expanded the program and more students attended.", "After the program got bigger, attendance improved.", "Attendance improved once the program was made bigger."),
        ("Rejection of the proposal surprised the committee.", "The committee was surprised when they rejected the proposal.", "They rejected the proposal and this surprised everyone.", "The committee felt surprised because the proposal got rejected."),
        ("The demolition of the building required approval.", "They demolished the building after getting approval.", "Before they knocked the building down, they got approval.", "Approval was needed before the building was demolished."),
        ("Her analysis of the data revealed an error.", "She analysed the data and found an error.", "When she looked at the data, she saw an error.", "An error was found after she looked at the data."),
        ("Implementation of the new timetable was delayed.", "They delayed putting the new timetable in place.", "The new timetable was put in place late.", "Putting in the new timetable happened later than planned."),
        ("The refusal of the request angered the students.", "The students were angry when the request was refused.", "They refused the request and the students got angry.", "Students felt angry because their request got refused."),
    ]
    for index, item in enumerate(nominalisation_items, start=1):
        questions.append(
            {
                "id": f"y8_nominalisation_{index:02d}",
                "skill": "Nominalisation",
                "difficulty": "Extension",
                "prompt": "Which sentence uses nominalisation, turning a process into a noun?",
                "choices": list(item),
                "answer": item[0],
                "solution": "Nominalisation converts a verb into an abstract noun, which makes writing more formal and compressed.",
            }
        )

    passive_items = [
        ("The committee approved the proposal.", "The proposal was approved by the committee.", "The proposal approved the committee.", "The committee was approved by the proposal.", "The proposal is approving the committee."),
        ("Scientists collected the samples in winter.", "The samples were collected by scientists in winter.", "The samples collected the scientists in winter.", "Scientists were collected by the samples in winter.", "The samples are collecting scientists in winter."),
        ("The council closed the walking track.", "The walking track was closed by the council.", "The walking track closed the council.", "The council was closed by the walking track.", "The walking track is closing the council."),
        ("The teacher marked every draft.", "Every draft was marked by the teacher.", "Every draft marked the teacher.", "The teacher was marked by every draft.", "Every draft is marking the teacher."),
        ("Volunteers planted three hundred seedlings.", "Three hundred seedlings were planted by volunteers.", "Three hundred seedlings planted the volunteers.", "Volunteers were planted by three hundred seedlings.", "Three hundred seedlings are planting volunteers."),
        ("The editor cut the final paragraph.", "The final paragraph was cut by the editor.", "The final paragraph cut the editor.", "The editor was cut by the final paragraph.", "The final paragraph is cutting the editor."),
        ("The museum rewrote the label.", "The label was rewritten by the museum.", "The label rewrote the museum.", "The museum was rewritten by the label.", "The label is rewriting the museum."),
        ("Students designed the entire display.", "The entire display was designed by students.", "The entire display designed the students.", "Students were designed by the entire display.", "The entire display is designing students."),
    ]
    for index, item in enumerate(passive_items, start=1):
        active, passive, *wrong = item
        questions.append(
            {
                "id": f"y8_passive_{index:02d}",
                "skill": "Active and passive voice",
                "difficulty": "Challenge",
                "prompt": f"Which sentence is the correct passive form of: {active}",
                "choices": [passive, *wrong],
                "answer": passive,
                "solution": "In the passive voice the object becomes the subject, the verb takes a form of 'to be', and the original subject follows 'by'.",
            }
        )

    clause_items = [
        ("Relative clause", "The student who wrote the report won the prize.", "The student wrote the report and won the prize.", "The student wrote the report, winning the prize.", "Writing the report, the student won the prize."),
        ("Subordinate clause of concession", "Although the evidence was limited, the conclusion held.", "The evidence was limited and the conclusion held.", "The evidence was limited; the conclusion held.", "Limited evidence, but the conclusion held."),
        ("Subordinate clause of condition", "If the data is incomplete, the graph will mislead.", "The data is incomplete and the graph misleads.", "Incomplete data, so a misleading graph.", "The graph misleads; the data is incomplete."),
        ("Subordinate clause of reason", "Because the sample was small, the result was unreliable.", "The sample was small and the result was unreliable.", "A small sample, an unreliable result.", "The result was unreliable; the sample was small."),
        ("Subordinate clause of time", "After the bell had rung, the corridor emptied.", "The bell rang and the corridor emptied.", "The bell rang; the corridor emptied.", "The corridor emptied, the bell having rung earlier that day."),
        ("Embedded relative clause", "The report, which ran to forty pages, was never read.", "The report ran to forty pages and was never read.", "The report was forty pages; nobody read it.", "Running to forty pages, the report was never read."),
        ("Compound sentence", "The claim is clear, and the evidence is specific.", "Although the claim is clear, the evidence is vague.", "The claim, which is clear, needs evidence.", "Being clear, the claim still needs evidence."),
        ("Complex sentence", "When the results arrived, the team revised the model.", "The results arrived, and the team revised the model.", "The results arrived; the team revised the model.", "The results arrived. The team revised the model."),
        ("Relative clause", "The building that housed the archive has been demolished.", "The building housed the archive and has been demolished.", "The building housed the archive; it is now demolished.", "Housing the archive, the building has been demolished."),
        ("Subordinate clause of purpose", "So that the results could be checked, the data was published.", "The data was published and the results were checked.", "The data was published; the results were checked.", "Publishing the data allowed the results to be checked."),
    ]
    for index, item in enumerate(clause_items, start=1):
        label, answer, *wrong = item
        questions.append(
            {
                "id": f"y8_clause_{index:02d}",
                "skill": "Clauses and sentence types",
                "difficulty": "Extension",
                "prompt": f"Which sentence contains a {label.lower()}?",
                "choices": [answer, *wrong],
                "answer": answer,
                "solution": f"A {label.lower()} is identified by the way the added group of words depends on, or modifies, the main clause.",
            }
        )

    punctuation_items = [
        ("The first draft was competent; the second was persuasive.", "The first draft was competent, the second was persuasive.", "The first draft was competent; and the second was persuasive.", "The first draft was competent: but the second was persuasive."),
        ("The evidence pointed to one conclusion: the sample was too small.", "The evidence pointed to one conclusion, that the sample: was too small.", "The evidence pointed: to one conclusion the sample was too small.", "The evidence pointed to one conclusion; the sample: was too small."),
        ("Three things matter here: accuracy, clarity and evidence.", "Three things matter here; accuracy, clarity and evidence.", "Three things matter here, accuracy: clarity and evidence.", "Three things matter: here accuracy, clarity and evidence."),
        ("The design - unusual, expensive and unpopular - was approved anyway.", "The design, unusual, expensive and unpopular was approved anyway.", "The design - unusual, expensive and unpopular, was approved anyway.", "The design unusual - expensive and unpopular - was approved anyway."),
        ("The results were surprising; however, they were consistent.", "The results were surprising, however, they were consistent.", "The results were surprising; however they were consistent, ", "The results were surprising however; they were consistent."),
        ("Rachel's argument, which relied on one source, was still convincing.", "Rachel's argument which relied on one source, was still convincing.", "Rachels argument, which relied on one source, was still convincing.", "Rachel's argument, which relied on one source was still convincing."),
        ("The witnesses' statements agreed on every detail.", "The witnesses statements agreed on every detail.", "The witness's statements agreed on every detail.", "The witnesses's statements agreed on every detail."),
        ("It's clear that the committee has changed its position.", "Its clear that the committee has changed it's position.", "It's clear that the committee has changed it's position.", "Its' clear that the committee has changed its position."),
    ]
    for index, item in enumerate(punctuation_items, start=1):
        questions.append(
            {
                "id": f"y8_punctuation_{index:02d}",
                "skill": "Punctuation",
                "difficulty": "Extension",
                "prompt": "Which sentence is punctuated correctly?",
                "choices": list(item),
                "answer": item[0],
                "solution": "Check that each mark does the job it is designed for: semicolons join clauses, colons introduce, dashes enclose, apostrophes show possession.",
            }
        )

    cohesion_items = [
        ("The trial produced clear results; _____, the sample was too small to generalise from.", "however", "therefore", "similarly", "for instance"),
        ("The evidence was collected independently; _____, it is unusually reliable.", "consequently", "nevertheless", "conversely", "meanwhile"),
        ("The first witness described a blue car; _____, the second described a blue van.", "similarly", "however", "therefore", "nonetheless"),
        ("Funding was cut in March; _____, the program continued until December.", "nevertheless", "consequently", "likewise", "in addition"),
        ("Several factors shaped the outcome; _____, the weather was the most significant.", "of these", "in contrast", "conversely", "regardless"),
        ("The policy reduced incidents at school; _____, it may simply have moved them elsewhere.", "on the other hand", "as a result", "in the same way", "for this reason"),
        ("The graph appeared convincing; _____, its vertical axis did not start at zero.", "in fact", "accordingly", "equally", "thereafter"),
        ("The council consulted residents early; _____, opposition was much lower than expected.", "as a result", "even so", "by contrast", "in comparison"),
    ]
    for index, item in enumerate(cohesion_items, start=1):
        sentence, answer, *wrong = item
        questions.append(
            {
                "id": f"y8_cohesion_{index:02d}",
                "skill": "Cohesion and connectives",
                "difficulty": "Extension",
                "prompt": f"Which connective best completes the sentence? {sentence}",
                "choices": [answer, *wrong],
                "answer": answer,
                "solution": f"'{answer}' signals the logical relationship the two clauses actually have.",
            }
        )

    return questions


def build_year9_grammar_questions():
    """Victorian Curriculum Year 9 language: structure, register, connotation, morphology, vocabulary."""
    questions = []

    parallel_items = [
        ("The course teaches students to plan an argument, gather evidence and evaluate sources.", "The course teaches students to plan an argument, gathering evidence and evaluation of sources.", "The course teaches planning an argument, to gather evidence and evaluating sources.", "The course teaches students planning, to gather evidence and that sources are evaluated."),
        ("She was praised for her precision, her patience and her honesty.", "She was praised for her precision, being patient and she was honest.", "She was praised for precision, patiently and honesty.", "She was praised for her precision, patience and being honest about things."),
        ("The report identifies the problem, explains its causes and proposes a remedy.", "The report identifies the problem, explanation of its causes and proposing a remedy.", "The report identifies the problem, its causes are explained and proposes a remedy.", "The report is identifying the problem, explains its causes and a remedy is proposed."),
        ("We came to listen, to question and to decide.", "We came to listen, questioning and for a decision.", "We came for listening, to question and deciding.", "We came to listen, we questioned and a decision was made."),
        ("Good writing is clear, concise and precise.", "Good writing is clear, concisely and with precision.", "Good writing is clarity, concise and precise.", "Good writing has clarity, is concise and precision."),
        ("The policy aims to reduce waste, lower costs and improve safety.", "The policy aims to reduce waste, lowering costs and improvement of safety.", "The policy aims at waste reduction, to lower costs and improving safety.", "The policy aims to reduce waste, costs are lowered and improving safety."),
    ]
    for index, item in enumerate(parallel_items, start=1):
        questions.append(
            {
                "id": f"y9_parallel_{index:02d}",
                "skill": "Sentence structure",
                "difficulty": "Extension",
                "prompt": "Which sentence maintains parallel structure?",
                "choices": list(item),
                "answer": item[0],
                "solution": "Items joined in a list must share the same grammatical form.",
            }
        )

    modifier_items = [
        ("Having checked the calculations, the student submitted the report.", "Having checked the calculations, the report was submitted.", "Having checked the calculations, submission of the report followed.", "Having checked the calculations, it was submitted."),
        ("Walking through the gallery, we noticed the missing label.", "Walking through the gallery, the missing label was noticed.", "Walking through the gallery, the label was found to be missing.", "Walking through the gallery, there was a missing label."),
        ("After reading the brief, the team revised the design.", "After reading the brief, the design was revised.", "After reading the brief, revision of the design occurred.", "After reading the brief, it was revised."),
        ("Exhausted by the heat, the runners slowed to a walk.", "Exhausted by the heat, the pace slowed to a walk.", "Exhausted by the heat, walking became the only option.", "Exhausted by the heat, the race was slowed."),
        ("She almost answered every question correctly.", "She answered almost every question correctly.", "Almost she answered every question correctly.", "She answered every question almost correctly."),
        ("The teacher explained clearly why the method failed.", "The teacher explained why the method failed clearly.", "Clearly the teacher explained why failed the method.", "The teacher clearly why the method failed explained."),
    ]
    for index, item in enumerate(modifier_items, start=1):
        if index == 5:
            prompt = "Which sentence places the modifier so that the meaning is 'nearly all the questions were correct'?"
            answer = item[1]
            choices = [item[1], item[0], item[2], item[3]]
        else:
            prompt = "Which sentence avoids a dangling or misplaced modifier?"
            answer = item[0]
            choices = list(item)
        questions.append(
            {
                "id": f"y9_modifier_{index:02d}",
                "skill": "Modifiers",
                "difficulty": "Advanced",
                "prompt": prompt,
                "choices": choices,
                "answer": answer,
                "solution": "A modifier must sit next to the word it describes, and an opening participle must describe the subject of the main clause.",
            }
        )

    register_items = [
        ("The imagery in the final stanza reinforces the speaker's isolation.", "The imagery at the end is pretty cool and shows she is lonely.", "I reckon the last bit makes you feel sorry for her.", "The poem is about loneliness and stuff like that."),
        ("The data suggests a correlation that warrants further investigation.", "The data kind of shows they might be linked somehow.", "It looks like there's a link, which is interesting.", "The numbers seem to go together a fair bit."),
        ("The witness's account contradicts the physical evidence.", "What the witness said doesn't match up with the stuff they found.", "The witness got it wrong compared to the evidence.", "The witness's version was a bit off from the evidence."),
        ("This response demonstrates a limited understanding of the text.", "This response doesn't really get the text at all.", "The student sort of missed the point of the text.", "This answer is not great on understanding the text."),
        ("The council should reconsider the proposal in light of new evidence.", "The council needs to have another think about it now.", "Maybe the council could look at it again or something.", "The council ought to take another crack at the proposal."),
        ("The experiment yielded results consistent with the hypothesis.", "The experiment turned out pretty much how they thought.", "The results were basically what was expected, more or less.", "The experiment worked out the way they reckoned it would."),
    ]
    for index, item in enumerate(register_items, start=1):
        questions.append(
            {
                "id": f"y9_register_{index:02d}",
                "skill": "Register and tone",
                "difficulty": "Extension",
                "prompt": "Which sentence is most appropriate for a formal analytical response?",
                "choices": list(item),
                "answer": item[0],
                "solution": "Formal register uses precise metalanguage and avoids colloquialism, hedging fillers and vague quantifiers.",
            }
        )

    connotation_items = [
        ("stubborn", "determined", "persistent", "resolute"),
        ("cheap", "affordable", "economical", "inexpensive"),
        ("nosy", "curious", "inquisitive", "interested"),
        ("scrawny", "slender", "slim", "lean"),
        ("crowd", "gathering", "audience", "assembly"),
        ("interrogated", "questioned", "asked", "consulted"),
        ("odour", "scent", "aroma", "fragrance"),
        ("meddling", "helping", "assisting", "contributing"),
    ]
    for index, item in enumerate(connotation_items, start=1):
        questions.append(
            {
                "id": f"y9_connotation_{index:02d}",
                "skill": "Connotation",
                "difficulty": "Extension",
                "prompt": "Which word carries the most negative connotation?",
                "choices": list(item),
                "answer": item[0],
                "solution": f"All four words share a similar denotation, but '{item[0]}' adds a critical or unfavourable attitude.",
            }
        )

    vocabulary_items = [
        ("ambivalent", "having mixed or conflicting feelings", "completely certain", "extremely noisy", "carefully organised"),
        ("substantiate", "support a claim with evidence", "shorten a statement", "hide a detail", "guess an outcome"),
        ("nuanced", "showing subtle differences", "simple and obvious", "loud and forceful", "poorly organised"),
        ("scrutinise", "examine closely and critically", "ignore deliberately", "repeat loudly", "decorate carefully"),
        ("inadvertent", "unintentional", "carefully planned", "openly hostile", "widely admired"),
        ("concede", "admit that a point is valid", "deny every claim", "shorten an argument", "repeat a question"),
        ("cohesive", "well connected and unified", "scattered and disjointed", "extremely fragile", "unusually brief"),
        ("discerning", "showing good judgement", "easily fooled", "completely unaware", "entirely ordinary"),
        ("pragmatic", "guided by practical results", "guided only by theory", "driven by emotion", "based on tradition"),
        ("superfluous", "more than is needed", "essential to the whole", "extremely rare", "carefully hidden"),
        ("tenuous", "weak or slight", "firmly established", "widely believed", "highly detailed"),
        ("candid", "honest and direct", "carefully evasive", "highly decorated", "deliberately vague"),
        ("prolific", "producing a great deal", "producing very little", "working slowly", "acting unfairly"),
        ("obsolete", "no longer in use", "recently invented", "widely popular", "under construction"),
        ("meticulous", "extremely careful about detail", "quick and approximate", "loud and confident", "unwilling to begin"),
        ("resilient", "able to recover from difficulty", "easily and permanently damaged", "unwilling to change", "slow to understand"),
        ("arbitrary", "based on chance rather than reason", "based on careful rules", "agreed by everyone", "proven by evidence"),
        ("empirical", "based on observation or experiment", "based on opinion alone", "based on tradition", "based on imagination"),
    ]
    for index, item in enumerate(vocabulary_items, start=1):
        word, answer, *wrong = item
        questions.append(
            {
                "id": f"y9_vocabulary_{index:02d}",
                "skill": "Vocabulary",
                "difficulty": "Extension" if index <= 12 else "Advanced",
                "prompt": f"Which meaning is closest to '{word}'?",
                "choices": [answer, *wrong],
                "answer": answer,
                "solution": f"'{word}' means {answer}.",
            }
        )

    root_items = [
        ("bene", "benevolent", "good or well", "against", "under", "across"),
        ("chron", "chronological", "time", "shape", "life", "light"),
        ("dict", "contradict", "to say or speak", "to carry", "to break", "to see"),
        ("cred", "incredible", "to believe", "to build", "to write", "to hear"),
        ("path", "empathy", "feeling or suffering", "distance", "measurement", "study"),
        ("scrib", "inscription", "to write", "to cut", "to lead", "to turn"),
        ("ambi", "ambiguous", "both or around", "beyond", "before", "without"),
        ("mal", "malicious", "bad or evil", "large", "many", "single"),
        ("terr", "subterranean", "earth or land", "water", "fire", "air"),
        ("voc", "vocation", "to call", "to hold", "to place", "to grow"),
        ("morph", "metamorphosis", "form or shape", "colour", "sound", "weight"),
        ("ject", "projection", "to throw", "to join", "to close", "to open"),
    ]
    for index, item in enumerate(root_items, start=1):
        root, example, answer, *wrong = item
        questions.append(
            {
                "id": f"y9_root_{index:02d}",
                "skill": "Word origins",
                "difficulty": "Advanced",
                "prompt": f"In the word '{example}', the root '{root}' means",
                "choices": [answer, *wrong],
                "answer": answer,
                "solution": f"The root '{root}' means {answer}, which explains the meaning of '{example}' and related words.",
            }
        )

    confused_items = [
        ("The graph implies a downward trend.", "The graph infers a downward trend.", "A writer or text implies; a reader or listener infers."),
        ("The reader may infer that the narrator is unreliable.", "The reader may imply that the narrator is unreliable.", "Infer means to work something out from evidence."),
        ("The lawyer tried to elicit a clear answer.", "The lawyer tried to illicit a clear answer.", "Elicit means to draw out; illicit means illegal."),
        ("Please be discreet about the announcement.", "Please be discrete about the announcement.", "Discreet means tactful; discrete means separate."),
        ("The essay should cite at least two sources.", "The essay should site at least two sources.", "Cite means to quote a source; a site is a place."),
        ("The novel contains an allusion to a Greek myth.", "The novel contains an illusion to a Greek myth.", "An allusion is an indirect reference; an illusion is a false impression."),
        ("One criterion was never explained.", "One criteria was never explained.", "Criterion is singular; criteria is the plural."),
        ("This phenomenon has been recorded twice.", "This phenomena has been recorded twice.", "Phenomenon is singular; phenomena is the plural."),
        ("The principle behind the design is simple.", "The principal behind the design is simple.", "A principle is a rule or belief; a principal leads a school."),
        ("The council will advise residents next week.", "The council will advice residents next week.", "Advise is the verb; advice is the noun."),
        ("Fewer students chose the elective this year.", "Less students chose the elective this year.", "Use fewer for countable nouns and less for quantities."),
        ("The team performed better than expected.", "The team performed better then expected.", "Than compares; then refers to time or sequence."),
        ("Whose argument was the most convincing?", "Who's argument was the most convincing?", "Whose shows possession; who's means who is."),
        ("The report complements the earlier study.", "The report compliments the earlier study.", "Complement means to complete; compliment means to praise."),
    ]
    for index, item in enumerate(confused_items, start=1):
        correct, wrong, explanation = item
        # Trim the final mark so the padded distractors work for questions as well as statements.
        correct_stem = correct.rstrip(".?!")
        wrong_stem = wrong.rstrip(".?!")
        correct_end = correct[len(correct_stem):]
        wrong_end = wrong[len(wrong_stem):]
        questions.append(
            {
                "id": f"y9_confused_{index:02d}",
                "skill": "Word choice",
                "difficulty": "Extension" if index <= 7 else "Advanced",
                "prompt": "Choose the sentence with the correct word choice.",
                "choices": [
                    correct,
                    wrong,
                    f"{correct_stem}, basically{correct_end}",
                    f"{wrong_stem}, sort of{wrong_end}",
                ],
                "answer": correct,
                "solution": explanation,
            }
        )

    spelling_items = [
        ("accommodation", "The excursion accommodation was confirmed on Tuesday.", "acommodation", "accomodation", "accommadation"),
        ("conscientious", "She is a conscientious note-taker.", "consciencious", "conscientous", "concientious"),
        ("occurrence", "The second occurrence changed the pattern.", "occurence", "ocurrence", "occurrance"),
        ("privilege", "Leadership is a privilege and a responsibility.", "priviledge", "privelege", "privilage"),
        ("maintenance", "The equipment required regular maintenance.", "maintainance", "maintenence", "maintanence"),
        ("unnecessary", "The final paragraph was unnecessary.", "unecessary", "unneccessary", "unnecesary"),
        ("questionnaire", "The questionnaire was completed anonymously.", "questionaire", "questionnair", "questionnare"),
        ("parliament", "The bill was debated in parliament.", "parliment", "parlaiment", "parliamant"),
        ("independent", "The two studies were entirely independent.", "independant", "indipendent", "independet"),
        ("acknowledgement", "The acknowledgement appeared on the final page.", "acknowlegement", "aknowledgement", "acknowledgemant"),
        ("perseverance", "Her perseverance was noted by every teacher.", "perserverance", "perseverence", "persaverance"),
        ("exaggerate", "Do not exaggerate the strength of the evidence.", "exagerate", "exaggerrate", "exsaggerate"),
    ]
    for index, item in enumerate(spelling_items, start=1):
        word, sentence, *misspellings = item
        questions.append(
            {
                "id": f"y9_spelling_{index:02d}",
                "skill": "Spelling",
                "difficulty": "Extension",
                "prompt": "Choose the sentence with the correct spelling.",
                "choices": [sentence, *[sentence.replace(word, wrong, 1) for wrong in misspellings]],
                "answer": sentence,
                "solution": f"The correct spelling is '{word}'.",
            }
        )

    return questions


def build_language_analysis_questions():
    """Identify persuasive and literary techniques, then explain their effect."""
    technique_pool = [
        "metaphor",
        "simile",
        "personification",
        "hyperbole",
        "alliteration",
        "rhetorical question",
        "irony",
        "juxtaposition",
        "emotive language",
        "inclusive language",
        "repetition",
        "understatement",
        "appeal to authority",
        "anecdote",
        "statistics",
    ]
    generic_effects = [
        "It supplies factual information without implying any judgement.",
        "It signals that the narrator has changed midway through the text.",
        "It corrects a factual error made earlier in the text.",
    ]
    items = [
        ("The new policy is a bandage on a broken leg.", "metaphor", "It dismisses the policy as a token gesture that ignores the real damage."),
        ("The corridor emptied like water leaving a bath.", "simile", "It makes the sudden, complete departure vivid and slightly comic."),
        ("The old timetable clung stubbornly to the noticeboard.", "personification", "It gives the timetable a will of its own, suggesting outdated habits are hard to remove."),
        ("I have read that paragraph a thousand times and still cannot follow it.", "hyperbole", "It exaggerates repetition to convey genuine frustration with unclear writing."),
        ("Careless cutting costs councils considerably.", "alliteration", "The repeated sound makes the warning memorable and quotable."),
        ("How much longer must students wait for a safe crossing?", "rhetorical question", "It pressures the reader to supply the answer the writer wants."),
        ("The safety review was published the week after the accident.", "irony", "The timing quietly exposes the gap between official concern and actual protection."),
        ("The stadium cost forty million dollars; the library closed in March.", "juxtaposition", "Placing the two facts side by side implies a criticism without stating it."),
        ("Children are being abandoned to a system that has already failed them.", "emotive language", "Strong emotional wording provokes indignation before the reader weighs the evidence."),
        ("We all want the same thing for our children.", "inclusive language", "It positions the reader inside the writer's group, making disagreement feel disloyal."),
        ("Not next year, not next term, not next week.", "repetition", "The insistent pattern builds urgency and signals impatience."),
        ("Losing the entire archive was, admittedly, inconvenient.", "understatement", "Deliberately downplaying a disaster draws attention to how serious it really was."),
        ("The state's chief health officer has endorsed the change.", "appeal to authority", "It borrows credibility from an expert so the claim seems settled."),
        ("Last winter my neighbour waited three hours for a bus that never came.", "anecdote", "A single human story makes an abstract problem feel immediate."),
        ("Sixty-one per cent of respondents reported the same delay.", "statistics", "A precise figure lends the claim an air of objectivity and scale."),
        ("Her argument was a locked door with no handle.", "metaphor", "It conveys that the reasoning offered the reader no way in."),
        ("The silence after the announcement sat in the room like a guest nobody invited.", "simile", "It makes the discomfort concrete and faintly absurd."),
        ("The deadline stalked us through the last week of term.", "personification", "It presents the deadline as a predator, conveying sustained pressure."),
        ("Are we seriously expected to believe that nothing could have been done?", "rhetorical question", "It invites the reader to reject the official explanation as implausible."),
        ("The report praised the process. It did not mention the outcome.", "juxtaposition", "The unspoken contrast between process and outcome implies the outcome was poor."),
    ]
    questions = []
    for index, (quote, technique, effect) in enumerate(items, start=1):
        pool = [item for item in technique_pool if item != technique]
        distractors = [pool[(index * 3 + offset) % len(pool)] for offset in range(3)]
        questions.append(
            {
                "id": f"lang_tech_{index:02d}",
                "skill": "Language techniques",
                "difficulty": "Extension",
                "prompt": f"Which technique is used here? '{quote}'",
                "choices": [technique, *distractors],
                "answer": technique,
                "solution": f"The line works as {technique}. {effect}",
            }
        )
        questions.append(
            {
                "id": f"lang_effect_{index:02d}",
                "skill": "Language techniques",
                "difficulty": "Advanced",
                "prompt": f"What is the main effect of this line? '{quote}'",
                "choices": [effect, *generic_effects],
                "answer": effect,
                "solution": f"The line uses {technique}, and its purpose is the effect described.",
            }
        )
    return questions


def build_extra_writing_prompts():
    prompts = [
        ("Analytical", "Explain how a writer builds a persuasive case without ever raising their voice. Refer to specific techniques.", ["clear thesis", "technique analysis", "embedded quotation", "effect on reader", "linked conclusion"]),
        ("Analytical", "How do writers use structure, rather than vocabulary, to control what a reader believes?", ["clear thesis", "structural evidence", "close analysis", "counter-example", "formal register"]),
        ("Analytical", "Discuss how setting can function as an argument rather than a backdrop.", ["clear thesis", "textual evidence", "precise metalanguage", "sustained analysis", "conclusion"]),
        ("Analytical", "Explain how an unreliable narrator changes the responsibilities of the reader.", ["clear thesis", "evidence of unreliability", "reader positioning", "evaluation", "conclusion"]),
        ("Argumentative", "Artificial intelligence should be permitted in schoolwork provided its use is declared. Argue for or against.", ["clear contention", "two developed arguments", "counterargument and rebuttal", "concrete example", "decisive conclusion"]),
        ("Argumentative", "Standardised testing measures preparation more than ability. Argue for or against.", ["clear contention", "evidence", "rebuttal", "qualified claims", "conclusion"]),
        ("Argumentative", "Local councils should prioritise long-term environmental works over short-term convenience. Argue your case.", ["clear contention", "cost-benefit reasoning", "rebuttal of the strongest objection", "specific example", "call to action"]),
        ("Argumentative", "Anonymous online comment sections do more harm than good. Argue for or against.", ["clear contention", "two arguments", "acknowledgement of the other side", "evidence", "conclusion"]),
        ("Argumentative", "Students should study fewer subjects in greater depth. Argue for or against.", ["clear contention", "developed reasoning", "rebuttal", "school-based example", "decisive conclusion"]),
        ("Comparative", "Compare how two texts you have read present power and those who lack it.", ["comparative thesis", "balanced treatment", "quotation from both texts", "evaluative judgement", "conclusion"]),
        ("Comparative", "Compare a news report and an opinion piece on the same issue. Which is more persuasive, and why?", ["comparative thesis", "identification of purpose", "technique comparison", "judgement", "conclusion"]),
        ("Comparative", "Compare how two writers use silence or omission to shape meaning.", ["comparative thesis", "close reading", "technique comparison", "evaluation", "conclusion"]),
        ("Discursive", "Can a statistic be accurate and still be misleading? Explore the question.", ["exploratory opening", "multiple perspectives", "worked example", "qualified reasoning", "reflective ending"]),
        ("Discursive", "Is it fair to judge people from the past by the standards of the present?", ["exploratory opening", "competing viewpoints", "historical example", "qualification", "reflective ending"]),
        ("Discursive", "When does confidence become overconfidence?", ["exploratory opening", "definitions", "contrasting examples", "nuanced reasoning", "reflective ending"]),
        ("Creative", "Write a narrative in which a character discovers that the version of an event they have told for years is not true.", ["controlled opening", "subtext", "sensory detail", "turning point", "restrained resolution"]),
        ("Creative", "Write a story in which the setting knows something the characters do not.", ["atmospheric opening", "sustained imagery", "tension", "revelation", "controlled ending"]),
        ("Creative", "Write a narrative that ends with the same sentence it begins with, but changed in meaning.", ["circular structure", "subtext", "character change", "precise detail", "resonant ending"]),
        ("Creative", "Write a story told entirely through what a character refuses to say.", ["distinctive voice", "implication", "dialogue control", "tension", "resolution"]),
        ("Persuasive speech", "Write a three-minute speech arguing that one school rule should change. Address the strongest objection directly.", ["direct address", "clear contention", "rebuttal", "rhetorical technique", "call to action"]),
        ("Persuasive speech", "Write a speech persuading your year level to take one specific action for the local environment.", ["hook", "contention", "evidence", "inclusive language", "call to action"]),
        ("Reflective", "Describe a time when you changed your mind about something you were certain of.", ["clear situation", "honest reflection", "specific detail", "insight", "controlled ending"]),
    ]
    return [{"type": kind, "prompt": prompt, "success": success} for kind, prompt, success in prompts]


MATH_QUESTIONS.extend(build_year8_math_questions())
MATH_QUESTIONS.extend(build_year9_math_questions())
MATH_QUESTIONS.extend(build_advanced_math_questions())
GRAMMAR_QUESTIONS.extend(build_year8_grammar_questions())
GRAMMAR_QUESTIONS.extend(build_year9_grammar_questions())
GRAMMAR_QUESTIONS.extend(build_language_analysis_questions())
WRITING_PROMPTS.extend(build_extra_writing_prompts())


def unique_choices(choices, answer):
    cleaned = []
    for choice in [*choices, answer]:
        if choice not in cleaned:
            cleaned.append(choice)
    fillers = ["No correction needed.", "Cannot be determined.", "Both versions are possible.", "None of these."]
    for filler in fillers:
        if len(cleaned) >= 4:
            break
        if filler not in cleaned and filler != answer:
            cleaned.append(filler)
    return cleaned[:4]


for question in MATH_QUESTIONS:
    question["choices"] = unique_choices(question["choices"], question["answer"])

READING_QUESTIONS = []
for task in READING_TASKS:
    for question in task["questions"]:
        question["title"] = task["title"]
        question["passage"] = task["passage"]
        question.setdefault("difficulty", "Extension")
        question["choices"] = unique_choices(question["choices"], question["answer"])
        READING_QUESTIONS.append(question)

for question in GRAMMAR_QUESTIONS:
    question["choices"] = unique_choices(question["choices"], question["answer"])


def all_mcq_questions():
    combined = []
    for question in MATH_QUESTIONS:
        item = dict(question)
        item["domain"] = "Maths"
        combined.append(item)
    for question in READING_QUESTIONS:
        item = dict(question)
        item["domain"] = "Reading"
        item["topic"] = question["skill"]
        combined.append(item)
    for question in GRAMMAR_QUESTIONS:
        item = dict(question)
        item["domain"] = "Grammar and vocabulary"
        item["topic"] = question["skill"]
        combined.append(item)
    return combined


QUESTION_LOOKUP = {question["id"]: question for question in all_mcq_questions()}
DIFFICULTY_ORDER = ["Challenge", "Extension", "Advanced"]
DIFFICULTY_LABELS = {
    "Challenge": "Challenge (Year 8)",
    "Extension": "Extension (Year 9)",
    "Advanced": "Advanced (beyond Year 9)",
}
ACTIVE_DIFFICULTIES = set(DIFFICULTY_ORDER)


def is_active_question(question):
    return question.get("difficulty") in ACTIVE_DIFFICULTIES


def active_mcq_questions():
    return [question for question in all_mcq_questions() if is_active_question(question)]


def css():
    st.markdown(
        """
        <style>
        :root {
            --navy: #16213e;
            --blue: #1e6f9f;
            --red: #c33f31;
            --gold: #f0b429;
            --paper: #fffaf1;
            --ink: #242938;
            --line: #d9e1ec;
        }
        .stApp { background: linear-gradient(180deg, #f7fbff 0%, #fffaf1 100%); color: var(--ink); }
        .block-container { padding-top: 1.4rem; max-width: 1180px; }
        .plc-hero {
            background: linear-gradient(135deg, var(--navy), var(--blue));
            color: white;
            padding: 24px 28px;
            border-radius: 8px;
            border-bottom: 6px solid var(--gold);
            box-shadow: 0 16px 40px rgba(22, 33, 62, 0.18);
        }
        .plc-hero h1 { margin: 0 0 8px; font-size: 2.2rem; }
        .plc-hero p { margin: 0; font-size: 1.03rem; opacity: 0.94; }
        .notice {
            background: #ffffff;
            border: 1px solid var(--line);
            border-left: 5px solid var(--red);
            padding: 14px 16px;
            border-radius: 8px;
            margin: 16px 0;
        }
        .skill-card {
            background: white;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
            min-height: 128px;
        }
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
            .plc-hero h1 { font-size: 1.65rem; }
            .block-container { padding: 0.8rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    defaults = {
        "plc_mock_ids": [],
        "plc_mock_orders": {},
        "plc_mock_submitted": False,
        "plc_mock_confirming": False,
        "plc_history": [],
        "plc_written_history": [],
        "plc_seen_ids": [],
        "plc_practice_ids": [],
        "plc_practice_orders": {},
        "plc_practice_submitted": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if not st.session_state["plc_mock_ids"]:
        new_mock()
    if not st.session_state["plc_practice_ids"]:
        new_practice("Maths", "All topics", "All difficulties", 8)


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
        st.session_state[seen_key] = list(dict.fromkeys(st.session_state.get(seen_key, []) + [q["id"] for q in selected]))
    return selected


def shuffle_orders(questions):
    return {question["id"]: random.sample(question["choices"], len(question["choices"])) for question in questions}


def new_mock():
    maths = choose_questions([question for question in MATH_QUESTIONS if is_active_question(question)], 10, "plc_seen_ids")
    reading = choose_questions([question for question in READING_QUESTIONS if is_active_question(question)], 6, "plc_seen_ids")
    grammar = choose_questions([question for question in GRAMMAR_QUESTIONS if is_active_question(question)], 6, "plc_seen_ids")
    selected = maths + reading + grammar
    random.shuffle(selected)
    st.session_state["plc_mock_ids"] = [question["id"] for question in selected]
    st.session_state["plc_mock_orders"] = shuffle_orders(selected)
    st.session_state["plc_mock_submitted"] = False
    st.session_state["plc_mock_confirming"] = False
    clear_answers("plc_answer_")


def new_practice(domain, topic, difficulty, count):
    pool = active_mcq_questions()
    if domain != "All":
        pool = [question for question in pool if question["domain"] == domain]
    if topic != "All topics":
        pool = [question for question in pool if question["topic"] == topic]
    if difficulty != "All difficulties":
        pool = [question for question in pool if question.get("difficulty") == difficulty]
    selected = choose_questions(pool, count, "plc_seen_ids")
    st.session_state["plc_practice_ids"] = [question["id"] for question in selected]
    st.session_state["plc_practice_orders"] = shuffle_orders(selected)
    st.session_state["plc_practice_submitted"] = False
    clear_answers("plc_practice_answer_")


def clear_answers(prefix):
    for question_id in QUESTION_LOOKUP:
        st.session_state.pop(f"{prefix}{question_id}", None)


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
    if percent >= 0.86:
        return "Above Year 9 standard: keep training speed, proof and multi-step accuracy."
    if percent >= 0.7:
        return "Solid Year 9 standard: practise the missed question families."
    if percent >= 0.55:
        return "Working at Year 8 standard: consolidate the Year 9 methods that are slipping."
    return "Method review needed: work through the worked solutions before retrying the topic."


def results_to_csv(results):
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["Question", "Domain", "Topic", "Difficulty", "Your answer", "Correct answer", "Result", "Worked solution"],
    )
    writer.writeheader()
    for index, result in enumerate(results, start=1):
        question = result["question"]
        writer.writerow(
            {
                "Question": index,
                "Domain": question["domain"],
                "Topic": question["topic"],
                "Difficulty": question.get("difficulty", ""),
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
    for item in st.session_state["plc_history"]:
        writer.writerow(item)
    return output.getvalue()


def writing_feedback(text, prompt_data):
    words = [word.strip(".,;:!?()[]\"'").lower() for word in text.split() if word.strip()]
    word_count = len(words)
    lower = text.lower()
    strong_words = {
        "therefore", "however", "although", "consequently", "significant", "effective", "evidence",
        "because", "clearly", "ultimately", "furthermore", "nevertheless", "conversely", "implies",
        "suggests", "positions", "emphasises", "undermines", "demonstrates", "arguably",
    }
    structure_terms = {"firstly", "secondly", "finally", "for example", "in conclusion", "on the other hand", "by contrast", "in addition"}
    score = 0
    criteria = []
    if word_count >= 250:
        score += 4
        criteria.append("Length and development: strong for Year 8-9")
    elif word_count >= 150:
        score += 3
        criteria.append("Length and development: sound, but push for more development")
    else:
        score += 1
        criteria.append("Length and development: too short for an analytical response")
    used_strong = sorted(strong_words.intersection(words))
    if len(used_strong) >= 4:
        score += 4
        criteria.append("Vocabulary: precise and persuasive")
    elif len(used_strong) >= 2:
        score += 3
        criteria.append("Vocabulary: developing")
    else:
        score += 1
        criteria.append("Vocabulary: add stronger academic words")
    structure_hits = [term for term in structure_terms if term in lower]
    if len(structure_hits) >= 3:
        score += 4
        criteria.append("Structure: clear sequence")
    elif len(structure_hits) >= 1:
        score += 2
        criteria.append("Structure: partly signposted")
    else:
        score += 1
        criteria.append("Structure: add signposting")
    if any(mark in text for mark in [".", "?", "!"]) and "," in text:
        score += 3
        criteria.append("Sentence control: varied punctuation")
    else:
        score += 1
        criteria.append("Sentence control: revise punctuation")
    missing = [item for item in prompt_data["success"] if item not in lower]
    return {
        "score": min(score, 15),
        "word_count": word_count,
        "criteria": criteria,
        "strong_words": used_strong,
        "missing": missing[:3],
    }


def render_mcq(question_ids, orders, prefix, submitted):
    grouped_passages = {}
    for question_id in question_ids:
        question = QUESTION_LOOKUP[question_id]
        if question["domain"] == "Reading":
            grouped_passages.setdefault(question["title"], question["passage"])

    for title, passage in grouped_passages.items():
        with st.expander(f"Reading passage: {title}", expanded=True):
            st.write(passage)

    for index, question_id in enumerate(question_ids, start=1):
        question = QUESTION_LOOKUP[question_id]
        with st.container(border=True):
            st.markdown(f"**Question {index}. {question['prompt']}**")
            level = question.get("difficulty", "")
            st.caption(f"{question['domain']} | {question['topic']} | {DIFFICULTY_LABELS.get(level, level)}")
            st.radio(
                "Choose one answer",
                orders.get(question_id, question["choices"]),
                index=None,
                key=f"{prefix}{question_id}",
                horizontal=True,
                disabled=submitted,
                label_visibility="collapsed",
            )
            if submitted:
                selected = st.session_state.get(f"{prefix}{question_id}")
                if selected == question["answer"]:
                    st.success("Correct.")
                else:
                    st.error(f"Correct answer: {question['answer']}")
                st.write(f"**Worked solution:** {question['solution']}")
                if question.get("trap"):
                    st.caption(f"Exam trap: {question['trap']}")


def record_results(mode, results):
    score = sum(1 for result in results if result["correct"])
    total = len(results)
    focus = Counter(result["question"]["topic"] for result in results if not result["correct"])
    st.session_state["plc_history"].append(
        {
            "Date": datetime.now().astimezone().isoformat(timespec="seconds"),
            "Mode": mode,
            "Score": score,
            "Total": total,
            "Accuracy": f"{round(score / total * 100)}%" if total else "0%",
            "Focus": ", ".join(topic for topic, _ in focus.most_common(3)) or "Maintain accuracy",
        }
    )


def render_header():
    st.markdown(
        """
        <div class="plc-hero">
            <h1>PLC Year 7 Level Test Prep &mdash; Extension Bank</h1>
            <p>Year 8 to Year 9 Victorian Curriculum material for a student who has already mastered the Year 7 placement content. Every Year 6&ndash;7 question has been retired.</p>
        </div>
        <div class="notice">
            This is independent preparation. It does not copy PLC or Studocu documents, and it is not affiliated with or endorsed by PLC.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mock_tab():
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Placement-style mock test")
        st.caption("Mixed maths, reading and grammar drawn from Year 8-9 material only. Answers begin blank, and submission asks for confirmation.")
    with right:
        st.button("New mock test", type="primary", width="stretch", on_click=new_mock)

    question_ids = st.session_state["plc_mock_ids"]
    render_mcq(question_ids, st.session_state["plc_mock_orders"], "plc_answer_", st.session_state["plc_mock_submitted"])

    unanswered = [qid for qid in question_ids if st.session_state.get(f"plc_answer_{qid}") is None]
    st.divider()
    if not st.session_state["plc_mock_submitted"]:
        if st.session_state["plc_mock_confirming"]:
            if unanswered:
                st.warning(f"{len(unanswered)} question(s) are unanswered. Submit anyway?")
            else:
                st.warning("Ready to submit and see the worked solutions?")
            c1, c2 = st.columns(2)
            if c1.button("Yes, submit mock test", type="primary", width="stretch"):
                results = mark(question_ids, "plc_answer_")
                record_results("Mock test", results)
                st.session_state["plc_mock_submitted"] = True
                st.session_state["plc_mock_confirming"] = False
                st.rerun()
            if c2.button("Keep working", width="stretch"):
                st.session_state["plc_mock_confirming"] = False
                st.rerun()
        else:
            if st.button("Submit mock test", type="primary", width="stretch"):
                st.session_state["plc_mock_confirming"] = True
                st.rerun()

    if st.session_state["plc_mock_submitted"]:
        results = mark(question_ids, "plc_answer_")
        render_results(results, "mock")


def render_practice_tab():
    st.subheader("Targeted skill practice")
    st.info(
        "Every Year 6-7 question has been removed. The bank now runs from Challenge (Year 8) through "
        "Extension (Year 9) to Advanced (beyond Year 9)."
    )

    st.markdown("**New Year 8 topics**")
    year8_buttons = st.columns(3)
    if year8_buttons[0].button("Indices", width="stretch"):
        new_practice("Maths", "Indices and scientific notation", "All difficulties", 12)
        st.rerun()
    if year8_buttons[1].button("Percentages and finance", width="stretch"):
        new_practice("Maths", "Percentages and finance", "All difficulties", 12)
        st.rerun()
    if year8_buttons[2].button("Measurement", width="stretch"):
        new_practice("Maths", "Measurement", "All difficulties", 12)
        st.rerun()

    st.markdown("**New Year 9 topics**")
    year9_buttons = st.columns(3)
    if year9_buttons[0].button("Linear graphs", type="primary", width="stretch"):
        new_practice("Maths", "Linear relationships", "All difficulties", 12)
        st.rerun()
    if year9_buttons[1].button("Trigonometry", type="primary", width="stretch"):
        new_practice("Maths", "Pythagoras and trigonometry", "All difficulties", 12)
        st.rerun()
    if year9_buttons[2].button("Simultaneous equations", type="primary", width="stretch"):
        new_practice("Maths", "Simultaneous equations", "All difficulties", 10)
        st.rerun()

    st.markdown("**English at Year 8-9 level**")
    english_buttons = st.columns(3)
    if english_buttons[0].button("Language techniques", width="stretch"):
        new_practice("Grammar and vocabulary", "Language techniques", "All difficulties", 12)
        st.rerun()
    if english_buttons[1].button("Clauses and modality", width="stretch"):
        new_practice("Grammar and vocabulary", "Clauses and sentence types", "All difficulties", 10)
        st.rerun()
    if english_buttons[2].button("Argument analysis", width="stretch"):
        new_practice("Reading", "Analysis of argument", "All difficulties", 6)
        st.rerun()

    st.markdown("**Hardest material only**")
    advanced_buttons = st.columns(3)
    if advanced_buttons[0].button("Advanced maths", width="stretch"):
        new_practice("Maths", "All topics", "Advanced", 12)
        st.rerun()
    if advanced_buttons[1].button("Advanced English", width="stretch"):
        new_practice("Grammar and vocabulary", "All topics", "Advanced", 12)
        st.rerun()
    if advanced_buttons[2].button("Advanced reading", width="stretch"):
        new_practice("Reading", "All topics", "Advanced", 10)
        st.rerun()

    st.divider()
    all_questions = active_mcq_questions()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        domain = st.selectbox("Area", ["All", "Maths", "Reading", "Grammar and vocabulary"], key="plc_domain")
    topic_pool = all_questions if domain == "All" else [q for q in all_questions if q["domain"] == domain]
    topic_options = ["All topics"] + sorted({question["topic"] for question in topic_pool})
    with c2:
        topic = st.selectbox("Topic", topic_options, key="plc_topic")
    difficulty_pool = topic_pool if topic == "All topics" else [q for q in topic_pool if q["topic"] == topic]
    available = {question.get("difficulty") for question in difficulty_pool}
    difficulty_options = ["All difficulties"] + [level for level in DIFFICULTY_ORDER if level in available]
    with c3:
        difficulty = st.selectbox(
            "Difficulty",
            difficulty_options,
            key="plc_difficulty",
            format_func=lambda level: DIFFICULTY_LABELS.get(level, level),
        )
    count_pool = difficulty_pool if difficulty == "All difficulties" else [q for q in difficulty_pool if q.get("difficulty") == difficulty]
    with c4:
        count = st.number_input("Questions", min_value=1, max_value=max(1, min(20, len(count_pool))), value=min(8, max(1, len(count_pool))), step=1)
    if st.button("Start skill practice", type="primary", width="stretch"):
        new_practice(domain, topic, difficulty, int(count))
        st.rerun()

    question_ids = st.session_state["plc_practice_ids"]
    render_mcq(question_ids, st.session_state["plc_practice_orders"], "plc_practice_answer_", st.session_state["plc_practice_submitted"])
    st.divider()
    if not st.session_state["plc_practice_submitted"]:
        if st.button("Submit practice answers", type="primary", width="stretch"):
            st.session_state["plc_practice_submitted"] = True
            results = mark(question_ids, "plc_practice_answer_")
            record_results("Skill practice", results)
            st.rerun()
    else:
        results = mark(question_ids, "plc_practice_answer_")
        render_results(results, "practice")


def render_results(results, key):
    score = sum(1 for result in results if result["correct"])
    total = len(results)
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{score}/{total}")
    c2.metric("Accuracy", f"{round(score / total * 100)}%" if total else "0%")
    c3.metric("Readiness", score_band(score, total).split(":")[0])
    st.info(score_band(score, total))
    topic_rows = []
    for topic, count in Counter(result["question"]["topic"] for result in results if not result["correct"]).most_common():
        topic_rows.append({"Focus area": topic, "Missed": count})
    if topic_rows:
        st.warning("Next practice focus: " + ", ".join(row["Focus area"] for row in topic_rows[:3]))
        st.dataframe(topic_rows, hide_index=True, width="stretch")
    rows = []
    for index, result in enumerate(results, start=1):
        question = result["question"]
        rows.append(
            {
                "Q": index,
                "Area": question["domain"],
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
        file_name=f"plc_year7_{key}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        width="stretch",
    )


def render_writing_tab():
    st.subheader("Writing practice")
    prompt_labels = [f"{item['type']}: {item['prompt']}" for item in WRITING_PROMPTS]
    selected_label = st.selectbox("Choose a writing task", prompt_labels)
    prompt_data = WRITING_PROMPTS[prompt_labels.index(selected_label)]
    st.info(prompt_data["prompt"])
    st.caption("Aim for 250-400 words. Year 8-9 responses need a clear thesis, embedded evidence, analysis of effect and a controlled formal register.")
    text = st.text_area("Rachel's response", height=280, placeholder="Write the response here...")
    if st.button("Submit writing for feedback", type="primary", width="stretch"):
        feedback = writing_feedback(text, prompt_data)
        st.session_state["plc_written_history"].append(
            {
                "Date": datetime.now().astimezone().isoformat(timespec="seconds"),
                "Prompt": prompt_data["prompt"],
                "Type": prompt_data["type"],
                "Score": feedback["score"],
                "Words": feedback["word_count"],
            }
        )
        st.session_state["plc_last_writing"] = {"text": text, "feedback": feedback, "prompt": prompt_data}
        st.rerun()
    if "plc_last_writing" in st.session_state:
        item = st.session_state["plc_last_writing"]
        feedback = item["feedback"]
        c1, c2 = st.columns(2)
        c1.metric("Estimated writing score", f"{feedback['score']}/15")
        c2.metric("Words", feedback["word_count"])
        for criterion in feedback["criteria"]:
            st.write(f"- {criterion}")
        if feedback["strong_words"]:
            st.success("Strong words used: " + ", ".join(feedback["strong_words"]))
        else:
            st.warning("Add stronger linking and analytical words such as however, therefore, significant, evidence and ultimately.")
        if feedback["missing"]:
            st.info("Next revision targets: " + ", ".join(feedback["missing"]))
        export_text = f"Prompt: {item['prompt']['prompt']}\n\nResponse:\n{item['text']}\n\nFeedback:\n{json.dumps(feedback, indent=2)}"
        st.download_button(
            "Export writing feedback (TXT)",
            data=export_text,
            file_name=f"plc_writing_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            width="stretch",
        )


def render_plan_tab():
    st.subheader("Preparation plan")
    st.caption("The Year 6-7 bank is retired. Everything below is Victorian Curriculum Year 8 to Year 9.")

    st.markdown("**Maths: what is new**")
    maths_rows = [
        {"Topic": "Indices and scientific notation", "Level": "Year 8-9", "Covers": "Index laws, zero and negative indices, standard form"},
        {"Topic": "Algebraic manipulation", "Level": "Year 8-9", "Covers": "Expanding, binomial products, difference of two squares, factorising"},
        {"Topic": "Linear equations", "Level": "Year 8-9", "Covers": "Brackets, variables both sides, equations with fractions"},
        {"Topic": "Linear relationships", "Level": "Year 9", "Covers": "Gradient, y-intercept, equation of a line, midpoint, distance"},
        {"Topic": "Simultaneous equations", "Level": "Year 9", "Covers": "Substitution and elimination, including scaling both equations"},
        {"Topic": "Pythagoras and trigonometry", "Level": "Year 9", "Covers": "Missing sides, missing angles, angle of elevation, 3D diagonals"},
        {"Topic": "Percentages and finance", "Level": "Year 8-9", "Covers": "Reverse percentages, successive change, simple and compound interest"},
        {"Topic": "Measurement", "Level": "Year 8-9", "Covers": "Circles, composite areas, surface area and volume of solids"},
        {"Topic": "Geometric reasoning", "Level": "Year 8-9", "Covers": "Parallel line angles with algebra, similarity and area scale factor"},
        {"Topic": "Statistics", "Level": "Year 9", "Covers": "Quartiles, interquartile range, effect of removing a value"},
        {"Topic": "Probability", "Level": "Year 8-9", "Covers": "Two-step events with and without replacement"},
        {"Topic": "Number theory and counting", "Level": "Beyond Year 9", "Covers": "Divisor counting, arrangements, pigeonhole, cyclic units digits"},
    ]
    st.dataframe(maths_rows, hide_index=True, width="stretch")

    st.markdown("**English: what is new**")
    english_rows = [
        {"Skill": "Analysis of argument", "Level": "Year 9", "Covers": "Contention, rebuttal by reversal, concession, evaluating evidence"},
        {"Skill": "Language techniques", "Level": "Year 8-9", "Covers": "Naming the technique and explaining its effect on the reader"},
        {"Skill": "Modality and nominalisation", "Level": "Year 8", "Covers": "High and low modality, turning processes into abstract nouns"},
        {"Skill": "Clauses and voice", "Level": "Year 8", "Covers": "Relative and subordinate clauses, active and passive voice"},
        {"Skill": "Punctuation", "Level": "Year 8-9", "Covers": "Semicolons, colons, dashes, non-defining clauses, possessives"},
        {"Skill": "Sentence craft", "Level": "Year 9", "Covers": "Parallel structure, dangling and misplaced modifiers"},
        {"Skill": "Register and connotation", "Level": "Year 9", "Covers": "Formal analytical register, shades of meaning between synonyms"},
        {"Skill": "Word origins", "Level": "Year 9", "Covers": "Greek and Latin roots used to unlock unfamiliar words"},
    ]
    st.dataframe(english_rows, hide_index=True, width="stretch")

    st.markdown("**Recommended sequence**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Step 1 &mdash; Year 8 core</strong>
            <p>Index laws, expanding and factorising, equations with brackets, reverse and successive percentages.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Step 2 &mdash; Year 9 core</strong>
            <p>Linear graphs and gradient, simultaneous equations, right-angle trigonometry, quartiles and the IQR.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Step 3 &mdash; Advanced</strong>
            <p>Surds, quadratic factorising, average speed, counting arguments and multi-step ratio problems.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write("Recommended weekly rhythm:")
    st.write("- 2 new-learning maths sessions following the three steps above, in order.")
    st.write("- 1 Advanced-only maths session once a topic feels secure at Extension level.")
    st.write("- 1 English session: a reading passage plus language techniques or clause work.")
    st.write("- 1 analytical or argumentative writing response each week, planned before it is written.")
    st.write("- 1 mixed mock test every weekend with every error corrected in full working.")


def render_record_tab():
    st.subheader("Practice record")
    if st.session_state["plc_history"]:
        st.dataframe(st.session_state["plc_history"], hide_index=True, width="stretch")
        st.download_button(
            "Export practice record (CSV)",
            data=history_to_csv(),
            file_name=f"plc_practice_record_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            width="stretch",
        )
    else:
        st.info("Submit a mock test or skill practice set to start the record.")
    if st.session_state["plc_written_history"]:
        st.subheader("Writing record")
        st.dataframe(st.session_state["plc_written_history"], hide_index=True, width="stretch")


def main():
    st.set_page_config(page_title="PLC Year 7 Level Test Prep", layout="wide")
    css()
    init_state()
    render_header()
    tabs = st.tabs(["Mock test", "Skill practice", "Writing", "Study plan", "Practice record"])
    with tabs[0]:
        render_mock_tab()
    with tabs[1]:
        render_practice_tab()
    with tabs[2]:
        render_writing_tab()
    with tabs[3]:
        render_plan_tab()
    with tabs[4]:
        render_record_tab()


if __name__ == "__main__":
    main()
