import html
import random
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None


QUESTION_BANK = [
    {
        "id": "n01",
        "topic": "Number",
        "difficulty": "Warm-up",
        "prompt": "What is the value of 36 + 48 - 19?",
        "choices": ["55", "65", "67", "75", "83"],
        "answer": "65",
        "hint": "Add first, then subtract.",
        "solution": "36 + 48 = 84, and 84 - 19 = 65.",
    },
    {
        "id": "n02",
        "topic": "Number",
        "difficulty": "Warm-up",
        "prompt": "A number is multiplied by 6 to give 144. What is the number?",
        "choices": ["18", "20", "22", "24", "30"],
        "answer": "24",
        "hint": "Use division to undo multiplication.",
        "solution": "144 divided by 6 is 24.",
    },
    {
        "id": "n03",
        "topic": "Number",
        "difficulty": "Core",
        "prompt": "Which of these numbers is divisible by both 3 and 5?",
        "choices": ["125", "210", "224", "302", "418"],
        "answer": "210",
        "hint": "A number divisible by both 3 and 5 must be divisible by 15.",
        "solution": "210 ends in 0, so it is divisible by 5. Its digit sum is 2 + 1 + 0 = 3, so it is divisible by 3.",
    },
    {
        "id": "n04",
        "topic": "Number",
        "difficulty": "Core",
        "prompt": "The product of two whole numbers is 84. One number is 7. What is the other number?",
        "choices": ["9", "10", "11", "12", "14"],
        "answer": "12",
        "hint": "Find 84 divided by 7.",
        "solution": "84 divided by 7 is 12.",
    },
    {
        "id": "n05",
        "topic": "Number",
        "difficulty": "Challenge",
        "prompt": "The sum of three consecutive whole numbers is 72. What is the largest of the three numbers?",
        "choices": ["22", "23", "24", "25", "26"],
        "answer": "25",
        "hint": "The middle number is the average of the three numbers.",
        "solution": "72 divided by 3 is 24, so the three numbers are 23, 24 and 25.",
    },
    {
        "id": "n06",
        "topic": "Number",
        "difficulty": "Challenge",
        "prompt": "A two-digit number has digits that add to 11. Reversing the digits makes a number 27 smaller. What is the original number?",
        "choices": ["47", "56", "65", "74", "83"],
        "answer": "74",
        "hint": "If reversing makes it smaller, the tens digit is larger than the ones digit.",
        "solution": "The digit pairs that add to 11 include 7 and 4. 74 - 47 = 27, so the original number is 74.",
    },
    {
        "id": "f01",
        "topic": "Fractions, decimals and percentages",
        "difficulty": "Warm-up",
        "prompt": "Which fraction is equal to 0.25?",
        "choices": ["1/2", "1/3", "1/4", "2/5", "3/5"],
        "answer": "1/4",
        "hint": "0.25 means 25 hundredths.",
        "solution": "0.25 = 25/100 = 1/4.",
    },
    {
        "id": "f02",
        "topic": "Fractions, decimals and percentages",
        "difficulty": "Warm-up",
        "prompt": "What is 20% of 75?",
        "choices": ["10", "12", "15", "20", "25"],
        "answer": "15",
        "hint": "20% is one fifth.",
        "solution": "One fifth of 75 is 75 divided by 5, which is 15.",
    },
    {
        "id": "f03",
        "topic": "Fractions, decimals and percentages",
        "difficulty": "Core",
        "prompt": "Which is the largest number?",
        "choices": ["0.6", "5/8", "58%", "0.59", "3/5"],
        "answer": "5/8",
        "hint": "Compare them as decimals.",
        "solution": "5/8 = 0.625, 3/5 = 0.6, 58% = 0.58. The largest is 5/8.",
    },
    {
        "id": "f04",
        "topic": "Fractions, decimals and percentages",
        "difficulty": "Core",
        "prompt": "A jacket costs $80. It is reduced by 15%. What is the sale price?",
        "choices": ["$12", "$65", "$68", "$72", "$95"],
        "answer": "$68",
        "hint": "Find 15% of 80, then subtract it.",
        "solution": "10% of 80 is 8 and 5% is 4, so 15% is 12. The sale price is 80 - 12 = $68.",
    },
    {
        "id": "f05",
        "topic": "Fractions, decimals and percentages",
        "difficulty": "Challenge",
        "prompt": "Mia spent 2/5 of her money and had $36 left. How much money did she start with?",
        "choices": ["$45", "$54", "$60", "$72", "$90"],
        "answer": "$60",
        "hint": "If she spent 2/5, then 3/5 remains.",
        "solution": "3/5 of her money is $36, so 1/5 is $12. The total is 5 x 12 = $60.",
    },
    {
        "id": "f06",
        "topic": "Fractions, decimals and percentages",
        "difficulty": "Challenge",
        "prompt": "A class has 28 students. 3/7 of them walk to school. How many do not walk to school?",
        "choices": ["8", "10", "12", "16", "18"],
        "answer": "16",
        "hint": "First find how many walk.",
        "solution": "3/7 of 28 is 12. The number who do not walk is 28 - 12 = 16.",
    },
    {
        "id": "a01",
        "topic": "Algebra and patterns",
        "difficulty": "Warm-up",
        "prompt": "If x = 7, what is 3x + 4?",
        "choices": ["17", "21", "24", "25", "28"],
        "answer": "25",
        "hint": "Substitute 7 for x.",
        "solution": "3x + 4 = 3 x 7 + 4 = 21 + 4 = 25.",
    },
    {
        "id": "a02",
        "topic": "Algebra and patterns",
        "difficulty": "Warm-up",
        "prompt": "What is the next number in the pattern 4, 9, 14, 19, ...?",
        "choices": ["22", "23", "24", "25", "29"],
        "answer": "24",
        "hint": "Look at the difference between neighbouring terms.",
        "solution": "The pattern increases by 5 each time, so the next number is 19 + 5 = 24.",
    },
    {
        "id": "a03",
        "topic": "Algebra and patterns",
        "difficulty": "Core",
        "prompt": "Solve 2n - 5 = 17.",
        "choices": ["6", "9", "10", "11", "12"],
        "answer": "11",
        "hint": "Add 5 to both sides first.",
        "solution": "2n - 5 = 17, so 2n = 22 and n = 11.",
    },
    {
        "id": "a04",
        "topic": "Algebra and patterns",
        "difficulty": "Core",
        "prompt": "A pattern uses 3 matchsticks for the first shape, 5 for the second, 7 for the third. How many matchsticks are needed for the 10th shape?",
        "choices": ["19", "20", "21", "22", "23"],
        "answer": "21",
        "hint": "The pattern is odd numbers starting at 3.",
        "solution": "The rule is 2n + 1. For n = 10, 2 x 10 + 1 = 21.",
    },
    {
        "id": "a05",
        "topic": "Algebra and patterns",
        "difficulty": "Challenge",
        "prompt": "The rule for a sequence is multiply by 2, then subtract 1. If the input is 13, what is the output?",
        "choices": ["12", "24", "25", "26", "27"],
        "answer": "25",
        "hint": "Do the operations in the order given.",
        "solution": "13 x 2 = 26, and 26 - 1 = 25.",
    },
    {
        "id": "a06",
        "topic": "Algebra and patterns",
        "difficulty": "Challenge",
        "prompt": "A number machine changes 5 into 17 and 8 into 26. Which rule could it be using?",
        "choices": ["2n + 7", "3n + 2", "4n - 3", "5n - 8", "n + 12"],
        "answer": "3n + 2",
        "hint": "Test each rule with both 5 and 8.",
        "solution": "3 x 5 + 2 = 17 and 3 x 8 + 2 = 26, so the rule is 3n + 2.",
    },
    {
        "id": "g01",
        "topic": "Geometry",
        "difficulty": "Warm-up",
        "prompt": "How many degrees are in a straight angle?",
        "choices": ["45", "90", "120", "180", "360"],
        "answer": "180",
        "hint": "A straight angle forms a line.",
        "solution": "A straight angle is 180 degrees.",
    },
    {
        "id": "g02",
        "topic": "Geometry",
        "difficulty": "Warm-up",
        "prompt": "A triangle has angles 45 degrees and 65 degrees. What is the third angle?",
        "choices": ["60", "65", "70", "75", "80"],
        "answer": "70",
        "hint": "Angles in a triangle add to 180 degrees.",
        "solution": "45 + 65 = 110, so the third angle is 180 - 110 = 70 degrees.",
    },
    {
        "id": "g03",
        "topic": "Geometry",
        "difficulty": "Core",
        "prompt": "A rectangle has length 12 cm and width 7 cm. What is its perimeter?",
        "choices": ["19 cm", "38 cm", "42 cm", "76 cm", "84 cm"],
        "answer": "38 cm",
        "hint": "Perimeter is the distance around the outside.",
        "solution": "Perimeter = 2 x (12 + 7) = 38 cm.",
    },
    {
        "id": "g04",
        "topic": "Geometry",
        "difficulty": "Core",
        "prompt": "Which shape has exactly one pair of parallel sides?",
        "choices": ["Parallelogram", "Rectangle", "Rhombus", "Trapezium", "Square"],
        "answer": "Trapezium",
        "hint": "In Australian school usage, this is often called a trapezium.",
        "solution": "A trapezium has exactly one pair of parallel sides.",
    },
    {
        "id": "g05",
        "topic": "Geometry",
        "difficulty": "Challenge",
        "prompt": "The exterior angle of a regular polygon is 45 degrees. How many sides does the polygon have?",
        "choices": ["6", "8", "9", "10", "12"],
        "answer": "8",
        "hint": "Exterior angles of a polygon add to 360 degrees.",
        "solution": "360 divided by 45 is 8, so the polygon has 8 sides.",
    },
    {
        "id": "g06",
        "topic": "Geometry",
        "difficulty": "Challenge",
        "prompt": "A square and an equilateral triangle have the same perimeter. The square has side length 6 cm. What is the side length of the triangle?",
        "choices": ["6 cm", "7 cm", "8 cm", "9 cm", "12 cm"],
        "answer": "8 cm",
        "hint": "Find the square's perimeter first.",
        "solution": "The square's perimeter is 4 x 6 = 24 cm. An equilateral triangle with perimeter 24 cm has side length 24 divided by 3 = 8 cm.",
    },
    {
        "id": "m01",
        "topic": "Measurement",
        "difficulty": "Warm-up",
        "prompt": "How many millimetres are in 3.4 cm?",
        "choices": ["0.34", "3.4", "34", "340", "3400"],
        "answer": "34",
        "hint": "1 cm is 10 mm.",
        "solution": "3.4 cm = 3.4 x 10 = 34 mm.",
    },
    {
        "id": "m02",
        "topic": "Measurement",
        "difficulty": "Warm-up",
        "prompt": "A movie starts at 6:40 pm and runs for 95 minutes. What time does it finish?",
        "choices": ["7:55 pm", "8:05 pm", "8:10 pm", "8:15 pm", "8:25 pm"],
        "answer": "8:15 pm",
        "hint": "95 minutes is 1 hour and 35 minutes.",
        "solution": "6:40 pm + 1 hour = 7:40 pm. Add 35 minutes to get 8:15 pm.",
    },
    {
        "id": "m03",
        "topic": "Measurement",
        "difficulty": "Core",
        "prompt": "A garden bed is 5 m long and 3 m wide. What is its area?",
        "choices": ["8 square m", "15 square m", "16 square m", "30 square m", "45 square m"],
        "answer": "15 square m",
        "hint": "Area of a rectangle is length times width.",
        "solution": "Area = 5 x 3 = 15 square metres.",
    },
    {
        "id": "m04",
        "topic": "Measurement",
        "difficulty": "Core",
        "prompt": "A 2 litre bottle is used to fill 250 mL cups. How many full cups can be filled?",
        "choices": ["4", "6", "8", "10", "12"],
        "answer": "8",
        "hint": "2 litres is 2000 mL.",
        "solution": "2000 divided by 250 is 8.",
    },
    {
        "id": "m05",
        "topic": "Measurement",
        "difficulty": "Challenge",
        "prompt": "A rectangle has area 96 square cm and length 12 cm. What is its perimeter?",
        "choices": ["20 cm", "32 cm", "36 cm", "40 cm", "48 cm"],
        "answer": "40 cm",
        "hint": "Find the width first.",
        "solution": "Width = 96 divided by 12 = 8 cm. Perimeter = 2 x (12 + 8) = 40 cm.",
    },
    {
        "id": "m06",
        "topic": "Measurement",
        "difficulty": "Challenge",
        "prompt": "A cube has side length 4 cm. What is its volume?",
        "choices": ["12 cubic cm", "16 cubic cm", "32 cubic cm", "48 cubic cm", "64 cubic cm"],
        "answer": "64 cubic cm",
        "hint": "Volume of a cube is side x side x side.",
        "solution": "4 x 4 x 4 = 64 cubic centimetres.",
    },
    {
        "id": "d01",
        "topic": "Data and chance",
        "difficulty": "Warm-up",
        "prompt": "The scores 5, 7, 7, 8, 10 have which median?",
        "choices": ["5", "7", "7.5", "8", "10"],
        "answer": "7",
        "hint": "The median is the middle value when the list is ordered.",
        "solution": "The list is already ordered. The middle value is 7.",
    },
    {
        "id": "d02",
        "topic": "Data and chance",
        "difficulty": "Warm-up",
        "prompt": "A fair six-sided die is rolled. What is the chance of rolling an even number?",
        "choices": ["1/6", "1/3", "1/2", "2/3", "5/6"],
        "answer": "1/2",
        "hint": "The even outcomes are 2, 4 and 6.",
        "solution": "There are 3 even outcomes out of 6 possible outcomes, so the chance is 3/6 = 1/2.",
    },
    {
        "id": "d03",
        "topic": "Data and chance",
        "difficulty": "Core",
        "prompt": "The mean of 4, 6, 8 and x is 7. What is x?",
        "choices": ["7", "8", "9", "10", "12"],
        "answer": "10",
        "hint": "If the mean is 7 for four numbers, the total is 28.",
        "solution": "The total must be 4 x 7 = 28. Since 4 + 6 + 8 = 18, x = 10.",
    },
    {
        "id": "d04",
        "topic": "Data and chance",
        "difficulty": "Core",
        "prompt": "A bag has 3 red, 4 blue and 5 green counters. What is the chance of choosing a blue counter?",
        "choices": ["1/4", "1/3", "4/9", "4/12", "5/12"],
        "answer": "1/3",
        "hint": "Find the total number of counters.",
        "solution": "There are 12 counters in total and 4 are blue. The chance is 4/12 = 1/3.",
    },
    {
        "id": "d05",
        "topic": "Data and chance",
        "difficulty": "Challenge",
        "prompt": "Four numbers have a mean of 12. A fifth number, 17, is added. What is the new mean?",
        "choices": ["12", "13", "14", "15", "17"],
        "answer": "13",
        "hint": "First find the total of the first four numbers.",
        "solution": "The first four numbers total 4 x 12 = 48. Add 17 to get 65. The new mean is 65 divided by 5 = 13.",
    },
    {
        "id": "d06",
        "topic": "Data and chance",
        "difficulty": "Challenge",
        "prompt": "A spinner has equal sections numbered 1 to 8. What is the probability of spinning a prime number?",
        "choices": ["1/4", "3/8", "1/2", "5/8", "3/4"],
        "answer": "1/2",
        "hint": "List the prime numbers from 1 to 8.",
        "solution": "The prime numbers are 2, 3, 5 and 7. That is 4 outcomes out of 8, so the probability is 1/2.",
    },
    {
        "id": "p01",
        "topic": "Problem solving",
        "difficulty": "Warm-up",
        "prompt": "Tom has twice as many stickers as Ava. Together they have 36 stickers. How many stickers does Ava have?",
        "choices": ["9", "12", "18", "24", "27"],
        "answer": "12",
        "hint": "Think of Ava's amount as one part and Tom's as two parts.",
        "solution": "There are 3 equal parts in total. 36 divided by 3 is 12, so Ava has 12 stickers.",
    },
    {
        "id": "p02",
        "topic": "Problem solving",
        "difficulty": "Warm-up",
        "prompt": "A bus has 18 passengers. At the next stop, 7 get off and 12 get on. How many passengers are now on the bus?",
        "choices": ["19", "21", "23", "25", "37"],
        "answer": "23",
        "hint": "Subtract first, then add.",
        "solution": "18 - 7 = 11, and 11 + 12 = 23.",
    },
    {
        "id": "p03",
        "topic": "Problem solving",
        "difficulty": "Core",
        "prompt": "A code replaces A with 1, B with 2, C with 3, and so on. What is the value of MATH?",
        "choices": ["36", "40", "42", "48", "52"],
        "answer": "42",
        "hint": "Find each letter value and add.",
        "solution": "M = 13, A = 1, T = 20, H = 8. The total is 13 + 1 + 20 + 8 = 42.",
    },
    {
        "id": "p04",
        "topic": "Problem solving",
        "difficulty": "Core",
        "prompt": "A tournament has 8 teams. Each team plays every other team once. How many games are played?",
        "choices": ["16", "24", "28", "32", "56"],
        "answer": "28",
        "hint": "Count pairs of teams.",
        "solution": "Each game is a pair of teams. 8 x 7 divided by 2 = 28 games.",
    },
    {
        "id": "p05",
        "topic": "Problem solving",
        "difficulty": "Challenge",
        "prompt": "A clock shows 3:15. What is the smaller angle between the hour hand and minute hand?",
        "choices": ["0 degrees", "7.5 degrees", "15 degrees", "30 degrees", "45 degrees"],
        "answer": "7.5 degrees",
        "hint": "At 3:15 the hour hand has moved a quarter of the way from 3 to 4.",
        "solution": "The minute hand is at 3. The hour hand is 1/4 of 30 degrees past 3, which is 7.5 degrees.",
    },
    {
        "id": "p06",
        "topic": "Problem solving",
        "difficulty": "Challenge",
        "prompt": "Five friends each shake hands with every other friend exactly once. How many handshakes occur?",
        "choices": ["5", "8", "10", "15", "20"],
        "answer": "10",
        "hint": "Count pairs of friends.",
        "solution": "There are 5 x 4 divided by 2 = 10 pairs, so there are 10 handshakes.",
    },
]

