import random
from collections import Counter

import streamlit as st


QUESTIONS = [
    {
        "skill": "Apostrophes",
        "prompt": "Choose the sentence with the correct apostrophe use.",
        "choices": [
            "The teachers' meeting starts after school.",
            "The teacher's are meeting after school.",
            "The teachers meeting's starts after school.",
            "The teachers meeting starts after school's.",
        ],
        "answer": "The teachers' meeting starts after school.",
        "explanation": "Teachers' shows that the meeting belongs to more than one teacher.",
    },
    {
        "skill": "Apostrophes",
        "prompt": "Which sentence uses its or it's correctly?",
        "choices": [
            "The school changed its timetable for the athletics carnival.",
            "The school changed it's timetable for the athletics carnival.",
            "Its going to rain during lunch.",
            "The library closed because its Friday.",
        ],
        "answer": "The school changed its timetable for the athletics carnival.",
        "explanation": "Its is possessive. It's means it is or it has.",
    },
    {
        "skill": "Subject-verb agreement",
        "prompt": "Choose the sentence with correct subject-verb agreement.",
        "choices": [
            "The group of students is presenting today.",
            "The group of students are presenting today.",
            "The group of students were present today.",
            "The group of students have presents today.",
        ],
        "answer": "The group of students is presenting today.",
        "explanation": "The subject is group, which is singular, so it takes is.",
    },
    {
        "skill": "Subject-verb agreement",
        "prompt": "Which sentence is grammatically correct?",
        "choices": [
            "Neither Maya nor her friends are ready.",
            "Neither Maya nor her friends is ready.",
            "Neither Maya or her friends are ready.",
            "Neither Maya and her friends is ready.",
        ],
        "answer": "Neither Maya nor her friends are ready.",
        "explanation": "With neither/nor, the verb usually agrees with the subject closest to it. Friends is plural, so are is correct.",
    },
    {
        "skill": "Pronouns",
        "prompt": "Choose the correct pronoun.",
        "choices": [
            "Sofia and I volunteered at the canteen.",
            "Me and Sofia volunteered at the canteen.",
            "Sofia and me volunteered at the canteen.",
            "I and Sofia volunteered at the canteen.",
        ],
        "answer": "Sofia and I volunteered at the canteen.",
        "explanation": "Use I when the pronoun is part of the subject of the sentence.",
    },
    {
        "skill": "Pronouns",
        "prompt": "Which sentence uses whom correctly?",
        "choices": [
            "Whom did you invite to the debating final?",
            "Whom is presenting the speech?",
            "Whom wrote the persuasive essay?",
            "Whom will captain the team?",
        ],
        "answer": "Whom did you invite to the debating final?",
        "explanation": "Whom is used for the object of a verb or preposition. You invited whom.",
    },
    {
        "skill": "Commas",
        "prompt": "Choose the sentence with the best comma placement.",
        "choices": [
            "After the bell rang, the students packed their bags.",
            "After, the bell rang the students packed their bags.",
            "After the bell rang the students, packed their bags.",
            "After the bell, rang the students packed their bags.",
        ],
        "answer": "After the bell rang, the students packed their bags.",
        "explanation": "Use a comma after an introductory dependent clause.",
    },
    {
        "skill": "Commas",
        "prompt": "Which sentence correctly uses commas in a list?",
        "choices": [
            "For the excursion, bring a hat, water bottle, lunch and sunscreen.",
            "For the excursion bring, a hat water bottle lunch and sunscreen.",
            "For the excursion, bring a hat water, bottle lunch, and sunscreen.",
            "For the excursion bring a hat, water bottle lunch, and sunscreen.",
        ],
        "answer": "For the excursion, bring a hat, water bottle, lunch and sunscreen.",
        "explanation": "Commas separate items in a list. Australian style often omits the final comma unless it is needed for clarity.",
    },
    {
        "skill": "Sentence fragments",
        "prompt": "Which option is a complete sentence?",
        "choices": [
            "Because the library was closed, we studied in the classroom.",
            "Because the library was closed.",
            "In the classroom after school.",
            "Studying quietly near the windows.",
        ],
        "answer": "Because the library was closed, we studied in the classroom.",
        "explanation": "A complete sentence needs a full idea with a subject and a verb.",
    },
    {
        "skill": "Run-on sentences",
        "prompt": "Choose the best correction for this run-on sentence: The bus was late we missed the first activity.",
        "choices": [
            "The bus was late, so we missed the first activity.",
            "The bus was late we, missed the first activity.",
            "The bus was late and missed. The first activity.",
            "The bus was late, we missed the first activity.",
        ],
        "answer": "The bus was late, so we missed the first activity.",
        "explanation": "A comma with a coordinating conjunction can correctly join two independent clauses.",
    },
    {
        "skill": "Tense consistency",
        "prompt": "Choose the sentence with consistent verb tense.",
        "choices": [
            "Yesterday, I revised my notes and completed the worksheet.",
            "Yesterday, I revise my notes and completed the worksheet.",
            "Yesterday, I revised my notes and complete the worksheet.",
            "Yesterday, I am revising my notes and completed the worksheet.",
        ],
        "answer": "Yesterday, I revised my notes and completed the worksheet.",
        "explanation": "Both actions happened in the past, so both verbs should use past tense.",
    },
    {
        "skill": "Tense consistency",
        "prompt": "Which sentence keeps the tense consistent?",
        "choices": [
            "Each week, the class reads a chapter and discusses the themes.",
            "Each week, the class read a chapter and discusses the themes.",
            "Each week, the class reads a chapter and discussed the themes.",
            "Each week, the class was reading a chapter and discusses the themes.",
        ],
        "answer": "Each week, the class reads a chapter and discusses the themes.",
        "explanation": "Each week shows a regular action, so the present tense verbs reads and discusses fit.",
    },
    {
        "skill": "Commonly confused words",
        "prompt": "Choose the correct word for the sentence: I need to ___ my speech before Friday.",
        "choices": ["practise", "practice", "practised", "practical"],
        "answer": "practise",
        "explanation": "In Australian English, practise is the verb. Practice is the noun.",
    },
    {
        "skill": "Commonly confused words",
        "prompt": "Choose the correct word for the sentence: Netball ___ starts at 4 pm.",
        "choices": ["practice", "practise", "practising", "practised"],
        "answer": "practice",
        "explanation": "In Australian English, practice is the noun, as in a training session.",
    },
    {
        "skill": "Commonly confused words",
        "prompt": "Choose the correct word: The teacher gave us ___ about our essays.",
        "choices": ["advice", "advise", "advisor", "advised"],
        "answer": "advice",
        "explanation": "Advice is a noun. Advise is a verb.",
    },
    {
        "skill": "Commonly confused words",
        "prompt": "Choose the correct word: The coach will ___ the team before the final.",
        "choices": ["advise", "advice", "adviser", "advising"],
        "answer": "advise",
        "explanation": "Advise is the verb meaning to give advice.",
    },
    {
        "skill": "Commonly confused words",
        "prompt": "Which sentence uses licence/license correctly in Australian English?",
        "choices": [
            "My older brother needs a licence before he can drive alone.",
            "My older brother needs a license before he can drive alone.",
            "The council will licence a driver.",
            "The police checked his drivers license.",
        ],
        "answer": "My older brother needs a licence before he can drive alone.",
        "explanation": "In Australian English, licence is the noun and license is the verb.",
    },
    {
        "skill": "Commonly confused words",
        "prompt": "Choose the correct word: We should not ___ the results before the experiment is finished.",
        "choices": ["affect", "effect", "effort", "afford"],
        "answer": "affect",
        "explanation": "Affect is usually a verb meaning to influence. Effect is usually a noun meaning result.",
    },
    {
        "skill": "Commonly confused words",
        "prompt": "Choose the correct word: The new timetable had a positive ___ on attendance.",
        "choices": ["effect", "affect", "effort", "affection"],
        "answer": "effect",
        "explanation": "Effect is a noun meaning result or impact.",
    },
    {
        "skill": "Their, there, they're",
        "prompt": "Choose the correct sentence.",
        "choices": [
            "They're going to collect their bags over there.",
            "Their going to collect they're bags over there.",
            "There going to collect their bags over they're.",
            "They're going to collect there bags over their.",
        ],
        "answer": "They're going to collect their bags over there.",
        "explanation": "They're means they are, their shows possession, and there refers to a place.",
    },
    {
        "skill": "Your and you're",
        "prompt": "Choose the correct sentence.",
        "choices": [
            "You're welcome to bring your laptop.",
            "Your welcome to bring you're laptop.",
            "You're welcome to bring you're laptop.",
            "Your welcome to bring your laptop.",
        ],
        "answer": "You're welcome to bring your laptop.",
        "explanation": "You're means you are. Your shows possession.",
    },
    {
        "skill": "Conjunctions",
        "prompt": "Choose the best conjunction: I wanted to join the chess club, ___ the meeting was full.",
        "choices": ["but", "because", "so", "or"],
        "answer": "but",
        "explanation": "But shows contrast between wanting to join and the meeting being full.",
    },
    {
        "skill": "Conjunctions",
        "prompt": "Choose the best conjunction: We left early ___ we would arrive before the performance.",
        "choices": ["so that", "although", "unless", "whereas"],
        "answer": "so that",
        "explanation": "So that introduces the purpose of leaving early.",
    },
    {
        "skill": "Prepositions",
        "prompt": "Choose the sentence with the correct preposition.",
        "choices": [
            "The assignment is due on Friday.",
            "The assignment is due in Friday.",
            "The assignment is due at Friday.",
            "The assignment is due by Friday morning at the week.",
        ],
        "answer": "The assignment is due on Friday.",
        "explanation": "Use on with days of the week.",
    },
    {
        "skill": "Prepositions",
        "prompt": "Choose the best preposition: The science posters were displayed ___ the corridor.",
        "choices": ["in", "at", "on", "to"],
        "answer": "in",
        "explanation": "In the corridor is the natural phrase for a display located inside that space.",
    },
    {
        "skill": "Modifiers",
        "prompt": "Choose the sentence that places the modifier clearly.",
        "choices": [
            "Running across the oval, Liam dropped his hat.",
            "Liam dropped his hat running across the oval.",
            "The hat running across the oval was dropped by Liam.",
            "Dropped by Liam, running across the oval was his hat.",
        ],
        "answer": "Running across the oval, Liam dropped his hat.",
        "explanation": "The opening phrase clearly describes Liam, not the hat.",
    },
    {
        "skill": "Modifiers",
        "prompt": "Which sentence avoids a misplaced modifier?",
        "choices": [
            "The student wearing a red jumper won the prize.",
            "Wearing a red jumper, the prize was won by the student.",
            "The prize wearing a red jumper was won by the student.",
            "The student won the wearing a red jumper prize.",
        ],
        "answer": "The student wearing a red jumper won the prize.",
        "explanation": "The phrase wearing a red jumper is placed next to the student it describes.",
    },
    {
        "skill": "Parallel structure",
        "prompt": "Choose the sentence with parallel structure.",
        "choices": [
            "The project requires planning, researching and editing.",
            "The project requires planning, research and to edit.",
            "The project requires to plan, researching and editing.",
            "The project requires planning, researched and editing.",
        ],
        "answer": "The project requires planning, researching and editing.",
        "explanation": "The items in the list use the same grammatical form.",
    },
    {
        "skill": "Parallel structure",
        "prompt": "Which sentence is the most parallel?",
        "choices": [
            "A good captain listens carefully, speaks clearly and acts fairly.",
            "A good captain listens carefully, clear speech and acting fairly.",
            "A good captain is listening carefully, speaks clearly and fairness.",
            "A good captain listens carefully, speaking clearly and acts fair.",
        ],
        "answer": "A good captain listens carefully, speaks clearly and acts fairly.",
        "explanation": "List items should match in structure: listens, speaks and acts.",
    },
    {
        "skill": "Colons",
        "prompt": "Choose the sentence that uses a colon correctly.",
        "choices": [
            "Bring three items: a notebook, a pen and a calculator.",
            "Bring: three items, a notebook, a pen and a calculator.",
            "Bring three: items a notebook, a pen and a calculator.",
            "Bring three items a notebook: a pen and a calculator.",
        ],
        "answer": "Bring three items: a notebook, a pen and a calculator.",
        "explanation": "A colon can introduce a list after a complete introductory clause.",
    },
    {
        "skill": "Semicolons",
        "prompt": "Choose the sentence that uses a semicolon correctly.",
        "choices": [
            "The rain stopped; the game continued.",
            "The rain; stopped the game continued.",
            "The rain stopped the; game continued.",
            "The rain stopped; because the game continued.",
        ],
        "answer": "The rain stopped; the game continued.",
        "explanation": "A semicolon can link two closely related independent clauses.",
    },
    {
        "skill": "Capitalisation",
        "prompt": "Choose the sentence with correct capitalisation.",
        "choices": [
            "In July, our class visited the National Gallery of Victoria.",
            "In july, our class visited the national gallery of victoria.",
            "In July, our Class visited the National gallery of Victoria.",
            "In july, our class visited the National Gallery of victoria.",
        ],
        "answer": "In July, our class visited the National Gallery of Victoria.",
        "explanation": "Months and proper nouns need capital letters.",
    },
    {
        "skill": "Capitalisation",
        "prompt": "Which sentence uses capital letters correctly?",
        "choices": [
            "My aunt moved from Perth to Canberra in April.",
            "My Aunt moved from perth to Canberra in april.",
            "My aunt moved from Perth to canberra in April.",
            "My aunt moved from perth to canberra in April.",
        ],
        "answer": "My aunt moved from Perth to Canberra in April.",
        "explanation": "City names and months are proper nouns, so they need capitals. Family titles are lowercase when used after my.",
    },
    {
        "skill": "Direct speech",
        "prompt": "Choose the sentence with correct direct speech punctuation.",
        "choices": [
            "'Please open your books,' said Ms Nguyen.",
            "'Please open your books' said Ms Nguyen.",
            "'Please open your books, said Ms Nguyen.'",
            "Please open your books,' said Ms Nguyen.",
        ],
        "answer": "'Please open your books,' said Ms Nguyen.",
        "explanation": "The spoken words sit inside quotation marks, and the comma comes before the closing mark.",
    },
    {
        "skill": "Direct speech",
        "prompt": "Which sentence punctuates the question correctly?",
        "choices": [
            "'When is the geography test?' asked Noah.",
            "'When is the geography test,' asked Noah?",
            "'When is the geography test'? asked Noah.",
            "'When is the geography test' asked Noah?",
        ],
        "answer": "'When is the geography test?' asked Noah.",
        "explanation": "The question mark belongs inside the quotation marks because it is part of the spoken question.",
    },
    {
        "skill": "Relative clauses",
        "prompt": "Choose the sentence with the correct relative pronoun.",
        "choices": [
            "The student who won the award thanked her team.",
            "The student which won the award thanked her team.",
            "The student what won the award thanked her team.",
            "The student where won the award thanked her team.",
        ],
        "answer": "The student who won the award thanked her team.",
        "explanation": "Use who for people.",
    },
    {
        "skill": "Relative clauses",
        "prompt": "Choose the sentence with the clearest relative clause.",
        "choices": [
            "The book that I borrowed from the library was excellent.",
            "The book where I borrowed from the library was excellent.",
            "The book who I borrowed from the library was excellent.",
            "The book when I borrowed from the library was excellent.",
        ],
        "answer": "The book that I borrowed from the library was excellent.",
        "explanation": "That can introduce a relative clause about a thing.",
    },
    {
        "skill": "Active and passive voice",
        "prompt": "Which sentence is in active voice?",
        "choices": [
            "The students designed the mural.",
            "The mural was designed by the students.",
            "The mural was being designed.",
            "A design was completed for the mural.",
        ],
        "answer": "The students designed the mural.",
        "explanation": "In active voice, the subject performs the action.",
    },
    {
        "skill": "Active and passive voice",
        "prompt": "Choose the clearest active voice sentence.",
        "choices": [
            "The principal announced the new policy.",
            "The new policy was announced by the principal.",
            "The new policy was announced.",
            "There was an announcement of the new policy.",
        ],
        "answer": "The principal announced the new policy.",
        "explanation": "The active version names the person doing the action and is more direct.",
    },
    {
        "skill": "Comparatives",
        "prompt": "Choose the correct comparative sentence.",
        "choices": [
            "This explanation is clearer than the first one.",
            "This explanation is more clearer than the first one.",
            "This explanation is clearest than the first one.",
            "This explanation is most clear than the first one.",
        ],
        "answer": "This explanation is clearer than the first one.",
        "explanation": "Use clearer than for comparing two things.",
    },
    {
        "skill": "Comparatives",
        "prompt": "Choose the correct superlative sentence.",
        "choices": [
            "Of all the paragraphs, this one is the strongest.",
            "Of all the paragraphs, this one is stronger.",
            "Of all the paragraphs, this one is more stronger.",
            "Of all the paragraphs, this one is the most strongest.",
        ],
        "answer": "Of all the paragraphs, this one is the strongest.",
        "explanation": "Use the strongest when comparing one item with all others in a group.",
    },
    {
        "skill": "Articles",
        "prompt": "Choose the correct article.",
        "choices": [
            "We waited for an hour before the debate began.",
            "We waited for a hour before the debate began.",
            "We waited for the hour before a debate began.",
            "We waited for hour before the debate began.",
        ],
        "answer": "We waited for an hour before the debate began.",
        "explanation": "Use an before a vowel sound. Hour begins with a vowel sound because the h is silent.",
    },
    {
        "skill": "Articles",
        "prompt": "Choose the most natural sentence.",
        "choices": [
            "She gave a useful example in class.",
            "She gave an useful example in class.",
            "She gave useful example in class.",
            "She gave the useful example in class.",
        ],
        "answer": "She gave a useful example in class.",
        "explanation": "Useful starts with a consonant sound, so a is correct.",
    },
    {
        "skill": "Formal language",
        "prompt": "Choose the most formal sentence for an essay.",
        "choices": [
            "The evidence suggests that the character changes significantly.",
            "The evidence says the character totally changes heaps.",
            "The character, like, changes a lot in the story.",
            "You can see the character changes big time.",
        ],
        "answer": "The evidence suggests that the character changes significantly.",
        "explanation": "Formal writing avoids slang and uses precise academic language.",
    },
    {
        "skill": "Formal language",
        "prompt": "Choose the most suitable sentence for a school report.",
        "choices": [
            "The experiment demonstrated a clear relationship between heat and evaporation.",
            "The experiment showed heat and evaporation are kind of linked.",
            "The experiment was pretty good at showing stuff about heat.",
            "The experiment did a thing with heat and evaporation.",
        ],
        "answer": "The experiment demonstrated a clear relationship between heat and evaporation.",
        "explanation": "A report should use precise and formal wording.",
    },
]

