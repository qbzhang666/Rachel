import csv
import io
import json
import random
from collections import Counter
from datetime import datetime

import streamlit as st


MATH_QUESTIONS = [
    {
        "id": "m01",
        "topic": "Number reasoning",
        "difficulty": "Core",
        "prompt": "The sum of four consecutive whole numbers is 86. What is the largest number?",
        "choices": ["20", "21", "22", "23"],
        "answer": "23",
        "solution": "Four consecutive numbers have an average halfway between the middle two. 86 / 4 = 21.5, so the numbers are 20, 21, 22 and 23.",
        "trap": "A common trap is rounding the average to 22 and forgetting there are four numbers.",
    },
    {
        "id": "m02",
        "topic": "Number reasoning",
        "difficulty": "Core",
        "prompt": "A number leaves a remainder of 4 when divided by 7. Which of these could be the number?",
        "choices": ["53", "58", "61", "67"],
        "answer": "53",
        "solution": "53 = 7 x 7 + 4, so it leaves a remainder of 4.",
        "trap": "Do not choose a number just because it is near a multiple of 7. Check the exact remainder.",
    },
    {
        "id": "m03",
        "topic": "Number reasoning",
        "difficulty": "Challenge",
        "prompt": "The digits of a two-digit number add to 12. Reversing the digits makes a number 18 larger. What is the original number?",
        "choices": ["39", "48", "57", "75"],
        "answer": "57",
        "solution": "If reversing makes it larger, the ones digit is larger. The digit pair 5 and 7 adds to 12, and 75 - 57 = 18.",
        "trap": "The original number is the smaller one, not the reversed result.",
    },
    {
        "id": "m04",
        "topic": "Number reasoning",
        "difficulty": "Extension",
        "prompt": "How many positive divisors of 360 are multiples of 6?",
        "choices": ["12", "16", "18", "24"],
        "answer": "18",
        "solution": "A divisor of 360 that is a multiple of 6 can be written as 6 x k, where k is a divisor of 360 / 6 = 60. Since 60 = 2^2 x 3 x 5, it has (2 + 1)(1 + 1)(1 + 1) = 12 divisors.",
        "trap": "Divide by 6 first, then count divisors of 60.",
        "override_answer": "12",
    },
    {
        "id": "m05",
        "topic": "Fractions and ratios",
        "difficulty": "Core",
        "prompt": "A class has 30 students. Two-fifths are in the choir. How many are not in the choir?",
        "choices": ["10", "12", "18", "20"],
        "answer": "18",
        "solution": "Two-fifths of 30 is 12, so 30 - 12 = 18 students are not in the choir.",
        "trap": "The question asks for students not in the choir.",
    },
    {
        "id": "m06",
        "topic": "Fractions and ratios",
        "difficulty": "Challenge",
        "prompt": "The ratio of red to blue counters is 3:5. If there are 24 counters in total, how many are blue?",
        "choices": ["9", "12", "15", "18"],
        "answer": "15",
        "solution": "There are 8 equal parts in total. 24 / 8 = 3, so blue is 5 parts = 15.",
        "trap": "Use total parts, not just the blue part.",
    },
    {
        "id": "m07",
        "topic": "Fractions and ratios",
        "difficulty": "Challenge",
        "prompt": "A jacket is reduced by 20% to $96. What was the original price?",
        "choices": ["$112", "$115.20", "$120", "$128"],
        "answer": "$120",
        "solution": "After a 20% reduction, $96 is 80% of the original. Original price = 96 / 0.8 = $120.",
        "trap": "Do not subtract 20% from 96; 96 is already the reduced price.",
    },
    {
        "id": "m08",
        "topic": "Fractions and ratios",
        "difficulty": "Extension",
        "prompt": "A tin has black and white beads in the ratio 2:7. After 15 black beads are added, the ratio becomes 5:7. How many white beads are there?",
        "choices": ["21", "28", "35", "42"],
        "answer": "35",
        "solution": "White beads stay at 7 parts. Black increases from 2 parts to 5 parts, so 3 parts = 15. One part = 5, and white = 7 x 5 = 35.",
        "trap": "The added beads change only the black amount.",
    },
    {
        "id": "m09",
        "topic": "Algebra and patterns",
        "difficulty": "Core",
        "prompt": "If 4n - 7 = 29, what is n?",
        "choices": ["7", "8", "9", "10"],
        "answer": "9",
        "solution": "Add 7 to both sides: 4n = 36. Divide by 4: n = 9.",
        "trap": "Undo subtraction before division.",
    },
    {
        "id": "m10",
        "topic": "Algebra and patterns",
        "difficulty": "Challenge",
        "prompt": "A pattern starts 5, 9, 17, 33, ... Each term is double the previous term minus 1. What is the next term?",
        "choices": ["63", "64", "65", "67"],
        "answer": "65",
        "solution": "Double 33 to get 66, then subtract 1. The next term is 65.",
        "trap": "Do not continue by adding the previous difference.",
    },
    {
        "id": "m11",
        "topic": "Algebra and patterns",
        "difficulty": "Extension",
        "prompt": "The nth term of a sequence is 3n + 2. Which term is 47?",
        "choices": ["13th", "14th", "15th", "16th"],
        "answer": "15th",
        "solution": "Solve 3n + 2 = 47. Then 3n = 45 and n = 15.",
        "trap": "The question asks for the term number, not the term value.",
    },
    {
        "id": "m12",
        "topic": "Algebra and patterns",
        "difficulty": "Extension",
        "prompt": "A square pattern has 1 dot in the first figure, 4 in the second, 9 in the third and 16 in the fourth. How many dots are added to get from the 12th figure to the 13th?",
        "choices": ["23", "24", "25", "26"],
        "answer": "25",
        "solution": "The figures are square numbers. 13^2 - 12^2 = 169 - 144 = 25.",
        "trap": "Do not simply find the 13th figure; find the increase.",
    },
    {
        "id": "m13",
        "topic": "Geometry and measurement",
        "difficulty": "Core",
        "prompt": "A triangle has angles of 38 degrees and 76 degrees. What is the third angle?",
        "choices": ["56 degrees", "62 degrees", "66 degrees", "76 degrees"],
        "answer": "66 degrees",
        "solution": "Angles in a triangle add to 180 degrees. 180 - 38 - 76 = 66 degrees.",
        "trap": "Check both given angles before subtracting.",
    },
    {
        "id": "m14",
        "topic": "Geometry and measurement",
        "difficulty": "Challenge",
        "prompt": "A rectangle has perimeter 46 cm. Its length is 5 cm more than its width. What is its area?",
        "choices": ["102 square cm", "112 square cm", "126 square cm", "132 square cm"],
        "answer": "126 square cm",
        "solution": "Length + width = 23. If width is w, then length is w + 5. So 2w + 5 = 23, w = 9 and length = 14. Area = 14 x 9 = 126 square cm.",
        "trap": "The perimeter gives length + width after dividing by 2.",
    },
    {
        "id": "m15",
        "topic": "Geometry and measurement",
        "difficulty": "Challenge",
        "prompt": "A rectangle has perimeter 48 cm. Its length is 6 cm more than its width. What is its area?",
        "choices": ["108 square cm", "120 square cm", "135 square cm", "144 square cm"],
        "answer": "135 square cm",
        "solution": "Length + width = 24. If width is w, then length is w + 6. So 2w + 6 = 24, w = 9 and length = 15. Area = 15 x 9 = 135 square cm.",
        "trap": "The perimeter gives two lengths and two widths.",
    },
    {
        "id": "m16",
        "topic": "Geometry and measurement",
        "difficulty": "Extension",
        "prompt": "A 12 cm by 10 cm rectangle has a 4 cm by 3 cm rectangle cut from one corner. What is the remaining area?",
        "choices": ["96 square cm", "108 square cm", "112 square cm", "116 square cm"],
        "answer": "108 square cm",
        "solution": "The large rectangle area is 12 x 10 = 120. The cut-out area is 4 x 3 = 12. Remaining area = 108 square cm.",
        "trap": "The perimeter may change, but the area is found by subtraction.",
    },
    {
        "id": "m17",
        "topic": "Data and probability",
        "difficulty": "Core",
        "prompt": "Five numbers have a mean of 14. Four of them are 9, 12, 16 and 20. What is the fifth number?",
        "choices": ["11", "12", "13", "14"],
        "answer": "13",
        "solution": "The total must be 5 x 14 = 70. The known numbers add to 57, so the fifth number is 13.",
        "trap": "Find the required total first.",
    },
    {
        "id": "m18",
        "topic": "Data and probability",
        "difficulty": "Challenge",
        "prompt": "A bag has 4 green, 5 yellow and 3 purple counters. What is the probability of not choosing yellow?",
        "choices": ["5/12", "7/12", "1/2", "3/4"],
        "answer": "7/12",
        "solution": "There are 12 counters. Not yellow means green or purple, which is 4 + 3 = 7 counters. Probability = 7/12.",
        "trap": "The question asks for not yellow.",
    },
    {
        "id": "m19",
        "topic": "Data and probability",
        "difficulty": "Extension",
        "prompt": "How many different two-letter codes can be made from A, B, C, D and E if the two letters must be different?",
        "choices": ["10", "20", "25", "30"],
        "answer": "20",
        "solution": "There are 5 choices for the first letter and 4 remaining choices for the second, so 5 x 4 = 20.",
        "trap": "AB and BA are different codes because order matters.",
    },
    {
        "id": "m20",
        "topic": "Logic and problem solving",
        "difficulty": "Challenge",
        "prompt": "Three friends have different pets: a dog, a cat and a rabbit. Ava does not have the cat. Bea does not have the dog or rabbit. Which pet does Ava have?",
        "choices": ["Dog", "Cat", "Rabbit", "Cannot be determined"],
        "answer": "Dog",
        "solution": "Bea cannot have dog or rabbit, so Bea has the cat. Ava does not have the cat, leaving dog or rabbit. This alone is not enough unless the third friend has rabbit. So the safe answer is Cannot be determined.",
        "trap": "Do not assume missing information.",
        "override_answer": "Cannot be determined",
    },
    {
        "id": "m21",
        "topic": "Logic and problem solving",
        "difficulty": "Extension",
        "prompt": "Ten students sit around a circular table. Each student shakes hands with the two students sitting directly beside them. How many handshakes occur?",
        "choices": ["10", "18", "20", "45"],
        "answer": "10",
        "solution": "Each neighbour pair shakes once. Around a circle of 10 students there are 10 neighbouring pairs.",
        "trap": "Do not count each handshake twice.",
    },
    {
        "id": "m22",
        "topic": "Logic and problem solving",
        "difficulty": "Extension",
        "prompt": "A path from one corner of a 3 by 4 grid to the opposite corner uses only moves right or down. How many shortest paths are possible?",
        "choices": ["12", "20", "35", "60"],
        "answer": "35",
        "solution": "A shortest path needs 3 down moves and 4 right moves, 7 moves total. Choose the positions of the 3 down moves: 7 choose 3 = 35.",
        "trap": "The grid dimensions refer to squares, so there are 3 down and 4 right moves.",
    },
]


