# Student Practice Apps

Streamlit apps for students to practise grammar, improve persuasive writing and prepare for Year 7 AMC-style maths.

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

## AMC Year 7 maths prep

- Original AMC-style practice questions
- Year 7 topics including number, fractions, algebra, geometry, measurement, data and problem solving
- Topic and difficulty filters
- Hints before submission
- Clear Submit answers button
- Worked solutions after submission
- Score, accuracy and topic summary

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run grammar.py
```

For the persuasive writing coach:

```powershell
python -m streamlit run writting.py
```

For the AMC Year 7 maths prep app:

```powershell
python -m streamlit run Math.py
```

Then open the local URL shown in the terminal, usually `http://localhost:8501`.