QUIZ_SIZE = 10


def initialise_state() -> None:
    if "quiz_number" not in st.session_state:
        st.session_state.quiz_number = 0
        start_new_quiz()


def start_new_quiz() -> None:
    st.session_state.quiz_number = st.session_state.get("quiz_number", 0) + 1
    st.session_state.quiz_indexes = random.sample(range(len(QUESTIONS)), QUIZ_SIZE)
    st.session_state.submitted = False
    st.session_state.answers = {}


def answer_key(question_index: int) -> str:
    return f"quiz_{st.session_state.quiz_number}_question_{question_index}"


def collect_answers() -> dict[int, str | None]:
    return {
        question_index: st.session_state.get(answer_key(question_index))
        for question_index in st.session_state.quiz_indexes
    }


def get_score(answers: dict[int, str | None]) -> int:
    return sum(
        answers.get(question_index) == QUESTIONS[question_index]["answer"]
        for question_index in st.session_state.quiz_indexes
    )


def encouragement(score: int) -> tuple[str, str]:
    if score == QUIZ_SIZE:
        return (
            "Outstanding work.",
            "You handled every grammar point in this set. Try another round and see if you can keep the streak going.",
        )
    if score >= 8:
        return (
            "Great effort.",
            "You have strong control of these skills. Review the feedback for the couple of items that need polishing.",
        )
    if score >= 6:
        return (
            "Good progress.",
            "You are building solid habits. Focus on the skill areas listed below, then try a fresh set.",
        )
    if score >= 4:
        return (
            "Keep going.",
            "You have some useful foundations here. The explanations below will help you spot the patterns next time.",
        )
    return (
        "This is a practice round, not a final judgement.",
        "Read the feedback slowly, notice the repeated skill areas, and try again with a new set when you are ready.",
    )


