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


def unique_choices(choices, answer):
    cleaned = []
    for choice in [*choices, answer]:
        if choice not in cleaned:
            cleaned.append(choice)
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
        question["difficulty"] = "Reading"
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
    maths = choose_questions(MATH_QUESTIONS, 10, "plc_seen_ids")
    reading = choose_questions(READING_QUESTIONS, 6, "plc_seen_ids")
    grammar = choose_questions(GRAMMAR_QUESTIONS, 6, "plc_seen_ids")
    selected = maths + reading + grammar
    random.shuffle(selected)
    st.session_state["plc_mock_ids"] = [question["id"] for question in selected]
    st.session_state["plc_mock_orders"] = shuffle_orders(selected)
    st.session_state["plc_mock_submitted"] = False
    st.session_state["plc_mock_confirming"] = False
    clear_answers("plc_answer_")


def new_practice(domain, topic, difficulty, count):
    pool = all_mcq_questions()
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
    all_questions = all_mcq_questions()
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
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Weeks 1-2</strong>
            <p>Diagnostic mock tests, number skills, fractions, punctuation and short reading inference.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Weeks 3-5</strong>
            <p>Mixed problem solving, ratios, algebra patterns, vocabulary, paragraph writing and evidence use.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="skill-card">
            <strong>Weeks 6-8</strong>
            <p>Timed mock tests, extension questions, careful error review and polished persuasive/creative writing.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write("Recommended weekly rhythm:")
    st.write("- 2 maths sessions: one core accuracy, one extension reasoning.")
    st.write("- 2 English sessions: one reading/grammar, one writing response.")
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