TOPICS = ["All topics"] + sorted({question["topic"] for question in QUESTION_BANK})
DIFFICULTIES = ["All levels", "Warm-up", "Core", "Challenge"]


def get_question(question_id):
    return next(question for question in QUESTION_BANK if question["id"] == question_id)


def filter_questions(topic, difficulty):
    questions = QUESTION_BANK
    if topic != "All topics":
        questions = [question for question in questions if question["topic"] == topic]
    if difficulty != "All levels":
        questions = [question for question in questions if question["difficulty"] == difficulty]
    return questions


def choose_quiz(topic, difficulty, length, seed=None):
    questions = filter_questions(topic, difficulty)
    rng = random.Random(seed)
    length = min(length, len(questions))
    return rng.sample(questions, length)


def mark_quiz(questions, answers):
    results = []
    for question in questions:
        selected = answers.get(question["id"], "")
        results.append(
            {
                "question": question,
                "selected": selected,
                "correct": selected == question["answer"],
            }
        )
    return results


def score_message(score, total):
    if total == 0:
        return "Choose a quiz to begin."
    percent = score / total
    if percent >= 0.9:
        return "Excellent AMC-style thinking."
    if percent >= 0.7:
        return "Strong work. Review the missed solutions."
    if percent >= 0.5:
        return "Good practice. Focus on one topic at a time."
    return "Keep building confidence. Hints and worked solutions will help."