def show_results(answers: dict[int, str | None]) -> None:
    score = get_score(answers)
    percentage = round(score / QUIZ_SIZE * 100)
    title, message = encouragement(score)
    missed_skills = Counter(
        QUESTIONS[question_index]["skill"]
        for question_index in st.session_state.quiz_indexes
        if answers.get(question_index) != QUESTIONS[question_index]["answer"]
    )

    st.divider()
    st.subheader("Results")
    st.success(f"{title} {message}")

    col_score, col_accuracy, col_bank = st.columns(3)
    col_score.metric("Score", f"{score}/{QUIZ_SIZE}")
    col_accuracy.metric("Accuracy", f"{percentage}%")
    col_bank.metric("Question set", f"#{st.session_state.quiz_number}")
    st.progress(score / QUIZ_SIZE)

    if missed_skills:
        focus = ", ".join(skill for skill, _ in missed_skills.most_common(3))
        st.info(f"Focus for your next round: {focus}.")
    else:
        st.info("No missed skills in this round. Try a new random set for a bigger challenge.")

    st.subheader("Question feedback")
    for display_number, question_index in enumerate(st.session_state.quiz_indexes, start=1):
        question = QUESTIONS[question_index]
        selected = answers.get(question_index)
        is_correct = selected == question["answer"]
        status = "Correct" if is_correct else "Review"

        with st.expander(f"Question {display_number}: {question['skill']} - {status}", expanded=not is_correct):
            st.write(question["prompt"])
            if is_correct:
                st.markdown(f"**Your answer:** {selected}")
            else:
                st.markdown(f"**Your answer:** {selected}")
                st.markdown(f"**Correct answer:** {question['answer']}")
            st.caption(question["explanation"])