READING_TASKS = [
    {
        "title": "The Empty Courtyard",
        "passage": "When the bell rang, the courtyard emptied almost at once. Rachel stayed behind, not because she had forgotten her next class, but because she had noticed the new student still studying the map near the library steps. The girl turned the paper twice, pretending not to be lost. Rachel remembered her own first week, when every building seemed to have a secret name. She walked over and said, 'The science rooms are this way.' The girl smiled with relief.",
        "questions": [
            {
                "id": "r01",
                "skill": "Inference",
                "prompt": "Why does Rachel stay behind?",
                "choices": ["She has forgotten her class.", "She wants to help someone.", "She is waiting for the library.", "She dislikes science."],
                "answer": "She wants to help someone.",
                "solution": "Rachel notices the new student is lost and offers help.",
            },
            {
                "id": "r02",
                "skill": "Vocabulary in context",
                "prompt": "What does 'with relief' suggest about the new student?",
                "choices": ["She is still angry.", "She feels less worried.", "She is embarrassed by Rachel.", "She wants to be alone."],
                "answer": "She feels less worried.",
                "solution": "Relief means a worry or pressure has been reduced.",
            },
            {
                "id": "r03",
                "skill": "Author purpose",
                "prompt": "The passage mainly presents Rachel as",
                "choices": ["careful and kind", "careless and loud", "competitive and proud", "confused and impatient"],
                "answer": "careful and kind",
                "solution": "Rachel observes carefully and helps without making the new student feel awkward.",
            },
        ],
    },
    {
        "title": "A Different Kind of Test",
        "passage": "The mathematics test did not begin with difficult numbers. It began with ordinary ones arranged in unfamiliar ways. Several students rushed through the first page, smiling at how simple it looked. Mira paused. The question did not ask for the answer to the calculation; it asked which calculation could not be correct. She underlined the word 'not' twice. By the end, the students who had slowed down were the ones with time to check.",
        "questions": [
            {
                "id": "r04",
                "skill": "Main idea",
                "prompt": "What is the main message of the passage?",
                "choices": ["Fast students always win.", "Careful reading matters.", "Maths tests only use hard numbers.", "Checking wastes time."],
                "answer": "Careful reading matters.",
                "solution": "The key contrast is between rushing and noticing the word 'not'.",
            },
            {
                "id": "r05",
                "skill": "Inference",
                "prompt": "Why does Mira underline 'not' twice?",
                "choices": ["She is decorating the page.", "She has made a spelling mistake.", "She wants to avoid misreading the question.", "She has finished early."],
                "answer": "She wants to avoid misreading the question.",
                "solution": "The word changes what the question is asking.",
            },
            {
                "id": "r06",
                "skill": "Tone",
                "prompt": "The tone of the passage is best described as",
                "choices": ["thoughtful", "furious", "comic", "hopeless"],
                "answer": "thoughtful",
                "solution": "The passage calmly reflects on good test habits.",
            },
        ],
    },
    {
        "title": "The Debate Team",
        "passage": "At first, the debate team wanted the most confident speaker to give every argument. Their coach refused. 'A strong team is not a solo performance,' she said. Over the next month, each student became responsible for a different part: evidence, rebuttal, timing and summary. On competition day, their voices sounded different, but their ideas joined neatly. They did not win every round, yet they improved in every round.",
        "questions": [
            {
                "id": "r07",
                "skill": "Theme",
                "prompt": "Which theme best fits the passage?",
                "choices": ["Teamwork can be stronger than individual talent.", "Winning is the only sign of success.", "Speaking loudly is most important.", "Coaches should not give advice."],
                "answer": "Teamwork can be stronger than individual talent.",
                "solution": "The coach teaches them to share roles and improve as a team.",
            },
            {
                "id": "r08",
                "skill": "Text evidence",
                "prompt": "Which detail best supports the idea that the team became organised?",
                "choices": ["They wanted one confident speaker.", "Each student became responsible for a different part.", "They did not win every round.", "The coach refused."],
                "answer": "Each student became responsible for a different part.",
                "solution": "This detail shows clear roles and structure.",
            },
            {
                "id": "r09",
                "skill": "Inference",
                "prompt": "What does 'their ideas joined neatly' suggest?",
                "choices": ["Their arguments connected well.", "They all spoke at the same time.", "They copied each other's words.", "They avoided giving evidence."],
                "answer": "Their arguments connected well.",
                "solution": "The phrase means their different parts fitted together.",
            },
        ],
    },
    {
        "title": "The Rain Garden",
        "passage": "The new garden beside the oval looked messy in its first week. There were stones, shallow dips and plants that seemed too small to matter. By winter, however, students noticed that water no longer spread across the footpath after heavy rain. The dips collected the water, the stones slowed it, and the plants held the soil in place. What had looked unfinished was, in fact, carefully designed.",
        "questions": [
            {
                "id": "r10",
                "skill": "Cause and effect",
                "prompt": "Why did water stop spreading across the footpath?",
                "choices": ["The rain stopped completely.", "The garden collected and slowed the water.", "Students moved the water by hand.", "The oval became smaller."],
                "answer": "The garden collected and slowed the water.",
                "solution": "The dips, stones and plants work together to manage water.",
            },
            {
                "id": "r11",
                "skill": "Vocabulary in context",
                "prompt": "In the passage, 'designed' means",
                "choices": ["planned for a purpose", "painted brightly", "left alone", "damaged by rain"],
                "answer": "planned for a purpose",
                "solution": "The garden's features were arranged to solve a water problem.",
            },
            {
                "id": "r12",
                "skill": "Inference",
                "prompt": "What lesson does the passage suggest?",
                "choices": ["First impressions can be misleading.", "Gardens should never use stones.", "Rain is always harmful.", "Small plants are useless."],
                "answer": "First impressions can be misleading.",
                "solution": "The garden first looked messy but later proved carefully planned.",
            },
        ],
    },
]


GRAMMAR_QUESTIONS = [
    {
        "id": "g01",
        "skill": "Punctuation",
        "difficulty": "Core",
        "prompt": "Choose the correctly punctuated sentence.",
        "choices": ["Although it was raining, the team continued training.", "Although, it was raining the team continued training.", "Although it was raining the team, continued training.", "Although it was raining the team continued, training."],
        "answer": "Although it was raining, the team continued training.",
        "solution": "A comma separates the opening dependent clause from the main clause.",
    },
    {
        "id": "g02",
        "skill": "Apostrophes",
        "difficulty": "Core",
        "prompt": "Which sentence uses apostrophes correctly?",
        "choices": ["The students' lockers were repainted.", "The student's lockers were repainted.", "The students locker were repainted.", "The students's lockers were repainted."],
        "answer": "The students' lockers were repainted.",
        "solution": "Students' shows the lockers belong to more than one student.",
    },
    {
        "id": "g03",
        "skill": "Sentence structure",
        "difficulty": "Challenge",
        "prompt": "Which option best combines these ideas? The library was quiet. The students worked carefully.",
        "choices": ["The library was quiet, and the students worked carefully.", "The library was quiet the students worked carefully.", "Quiet library, students careful.", "The students carefully because the library."],
        "answer": "The library was quiet, and the students worked carefully.",
        "solution": "The comma plus conjunction joins two complete ideas correctly.",
    },
    {
        "id": "g04",
        "skill": "Vocabulary",
        "difficulty": "Challenge",
        "prompt": "Which word is closest in meaning to 'meticulous'?",
        "choices": ["careful", "careless", "rapid", "ordinary"],
        "answer": "careful",
        "solution": "Meticulous means very careful and precise.",
    },
    {
        "id": "g05",
        "skill": "Vocabulary",
        "difficulty": "Extension",
        "prompt": "Which word best completes the sentence? Her explanation was so _____ that even a complex idea seemed clear.",
        "choices": ["lucid", "vague", "reluctant", "fragile"],
        "answer": "lucid",
        "solution": "Lucid means clear and easy to understand.",
    },
    {
        "id": "g06",
        "skill": "Inference language",
        "difficulty": "Extension",
        "prompt": "Which sentence shows the strongest analytical expression?",
        "choices": ["This suggests that the character values belonging more than popularity.", "The character is good and nice.", "I liked the character because she was interesting.", "This quote is in the story."],
        "answer": "This suggests that the character values belonging more than popularity.",
        "solution": "It uses precise inference and explains meaning.",
    },
    {
        "id": "g07",
        "skill": "Subject-verb agreement",
        "difficulty": "Core",
        "prompt": "Choose the correct sentence.",
        "choices": ["The group of musicians is rehearsing.", "The group of musicians are rehearsing.", "The group of musicians were rehearse.", "The group of musicians have rehearsing."],
        "answer": "The group of musicians is rehearsing.",
        "solution": "The subject is group, which is singular.",
    },
    {
        "id": "g08",
        "skill": "Pronouns",
        "difficulty": "Core",
        "prompt": "Choose the correct pronoun.",
        "choices": ["Maya and I presented the project.", "Maya and me presented the project.", "Me and Maya presented the project.", "I and Maya presented the project."],
        "answer": "Maya and I presented the project.",
        "solution": "Use I when the pronoun is part of the subject.",
    },
    {
        "id": "g09",
        "skill": "Vocabulary",
        "difficulty": "Challenge",
        "prompt": "Which word is closest in meaning to 'resilient'?",
        "choices": ["able to recover", "easily broken", "very noisy", "quickly forgotten"],
        "answer": "able to recover",
        "solution": "Resilient means able to recover after difficulty.",
    },
    {
        "id": "g10",
        "skill": "Editing",
        "difficulty": "Extension",
        "prompt": "Which sentence is the most concise?",
        "choices": ["The experiment failed because the instructions were unclear.", "Due to the fact that the instructions were unclear, the experiment was not successful.", "The experiment was something that did not succeed because of unclear instructions.", "There was a failure in the experiment in relation to the instructions."],
        "answer": "The experiment failed because the instructions were unclear.",
        "solution": "It gives the same meaning with fewer, clearer words.",
    },
]


