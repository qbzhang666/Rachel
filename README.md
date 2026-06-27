# Student Practice Apps

Streamlit apps for students to practise grammar, improve persuasive writing and prepare for Years 7-9 AMC-style maths.

## Grammar practice

- 10 random questions per test
- Expanded grammar bank with beginner-to-advanced coverage
- Australian English examples
- Multiple choice answers with shuffled options
- Score, accuracy and encouragement after submission
- Question-by-question feedback with explanations
- New random test button

## Persuasive writing coach

- Valid reasoning feedback
- Level 8 Australia Curriculum alignment checks
- Strong argument structure feedback
- Strong word suggestions, weak word replacements and persuasive phrase banks
- Persuasive technique scan
- 15 sample persuasive writing examples
- Topic idea lists for extra practice
- Child-friendly Submit writing button
- Self-check checklist with next-step guidance
- Improved draft and downloadable feedback report

## AMC Years 7-9 maths prep

- Original AMC-style practice questions
- Years 7, 8 and 9 levels
- Topics including number, fractions, algebra, geometry, measurement, data and problem solving
- AMC level, topic, difficulty and question-count filters
- Blank answer choices so students can see what they have answered
- Bright Take challenge button
- Clear Submit answers button with confirmation
- Worked solutions after submission
- Score, accuracy, topic summary and solution review table

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run grammar.py
```

For the persuasive writing coach:

```powershell
python -m streamlit run writting.py
```

For the AMC Years 7-9 maths prep app:

```powershell
python -m streamlit run Math.py
```

Then open the local URL shown in the terminal, usually `http://localhost:8501`.
