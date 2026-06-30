# Student Practice Apps

Streamlit apps for students to practise Years 7-9 grammar, improve persuasive writing and prepare for Years 7-9 AMC-style maths.

## Grammar practice

- Year 7, 8 and 9 level selector
- 10 random questions per test
- Expanded grammar bank with beginner-to-advanced coverage
- Australian English examples
- Multiple choice answers with shuffled options
- Score, accuracy and encouragement after submission
- Question-by-question feedback with explanations
- New random test button

## Persuasive writing coach

- Valid reasoning feedback
- Year 7, 8 and 9 Australian Curriculum alignment checks
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

## Red Rush Tower obby

- Streamlit-hosted browser game in `obby_game.py`
- Smoother controls for ages 12-15, with double jump and mobile buttons
- Vertical tower climb inspired by Roblox-style obby games
- Only red hazards to avoid, with wider platforms and optional checkpoints
- Difficulty, tower height and visual style options
- Original browser-generated phonk-style music loops

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

For the obby game:

```powershell
python -m streamlit run obby_game.py
```

On Streamlit Community Cloud, choose `obby_game.py` as the main file.

Then open the local URL shown in the terminal, usually `http://localhost:8501`.