WRITING_PROMPTS = [
    {
        "type": "Persuasive",
        "prompt": "Schools should give students more choice in what they read. Do you agree?",
        "success": ["clear position", "two developed reasons", "specific school example", "counterargument", "strong conclusion"],
    },
    {
        "type": "Persuasive",
        "prompt": "Homework should focus on reading and problem solving rather than worksheets. Do you agree?",
        "success": ["clear position", "balanced reasoning", "evidence or example", "persuasive vocabulary", "final recommendation"],
    },
    {
        "type": "Creative",
        "prompt": "Write about a student who discovers that a small mistake has unexpectedly helped someone.",
        "success": ["controlled opening", "character emotion", "specific detail", "turning point", "satisfying ending"],
    },
    {
        "type": "Creative",
        "prompt": "Write a story beginning with: The map was correct, but the building was not where it should have been.",
        "success": ["intriguing setting", "tension", "sensory detail", "clear problem", "resolution"],
    },
    {
        "type": "Analytical",
        "prompt": "Explain how a writer can show that a character is nervous without directly saying it.",
        "success": ["clear topic sentence", "examples", "precise vocabulary", "effect on reader", "linked conclusion"],
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


def build_extra_math_questions():
    questions = []
    for variant in range(1, 9):
        difficulty = "Core" if variant <= 2 else "Challenge" if variant <= 5 else "Extension"

        start = 14 + variant
        count = 3 + (variant % 3)
        total = count * start + count * (count - 1) // 2
        largest = start + count - 1
        questions.append(
            {
                "id": f"mx_num_consecutive_{variant}",
                "topic": "Number reasoning",
                "difficulty": difficulty,
                "prompt": f"The sum of {count} consecutive whole numbers is {total}. What is the largest number?",
                "choices": number_choices(largest, [start, largest - 1, largest + count]),
                "answer": str(largest),
                "solution": f"The numbers start at {start} and run for {count} terms, so they are {', '.join(str(start + i) for i in range(count))}. The largest is {largest}.",
                "trap": "Use the average to locate the middle, then check the whole set.",
            }
        )

        divisor = 6 + variant
        quotient = 8 + 2 * variant
        remainder = variant % divisor
        value = divisor * quotient + remainder
        questions.append(
            {
                "id": f"mx_num_remainder_{variant}",
                "topic": "Number reasoning",
                "difficulty": difficulty,
                "prompt": f"What is the remainder when {value} is divided by {divisor}?",
                "choices": number_choices(remainder, [remainder + 1, divisor - remainder, divisor - 1]),
                "answer": str(remainder),
                "solution": f"{divisor} x {quotient} = {divisor * quotient}. The difference between {value} and {divisor * quotient} is {remainder}.",
                "trap": "The remainder must be smaller than the divisor.",
            }
        )

        base = 7 + variant
        exponent = 12 + variant
        units = pow(base, exponent, 10)
        questions.append(
            {
                "id": f"mx_num_units_{variant}",
                "topic": "Number reasoning",
                "difficulty": "Extension",
                "prompt": f"What is the units digit of {base}^{exponent}?",
                "choices": number_choices(units, [(units + 2) % 10, (units + 4) % 10, (units + 6) % 10]),
                "answer": str(units),
                "solution": f"Only the units digit matters. Powers of {base % 10} repeat in a cycle, and the {exponent}th power has units digit {units}.",
                "trap": "Look for the units-digit cycle instead of trying to calculate the whole power.",
            }
        )

        total_students = 36 + 4 * variant
        numerator = 2 + variant % 3
        denominator = 6
        selected = total_students * numerator // denominator
        if total_students * numerator % denominator:
            total_students += denominator - (total_students * numerator % denominator)
            selected = total_students * numerator // denominator
        not_selected = total_students - selected
        questions.append(
            {
                "id": f"mx_frac_remaining_{variant}",
                "topic": "Fractions and ratios",
                "difficulty": difficulty,
                "prompt": f"In a group of {total_students} students, {numerator}/6 join a workshop. How many do not join?",
                "choices": number_choices(not_selected, [selected, not_selected - 2, not_selected + 3]),
                "answer": str(not_selected),
                "solution": f"{numerator}/6 of {total_students} is {selected}. The number who do not join is {total_students} - {selected} = {not_selected}.",
                "trap": "The question asks for the students who do not join.",
            }
        )

        ratio_a = 2 + variant % 4
        ratio_b = ratio_a + 3
        part = 4 + variant
        total = (ratio_a + ratio_b) * part
        b_amount = ratio_b * part
        questions.append(
            {
                "id": f"mx_frac_ratio_{variant}",
                "topic": "Fractions and ratios",
                "difficulty": difficulty,
                "prompt": f"The ratio of novels to information books is {ratio_a}:{ratio_b}. If there are {total} books altogether, how many are information books?",
                "choices": number_choices(b_amount, [ratio_a * part, total - b_amount, b_amount + part]),
                "answer": str(b_amount),
                "solution": f"There are {ratio_a + ratio_b} parts. Each part is {total} / {ratio_a + ratio_b} = {part}. Information books are {ratio_b} parts, so {ratio_b} x {part} = {b_amount}.",
                "trap": "Use the total number of ratio parts first.",
            }
        )

        original = 100 + 20 * variant
        discount = 10 + 5 * (variant % 5)
        sale = original * (100 - discount) // 100
        questions.append(
            {
                "id": f"mx_frac_percent_{variant}",
                "topic": "Fractions and ratios",
                "difficulty": "Challenge" if variant <= 5 else "Extension",
                "prompt": f"An item costing ${original} is reduced by {discount}%. What is the sale price?",
                "choices": money_choices(sale, [original - discount, original + discount, original * discount // 100]),
                "answer": f"${sale:g}",
                "solution": f"{discount}% of ${original} is ${original * discount // 100}. The sale price is ${original} - ${original * discount // 100} = ${sale}.",
                "trap": "The discount amount is not the final price.",
            }
        )

        coefficient = 3 + variant
        answer = 5 + variant
        constant = 7 + 2 * variant
        right = coefficient * answer + constant
        questions.append(
            {
                "id": f"mx_alg_linear_{variant}",
                "topic": "Algebra and patterns",
                "difficulty": difficulty,
                "prompt": f"If {coefficient}x + {constant} = {right}, what is x?",
                "choices": number_choices(answer, [answer - 2, answer + 2, coefficient + answer]),
                "answer": str(answer),
                "solution": f"Subtract {constant}: {coefficient}x = {right - constant}. Divide by {coefficient}: x = {answer}.",
                "trap": "Undo the addition before undoing the multiplication.",
            }
        )

        first = 4 + variant
        step = 3 + variant % 4
        term_no = 10 + variant
        term = first + (term_no - 1) * step
        questions.append(
            {
                "id": f"mx_alg_nth_{variant}",
                "topic": "Algebra and patterns",
                "difficulty": "Challenge",
                "prompt": f"A sequence starts {first}, {first + step}, {first + 2 * step}, ... Which term is {term}?",
                "choices": [f"{item}th" for item in number_choices(term_no, [term_no - 1, term_no + 1, term_no + 2])],
                "answer": f"{term_no}th",
                "solution": f"The nth term is {first} + (n - 1) x {step}. Solve {first} + (n - 1) x {step} = {term}, so n = {term_no}.",
                "trap": "The answer is the term number, not the term value.",
            }
        )

        n = 6 + variant
        added = 2 * n + 1
        questions.append(
            {
                "id": f"mx_alg_squaregrowth_{variant}",
                "topic": "Algebra and patterns",
                "difficulty": "Extension",
                "prompt": f"A square-dot pattern has n^2 dots in figure n. How many dots are added from figure {n} to figure {n + 1}?",
                "choices": number_choices(added, [2 * n, n + 1, (n + 1) ** 2]),
                "answer": str(added),
                "solution": f"Figure {n + 1} has {(n + 1) ** 2} dots and figure {n} has {n ** 2}. The increase is {(n + 1) ** 2} - {n ** 2} = {added}.",
                "trap": "Find the increase, not the total in the next figure.",
            }
        )

        angle_a = 35 + 3 * variant
        angle_b = 75 - variant
        third = 180 - angle_a - angle_b
        questions.append(
            {
                "id": f"mx_geo_triangle_{variant}",
                "topic": "Geometry and measurement",
                "difficulty": difficulty,
                "prompt": f"A triangle has angles of {angle_a} degrees and {angle_b} degrees. What is the third angle?",
                "choices": number_choices(third, [180 - angle_a, 180 - angle_b, third + 10], " degrees"),
                "answer": f"{third} degrees",
                "solution": f"Angles in a triangle add to 180 degrees. 180 - {angle_a} - {angle_b} = {third} degrees.",
                "trap": "Subtract both known angles.",
            }
        )

        width = 6 + variant
        length = width + 4 + variant % 3
        perimeter = 2 * (width + length)
        area = width * length
        questions.append(
            {
                "id": f"mx_geo_rectangle_{variant}",
                "topic": "Geometry and measurement",
                "difficulty": "Challenge",
                "prompt": f"A rectangle has perimeter {perimeter} cm and width {width} cm. What is its area?",
                "choices": number_choices(area, [perimeter * width, area + width, area - length], " square cm"),
                "answer": f"{area} square cm",
                "solution": f"Length + width = {perimeter // 2}. The length is {perimeter // 2} - {width} = {length}. Area = {length} x {width} = {area} square cm.",
                "trap": "Half the perimeter is length plus width.",
            }
        )

        outer = 12 + variant
        inner = outer - 4
        frame = outer * outer - inner * inner
        questions.append(
            {
                "id": f"mx_geo_frame_{variant}",
                "topic": "Geometry and measurement",
                "difficulty": "Extension",
                "prompt": f"A square frame has outside side length {outer} cm and a square hole of side length {inner} cm. What is the area of the frame?",
                "choices": number_choices(frame, [outer * inner, frame - 8, frame + 8], " square cm"),
                "answer": f"{frame} square cm",
                "solution": f"Subtract the inner square from the outer square: {outer}^2 - {inner}^2 = {outer * outer} - {inner * inner} = {frame}.",
                "trap": "Use area subtraction, not perimeter.",
            }
        )

        known = [8 + variant, 11 + variant, 14 + 2 * variant, 17 + variant]
        mean = 15 + variant
        missing = 5 * mean - sum(known)
        questions.append(
            {
                "id": f"mx_data_mean_{variant}",
                "topic": "Data and probability",
                "difficulty": difficulty,
                "prompt": f"Five numbers have a mean of {mean}. Four numbers are {known[0]}, {known[1]}, {known[2]} and {known[3]}. What is the fifth number?",
                "choices": number_choices(missing, [mean, missing - 2, missing + 3]),
                "answer": str(missing),
                "solution": f"The total must be 5 x {mean} = {5 * mean}. The four known numbers total {sum(known)}, so the missing number is {missing}.",
                "trap": "Mean questions often become total questions.",
            }
        )

        red = 3 + variant
        blue = 5 + variant
        total_counters = red + blue
        numerator = blue
        questions.append(
            {
                "id": f"mx_data_probability_{variant}",
                "topic": "Data and probability",
                "difficulty": "Challenge",
                "prompt": f"A bag contains {red} red counters and {blue} blue counters. One counter is chosen. What is the probability it is blue?",
                "choices": [f"{item}/{total_counters}" for item in number_choices(numerator, [red, numerator - 1, numerator + 1])],
                "answer": f"{numerator}/{total_counters}",
                "solution": f"There are {total_counters} counters in total and {blue} are blue, so the probability is {blue}/{total_counters}.",
                "trap": "Use the total number of counters as the denominator.",
            }
        )

        letters = 4 + variant % 4
        codes = letters * (letters - 1)
        questions.append(
            {
                "id": f"mx_data_codes_{variant}",
                "topic": "Data and probability",
                "difficulty": "Extension",
                "prompt": f"How many different two-letter codes can be made from {letters} different letters if the two letters must be different?",
                "choices": number_choices(codes, [letters * letters, codes // 2, codes + letters]),
                "answer": str(codes),
                "solution": f"There are {letters} choices for the first letter and {letters - 1} for the second, giving {letters} x {letters - 1} = {codes}.",
                "trap": "Order matters in a code.",
            }
        )

        boxes = 5 + variant
        guarantee = boxes + 1
        questions.append(
            {
                "id": f"mx_logic_guarantee_{variant}",
                "topic": "Logic and problem solving",
                "difficulty": "Challenge",
                "prompt": f"What is the smallest number of pencils needed to guarantee that at least two pencils are in the same one of {boxes} pencil cases?",
                "choices": number_choices(guarantee, [boxes, boxes + 2, 2 * boxes]),
                "answer": str(guarantee),
                "solution": f"You can put one pencil in each of the {boxes} cases without a pair. The next pencil guarantees a repeated case, so {boxes + 1} pencils are needed.",
                "trap": "Guarantee questions ask for the worst case before success is forced.",
            }
        )

        people = 6 + variant
        handshakes = people * (people - 1) // 2
        questions.append(
            {
                "id": f"mx_logic_pairs_{variant}",
                "topic": "Logic and problem solving",
                "difficulty": "Extension",
                "prompt": f"Each of {people} students sends one message to every other student. How many messages are sent if each pair sends only one message between them?",
                "choices": number_choices(handshakes, [people * (people - 1), handshakes - people, handshakes + people]),
                "answer": str(handshakes),
                "solution": f"This counts pairs of students: {people} x {people - 1} / 2 = {handshakes}.",
                "trap": "Each pair is counted once, not twice.",
            }
        )

        right_moves = 3 + variant % 4
        down_moves = 2 + variant % 3
        total_paths = 1
        for i in range(1, min(right_moves, down_moves) + 1):
            total_paths = total_paths * (max(right_moves, down_moves) + i) // i
        questions.append(
            {
                "id": f"mx_logic_paths_{variant}",
                "topic": "Logic and problem solving",
                "difficulty": "Extension",
                "prompt": f"A shortest grid path uses {right_moves} moves right and {down_moves} moves down. How many different shortest paths are possible?",
                "choices": number_choices(total_paths, [right_moves * down_moves, total_paths - 1, total_paths + right_moves]),
                "answer": str(total_paths),
                "solution": f"There are {right_moves + down_moves} moves. Choose the positions of the {min(right_moves, down_moves)} less frequent moves, giving {total_paths} paths.",
                "trap": "Arrange the moves rather than drawing every path.",
            }
        )

    return questions


def build_extra_reading_tasks():
    scenarios = [
        ("The Silent Bell", "Amelia", "the rehearsal room", "the clock above the piano had stopped", "composed", "calm and in control"),
        ("A Note in the Margin", "Nora", "the library", "someone had written a helpful question beside a difficult paragraph", "perceptive", "noticing details quickly"),
        ("The Long Way Around", "Sienna", "the sports field", "the usual gate was locked after the storm", "resourceful", "able to find practical solutions"),
        ("The Unfinished Poster", "Lily", "the art room", "the missing heading changed the meaning of the poster", "ambiguous", "able to mean more than one thing"),
        ("The Second Attempt", "Grace", "the science lab", "the first model collapsed just before judging", "resilient", "able to recover after difficulty"),
        ("The Borrowed Compass", "Maya", "the maths classroom", "a classmate returned the compass with a quiet apology", "contrite", "sorry for a mistake"),
        ("The Garden Roster", "Zoe", "the vegetable beds", "the smallest seedlings needed the most careful watering", "delicate", "easily damaged"),
        ("The Lost Timetable", "Chloe", "the front office", "the printed timetable had two rooms for the same lesson", "inconsistent", "not matching properly"),
        ("The Debate Folder", "Isla", "the debating room", "the strongest evidence was hidden behind old notes", "compelling", "powerful and convincing"),
        ("The Wet Shoes", "Ella", "the bus stop", "the shortest route crossed a flooded path", "prudent", "careful and sensible"),
        ("The Music Stand", "Ruby", "the auditorium", "one loose screw made the stand lean during practice", "precarious", "not steady or secure"),
        ("The Paper Crane", "Hannah", "the common room", "a folded crane marked every completed chapter", "methodical", "organised and systematic"),
        ("The Blue Ribbon", "Ava", "the athletics track", "the winner gave her ribbon to the injured reserve", "generous", "willing to give or share"),
        ("The Locked Cabinet", "Mila", "the science storeroom", "the key label had faded in the sunlight", "faint", "hard to see clearly"),
        ("The New Route", "Lucy", "the tram stop", "the replacement bus arrived before the announcement finished", "unexpected", "not planned or predicted"),
        ("The Shared Desk", "Emily", "the study hall", "two students had prepared different notes on the same topic", "collaborative", "working together"),
        ("The Missing Line", "Sophie", "the drama room", "the script made no sense until a page was turned over", "crucial", "extremely important"),
        ("The Quiet Captain", "Aria", "the netball court", "the captain listened before changing the play", "considerate", "thinking about others"),
        ("The Trial Run", "Violet", "the technology room", "the prototype worked only when the wires were reversed", "experimental", "based on testing"),
        ("The Lunch Bell", "Olivia", "the canteen", "the queue moved faster after one student organised the orders", "efficient", "working without waste"),
        ("The Ink Spill", "Charlotte", "the English room", "the spilled ink revealed an old note beneath the worksheet", "curious", "wanting to know more"),
        ("The Weather Chart", "Matilda", "the geography room", "the trend was clearer when the class used a graph", "evident", "easy to see"),
        ("The Empty Seat", "Harper", "the assembly hall", "the spare seat let a nervous visitor sit beside a friend", "reassuring", "making someone less worried"),
        ("The Broken Zipper", "Abigail", "the cloakroom", "a safety pin solved the problem before the excursion", "improvised", "made or done without preparation"),
        ("The Practice Timer", "Eva", "the music room", "shorter timed drills improved the ensemble's focus", "disciplined", "controlled and well organised"),
        ("The Old Photograph", "Scarlett", "the archives", "the photograph showed the school garden before the new path existed", "historical", "connected with the past"),
        ("The Misdirected Email", "Phoebe", "the computer lab", "the mistaken email alerted the club to a room change", "accidental", "happening by chance"),
        ("The Chess Clock", "Stella", "the games room", "rushing early moves left less time for careful thinking", "strategic", "planned to achieve a goal"),
        ("The Painted Line", "Alice", "the courtyard", "the new line guided visitors away from the construction area", "visible", "easy to see"),
        ("The Final Draft", "Georgia", "the English office", "removing one weak paragraph made the whole argument stronger", "concise", "short and clear"),
        ("The Library Ladder", "Clara", "the shelves", "the book she needed was not high but simply hidden behind another", "misleading", "giving the wrong idea"),
        ("The Warm-up Lap", "Madison", "the oval", "the coach asked for a slower lap to prevent injuries", "preventive", "designed to stop a problem"),
    ]
    tasks = []
    for index, (title, student, place, discovery, vocab, meaning) in enumerate(scenarios, start=1):
        passage = (
            f"{student} paused in {place} because {discovery}. At first, the problem seemed minor, "
            f"but it changed what the class needed to do next. Instead of guessing, {student} checked the details, "
            f"asked one careful question and adjusted the plan. The solution was not dramatic, yet it saved time and helped others feel prepared. "
            f"Her teacher later described the response as {vocab}."
        )
        tasks.append(
            {
                "title": title,
                "passage": passage,
                "questions": [
                    {
                        "id": f"rx{index:02d}a",
                        "skill": "Inference",
                        "prompt": f"Why does {student} pause?",
                        "choices": [
                            f"She notices that {discovery}.",
                            "She wants to avoid helping the class.",
                            "She has forgotten where she is going.",
                            "She is trying to make the problem worse.",
                        ],
                        "answer": f"She notices that {discovery}.",
                        "solution": "The opening sentence gives the reason for the pause.",
                    },
                    {
                        "id": f"rx{index:02d}b",
                        "skill": "Vocabulary in context",
                        "prompt": f"In the passage, '{vocab}' most nearly means",
                        "choices": [meaning, "careless and rushed", "ordinary and unimportant", "confused by every detail"],
                        "answer": meaning,
                        "solution": f"The word '{vocab}' describes the quality of the student's helpful response.",
                    },
                    {
                        "id": f"rx{index:02d}c",
                        "skill": "Text evidence",
                        "prompt": "Which detail best shows careful problem solving?",
                        "choices": [
                            "She checked the details and asked one careful question.",
                            "The problem seemed minor at first.",
                            "The solution was not dramatic.",
                            "Her teacher later described the response.",
                        ],
                        "answer": "She checked the details and asked one careful question.",
                        "solution": "This detail shows the method she used to solve the problem.",
                    },
                ],
            }
        )
    return tasks


def build_extra_grammar_questions():
    questions = []
    vocab_items = [
        ("meticulous", "very careful", "careless", "ordinary", "brief"),
        ("resilient", "able to recover", "easily defeated", "silent", "uncertain"),
        ("lucid", "clear", "hidden", "weak", "angry"),
        ("tentative", "not yet certain", "completely final", "very loud", "badly damaged"),
        ("concise", "short and clear", "needlessly long", "confused", "unfair"),
        ("significant", "important", "tiny", "accidental", "distant"),
        ("reluctant", "unwilling", "excited", "careless", "certain"),
        ("plausible", "believable", "impossible", "colourful", "silent"),
        ("assertive", "confident", "timid", "hidden", "late"),
        ("innovative", "new and original", "old-fashioned", "ordinary", "unclear"),
        ("fragile", "easily broken", "very strong", "carefully planned", "bright"),
        ("coherent", "logical and connected", "messy", "angry", "unfinished"),
        ("evaluate", "judge the value of", "copy exactly", "hide from view", "speak loudly"),
        ("infer", "work out from clues", "repeat word for word", "decorate", "measure"),
        ("justify", "give reasons for", "guess quickly", "avoid explaining", "make shorter"),
        ("contrast", "show differences", "make identical", "list randomly", "remove detail"),
        ("emphasise", "give importance to", "ignore", "shorten", "misplace"),
        ("precise", "exact", "vague", "heavy", "ordinary"),
        ("subtle", "not obvious", "extremely loud", "simple to count", "broken"),
        ("credible", "trustworthy", "unlikely", "colourless", "silent"),
    ]
    for index, (word, answer, *distractors) in enumerate(vocab_items, start=1):
        questions.append(
            {
                "id": f"gx_vocab_{index:02d}",
                "skill": "Vocabulary",
                "difficulty": "Challenge" if index <= 10 else "Extension",
                "prompt": f"Which meaning is closest to '{word}'?",
                "choices": [answer, *distractors],
                "answer": answer,
                "solution": f"'{word}' means {answer}.",
            }
        )

    punctuation_items = [
        ("Although the room was noisy, Mia finished her paragraph.", "Although the room was noisy Mia, finished her paragraph.", "Although, the room was noisy Mia finished her paragraph.", "Although the room was noisy Mia finished, her paragraph."),
        ("After the bell rang, the students packed their bags.", "After the bell rang the students, packed their bags.", "After, the bell rang the students packed their bags.", "After the bell, rang the students packed their bags."),
        ("Because the evidence was strong, the argument was convincing.", "Because the evidence was strong the argument, was convincing.", "Because, the evidence was strong the argument was convincing.", "Because the evidence, was strong the argument was convincing."),
        ("When the experiment ended, the class recorded its results.", "When the experiment ended the class, recorded its results.", "When, the experiment ended the class recorded its results.", "When the experiment, ended the class recorded its results."),
        ("If the question includes the word not, read it twice.", "If the question includes the word not read, it twice.", "If, the question includes the word not read it twice.", "If the question, includes the word not read it twice."),
        ("Before choosing an answer, check the units.", "Before choosing an answer check, the units.", "Before, choosing an answer check the units.", "Before choosing, an answer check the units."),
        ("While the team waited, the captain checked the notes.", "While the team waited the captain, checked the notes.", "While, the team waited the captain checked the notes.", "While the team, waited the captain checked the notes."),
        ("Since the path was flooded, we used the side gate.", "Since the path was flooded we, used the side gate.", "Since, the path was flooded we used the side gate.", "Since the path, was flooded we used the side gate."),
        ("The library was quiet, and the students worked carefully.", "The library was quiet and, the students worked carefully.", "The library was quiet and the students worked carefully.", "The library, was quiet and the students worked carefully."),
        ("The question looked simple, but it required careful reasoning.", "The question looked simple but, it required careful reasoning.", "The question looked simple but it required careful reasoning.", "The question, looked simple but it required careful reasoning."),
    ]
    for index, item in enumerate(punctuation_items, start=1):
        questions.append(
            {
                "id": f"gx_punct_{index:02d}",
                "skill": "Punctuation",
                "difficulty": "Core" if index <= 5 else "Challenge",
                "prompt": "Choose the correctly punctuated sentence.",
                "choices": list(item),
                "answer": item[0],
                "solution": "The correct sentence places commas where they separate clauses or joined ideas.",
            }
        )

    apostrophe_nouns = [("students", "lockers"), ("teachers", "meeting"), ("girls", "team"), ("writers", "drafts"), ("players", "uniforms"), ("children", "books"), ("school", "library"), ("Rachel", "notebook")]
    for index, (owner, object_name) in enumerate(apostrophe_nouns, start=1):
        if owner.endswith("s"):
            answer = f"The {owner}' {object_name} were ready."
            wrong = [f"The {owner}'s {object_name} were ready.", f"The {owner} {object_name} were ready.", f"The {owner}s' {object_name} were ready."]
        elif owner == "children":
            answer = f"The children's {object_name} were ready."
            wrong = [f"The childrens' {object_name} were ready.", f"The children {object_name} were ready.", f"The childrens {object_name} were ready."]
        else:
            answer = f"{owner}'s {object_name} was ready."
            wrong = [f"{owner}s' {object_name} was ready.", f"{owner} {object_name} was ready.", f"{owner}' {object_name} was ready."]
        questions.append(
            {
                "id": f"gx_apos_{index:02d}",
                "skill": "Apostrophes",
                "difficulty": "Core",
                "prompt": "Choose the sentence with the correct apostrophe use.",
                "choices": [answer, *wrong],
                "answer": answer,
                "solution": "Use apostrophes to show ownership, paying attention to singular and plural owners.",
            }
        )

    agreement_items = [
        ("The group of students is ready.", "group", "singular"),
        ("Neither the captain nor the players are late.", "players", "plural and closest to the verb"),
        ("Each of the answers is possible.", "Each", "singular"),
        ("The list of topics was helpful.", "list", "singular"),
        ("The boxes near the door are heavy.", "boxes", "plural"),
        ("Either the notes or the folder is missing.", "folder", "singular and closest to the verb"),
        ("The team of swimmers trains daily.", "team", "singular"),
        ("Several of the questions require diagrams.", "Several", "plural"),
        ("The collection of poems belongs on the shelf.", "collection", "singular"),
        ("Both of the examples support the claim.", "Both", "plural"),
    ]
    for index, (answer, subject, rule) in enumerate(agreement_items, start=1):
        questions.append(
            {
                "id": f"gx_agree_{index:02d}",
                "skill": "Subject-verb agreement",
                "difficulty": "Core" if index <= 5 else "Challenge",
                "prompt": "Choose the sentence with correct subject-verb agreement.",
                "choices": [
                    answer,
                    answer.replace(" is ", " are ").replace(" was ", " were ").replace(" trains ", " train ").replace(" belongs ", " belong ").replace(" require ", " requires ").replace(" support ", " supports "),
                    answer.replace(" are ", " is ").replace(" were ", " was ").replace(" train ", " trains ").replace(" belong ", " belongs "),
                    answer.replace(".", " yesterday."),
                ],
                "answer": answer,
                "solution": f"The subject is {subject}, which is {rule}.",
            }
        )

    concise_items = [
        ("The argument is convincing because the evidence is specific.", "Due to the fact that the evidence is specific, the argument can be seen as convincing."),
        ("The experiment failed because the instructions were unclear.", "The experiment was not successful due to the fact that the instructions were unclear."),
        ("Rachel revised the paragraph to make the idea clearer.", "Rachel made a revision of the paragraph for the purpose of making the idea clearer."),
        ("The graph shows a steady increase.", "The graph is able to show that there is an increase which is steady."),
        ("The character changes after the mistake.", "The character goes through a process of change after the mistake happens."),
        ("The conclusion links back to the question.", "The conclusion is something that makes a link back to the question."),
        ("The example supports the main point.", "The example is included for the purpose of giving support to the main point."),
        ("The sentence is vague and needs detail.", "The sentence has a vague quality and is in need of additional detail."),
        ("The team improved after practising regularly.", "The team became better as a result of the fact that it practised regularly."),
        ("The setting creates tension.", "The setting is something that creates a feeling of tension."),
    ]
    for index, (answer, wordy) in enumerate(concise_items, start=1):
        questions.append(
            {
                "id": f"gx_edit_{index:02d}",
                "skill": "Editing",
                "difficulty": "Challenge" if index <= 5 else "Extension",
                "prompt": "Which sentence is the most concise?",
                "choices": [answer, wordy, "There is a thing that makes the writing somewhat good.", "The idea is kind of there in a way."],
                "answer": answer,
                "solution": "Concise writing keeps the meaning while removing unnecessary words.",
            }
        )

    analytical_items = [
        "This suggests that the character values honesty more than popularity.",
        "The contrast reveals how pressure changes the narrator's choices.",
        "The image of the empty room emphasises the character's isolation.",
        "The writer positions the reader to admire the student's persistence.",
        "This detail foreshadows the later mistake.",
        "The dialogue shows tension without directly explaining it.",
        "The repeated phrase highlights the importance of belonging.",
        "The setting creates uncertainty before the problem is revealed.",
        "The evidence strengthens the argument by making the claim specific.",
        "The conclusion returns to the central idea and gives it impact.",
    ]
    for index, answer in enumerate(analytical_items, start=1):
        questions.append(
            {
                "id": f"gx_analysis_{index:02d}",
                "skill": "Inference language",
                "difficulty": "Extension",
                "prompt": "Which sentence uses the strongest analytical expression?",
                "choices": [answer, "This quote is in the text.", "I think the character is nice.", "The author wrote some words about this."],
                "answer": answer,
                "solution": "Strong analysis explains meaning, technique or effect rather than just giving an opinion.",
            }
        )

    connectors = [
        ("however", "The first method is fast; however, the second method is more accurate."),
        ("therefore", "The evidence is specific; therefore, the claim is more convincing."),
        ("although", "Although the task looked simple, it required careful reasoning."),
        ("consequently", "The team ignored the instructions; consequently, the model collapsed."),
        ("for example", "Specific evidence improves an argument; for example, statistics can make a claim more precise."),
        ("in contrast", "The first paragraph is descriptive; in contrast, the second paragraph is analytical."),
    ]
    for index, (connector, answer) in enumerate(connectors, start=1):
        questions.append(
            {
                "id": f"gx_connect_{index:02d}",
                "skill": "Sentence structure",
                "difficulty": "Challenge",
                "prompt": f"Which sentence uses '{connector}' correctly?",
                "choices": [answer, f"{connector.title()} the sentence no clear connection.", f"The idea {connector} because.", f"{connector}, and also but the reason."],
                "answer": answer,
                "solution": f"'{connector}' must connect ideas logically and grammatically.",
            }
        )

    pronoun_items = [
        ("Sofia and I organised the display.", "Use I as part of the subject."),
        ("The teacher gave the certificate to Mia and me.", "Use me as part of the object."),
        ("Whom did you invite to the practice debate?", "Use whom for the object of the verb."),
        ("Who will present the final paragraph?", "Use who for the subject of the verb."),
        ("The students completed their reflections.", "Their shows ownership by students."),
        ("It is important to check its battery before the test.", "Its is possessive; it's means it is."),
    ]
    for index, (answer, explanation) in enumerate(pronoun_items, start=1):
        questions.append(
            {
                "id": f"gx_pronoun_{index:02d}",
                "skill": "Pronouns",
                "difficulty": "Core" if index <= 2 else "Challenge",
                "prompt": "Choose the sentence with correct pronoun use.",
                "choices": [answer, answer.replace(" I ", " me ").replace(" me.", " I."), answer.replace("Who", "Whom").replace("Whom", "Who"), answer.replace("their", "there").replace("Its", "It's")],
                "answer": answer,
                "solution": explanation,
            }
        )

    return questions


def build_final_grammar_questions():
    questions = []
    word_choice_items = [
        ("accept", "I accept your explanation because it is supported by evidence.", "except", "Accept means receive or agree; except means excluding."),
        ("effect", "The new timetable had a positive effect on study habits.", "affect", "Effect is usually a noun meaning result."),
        ("affect", "Lack of sleep can affect concentration.", "effect", "Affect is usually a verb meaning influence."),
        ("practice", "Daily reading practice improves vocabulary.", "practise", "In Australian English, practice is the noun."),
        ("practise", "Students should practise explaining their reasoning.", "practice", "In Australian English, practise is the verb."),
        ("advice", "Her advice helped me revise the paragraph.", "advise", "Advice is the noun; advise is the verb."),
        ("advise", "The teacher will advise the team before the debate.", "advice", "Advise is the verb."),
        ("principal", "The principal spoke at assembly.", "principle", "Principal can mean the head of a school."),
        ("principle", "Fairness is an important principle.", "principal", "Principle means a rule or belief."),
        ("stationary", "The bus was stationary for ten minutes.", "stationery", "Stationary means not moving."),
        ("stationery", "Rachel packed her stationery before the test.", "stationary", "Stationery means writing materials."),
        ("complement", "The diagram should complement the explanation.", "compliment", "Complement means complete or go well with."),
        ("compliment", "The coach gave the team a sincere compliment.", "complement", "Compliment means praise."),
        ("weather", "The weather changed before sport.", "whether", "Weather refers to conditions such as rain or wind."),
        ("whether", "Check whether the answer uses the correct unit.", "weather", "Whether introduces a choice or possibility."),
        ("therefore", "The evidence is reliable; therefore, the claim is stronger.", "however", "Therefore shows a result."),
        ("however", "The method was quick; however, it was not accurate.", "therefore", "However shows contrast."),
        ("fewer", "There were fewer errors in the second draft.", "less", "Use fewer for countable things."),
        ("less", "The second route took less time.", "fewer", "Use less for an amount that is not counted individually."),
        ("between", "The choice was between two possible answers.", "among", "Use between for two clearly separate items."),
    ]
    for index, (answer_word, sentence, wrong_word, explanation) in enumerate(word_choice_items, start=1):
        wrong_sentence = sentence.replace(answer_word, wrong_word, 1)
        questions.append(
            {
                "id": f"gy_wordchoice_{index:02d}",
                "skill": "Word choice",
                "difficulty": "Challenge" if index <= 12 else "Extension",
                "prompt": "Choose the sentence with the correct word choice.",
                "choices": [
                    sentence,
                    wrong_sentence,
                    sentence.replace(".", " because."),
                    wrong_sentence.replace(".", " clearly."),
                ],
                "answer": sentence,
                "solution": explanation,
            }
        )

    spelling_items = [
        ("necessary", "It is necessary to check each answer.", "neccessary", "necesary", "nessessary"),
        ("separate", "Keep separate notes for maths and English.", "seperate", "seprate", "separete"),
        ("definitely", "Rachel definitely improved after reviewing mistakes.", "definately", "definatly", "definetely"),
        ("environment", "The learning environment was calm.", "enviroment", "enviornment", "envirenment"),
        ("argument", "A persuasive argument needs evidence.", "arguement", "argment", "arguemant"),
        ("rhythm", "The paragraph had a clear rhythm.", "rythm", "rhythym", "rhythem"),
        ("receive", "Students receive feedback after submission.", "recieve", "receve", "receieve"),
        ("believe", "I believe the second reason is stronger.", "beleive", "belive", "believee"),
        ("achieve", "A plan helps students achieve their goals.", "acheive", "achive", "achievee"),
        ("curiosity", "Curiosity can make a story engaging.", "curiousity", "curiosty", "curiocity"),
    ]
    for index, (word, sentence, *wrong_spellings) in enumerate(spelling_items, start=1):
        questions.append(
            {
                "id": f"gy_spelling_{index:02d}",
                "skill": "Spelling",
                "difficulty": "Core" if index <= 4 else "Challenge",
                "prompt": "Choose the sentence with the correct spelling.",
                "choices": [sentence, *[sentence.replace(word, wrong, 1) for wrong in wrong_spellings]],
                "answer": sentence,
                "solution": f"The correct spelling is '{word}'.",
            }
        )

    sentence_function_items = [
        ("Although the task was difficult, Rachel stayed calm.", "complex sentence", "It has a dependent clause joined to a main clause."),
        ("Rachel planned carefully, and she checked her answer.", "compound sentence", "It joins two complete ideas with a conjunction."),
        ("Because the evidence was precise, the paragraph became more convincing.", "complex sentence", "The because-clause depends on the main clause."),
        ("The answer seemed obvious, but the wording changed the meaning.", "compound sentence", "Two complete ideas are joined by but."),
        ("After reviewing the graph, Mia changed her conclusion.", "complex sentence", "The opening phrase depends on the main clause for full meaning."),
        ("The team practised regularly, so their timing improved.", "compound sentence", "The conjunction so links two complete ideas."),
        ("If the unit is missing, the answer may be incomplete.", "complex sentence", "The if-clause sets a condition for the main clause."),
        ("The library was quiet, yet the students still whispered.", "compound sentence", "Yet joins two complete contrasting ideas."),
        ("When the bell rang, the class packed up.", "complex sentence", "The when-clause gives time and depends on the main clause."),
        ("The claim is clear, and the evidence is specific.", "compound sentence", "Two complete ideas are joined by and."),
    ]
    for index, (sentence, answer, explanation) in enumerate(sentence_function_items, start=1):
        questions.append(
            {
                "id": f"gy_sentence_{index:02d}",
                "skill": "Sentence structure",
                "difficulty": "Extension" if index > 5 else "Challenge",
                "prompt": f"What type of sentence is this? {sentence}",
                "choices": [answer, "fragment", "run-on sentence", "simple sentence"],
                "answer": answer,
                "solution": explanation,
            }
        )

    return questions


def build_extra_writing_prompts():
    prompts = [
        ("Persuasive", "Students should learn financial skills before Year 7. Do you agree?", ["clear position", "real-life example", "two reasons", "counterargument", "strong conclusion"]),
        ("Persuasive", "School libraries are more important than ever. Do you agree?", ["clear position", "evidence", "specific school example", "persuasive vocabulary", "final recommendation"]),
        ("Persuasive", "Every student should take part in a team activity. Do you agree?", ["clear position", "balanced reasoning", "example", "counterargument", "call to action"]),
        ("Persuasive", "Tests should reward careful thinking more than speed. Do you agree?", ["clear position", "comparison", "evidence", "precise vocabulary", "conclusion"]),
        ("Persuasive", "Year 7 students should be taught how to use AI responsibly. Do you agree?", ["clear position", "ethical reason", "school example", "counterargument", "recommendation"]),
        ("Persuasive", "Outdoor learning should be included in every school week. Do you agree?", ["clear position", "health reason", "learning reason", "example", "conclusion"]),
        ("Persuasive", "Students should have one device-free lesson each day. Do you agree?", ["clear position", "focus reason", "wellbeing reason", "counterargument", "strong conclusion"]),
        ("Persuasive", "Schools should teach debating to all students. Do you agree?", ["clear position", "communication reason", "confidence reason", "example", "final judgement"]),
        ("Persuasive", "Homework should be shorter but more challenging. Do you agree?", ["clear position", "quality over quantity", "example", "counterargument", "recommendation"]),
        ("Persuasive", "Reading fiction helps students become better thinkers. Do you agree?", ["clear position", "reasoning", "text example", "persuasive vocabulary", "conclusion"]),
        ("Persuasive", "School canteens should focus on healthy food even if it costs more. Do you agree?", ["clear position", "health reason", "fairness issue", "counterargument", "recommendation"]),
        ("Persuasive", "Students should learn public speaking from primary school. Do you agree?", ["clear position", "confidence reason", "future reason", "example", "strong ending"]),
        ("Creative", "Write about a student who finds a message hidden inside an old textbook.", ["controlled opening", "sensory detail", "tension", "turning point", "resolution"]),
        ("Creative", "Write a story beginning with: The bell rang, but nobody moved.", ["intriguing opening", "character reaction", "specific setting", "problem", "ending"]),
        ("Creative", "Write about a competition where the most important victory is not winning.", ["character motivation", "conflict", "emotion", "turning point", "reflection"]),
        ("Creative", "Write about a map that leads to an unexpected place at school.", ["setting", "mystery", "precise detail", "rising tension", "resolution"]),
        ("Creative", "Write about a student who must apologise before the end of the day.", ["character flaw", "inner conflict", "dialogue", "change", "ending"]),
        ("Creative", "Write about the moment a quiet student surprises everyone.", ["controlled opening", "character contrast", "build-up", "specific action", "reflection"]),
        ("Creative", "Write about a storm that changes the plan for an important day.", ["weather detail", "problem", "adaptation", "emotion", "ending"]),
        ("Creative", "Write about a lost object that reveals something important.", ["object detail", "mystery", "character choice", "turning point", "resolution"]),
        ("Creative", "Write about two students who solve a problem in completely different ways.", ["character contrast", "dialogue", "problem", "cooperation", "ending"]),
        ("Creative", "Write about a door at school that is usually locked but is open today.", ["atmosphere", "curiosity", "tension", "discovery", "resolution"]),
        ("Creative", "Write about a rehearsal that goes wrong before a performance.", ["setting", "mistake", "emotion", "solution", "ending"]),
        ("Creative", "Write about a student who receives the wrong timetable.", ["clear problem", "school setting", "pace", "character reaction", "resolution"]),
        ("Analytical", "Explain how a writer can make a setting feel tense.", ["topic sentence", "technique examples", "precise vocabulary", "reader effect", "linked conclusion"]),
        ("Analytical", "Explain how dialogue can reveal a character's personality.", ["topic sentence", "examples", "inference", "effect", "conclusion"]),
        ("Analytical", "Explain how a writer can show courage without using the word courage.", ["topic sentence", "behaviour examples", "show not tell", "reader effect", "conclusion"]),
        ("Analytical", "Explain why specific evidence makes a persuasive argument stronger.", ["topic sentence", "example", "reasoning", "effect on reader", "conclusion"]),
        ("Analytical", "Explain how contrast can make a story more interesting.", ["topic sentence", "contrast example", "effect", "precise vocabulary", "linked ending"]),
        ("Analytical", "Explain how a conclusion can strengthen a persuasive response.", ["topic sentence", "summary", "final judgement", "reader effect", "conclusion"]),
        ("Analytical", "Explain how a writer can create sympathy for a character.", ["topic sentence", "character detail", "inference", "reader effect", "conclusion"]),
        ("Analytical", "Explain why planning improves writing under exam conditions.", ["topic sentence", "reason one", "reason two", "example", "conclusion"]),
        ("Analytical", "Explain how word choice can change the tone of a paragraph.", ["topic sentence", "word examples", "tone", "effect", "conclusion"]),
        ("Analytical", "Explain how a writer can make an ordinary event seem important.", ["topic sentence", "detail", "structure", "reader effect", "conclusion"]),
        ("Reflective", "Describe a time when careful preparation made a difficult task easier.", ["clear event", "personal reflection", "specific detail", "lesson", "controlled ending"]),
    ]
    return [{"type": kind, "prompt": prompt, "success": success} for kind, prompt, success in prompts]


def build_learning_sequence_math_questions():
    questions = []
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (9, 40, 41), (12, 35, 37)]

    for variant in range(1, 7):
        difficulty = "Core" if variant <= 2 else "Challenge" if variant <= 4 else "Extension"

        addend = 5 + variant
        answer = 8 + variant
        right_side = answer + addend
        questions.append(
            {
                "id": f"learn_linear_one_{variant}",
                "topic": "Linear equations",
                "difficulty": "Core",
                "prompt": f"Solve x + {addend} = {right_side}.",
                "choices": number_choices(answer, [answer - 2, answer + 2, right_side]),
                "answer": str(answer),
                "solution": f"Subtract {addend} from both sides: x = {right_side} - {addend} = {answer}.",
                "trap": "Whatever you do to one side of an equation, do to the other side.",
            }
        )

        coefficient = 3 + variant
        constant = 4 + 2 * variant
        answer = 5 + variant
        right_side = coefficient * answer + constant
        questions.append(
            {
                "id": f"learn_linear_two_{variant}",
                "topic": "Linear equations",
                "difficulty": difficulty,
                "prompt": f"Solve {coefficient}x + {constant} = {right_side}.",
                "choices": number_choices(answer, [answer - 1, answer + 2, coefficient + answer]),
                "answer": str(answer),
                "solution": f"Subtract {constant}: {coefficient}x = {right_side - constant}. Divide by {coefficient}: x = {answer}.",
                "trap": "Undo addition or subtraction before multiplication or division.",
            }
        )

        left_coefficient = 5 + variant
        right_coefficient = 2 + variant
        answer = 4 + variant
        left_constant = 7 + variant
        right_constant = (left_coefficient - right_coefficient) * answer + left_constant
        questions.append(
            {
                "id": f"learn_linear_both_{variant}",
                "topic": "Linear equations",
                "difficulty": "Challenge" if variant <= 3 else "Extension",
                "prompt": f"Solve {left_coefficient}x + {left_constant} = {right_coefficient}x + {right_constant}.",
                "choices": number_choices(answer, [answer - 2, answer + 1, right_constant - left_constant]),
                "answer": str(answer),
                "solution": f"Move the x terms to one side: {left_coefficient - right_coefficient}x + {left_constant} = {right_constant}. Then {left_coefficient - right_coefficient}x = {right_constant - left_constant}, so x = {answer}.",
                "trap": "Collect variables on one side and numbers on the other.",
            }
        )

        groups = 3 + variant
        extra = 6 + variant
        total = groups * answer + extra
        questions.append(
            {
                "id": f"learn_linear_word_{variant}",
                "topic": "Linear equations",
                "difficulty": "Challenge" if variant <= 3 else "Extension",
                "prompt": f"Rachel thinks of a number. {groups} times the number plus {extra} is {total}. What is the number?",
                "choices": number_choices(answer, [answer - 2, answer + 2, total // groups]),
                "answer": str(answer),
                "solution": f"Let the number be x. The equation is {groups}x + {extra} = {total}. Subtract {extra}, then divide by {groups}: x = {answer}.",
                "trap": "Translate the words into an equation before calculating.",
            }
        )

        first = 9 + 2 * variant
        total = first + first + 1 + first + 2
        questions.append(
            {
                "id": f"learn_consecutive_int_{variant}",
                "topic": "Consecutive-number algebra",
                "difficulty": difficulty,
                "prompt": f"The sum of three consecutive integers is {total}. What is the largest integer?",
                "choices": number_choices(first + 2, [first, first + 1, first + 3]),
                "answer": str(first + 2),
                "solution": f"Let the integers be n, n + 1 and n + 2. Then 3n + 3 = {total}, so n = {first}. The largest is {first + 2}.",
                "trap": "Represent consecutive integers as n, n + 1 and n + 2.",
            }
        )

        first_odd = 7 + 2 * variant
        if first_odd % 2 == 0:
            first_odd += 1
        total = first_odd + first_odd + 2 + first_odd + 4
        questions.append(
            {
                "id": f"learn_consecutive_odd_{variant}",
                "topic": "Consecutive-number algebra",
                "difficulty": "Challenge" if variant <= 3 else "Extension",
                "prompt": f"The sum of three consecutive odd numbers is {total}. What is the smallest number?",
                "choices": number_choices(first_odd, [first_odd + 2, first_odd + 4, first_odd - 2]),
                "answer": str(first_odd),
                "solution": f"Let the odd numbers be n, n + 2 and n + 4. Then 3n + 6 = {total}, so 3n = {total - 6} and n = {first_odd}.",
                "trap": "Consecutive odd numbers increase by 2, not by 1.",
            }
        )

        a, b, c = triples[variant - 1]
        scale = 1 + variant % 3
        short_a = a * scale
        short_b = b * scale
        hyp = c * scale
        questions.append(
            {
                "id": f"learn_pyth_hyp_{variant}",
                "topic": "Pythagoras",
                "difficulty": "Core" if variant <= 2 else "Challenge",
                "prompt": f"A right-angled triangle has shorter sides {short_a} cm and {short_b} cm. What is the hypotenuse?",
                "choices": number_choices(hyp, [short_a + short_b, hyp - scale, hyp + scale], " cm"),
                "answer": f"{hyp} cm",
                "solution": f"Use a^2 + b^2 = c^2. {short_a}^2 + {short_b}^2 = {short_a ** 2 + short_b ** 2}, so c = {hyp} cm.",
                "trap": "The hypotenuse is the longest side and is opposite the right angle.",
            }
        )

        questions.append(
            {
                "id": f"learn_pyth_side_{variant}",
                "topic": "Pythagoras",
                "difficulty": "Challenge" if variant <= 3 else "Extension",
                "prompt": f"A right-angled triangle has hypotenuse {hyp} cm and one shorter side {short_a} cm. What is the other shorter side?",
                "choices": number_choices(short_b, [hyp - short_a, short_b + scale, short_b - scale], " cm"),
                "answer": f"{short_b} cm",
                "solution": f"Use c^2 - a^2 = b^2. {hyp}^2 - {short_a}^2 = {hyp ** 2 - short_a ** 2}, so the missing side is {short_b} cm.",
                "trap": "When finding a shorter side, subtract the square of the known side from the square of the hypotenuse.",
            }
        )

        questions.append(
            {
                "id": f"learn_pyth_word_{variant}",
                "topic": "Pythagoras",
                "difficulty": "Extension",
                "prompt": f"A ladder reaches {short_b} m up a wall. Its foot is {short_a} m from the wall. How long is the ladder?",
                "choices": number_choices(hyp, [short_b, short_a + short_b, hyp + scale], " m"),
                "answer": f"{hyp} m",
                "solution": f"The ladder is the hypotenuse of the right triangle. The matching Pythagorean triple is {short_a}, {short_b}, {hyp}, so the ladder is {hyp} m.",
                "trap": "Draw the wall, ground and ladder as a right triangle before choosing the side.",
            }
        )

    return questions


def build_mastered_extension_questions():
    questions = []

    for variant in range(1, 7):
        difficulty = "Challenge" if variant <= 3 else "Extension"

        first = 2 + variant
        common_difference = 3 + variant
        term_number = 14 + variant
        term_value = first + (term_number - 1) * common_difference
        questions.append(
            {
                "id": f"master_alg_pattern_{variant}",
                "topic": "Algebra and patterns",
                "difficulty": difficulty,
                "prompt": f"A sequence has nth term {common_difference}n + {first - common_difference}. Which term is {term_value}?",
                "choices": number_choices(term_number, [term_number - 1, term_number + 1, term_value // common_difference]),
                "answer": str(term_number),
                "solution": f"Solve {common_difference}n + {first - common_difference} = {term_value}. This gives {common_difference}n = {term_value - first + common_difference}, so n = {term_number}.",
                "trap": "Use the nth-term rule; do not just continue the sequence by hand.",
            }
        )

        ratio_a = 2 + variant
        ratio_b = 5 + variant
        one_part = 4 + variant
        added = 2 * one_part
        final_a = ratio_a + 2
        total_b = ratio_b * one_part
        questions.append(
            {
                "id": f"master_ratio_change_{variant}",
                "topic": "Fractions and ratios",
                "difficulty": difficulty,
                "prompt": f"The ratio of green to silver beads is {ratio_a}:{ratio_b}. After {added} green beads are added, the ratio is {final_a}:{ratio_b}. How many silver beads are there?",
                "choices": number_choices(total_b, [ratio_a * one_part, final_a * one_part, total_b + added]),
                "answer": str(total_b),
                "solution": f"The silver part stays at {ratio_b}. Green increases by 2 parts, and 2 parts = {added}, so 1 part = {one_part}. Silver beads = {ratio_b} x {one_part} = {total_b}.",
                "trap": "Only the green amount changes; the silver amount is fixed.",
            }
        )

    return questions


def build_mastered_reading_tasks():
    tasks = []
    entries = [
        ("A Polished Speech", "a student rewrites a speech so it sounds less dramatic but more convincing", "to show that restraint can make persuasion stronger"),
        ("The Open Notebook", "a narrator compares messy planning with a confident final answer", "to highlight the hidden work behind success"),
        ("The Late Bus", "a delayed journey becomes a lesson in patience and preparation", "to suggest that small problems can test character"),
        ("The Science Display", "two projects are described: one colourful, one carefully explained", "to contrast appearance with substance"),
        ("The Practice Room", "music practice is shown as repetitive before it becomes expressive", "to show that skill develops through disciplined repetition"),
        ("The Quiet Helper", "a student solves a problem without asking for praise", "to celebrate quiet responsibility"),
        ("The Missing Graph", "an argument becomes weaker when its evidence is removed", "to show why evidence matters"),
        ("The First Draft", "a weak paragraph is improved through precise editing", "to demonstrate the value of revision"),
    ]
    for index, (title, situation, purpose) in enumerate(entries, start=1):
        passage = (
            f"The passage describes {situation}. The writer gives practical details before offering a reflective final sentence. "
            f"This structure encourages the reader to look beyond the obvious event and consider the lesson behind it."
        )
        tasks.append(
            {
                "title": f"Author Purpose Extension: {title}",
                "passage": passage,
                "questions": [
                    {
                        "id": f"master_author_{index:02d}a",
                        "skill": "Author purpose",
                        "prompt": "What is the writer's main purpose?",
                        "choices": [purpose, "to list unrelated school events", "to entertain with a mystery ending", "to argue that preparation is unnecessary"],
                        "answer": purpose,
                        "solution": "The reflective final sentence points to the lesson the writer wants readers to notice.",
                    },
                    {
                        "id": f"master_author_{index:02d}b",
                        "skill": "Text evidence",
                        "prompt": "Which feature most clearly supports the writer's purpose?",
                        "choices": ["The practical details followed by a reflective final sentence.", "The absence of any school setting.", "The use of random facts without connection.", "The refusal to explain the situation."],
                        "answer": "The practical details followed by a reflective final sentence.",
                        "solution": "The structure moves from event to meaning, which reveals purpose.",
                    },
                ],
            }
        )
    return tasks


def build_mastered_grammar_questions():
    questions = []
    advanced_apostrophes = [
        ("The Year 8 students' essays were displayed near the library.", "students' shows plural ownership."),
        ("The children's debating coach praised their rebuttals.", "children's is the plural possessive because children is already plural."),
        ("James's explanation was clearer after revision.", "James's is a standard singular possessive form."),
        ("The two captains' strategies were completely different.", "captains' shows ownership by two captains."),
        ("Someone else's calculator was left in the room.", "else's shows possession in the phrase someone else."),
        ("The girls' lockers and the teachers' offices were repainted.", "Both girls and teachers are plural possessive nouns."),
        ("The school's values were printed on the program.", "school's is singular possessive."),
        ("The students' and teachers' opinions were both considered.", "Separate apostrophes show two different groups owning opinions."),
    ]
    for index, (answer, solution) in enumerate(advanced_apostrophes, start=1):
        questions.append(
            {
                "id": f"master_apos_{index:02d}",
                "skill": "Apostrophes",
                "difficulty": "Extension",
                "prompt": "Choose the sentence with the correct advanced apostrophe use.",
                "choices": [
                    answer,
                    answer.replace("'", ""),
                    answer.replace("s'", "s's"),
                    answer.replace("'s", "s'"),
                ],
                "answer": answer,
                "solution": solution,
            }
        )

    vocabulary = [
        ("nuanced", "showing subtle differences", "simple and obvious", "careless", "unrelated"),
        ("scrutinise", "examine closely", "ignore", "decorate", "repeat loudly"),
        ("ambivalent", "having mixed feelings", "completely certain", "very noisy", "well organised"),
        ("substantiate", "support with evidence", "make shorter", "hide from view", "guess quickly"),
        ("inadvertent", "accidental", "deliberate", "confident", "colourful"),
        ("concede", "admit a point", "deny every fact", "write quickly", "make louder"),
        ("cohesive", "well connected", "scattered", "fragile", "late"),
        ("discerning", "showing good judgement", "careless", "unaware", "ordinary"),
    ]
    for index, (word, answer, *distractors) in enumerate(vocabulary, start=1):
        questions.append(
            {
                "id": f"master_vocab_{index:02d}",
                "skill": "Vocabulary",
                "difficulty": "Extension",
                "prompt": f"Which meaning is closest to '{word}'?",
                "choices": [answer, *distractors],
                "answer": answer,
                "solution": f"'{word}' means {answer}.",
            }
        )

    spelling = [
        ("accommodation", "The excursion accommodation was confirmed."),
        ("recommendation", "Her recommendation was practical and fair."),
        ("conscience", "His conscience made him apologise."),
        ("conscious", "She was conscious of the time limit."),
        ("parallel", "The two lines are parallel."),
        ("occurrence", "The second occurrence changed the pattern."),
        ("privilege", "Leadership is a privilege and a responsibility."),
        ("maintenance", "The equipment needed regular maintenance."),
    ]
    for index, (word, sentence) in enumerate(spelling, start=1):
        questions.append(
            {
                "id": f"master_spell_{index:02d}",
                "skill": "Spelling",
                "difficulty": "Extension",
                "prompt": "Choose the sentence with the correct Year 8-9 spelling.",
                "choices": [
                    sentence,
                    sentence.replace(word, word.replace("mm", "m").replace("cc", "c").replace("ai", "ia"), 1),
                    sentence.replace(word, word + "e", 1),
                    sentence.replace(word, word[:-1], 1),
                ],
                "answer": sentence,
                "solution": f"The correct spelling is '{word}'.",
            }
        )

    return questions


def build_advanced_challenge_math_questions():
    questions = []
    triples = [(20, 21, 29), (11, 60, 61), (28, 45, 53), (33, 56, 65), (16, 63, 65), (48, 55, 73)]

    for variant in range(1, 7):
        difficulty = "Extension"

        answer = 4 + variant
        left_multiplier = 2 + variant
        inner_add = 3 + variant
        right_coefficient = variant
        right_constant = left_multiplier * (answer + inner_add) - right_coefficient * answer
        questions.append(
            {
                "id": f"adv_linear_brackets_{variant}",
                "topic": "Linear equations",
                "difficulty": difficulty,
                "prompt": f"Solve {left_multiplier}(x + {inner_add}) = {right_coefficient}x + {right_constant}.",
                "choices": number_choices(answer, [answer - 2, answer + 2, right_constant - inner_add]),
                "answer": str(answer),
                "solution": f"Expand the left side: {left_multiplier}x + {left_multiplier * inner_add} = {right_coefficient}x + {right_constant}. Then collect terms to get x = {answer}.",
                "trap": "Expand brackets before moving terms.",
            }
        )

        first = 6 + 2 * variant
        numbers = [first + 2 * i for i in range(4)]
        total = sum(numbers)
        questions.append(
            {
                "id": f"adv_consecutive_even_{variant}",
                "topic": "Consecutive-number algebra",
                "difficulty": difficulty,
                "prompt": f"The sum of four consecutive even numbers is {total}. What is the second largest number?",
                "choices": number_choices(numbers[-2], [numbers[0], numbers[1], numbers[-1]]),
                "answer": str(numbers[-2]),
                "solution": f"Let the numbers be n, n + 2, n + 4 and n + 6. Then 4n + 12 = {total}, so n = {first}. The second largest is {numbers[-2]}.",
                "trap": "Consecutive even numbers increase by 2.",
            }
        )

        first_odd = 9 + 2 * variant
        odd_numbers = [first_odd + 2 * i for i in range(5)]
        total = sum(odd_numbers)
        questions.append(
            {
                "id": f"adv_consecutive_odd5_{variant}",
                "topic": "Consecutive-number algebra",
                "difficulty": difficulty,
                "prompt": f"Five consecutive odd numbers have a sum of {total}. What is the largest number?",
                "choices": number_choices(odd_numbers[-1], [odd_numbers[0], odd_numbers[2], odd_numbers[-2]]),
                "answer": str(odd_numbers[-1]),
                "solution": f"The middle number is the average: {total} / 5 = {odd_numbers[2]}. The five odd numbers are {', '.join(str(n) for n in odd_numbers)}, so the largest is {odd_numbers[-1]}.",
                "trap": "For five consecutive odd numbers, the average is the middle number.",
            }
        )

        ratio_a = 3 + variant
        ratio_b = 5 + variant
        ratio_c = 7 + variant
        total = (ratio_a + ratio_b + ratio_c) * (4 + variant)
        target = ratio_c * (4 + variant)
        questions.append(
            {
                "id": f"adv_ratio_threepart_{variant}",
                "topic": "Fractions and ratios",
                "difficulty": difficulty,
                "prompt": f"The ratio of bronze, silver and gold tokens is {ratio_a}:{ratio_b}:{ratio_c}. There are {total} tokens altogether. How many gold tokens are there?",
                "choices": number_choices(target, [ratio_a * (4 + variant), ratio_b * (4 + variant), total - target]),
                "answer": str(target),
                "solution": f"There are {ratio_a + ratio_b + ratio_c} parts. One part is {total} / {ratio_a + ratio_b + ratio_c} = {4 + variant}. Gold is {ratio_c} parts, so {ratio_c} x {4 + variant} = {target}.",
                "trap": "Use all three ratio parts to find one part.",
            }
        )

        original = 80 + 20 * variant
        first_discount = 10 + variant
        second_discount = 5 + variant
        final = original * (100 - first_discount) * (100 - second_discount) / 10000
        questions.append(
            {
                "id": f"adv_percent_successive_{variant}",
                "topic": "Fractions and ratios",
                "difficulty": difficulty,
                "prompt": f"A ${original} item is reduced by {first_discount}% and then by another {second_discount}%. What is the final price, to the nearest dollar?",
                "choices": money_choices(round(final), [round(original * (100 - first_discount - second_discount) / 100), original - first_discount - second_discount, round(final) + 5]),
                "answer": f"${round(final):g}",
                "solution": f"Successive discounts multiply: {original} x {(100 - first_discount) / 100:g} x {(100 - second_discount) / 100:g} = ${final:.2f}, about ${round(final)}.",
                "trap": "Two discounts are not the same as adding the percentages first.",
            }
        )

        a, b, c = triples[variant - 1]
        questions.append(
            {
                "id": f"adv_pyth_map_{variant}",
                "topic": "Pythagoras",
                "difficulty": difficulty,
                "prompt": f"On a map, Rachel walks {a} m east and then {b} m north. What is her straight-line distance from the starting point?",
                "choices": number_choices(c, [a + b, c - 2, c + 2], " m"),
                "answer": f"{c} m",
                "solution": f"The east and north paths form the shorter sides of a right triangle. The straight-line distance is sqrt({a}^2 + {b}^2) = sqrt({a * a + b * b}) = {c} m.",
                "trap": "The straight-line distance is the hypotenuse, not the total walking distance.",
            }
        )

    return questions


MATH_QUESTIONS.extend(build_extra_math_questions())
MATH_QUESTIONS.extend(build_learning_sequence_math_questions())
MATH_QUESTIONS.extend(build_mastered_extension_questions())
MATH_QUESTIONS.extend(build_advanced_challenge_math_questions())
READING_TASKS.extend(build_extra_reading_tasks())
READING_TASKS.extend(build_mastered_reading_tasks())
GRAMMAR_QUESTIONS.extend(build_extra_grammar_questions())
GRAMMAR_QUESTIONS.extend(build_final_grammar_questions())
GRAMMAR_QUESTIONS.extend(build_mastered_grammar_questions())
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
    if "override_answer" in question:
        question["answer"] = question.pop("override_answer")
    question["choices"] = unique_choices(question["choices"], question["answer"])

READING_QUESTIONS = []
for task in READING_TASKS:
    for question in task["questions"]:
        question["title"] = task["title"]
        question["passage"] = task["passage"]
        if question["id"].startswith("master_author_"):
            question["difficulty"] = "Extension"
        elif question["id"].startswith("rx"):
            question["difficulty"] = "Challenge"
        else:
            question["difficulty"] = "Core"
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
ACTIVE_DIFFICULTIES = {"Challenge", "Extension"}


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
        return "Extension-ready: keep training speed, proof and accuracy."
    if percent >= 0.7:
        return "Strong Year 7 readiness: practise the missed question families."
    if percent >= 0.55:
        return "Developing: focus on careful reading and core methods."
    return "Foundation review needed: slow practice with worked corrections will help."


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
    strong_words = {"therefore", "however", "although", "consequently", "significant", "effective", "evidence", "because", "clearly", "ultimately"}
    structure_terms = {"firstly", "secondly", "finally", "for example", "in conclusion", "on the other hand"}
    score = 0
    criteria = []
    if word_count >= 180:
        score += 4
        criteria.append("Length and development: strong")
    elif word_count >= 100:
        score += 3
        criteria.append("Length and development: sound")
    else:
        score += 1
        criteria.append("Length and development: needs more detail")
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
            st.caption(f"{question['domain']} | {question['topic']} | {question.get('difficulty', '')}")
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
            <h1>PLC Year 7 Level Test Prep</h1>
            <p>Original practice for a strong Year 6 student preparing for Year 7 maths, English, reading and writing placement.</p>
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
        st.caption("Mixed maths, reading and grammar. Answers begin blank, and submission asks for confirmation.")
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
        "Harder mode is now active: Core questions are retired from normal practice. Rachel will see Challenge "
        "and Extension questions only, including harder Year 8-9 material."
    )

    st.markdown("**Quick starts for completed areas at harder level**")
    completed_buttons = st.columns(3)
    if completed_buttons[0].button("Harder algebra", width="stretch"):
        new_practice("Maths", "Algebra and patterns", "Extension", 12)
        st.rerun()
    if completed_buttons[1].button("Harder fractions", width="stretch"):
        new_practice("Maths", "Fractions and ratios", "Extension", 12)
        st.rerun()
    if completed_buttons[2].button("Author purpose", width="stretch"):
        new_practice("Reading", "Author purpose", "Reading", 10)
        st.rerun()
    completed_buttons = st.columns(3)
    if completed_buttons[0].button("Apostrophes plus", width="stretch"):
        new_practice("Grammar and vocabulary", "Apostrophes", "Extension", 12)
        st.rerun()
    if completed_buttons[1].button("Advanced vocabulary", width="stretch"):
        new_practice("Grammar and vocabulary", "Vocabulary", "Extension", 12)
        st.rerun()
    if completed_buttons[2].button("Advanced spelling", width="stretch"):
        new_practice("Grammar and vocabulary", "Spelling", "Extension", 10)
        st.rerun()

    st.markdown("**Next learning sequence**")
    sequence_buttons = st.columns(3)
    if sequence_buttons[0].button("1. Linear equations", type="primary", width="stretch"):
        new_practice("Maths", "Linear equations", "Challenge", 10)
        st.rerun()
    if sequence_buttons[1].button("2. Consecutive numbers", type="primary", width="stretch"):
        new_practice("Maths", "Consecutive-number algebra", "Challenge", 10)
        st.rerun()
    if sequence_buttons[2].button("3. Pythagoras", type="primary", width="stretch"):
        new_practice("Maths", "Pythagoras", "Challenge", 10)
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
    difficulty_options = ["All difficulties"] + sorted({question.get("difficulty", "") for question in difficulty_pool if question.get("difficulty", "")})
    with c3:
        difficulty = st.selectbox("Difficulty", difficulty_options, key="plc_difficulty")
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
    st.caption("Aim for 180-300 words. Focus on structure, precise vocabulary and controlled sentences.")
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
    st.markdown("**Current status**")
    status_rows = [
        {"Area": "Algebra and patterns", "Status": "Completed", "Next action": "Practise at Year 8-9 extension level"},
        {"Area": "Apostrophes", "Status": "Completed", "Next action": "Use advanced plural, shared and separate possession"},
        {"Area": "Author purpose", "Status": "Completed", "Next action": "Practise harder purpose, structure and evidence questions"},
        {"Area": "Fractions and ratios", "Status": "Completed", "Next action": "Use changing ratios, reverse percentages and multi-step problems"},
        {"Area": "Vocabulary", "Status": "Completed", "Next action": "Move to nuanced Year 8-9 academic vocabulary"},
        {"Area": "Spelling", "Status": "Completed", "Next action": "Practise higher-level spelling and commonly confused words"},
        {"Area": "Linear equations", "Status": "To learn", "Next action": "One-step, two-step, variables both sides, word problems"},
        {"Area": "Consecutive-number algebra", "Status": "To learn", "Next action": "Integers, odd/even numbers, form and solve equations"},
        {"Area": "Pythagoras", "Status": "To learn", "Next action": "Hypotenuse, missing shorter side, word problems and diagrams"},
    ]
    st.dataframe(status_rows, hide_index=True, width="stretch")

    st.markdown("**Recommended next sequence**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Step 1</strong>
            <p>Linear equations: understand equation balance, solve one-step and two-step equations, then variables on both sides.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Step 2</strong>
            <p>Consecutive-number algebra: use n, n+1, n+2 and n, n+2, n+4 to form and solve equations.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Step 3</strong>
            <p>Pythagoras: understand right triangles, find the hypotenuse, find missing shorter sides, then solve word problems.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write("Recommended weekly rhythm:")
    st.write("- 2 new-learning maths sessions: linear equations first, then consecutive-number algebra, then Pythagoras.")
    st.write("- 1 harder review session from the completed areas: algebra, fractions, apostrophes, author purpose, vocabulary or spelling.")
    st.write("- 1 English session: reading/grammar plus one short writing response.")
    st.write("- 1 mixed mock test every weekend with corrections written out.")


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