def topic_summary(results):
    summary = {}
    for result in results:
        topic = result["question"]["topic"]
        if topic not in summary:
            summary[topic] = {"correct": 0, "total": 0}
        summary[topic]["total"] += 1
        if result["correct"]:
            summary[topic]["correct"] += 1
    return summary


def render_streamlit_app():
    st.set_page_config(page_title="AMC Year 7 Maths Prep", layout="wide")
    st.markdown(
        """
        <style>
        .block-container { max-width: 1180px; padding-top: 2rem; }
        [data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #d9e2ec;
            border-radius: 8px;
            padding: 0.75rem 1rem;
        }
        div.stButton > button[kind="primary"] {
            min-height: 48px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("AMC Year 7 Maths Prep")
    st.caption("Original AMC-style practice questions for Year 7. These are not official AMC questions.")

    if "math_topic" not in st.session_state:
        st.session_state["math_topic"] = "All topics"
    if "math_difficulty" not in st.session_state:
        st.session_state["math_difficulty"] = "All levels"
    if "math_length" not in st.session_state:
        st.session_state["math_length"] = 10
    if "math_quiz_ids" not in st.session_state:
        st.session_state["math_quiz_ids"] = [
            question["id"]
            for question in choose_quiz("All topics", "All levels", 10, seed=7)
        ]
    if "math_submitted" not in st.session_state:
        st.session_state["math_submitted"] = False

    def new_quiz():
        topic = st.session_state["math_topic"]
        difficulty = st.session_state["math_difficulty"]
        length = st.session_state["math_length"]
        questions = choose_quiz(topic, difficulty, length)
        st.session_state["math_quiz_ids"] = [question["id"] for question in questions]
        st.session_state["math_submitted"] = False
        for question in QUESTION_BANK:
            st.session_state.pop(f"answer_{question['id']}", None)

    def submit_quiz():
        st.session_state["math_submitted"] = True

    controls, tips = st.columns([2, 1])
    with controls:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.selectbox("Topic", TOPICS, key="math_topic")
        with c2:
            st.selectbox("Difficulty", DIFFICULTIES, key="math_difficulty")
        with c3:
            available_count = len(filter_questions(st.session_state["math_topic"], st.session_state["math_difficulty"]))
            max_length = max(1, min(20, available_count))
            if st.session_state["math_length"] > max_length:
                st.session_state["math_length"] = max_length
            st.number_input("Questions", min_value=1, max_value=max_length, step=1, key="math_length")
        b1, b2 = st.columns(2)
        with b1:
            st.button("New quiz", use_container_width=True, on_click=new_quiz)
        with b2:
            st.button("Submit answers", type="primary", use_container_width=True, on_click=submit_quiz)
    with tips:
        st.markdown("**Practice focus**")
        st.write("- Read each question carefully.")
        st.write("- Try a hint before checking the solution.")
        st.write("- After submitting, redo missed questions.")

    questions = [get_question(question_id) for question_id in st.session_state["math_quiz_ids"]]
    if not questions:
        st.warning("No questions match those filters. Choose another topic or difficulty.")
        return

    answers = {}
    for index, question in enumerate(questions, start=1):
        with st.container(border=True):
            st.markdown(f"**Question {index}. {question['prompt']}**")
            st.caption(f"{question['topic']} | {question['difficulty']}")
            answers[question["id"]] = st.radio(
                "Choose one answer",
                question["choices"],
                key=f"answer_{question['id']}",
                horizontal=True,
                label_visibility="collapsed",
            )
            with st.expander("Hint"):
                st.write(question["hint"])

            if st.session_state["math_submitted"]:
                if answers[question["id"]] == question["answer"]:
                    st.success("Correct")
                else:
                    st.error(f"Not quite. Correct answer: {question['answer']}")
                st.write(f"**Worked solution:** {question['solution']}")

    if st.session_state["math_submitted"]:
        results = mark_quiz(questions, answers)
        score = sum(1 for result in results if result["correct"])
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Score", f"{score}/{len(questions)}")
        m2.metric("Accuracy", f"{round(score / len(questions) * 100)}%")
        m3.metric("Questions", len(questions))
        st.info(score_message(score, len(questions)))

        rows = []
        for topic, data in topic_summary(results).items():
            rows.append(
                {
                    "Topic": topic,
                    "Correct": data["correct"],
                    "Total": data["total"],
                    "Accuracy": f"{round(data['correct'] / data['total'] * 100)}%",
                }
            )
        st.dataframe(rows, hide_index=True, use_container_width=True)


def escape_html(value):
    return html.escape(str(value), quote=True)


def render_http_page(questions=None, results=None, topic="All topics", difficulty="All levels", length=10):
    if questions is None:
        questions = choose_quiz(topic, difficulty, int(length), seed=11)
    options = "".join(f"<option {'selected' if t == topic else ''}>{escape_html(t)}</option>" for t in TOPICS)
    difficulty_options = "".join(f"<option {'selected' if d == difficulty else ''}>{escape_html(d)}</option>" for d in DIFFICULTIES)
    question_inputs = []
    for index, question in enumerate(questions, start=1):
        choices = []
        for choice in question["choices"]:
            checked = ""
            if results:
                selected = next((item["selected"] for item in results if item["question"]["id"] == question["id"]), "")
                checked = " checked" if selected == choice else ""
            choices.append(
                f"<label class=\"choice\"><input type=\"radio\" name=\"answer_{question['id']}\" value=\"{escape_html(choice)}\"{checked}> {escape_html(choice)}</label>"
            )
        feedback = ""
        if results:
            result = next(item for item in results if item["question"]["id"] == question["id"])
            status = "Correct" if result["correct"] else f"Correct answer: {question['answer']}"
            feedback = f"<div class=\"feedback {'ok' if result['correct'] else 'no'}\"><strong>{escape_html(status)}</strong><br><strong>Worked solution:</strong> {escape_html(question['solution'])}</div>"
        question_inputs.append(
            f"""
            <section class="question">
                <h2>Question {index}</h2>
                <p>{escape_html(question['prompt'])}</p>
                <small>{escape_html(question['topic'])} | {escape_html(question['difficulty'])}</small>
                <div class="choices">{''.join(choices)}</div>
                <details><summary>Hint</summary><p>{escape_html(question['hint'])}</p></details>
                {feedback}
                <input type="hidden" name="qid" value="{escape_html(question['id'])}">
            </section>
            """
        )
    result_html = ""
    if results:
        score = sum(1 for result in results if result["correct"])
        total = len(results)
        result_html = f"""
        <section class="summary">
            <div><span>Score</span><strong>{score}/{total}</strong></div>
            <div><span>Accuracy</span><strong>{round(score / total * 100)}%</strong></div>
            <div><span>Message</span><strong>{escape_html(score_message(score, total))}</strong></div>
        </section>
        """
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AMC Year 7 Maths Prep</title>
    <style>
        :root {{ --ink:#172033; --muted:#5b6472; --line:#d9e2ec; --soft:#f5f7fa; --blue:#2563eb; --green:#0f766e; --red:#b42318; }}
        * {{ box-sizing:border-box; }}
        body {{ margin:0; font-family:Arial, Helvetica, sans-serif; background:var(--soft); color:var(--ink); }}
        header, form, .summary {{ width:min(1100px, calc(100% - 32px)); margin:22px auto; }}
        h1 {{ font-size:2rem; margin:0 0 8px; }}
        .controls, .question, .summary div {{ background:white; border:1px solid var(--line); border-radius:8px; padding:16px; }}
        .controls {{ display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:12px; align-items:end; }}
        label {{ font-weight:700; display:block; margin-bottom:6px; }}
        select, input[type="number"] {{ width:100%; padding:10px; border:1px solid var(--line); border-radius:8px; font:inherit; }}
        button {{ min-height:42px; border:0; border-radius:8px; background:var(--blue); color:white; font-weight:700; padding:10px 14px; cursor:pointer; }}
        .question {{ margin-top:16px; }}
        .question h2 {{ margin:0 0 8px; font-size:1.1rem; }}
        small {{ color:var(--muted); }}
        .choices {{ display:flex; flex-wrap:wrap; gap:10px; margin:14px 0; }}
        .choice {{ border:1px solid var(--line); border-radius:8px; padding:9px 12px; background:#f8fafc; font-weight:400; }}
        details {{ margin-top:8px; }}
        .feedback {{ margin-top:12px; padding:12px; border-radius:8px; border:1px solid var(--line); }}
        .feedback.ok {{ background:#ecfdf3; color:var(--green); }}
        .feedback.no {{ background:#fef3f2; color:var(--red); }}
        .summary {{ display:grid; grid-template-columns:1fr 1fr 2fr; gap:12px; }}
        .summary span {{ color:var(--muted); display:block; }}
        .summary strong {{ font-size:1.3rem; }}
        @media (max-width:760px) {{ .controls, .summary {{ grid-template-columns:1fr; }} .choices {{ display:block; }} .choice {{ margin:8px 0; }} }}
    </style>
</head>
<body>
    <header>
        <h1>AMC Year 7 Maths Prep</h1>
        <p>Original AMC-style practice questions for Year 7. These are not official AMC questions.</p>
    </header>
    {result_html}
    <form method="post" action="/quiz">
        <section class="controls">
            <div><label>Topic</label><select name="topic">{options}</select></div>
            <div><label>Difficulty</label><select name="difficulty">{difficulty_options}</select></div>
            <div><label>Questions</label><input type="number" name="length" min="1" max="20" value="{escape_html(length)}"></div>
            <button type="submit" name="action" value="new">New quiz</button>
        </section>
    </form>
    <form method="post" action="/submit">
        <input type="hidden" name="topic" value="{escape_html(topic)}">
        <input type="hidden" name="difficulty" value="{escape_html(difficulty)}">
        <input type="hidden" name="length" value="{escape_html(length)}">
        {''.join(question_inputs)}
        <section class="controls">
            <button type="submit">Submit answers</button>
        </section>
    </form>
</body>
</html>"""


class MathHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_html(render_http_page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        fields = parse_qs(body)
        path = urlparse(self.path).path
        topic = fields.get("topic", ["All topics"])[0]
        difficulty = fields.get("difficulty", ["All levels"])[0]
        quiz_length = int(fields.get("length", ["10"])[0])

        if path == "/quiz":
            questions = choose_quiz(topic, difficulty, quiz_length)
            self.send_html(render_http_page(questions=questions, topic=topic, difficulty=difficulty, length=quiz_length))
            return

        if path == "/submit":
            question_ids = fields.get("qid", [])
            questions = [get_question(question_id) for question_id in question_ids]
            answers = {question_id: fields.get(f"answer_{question_id}", [""])[0] for question_id in question_ids}
            results = mark_quiz(questions, answers)
            self.send_html(render_http_page(questions=questions, results=results, topic=topic, difficulty=difficulty, length=quiz_length))
            return

        self.send_error(404)

    def send_html(self, content):
        encoded = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def get_cli_port(default=8508):
    if "--port" not in sys.argv:
        return default
    index = sys.argv.index("--port")
    try:
        return int(sys.argv[index + 1])
    except (IndexError, ValueError):
        return default


def run_http_app(start_port=8508):
    for port in range(start_port, start_port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), MathHandler)
            break
        except OSError:
            continue
    else:
        raise RuntimeError("No free local port found between 8508 and 8527.")
    print("AMC Year 7 Maths Prep")
    print("Streamlit is not installed, so the built-in web app is running.")
    print(f"Open http://127.0.0.1:{server.server_port}")
    server.serve_forever()


def main():
    if st is None:
        run_http_app(get_cli_port())
    else:
        render_streamlit_app()


if __name__ == "__main__":
    main()