st.set_page_config(
    page_title="Year 8+ Grammar Practice",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #f7f8fb;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #d9deea;
        border-radius: 8px;
        padding: 1rem 1.1rem;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d9deea;
        border-radius: 8px;
        padding: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

initialise_state()

st.title("Year 8+ Grammar Practice")
st.write(
    "Answer 10 random multiple choice questions. Submit your test to see your score, encouragement and targeted feedback."
)

sidebar_col_1, sidebar_col_2 = st.sidebar.columns(2)
sidebar_col_1.metric("Questions", QUIZ_SIZE)
sidebar_col_2.metric("Bank", len(QUESTIONS))
st.sidebar.write("Designed for Australian Year 8 and above grammar practice.")
if st.sidebar.button("New random test", use_container_width=True):
    start_new_quiz()
    st.rerun()

if st.session_state.submitted:
    st.info("This test has been submitted. Start a new random test when you are ready for another set.")

with st.form("grammar_quiz"):
    for display_number, question_index in enumerate(st.session_state.quiz_indexes, start=1):
        question = QUESTIONS[question_index]
        st.markdown(f"**{display_number}. {question['prompt']}**")
        st.radio(
            label=f"Question {display_number} options",
            options=question["choices"],
            key=answer_key(question_index),
            index=None,
            disabled=st.session_state.submitted,
            label_visibility="collapsed",
        )

    submitted = st.form_submit_button(
        "Submit test",
        use_container_width=True,
        disabled=st.session_state.submitted,
    )

if submitted:
    answers = collect_answers()
    unanswered = [
        display_number
        for display_number, question_index in enumerate(st.session_state.quiz_indexes, start=1)
        if answers.get(question_index) is None
    ]

    if unanswered:
        st.warning(
            "Please answer every question before submitting. Still waiting on: "
            + ", ".join(str(number) for number in unanswered)
            + "."
        )
    else:
        st.session_state.answers = answers
        st.session_state.submitted = True
        st.rerun()

if st.session_state.submitted:
    show_results(st.session_state.answers)
