# Student Practice Apps

Streamlit apps for students to practise Years 7-9 grammar, improve persuasive writing, prepare for Years 7-9 AMC-style maths, and prepare for PLC-style Year 7 placement practice.

## Grammar practice

- Year 7, 8 and 9 level selector
- 5, 10, 15 or 20 questions per test
- 121-question grammar bank with beginner-to-advanced coverage
- Australian English examples
- Multiple choice answers with shuffled options
- Skill focus and smart, review or fresh practice modes
- Mistake memory that adds fresh questions from weaker skills
- Question-by-question rules, next-time strategies and progress feedback
- Practice XP, personal bests and calm progress encouragement
- Per-test CSV and progress JSON exports

## Persuasive writing coach

- Valid reasoning feedback
- Year 7, 8 and 9 Australian Curriculum alignment checks
- Strong argument structure feedback
- Strong word suggestions, weak word replacements and persuasive phrase banks
- Persuasive technique scan
- 15 sample persuasive writing examples
- 24 levelled writing missions and expanded topic idea lists
- Child-friendly Submit writing button
- Prioritised three-step revision plan and remembered weak areas
- Revision score comparisons, practice XP and personal bests
- Automatic diagnosis table with clear next-step guidance
- Improved draft plus TXT, CSV, JSON and print-ready HTML exports

## AMC Years 7-9 maths prep

- 154 original AMC-style practice questions and fresh number variants
- Years 7, 8 and 9 levels
- Topics including number, fractions, algebra, geometry, measurement, data and problem solving
- AMC level, topic, difficulty and question-count filters
- Blank answer choices so students can see what they have answered
- Bright Take challenge button
- Clear Submit answers button with confirmation
- Smart, review or fresh practice modes
- Mistake memory that adds similar questions with different values
- Worked solutions and next-time strategies after submission
- Score, accuracy, personal best, topic summary and solution review table
- Per-test CSV and progress JSON exports

## Red Rush Tower obby

- Streamlit-hosted browser game in `obby_game.py`
- Smoother controls for ages 12-15, with double jump and mobile buttons
- Vertical tower climb inspired by Roblox-style obby games
- Only red hazards to avoid, with wider platforms and optional checkpoints
- Difficulty, tower height and visual style options
- Original browser-generated phonk-style music loops

## DELF Junior A1 French prep

- Current four-skill DELF Junior A1 exam overview
- 10 listening challenges using selected audio from the completed local French course
- 10 original everyday reading documents with detailed answer evidence
- 48-question grammar and vocabulary lab with smart mistake review
- Two-part writing practice: form completion and a message of at least 40 words
- Automatic writing feedback by criterion, with TXT, CSV and printable HTML exports
- All three speaking tasks: guided interview, information cards and interactive roleplay
- Unticked answers, clear submission confirmation, progress XP and downloadable records

## PLC Year 7 level test prep

- Independent PLC-style preparation app in `PLC_Year7.py`
- Original practice questions only; not official PLC or Studocu material
- Expanded two-month bank: 232 maths questions, 44 reading passages, 124 reading questions, 154 grammar/vocabulary questions and 40 writing prompts
- Completed areas can now be practised at harder Year 8-9 level: algebra and patterns, apostrophes, author purpose, fractions and ratios, vocabulary and spelling
- New learning sequence added: linear equations, consecutive-number algebra, then Pythagoras
- Quick-start buttons for harder completed-topic practice and the next learning sequence
- Mixed mock tests for Year 7 entry-level maths, reading, grammar and vocabulary
- Extension maths questions for stronger placement readiness
- Reading passages with inference, vocabulary, tone and evidence questions
- Writing tasks for persuasive, creative and analytical responses
- Blank answer choices, submission confirmation, worked solutions and exam-trap feedback
- Practice record and CSV exports for parent/student review

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

For the DELF Junior A1 French preparation app:

```powershell
python -m streamlit run Delf_A1.py
```

For the PLC Year 7 level test preparation app:

```powershell
python -m streamlit run PLC_Year7.py
```

On Streamlit Community Cloud, choose `obby_game.py` as the main file.

Then open the local URL shown in the terminal, usually `http://localhost:8501`.
