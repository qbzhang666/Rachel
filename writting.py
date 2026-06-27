import html
import re
import sys
from collections import Counter
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None


PERSUASIVE_TECHNIQUES = {
    "Rhetorical question": [
        "should",
        "why",
        "how",
        "what if",
        "can we",
        "do we",
        "is it fair",
    ],
    "Inclusive language": ["we", "us", "our", "ourselves", "together"],
    "Direct address": ["you", "your", "yours"],
    "High modality": [
        "must",
        "need",
        "needs",
        "should",
        "will",
        "cannot",
        "undeniably",
        "certainly",
    ],
    "Emotive language": [
        "harmful",
        "devastating",
        "urgent",
        "unfair",
        "powerful",
        "dangerous",
        "valuable",
        "vital",
        "responsible",
        "shocking",
        "hopeful",
    ],
    "Evidence appeal": [
        "research",
        "evidence",
        "data",
        "statistics",
        "expert",
        "study",
        "survey",
        "according to",
    ],
}

REASONING_MARKERS = [
    "because",
    "therefore",
    "so",
    "as a result",
    "this means",
    "this shows",
    "for this reason",
    "consequently",
    "if",
    "then",
    "leads to",
    "causes",
]

EVIDENCE_MARKERS = [
    "for example",
    "for instance",
    "evidence",
    "research",
    "data",
    "statistics",
    "survey",
    "study",
    "according to",
    "expert",
    "source",
    "case",
]

COUNTER_ARGUMENT_MARKERS = [
    "although",
    "however",
    "some people argue",
    "opponents",
    "critics",
    "on the other hand",
    "while",
    "despite",
    "nevertheless",
]

REFUTATION_MARKERS = [
    "however",
    "but",
    "yet",
    "nevertheless",
    "this overlooks",
    "this ignores",
    "in reality",
    "more importantly",
]

STRONG_WORDS = [
    "essential",
    "vital",
    "urgent",
    "significant",
    "responsible",
    "effective",
    "fair",
    "equitable",
    "sustainable",
    "beneficial",
    "powerful",
    "convincing",
    "reasonable",
    "credible",
    "practical",
    "harmful",
    "damaging",
    "valuable",
    "necessary",
    "immediate",
    "meaningful",
    "serious",
    "lasting",
    "positive",
    "negative",
    "proven",
    "reliable",
    "thoughtful",
]

WEAK_WORD_REPLACEMENTS = {
    "good": ["effective", "valuable", "beneficial"],
    "bad": ["harmful", "damaging", "unfair"],
    "very": ["extremely", "deeply", "significantly"],
    "really": ["genuinely", "clearly", "strongly"],
    "thing": ["issue", "reason", "factor"],
    "things": ["issues", "reasons", "factors"],
    "stuff": ["evidence", "details", "materials"],
    "nice": ["positive", "respectful", "encouraging"],
    "big": ["significant", "major", "substantial"],
    "a lot": ["many", "frequently", "a significant amount"],
    "I think": ["It is clear that", "The evidence suggests that"],
}

OVERCLAIM_WORDS = [
    "always",
    "never",
    "everyone",
    "no one",
    "all",
    "none",
    "definitely",
    "obviously",
    "proves",
]

FORMAL_TONE_WARNINGS = [
    "lol",
    "u",
    "ur",
    "gonna",
    "wanna",
    "kinda",
    "sorta",
    "you guys",
]

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "but",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "our",
    "so",
    "that",
    "the",
    "their",
    "there",
    "this",
    "to",
    "was",
    "we",
    "were",
    "will",
    "with",
    "you",
    "your",
}

SAMPLE_WRITING = (
    "I think school uniforms are good because they make students look the same. "
    "Uniforms can stop people from showing off expensive clothes. This is important because some students feel left out.\n\n"
    "Another reason is that uniforms save time in the morning. Students do not need to choose what to wear, so they can focus on school.\n\n"
    "Some people say uniforms are bad because they stop students from showing personality. However, students can still show personality through their actions, ideas and friendships.\n\n"
    "In conclusion, school uniforms should stay because they are fair and useful."
)


@dataclass
class ScoreCard:
    score: int
    strengths: list[str]
    improvements: list[str]


@dataclass
class Analysis:
    words: list[str]
    sentences: list[str]
    paragraphs: list[str]
    reasoning: ScoreCard
    curriculum: ScoreCard
    arguments: ScoreCard
    strong_words: ScoreCard
    techniques: ScoreCard
    technique_hits: dict[str, list[str]]
    weak_word_hits: dict[str, int]
    overclaims: list[str]
    overall_score: int


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def split_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    if len(paragraphs) > 1:
        return paragraphs
    sentences = split_sentences(text)
    if len(sentences) >= 6:
        grouped = []
        for index in range(0, len(sentences), 3):
            grouped.append(" ".join(sentences[index : index + 3]))
        return grouped
    return paragraphs


def contains_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(re.search(rf"\b{re.escape(term)}\b", lower) for term in terms)


def count_terms(text: str, terms: list[str]) -> int:
    lower = text.lower()
    total = 0
    for term in terms:
        total += len(re.findall(rf"\b{re.escape(term)}\b", lower))
    return total


def unique_terms_found(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", lower)]


def clamp_score(score: int) -> int:
    return max(0, min(100, score))


def get_first_sentence(paragraph: str) -> str:
    sentences = split_sentences(paragraph)
    return sentences[0] if sentences else paragraph.strip()


def has_position(text: str) -> bool:
    opening = " ".join(split_sentences(text)[:3]).lower()
    position_markers = [
        "should",
        "must",
        "need to",
        "needs to",
        "ought to",
        "is essential",
        "is vital",
        "is necessary",
        "i believe",
        "i strongly believe",
        "it is clear",
        "we must",
    ]
    return contains_any(opening, position_markers)


def detect_techniques(text: str, sentences: list[str], words: list[str]) -> dict[str, list[str]]:
    lower_text = text.lower()
    hits: dict[str, list[str]] = {}

    rhetorical_questions = []
    for sentence in sentences:
        lower_sentence = sentence.lower()
        if sentence.endswith("?") and any(marker in lower_sentence for marker in PERSUASIVE_TECHNIQUES["Rhetorical question"]):
            rhetorical_questions.append(sentence)
    hits["Rhetorical question"] = rhetorical_questions

    for technique, markers in PERSUASIVE_TECHNIQUES.items():
        if technique == "Rhetorical question":
            continue
        found = unique_terms_found(lower_text, markers)
        hits[technique] = found

    triplets = re.findall(
        r"\b([A-Za-z]{3,})\b,\s+\b([A-Za-z]{3,})\b,\s+(?:and\s+)?\b([A-Za-z]{3,})\b",
        text,
    )
    hits["Rule of three"] = [", ".join(match) for match in triplets[:5]]

    content_words = [word for word in words if len(word) >= 5 and word not in STOP_WORDS]
    repeated = [
        word
        for word, count in Counter(content_words).most_common(8)
        if count >= 3
    ]
    hits["Purposeful repetition"] = repeated

    contrast_hits = []
    for pattern in [r"\bnot only\b.*\bbut also\b", r"\bwhile\b.*\bhowever\b", r"\binstead of\b"]:
        contrast_hits.extend(re.findall(pattern, lower_text))
    hits["Contrast"] = contrast_hits[:5]

    return hits


def find_weak_words(text: str) -> dict[str, int]:
    lower = text.lower()
    hits = {}
    for weak_word in WEAK_WORD_REPLACEMENTS:
        hits[weak_word] = len(re.findall(rf"\b{re.escape(weak_word)}\b", lower))
    return {word: count for word, count in hits.items() if count > 0}


def find_overclaims(sentences: list[str]) -> list[str]:
    overclaims = []
    for sentence in sentences:
        lower = sentence.lower()
        has_overclaim = contains_any(lower, OVERCLAIM_WORDS)
        has_support = contains_any(lower, EVIDENCE_MARKERS + REASONING_MARKERS)
        if has_overclaim and not has_support:
            overclaims.append(sentence)
    return overclaims[:5]


def score_reasoning(text: str, sentences: list[str], overclaims: list[str]) -> ScoreCard:
    score = 20
    strengths = []
    improvements = []

    if has_position(text):
        score += 20
        strengths.append("The opening shows a clear position.")
    else:
        improvements.append("Add a clear contention in the introduction using words like must, should, or need to.")

    evidence_count = count_terms(text, EVIDENCE_MARKERS)
    if evidence_count >= 3:
        score += 20
        strengths.append("Evidence signals appear several times.")
    elif evidence_count >= 1:
        score += 10
        strengths.append("There is some evidence language.")
        improvements.append("Add more specific facts, examples, statistics, or expert views.")
    else:
        improvements.append("Support each main claim with evidence instead of only opinion.")

    reasoning_count = count_terms(text, REASONING_MARKERS)
    if reasoning_count >= 5:
        score += 25
        strengths.append("Reasoning links claims to consequences.")
    elif reasoning_count >= 2:
        score += 15
        strengths.append("Some reasoning connectives are used.")
        improvements.append("Explain why each piece of evidence proves the point.")
    else:
        improvements.append("Use because, therefore, this shows, and as a result to make the reasoning visible.")

    if contains_any(text, COUNTER_ARGUMENT_MARKERS):
        score += 15
        strengths.append("A counterargument is included.")
    else:
        improvements.append("Include one opposing view, then refute it.")

    if overclaims:
        score -= min(20, len(overclaims) * 6)
        improvements.append("Qualify overclaims such as always, never, everyone, or proves unless evidence is given.")

    return ScoreCard(clamp_score(score), strengths, improvements)


def score_curriculum(text: str, words: list[str], sentences: list[str], paragraphs: list[str]) -> ScoreCard:
    score = 20
    strengths = []
    improvements = []

    word_count = len(words)
    if word_count >= 350:
        score += 15
        strengths.append("The draft has enough length for developed Year 8 argument writing.")
    elif word_count >= 180:
        score += 10
        strengths.append("The draft has a workable length.")
        improvements.append("Develop the body paragraphs further for a stronger Year 8 response.")
    else:
        improvements.append("Aim for a fuller persuasive response with an introduction, body paragraphs, and conclusion.")

    if len(paragraphs) >= 4:
        score += 20
        strengths.append("Paragraphing supports a clear persuasive structure.")
    elif len(paragraphs) >= 2:
        score += 10
        improvements.append("Separate the writing into introduction, body paragraphs, and conclusion.")
    else:
        improvements.append("Use paragraphs to organise the argument.")

    cohesive_devices = count_terms(
        text,
        [
            "firstly",
            "secondly",
            "finally",
            "therefore",
            "however",
            "furthermore",
            "moreover",
            "in addition",
            "as a result",
            "consequently",
        ],
    )
    if cohesive_devices >= 4:
        score += 20
        strengths.append("Cohesive devices help ideas flow.")
    elif cohesive_devices >= 2:
        score += 10
        improvements.append("Use more linking phrases to guide the reader through the argument.")
    else:
        improvements.append("Add linking phrases such as firstly, furthermore, however, and therefore.")

    advanced_words = [word for word in words if len(word) >= 9 and word not in STOP_WORDS]
    if len(set(advanced_words)) >= 10:
        score += 15
        strengths.append("Vocabulary shows a developing Year 8 level.")
    elif len(set(advanced_words)) >= 5:
        score += 8
        improvements.append("Upgrade repeated simple words with more precise vocabulary.")
    else:
        improvements.append("Add more precise and formal vocabulary.")

    sentence_lengths = [len(tokenize_words(sentence)) for sentence in sentences]
    if sentence_lengths:
        average_length = sum(sentence_lengths) / len(sentence_lengths)
        has_variety = max(sentence_lengths) - min(sentence_lengths) >= 10 if len(sentence_lengths) > 1 else False
        if 10 <= average_length <= 28 and has_variety:
            score += 15
            strengths.append("Sentence length is controlled and varied.")
        elif 8 <= average_length <= 32:
            score += 8
            improvements.append("Vary sentence openings and lengths for stronger control.")
        else:
            improvements.append("Check sentence length: avoid fragments, run-ons, and overly short repeated sentences.")

    if contains_any(text, FORMAL_TONE_WARNINGS):
        score -= 10
        improvements.append("Keep the tone formal by removing slang and texting language.")

    return ScoreCard(clamp_score(score), strengths, improvements)


def score_arguments(text: str, paragraphs: list[str]) -> ScoreCard:
    score = 20
    strengths = []
    improvements = []

    topic_sentence_count = 0
    for paragraph in paragraphs:
        first_sentence = get_first_sentence(paragraph)
        if len(tokenize_words(first_sentence)) >= 7:
            topic_sentence_count += 1

    if topic_sentence_count >= 3:
        score += 20
        strengths.append("Body paragraphs begin with clear topic sentences.")
    elif topic_sentence_count >= 1:
        score += 10
        improvements.append("Begin each body paragraph with a clear reason that supports the contention.")
    else:
        improvements.append("Add topic sentences to announce each main argument.")

    evidence_count = count_terms(text, EVIDENCE_MARKERS)
    if evidence_count >= 3:
        score += 25
        strengths.append("Arguments are supported by evidence signals.")
    elif evidence_count >= 1:
        score += 12
        improvements.append("Make each example specific and connect it back to the contention.")
    else:
        improvements.append("Add examples, facts, statistics, expert views, or scenarios.")

    if contains_any(text, COUNTER_ARGUMENT_MARKERS) and contains_any(text, REFUTATION_MARKERS):
        score += 20
        strengths.append("The argument addresses and challenges an opposing view.")
    elif contains_any(text, COUNTER_ARGUMENT_MARKERS):
        score += 10
        improvements.append("After the opposing view, explain why your view is stronger.")
    else:
        improvements.append("Add a counterargument paragraph to make the argument more balanced and convincing.")

    conclusion_markers = ["in conclusion", "ultimately", "therefore", "overall", "to conclude"]
    final_paragraph = paragraphs[-1] if paragraphs else ""
    if contains_any(final_paragraph, conclusion_markers):
        score += 15
        strengths.append("The ending signals a conclusion.")
    else:
        improvements.append("Finish with a conclusion that restates the contention and leaves the reader with a call to action.")

    return ScoreCard(clamp_score(score), strengths, improvements)


def score_strong_words(text: str, words: list[str], weak_word_hits: dict[str, int]) -> ScoreCard:
    score = 25
    strengths = []
    improvements = []

    strong_hits = unique_terms_found(text, STRONG_WORDS)
    if len(strong_hits) >= 10:
        score += 35
        strengths.append("Strong vocabulary is used frequently.")
    elif len(strong_hits) >= 5:
        score += 25
        strengths.append("There is some strong vocabulary.")
        improvements.append("Add more precise high-impact words to key claims.")
    elif len(strong_hits) >= 2:
        score += 12
        improvements.append("Use more strong, specific words in the topic sentences and conclusion.")
    else:
        improvements.append("Replace simple words with stronger persuasive vocabulary.")

    high_modality_count = count_terms(text, PERSUASIVE_TECHNIQUES["High modality"])
    if high_modality_count >= 4:
        score += 25
        strengths.append("High modality words make the stance confident.")
    elif high_modality_count >= 1:
        score += 12
        improvements.append("Use more high modality words such as must, should, cannot, and need.")
    else:
        improvements.append("Add high modality language to sound more decisive.")

    weak_total = sum(weak_word_hits.values())
    if weak_total == 0:
        score += 15
        strengths.append("Few weak filler words were detected.")
    elif weak_total <= 4:
        score += 8
        improvements.append("Replace remaining weak words with more precise alternatives.")
    else:
        score -= min(25, weak_total * 3)
        improvements.append("Too many weak words reduce the force of the argument.")

    repeated_words = [
        word for word, count in Counter(words).items()
        if count >= 6 and word not in STOP_WORDS and len(word) >= 4
    ]
    if repeated_words:
        score -= min(12, len(repeated_words) * 4)
        improvements.append("Avoid accidental repetition by using synonyms for repeated key words.")

    return ScoreCard(clamp_score(score), strengths, improvements)


def score_techniques(technique_hits: dict[str, list[str]]) -> ScoreCard:
    score = 15
    strengths = []
    improvements = []

    used_techniques = [name for name, hits in technique_hits.items() if hits]
    technique_count = len(used_techniques)

    if technique_count >= 6:
        score += 65
        strengths.append("A broad range of persuasive techniques is used.")
    elif technique_count >= 4:
        score += 45
        strengths.append("Several persuasive techniques are present.")
        improvements.append("Add one or two techniques where they will strengthen the argument.")
    elif technique_count >= 2:
        score += 25
        improvements.append("Use a wider range of techniques, not just one repeated method.")
    else:
        improvements.append("Add rhetorical questions, inclusive language, emotive language, evidence appeals, and high modality.")

    if technique_hits.get("Evidence appeal"):
        score += 10
    else:
        improvements.append("Use evidence appeals to make persuasion feel credible.")

    if technique_hits.get("Rhetorical question"):
        score += 10
    else:
        improvements.append("Add a rhetorical question where it will make the reader reflect.")

    return ScoreCard(clamp_score(score), strengths, improvements)


def analyse_text(text: str) -> Analysis:
    words = tokenize_words(text)
    sentences = split_sentences(text)
    paragraphs = split_paragraphs(text)
    weak_word_hits = find_weak_words(text)
    overclaims = find_overclaims(sentences)
    technique_hits = detect_techniques(text, sentences, words)

    reasoning = score_reasoning(text, sentences, overclaims)
    curriculum = score_curriculum(text, words, sentences, paragraphs)
    arguments = score_arguments(text, paragraphs)
    strong_words = score_strong_words(text, words, weak_word_hits)
    techniques = score_techniques(technique_hits)

    overall_score = round(
        (
            reasoning.score * 0.25
            + curriculum.score * 0.2
            + arguments.score * 0.25
            + strong_words.score * 0.15
            + techniques.score * 0.15
        )
    )

    return Analysis(
        words=words,
        sentences=sentences,
        paragraphs=paragraphs,
        reasoning=reasoning,
        curriculum=curriculum,
        arguments=arguments,
        strong_words=strong_words,
        techniques=techniques,
        technique_hits=technique_hits,
        weak_word_hits=weak_word_hits,
        overclaims=overclaims,
        overall_score=overall_score,
    )


def score_label(score: int) -> str:
    if score >= 85:
        return "Advanced"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Developing"
    return "Needs work"


def replace_weak_phrases(text: str) -> str:
    improved = text
    direct_replacements = {
        "I think": "It is clear that",
        "really good": "highly valuable",
        "very good": "highly effective",
        "really bad": "seriously harmful",
        "very bad": "deeply damaging",
        "a lot of": "many",
        "lots of": "many",
        "stuff": "evidence",
        "things": "factors",
        "thing": "issue",
    }
    for weak, replacement in direct_replacements.items():
        improved = re.sub(rf"\b{re.escape(weak)}\b", replacement, improved, flags=re.IGNORECASE)
    return improved


def infer_topic(text: str, topic: str) -> str:
    if topic.strip():
        return topic.strip()
    words = [
        word
        for word in tokenize_words(text)
        if word not in STOP_WORDS and len(word) >= 5
    ]
    if not words:
        return "this issue"
    common = [word for word, _ in Counter(words).most_common(3)]
    return " ".join(common)


def build_improved_draft(text: str, topic: str, audience: str) -> str:
    paragraphs = split_paragraphs(replace_weak_phrases(text))
    topic_phrase = infer_topic(text, topic)
    audience_phrase = audience.strip() or "readers"

    if not paragraphs:
        return (
            f"It is clear that {topic_phrase} deserves serious attention. "
            f"{audience_phrase.capitalize()} should recognise that this issue matters because it affects fairness, wellbeing, and future choices.\n\n"
            "Firstly, [add your strongest reason here]. For example, [add a specific fact, statistic, expert view, or real scenario]. "
            "This evidence matters because [explain how it proves your contention].\n\n"
            "Some people may argue that [add an opposing view]. However, this argument overlooks [explain the weakness]. "
            "A more responsible approach is to [state your solution or preferred action].\n\n"
            f"Ultimately, {topic_phrase} should not be ignored. If we want a fairer and more thoughtful community, we must act with purpose and confidence."
        )

    opening = paragraphs[0]
    if not has_position(opening):
        opening = (
            f"It is clear that {topic_phrase} is an important issue for {audience_phrase}. "
            f"{opening}"
        )

    improved_parts = [opening]
    body_paragraphs = paragraphs[1:-1] if len(paragraphs) >= 3 else paragraphs[1:]

    for index, paragraph in enumerate(body_paragraphs, start=1):
        paragraph_text = paragraph
        if not contains_any(paragraph_text, EVIDENCE_MARKERS):
            paragraph_text += " For example, [add a specific fact, statistic, expert view, or scenario here]."
        if not contains_any(paragraph_text, REASONING_MARKERS):
            paragraph_text += " This shows why the argument is reasonable and important."
        if index == 1 and not paragraph_text.lower().startswith(("firstly", "first", "to begin")):
            paragraph_text = "Firstly, " + paragraph_text[0].lower() + paragraph_text[1:]
        elif index == 2 and not paragraph_text.lower().startswith(("secondly", "furthermore", "another")):
            paragraph_text = "Furthermore, " + paragraph_text[0].lower() + paragraph_text[1:]
        improved_parts.append(paragraph_text)

    if not contains_any(text, COUNTER_ARGUMENT_MARKERS):
        improved_parts.append(
            "Although some people may disagree, this opposing view is less convincing because [explain what it ignores]. "
            "A stronger position considers both the immediate impact and the long-term consequences."
        )

    conclusion = paragraphs[-1] if len(paragraphs) >= 2 else ""
    if conclusion and contains_any(conclusion, ["in conclusion", "ultimately", "therefore", "overall", "to conclude"]):
        improved_parts.append(conclusion)
    else:
        improved_parts.append(
            f"Ultimately, {topic_phrase} requires a confident response. "
            "The evidence, reasoning, and consequences all show that action is necessary."
        )

    return "\n\n".join(improved_parts)


def build_feedback_report(analysis: Analysis, text: str, topic: str, audience: str) -> str:
    categories = [
        ("Valid reasoning", analysis.reasoning),
        ("Level 8 Australia Curriculum", analysis.curriculum),
        ("Strong arguments", analysis.arguments),
        ("Use of strong words", analysis.strong_words),
        ("Persuasive technique", analysis.techniques),
    ]
    lines = [
        "Persuasive Writing Feedback",
        "",
        f"Topic: {topic or 'Not provided'}",
        f"Audience: {audience or 'Not provided'}",
        f"Overall score: {analysis.overall_score}/100 ({score_label(analysis.overall_score)})",
        "",
        f"Word count: {len(analysis.words)}",
        f"Sentence count: {len(analysis.sentences)}",
        f"Paragraph count: {len(analysis.paragraphs)}",
        "",
    ]

    for title, card in categories:
        lines.append(f"{title}: {card.score}/100 ({score_label(card.score)})")
        for item in card.strengths:
            lines.append(f"  Strength: {item}")
        for item in card.improvements:
            lines.append(f"  Improve: {item}")
        lines.append("")

    if analysis.overclaims:
        lines.append("Overclaims to check:")
        lines.extend(f"  - {sentence}" for sentence in analysis.overclaims)
        lines.append("")

    if analysis.weak_word_hits:
        lines.append("Weak words to upgrade:")
        for word, count in analysis.weak_word_hits.items():
            replacements = ", ".join(WEAK_WORD_REPLACEMENTS[word])
            lines.append(f"  - {word} ({count}): try {replacements}")
        lines.append("")

    lines.append("Improved draft:")
    lines.append(build_improved_draft(text, topic, audience))
    return "\n".join(lines)


def render_score_card(title: str, card: ScoreCard) -> None:
    st.subheader(title)
    st.metric("Score", f"{card.score}/100", score_label(card.score))
    st.progress(card.score)

    if card.strengths:
        st.markdown("**What is working**")
        for strength in card.strengths:
            st.write(f"- {strength}")

    if card.improvements:
        st.markdown("**Next improvements**")
        for improvement in card.improvements:
            st.write(f"- {improvement}")


def render_technique_table(analysis: Analysis) -> None:
    rows = []
    for technique, hits in analysis.technique_hits.items():
        examples = ", ".join(hits[:3]) if hits else "Not detected"
        rows.append(
            {
                "Technique": technique,
                "Detected": "Yes" if hits else "No",
                "Examples": examples,
            }
        )
    st.dataframe(rows, hide_index=True, use_container_width=True)


def render_word_bank() -> None:
    st.markdown("**Upgrade common weak words**")
    rows = []
    for weak, replacements in WEAK_WORD_REPLACEMENTS.items():
        rows.append(
            {
                "Instead of": weak,
                "Try": ", ".join(replacements),
            }
        )
    st.dataframe(rows, hide_index=True, use_container_width=True)

    st.markdown("**Strong persuasive words**")
    columns = st.columns(4)
    for index, word in enumerate(STRONG_WORDS):
        columns[index % 4].write(f"- {word}")


def render_checklist(analysis: Analysis) -> None:
    checklist = [
        ("Clear contention in the introduction", has_position(" ".join(analysis.sentences[:3]))),
        ("At least three organised paragraphs", len(analysis.paragraphs) >= 3),
        ("Evidence or examples are included", count_terms(" ".join(analysis.sentences), EVIDENCE_MARKERS) >= 1),
        ("Reasoning links are visible", count_terms(" ".join(analysis.sentences), REASONING_MARKERS) >= 2),
        ("Counterargument is addressed", contains_any(" ".join(analysis.sentences), COUNTER_ARGUMENT_MARKERS)),
        ("High modality language is used", count_terms(" ".join(analysis.sentences), PERSUASIVE_TECHNIQUES["High modality"]) >= 1),
        ("At least three persuasive techniques are used", len([hits for hits in analysis.technique_hits.values() if hits]) >= 3),
        ("Formal tone is mostly controlled", not contains_any(" ".join(analysis.sentences), FORMAL_TONE_WARNINGS)),
    ]

    for item, done in checklist:
        st.checkbox(item, value=done, disabled=True)


def run_console_app() -> None:
    print("Persuasive Writing Coach")
    print("Streamlit is not installed in this Python environment, so console mode is running.")
    print("Paste writing, then press Ctrl+Z and Enter on Windows to analyse.")
    print()

    text = sys.stdin.read().strip()
    if not text:
        print("No writing pasted. Analysing the built-in sample instead.")
        text = SAMPLE_WRITING

    analysis = analyse_text(text)
    print()
    print(f"Overall: {analysis.overall_score}/100 ({score_label(analysis.overall_score)})")
    print(f"Valid reasoning: {analysis.reasoning.score}/100")
    print(f"Level 8 Australia Curriculum: {analysis.curriculum.score}/100")
    print(f"Strong arguments: {analysis.arguments.score}/100")
    print(f"Use of strong words: {analysis.strong_words.score}/100")
    print(f"Persuasive technique: {analysis.techniques.score}/100")
    print()

    for title, card in [
        ("Valid reasoning", analysis.reasoning),
        ("Level 8 Australia Curriculum", analysis.curriculum),
        ("Strong arguments", analysis.arguments),
        ("Use of strong words", analysis.strong_words),
        ("Persuasive technique", analysis.techniques),
    ]:
        print(title)
        for improvement in card.improvements[:3]:
            print(f"- {improvement}")
        print()

    print("Improved draft")
    print(build_improved_draft(text, "", ""))


def escape_html(value: str) -> str:
    return html.escape(value, quote=True)


def render_html_list(items: list[str], empty_message: str) -> str:
    if not items:
        return f"<li>{escape_html(empty_message)}</li>"
    return "".join(f"<li>{escape_html(item)}</li>" for item in items)


def render_html_score(title: str, card: ScoreCard) -> str:
    return f"""
    <section class="panel">
        <div class="panel-head">
            <h2>{escape_html(title)}</h2>
            <span class="badge">{card.score}/100 {escape_html(score_label(card.score))}</span>
        </div>
        <div class="bar"><span style="width:{card.score}%"></span></div>
        <h3>What is working</h3>
        <ul>{render_html_list(card.strengths, "No clear strength detected yet.")}</ul>
        <h3>Next improvements</h3>
        <ul>{render_html_list(card.improvements, "Keep refining this area.")}</ul>
    </section>
    """


def render_http_page(
    writing: str = "",
    topic: str = "",
    audience: str = "",
    analysis: Analysis | None = None,
) -> str:
    report = ""
    improved = ""
    scores = ""
    technique_rows = ""
    weak_words = ""
    overclaims = ""

    if analysis is not None:
        improved = build_improved_draft(writing, topic, audience)
        report = build_feedback_report(analysis, writing, topic, audience)
        cards = [
            ("1. Valid reasoning", analysis.reasoning),
            ("2. Level 8 Australia Curriculum", analysis.curriculum),
            ("3. Strong arguments", analysis.arguments),
            ("4. Use of strong words", analysis.strong_words),
            ("5. Persuasive technique", analysis.techniques),
        ]
        scores = "".join(render_html_score(title, card) for title, card in cards)
        technique_rows = "".join(
            "<tr>"
            f"<td>{escape_html(name)}</td>"
            f"<td>{'Yes' if hits else 'No'}</td>"
            f"<td>{escape_html(', '.join(hits[:3]) if hits else 'Not detected')}</td>"
            "</tr>"
            for name, hits in analysis.technique_hits.items()
        )
        weak_words = "".join(
            f"<li><strong>{escape_html(word)}</strong> appeared {count} time(s). Try {escape_html(', '.join(WEAK_WORD_REPLACEMENTS[word]))}.</li>"
            for word, count in analysis.weak_word_hits.items()
        )
        overclaims = "".join(f"<li>{escape_html(sentence)}</li>" for sentence in analysis.overclaims)

    results_html = ""
    if analysis is not None:
        results_html = f"""
        <section class="summary">
            <div>
                <span>Overall</span>
                <strong>{analysis.overall_score}/100</strong>
                <small>{escape_html(score_label(analysis.overall_score))}</small>
            </div>
            <div><span>Words</span><strong>{len(analysis.words)}</strong><small>total</small></div>
            <div><span>Sentences</span><strong>{len(analysis.sentences)}</strong><small>total</small></div>
            <div><span>Paragraphs</span><strong>{len(analysis.paragraphs)}</strong><small>total</small></div>
        </section>

        <main class="grid">
            {scores}
        </main>

        <section class="panel full">
            <h2>Technique scan</h2>
            <table>
                <thead><tr><th>Technique</th><th>Detected</th><th>Examples</th></tr></thead>
                <tbody>{technique_rows}</tbody>
            </table>
        </section>

        <section class="two-col">
            <div class="panel">
                <h2>Claims to qualify</h2>
                <ul>{overclaims or "<li>No unsupported overclaims detected.</li>"}</ul>
            </div>
            <div class="panel">
                <h2>Weak words found</h2>
                <ul>{weak_words or "<li>No common weak words detected.</li>"}</ul>
            </div>
        </section>

        <section class="panel full">
            <h2>Improved draft</h2>
            <textarea readonly>{escape_html(improved)}</textarea>
        </section>

        <section class="panel full">
            <h2>Feedback report</h2>
            <textarea readonly>{escape_html(report)}</textarea>
        </section>
        """

    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Persuasive Writing Coach</title>
    <style>
        :root {{
            color-scheme: light;
            --ink: #172033;
            --muted: #5b6472;
            --line: #d9e2ec;
            --surface: #ffffff;
            --soft: #f5f7fa;
            --accent: #2563eb;
            --accent-dark: #1e3a8a;
            --green: #0f766e;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            color: var(--ink);
            background: var(--soft);
        }}
        header {{
            background: var(--surface);
            border-bottom: 1px solid var(--line);
            padding: 24px max(24px, calc((100vw - 1180px) / 2));
        }}
        h1 {{ margin: 0; font-size: 2rem; }}
        h2 {{ margin: 0; font-size: 1.15rem; }}
        h3 {{ margin: 18px 0 8px; font-size: 0.95rem; color: var(--accent-dark); }}
        form, .summary, .grid, .two-col, .panel.full {{
            width: min(1180px, calc(100% - 32px));
            margin: 20px auto;
        }}
        form {{
            display: grid;
            grid-template-columns: minmax(0, 2fr) minmax(260px, 1fr);
            gap: 16px;
            align-items: start;
        }}
        label {{ display: block; font-weight: 700; margin-bottom: 8px; }}
        textarea, input {{
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px;
            font: inherit;
            background: var(--surface);
            color: var(--ink);
        }}
        textarea {{ min-height: 320px; resize: vertical; line-height: 1.5; }}
        .side {{
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
        }}
        .side label + input {{ margin-bottom: 14px; }}
        .actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }}
        button, .sample-link {{
            border: 0;
            border-radius: 8px;
            background: var(--accent);
            color: white;
            padding: 10px 14px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 40px;
        }}
        .sample-link {{ background: var(--green); }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
        }}
        .summary div, .panel {{
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
        }}
        .summary span, .summary small {{
            display: block;
            color: var(--muted);
            font-size: 0.9rem;
        }}
        .summary strong {{ display: block; font-size: 1.8rem; margin: 6px 0; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
        }}
        .two-col {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
        }}
        .panel-head {{
            display: flex;
            justify-content: space-between;
            gap: 10px;
            align-items: center;
        }}
        .badge {{
            background: #e0ecff;
            color: var(--accent-dark);
            border-radius: 999px;
            padding: 6px 10px;
            font-weight: 700;
            white-space: nowrap;
        }}
        .bar {{
            height: 10px;
            background: #e6ebf2;
            border-radius: 999px;
            overflow: hidden;
            margin: 14px 0;
        }}
        .bar span {{
            display: block;
            height: 100%;
            background: var(--accent);
        }}
        ul {{ padding-left: 20px; margin: 8px 0 0; }}
        li {{ margin: 6px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th, td {{ border-bottom: 1px solid var(--line); text-align: left; padding: 10px; vertical-align: top; }}
        th {{ color: var(--accent-dark); }}
        .full textarea {{ min-height: 260px; margin-top: 12px; }}
        @media (max-width: 780px) {{
            form, .grid, .two-col, .summary {{
                grid-template-columns: 1fr;
            }}
            h1 {{ font-size: 1.6rem; }}
            .panel-head {{ align-items: flex-start; flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Persuasive Writing Coach</h1>
    </header>

    <form method="post" action="/analyse">
        <div>
            <label for="writing">Paste persuasive writing</label>
            <textarea id="writing" name="writing" placeholder="Paste an introduction, body paragraphs, or full persuasive essay here.">{escape_html(writing)}</textarea>
        </div>
        <div class="side">
            <label for="topic">Topic</label>
            <input id="topic" name="topic" value="{escape_html(topic)}" placeholder="Example: school uniforms">
            <label for="audience">Audience</label>
            <input id="audience" name="audience" value="{escape_html(audience)}" placeholder="Example: Year 8 students">
            <div class="actions">
                <button type="submit">Analyse writing</button>
                <a class="sample-link" href="/sample">Load sample</a>
            </div>
        </div>
    </form>

    {results_html}
</body>
</html>"""


class WritingCoachHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/sample":
            self.send_html(
                render_http_page(
                    writing=SAMPLE_WRITING,
                    topic="school uniforms",
                    audience="Year 8 students",
                    analysis=analyse_text(SAMPLE_WRITING),
                )
            )
            return
        self.send_html(render_http_page())

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/analyse":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        fields = parse_qs(body)
        writing = fields.get("writing", [""])[0]
        topic = fields.get("topic", [""])[0]
        audience = fields.get("audience", [""])[0]
        analysis = analyse_text(writing) if writing.strip() else None
        self.send_html(render_http_page(writing, topic, audience, analysis))

    def send_html(self, content: str) -> None:
        encoded = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def run_http_app(start_port: int = 8501) -> None:
    for port in range(start_port, start_port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), WritingCoachHandler)
            break
        except OSError:
            continue
    else:
        raise RuntimeError("No free local port found between 8501 and 8520.")

    print("Persuasive Writing Coach")
    print("Streamlit is not installed, so the built-in web app is running.")
    print(f"Open http://127.0.0.1:{server.server_port}")
    server.serve_forever()


def get_cli_port(default: int = 8501) -> int:
    if "--port" not in sys.argv:
        return default
    index = sys.argv.index("--port")
    try:
        return int(sys.argv[index + 1])
    except (IndexError, ValueError):
        return default


def load_sample() -> None:
    st.session_state["writing_text"] = SAMPLE_WRITING
    st.session_state["topic_text"] = "school uniforms"
    st.session_state["audience_text"] = "Year 8 students"


def main() -> None:
    if st is None:
        if "--console" in sys.argv:
            run_console_app()
        else:
            run_http_app(get_cli_port())
        return

    st.set_page_config(page_title="Persuasive Writing Coach", layout="wide")

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
        }
        [data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #d9e2ec;
            border-radius: 8px;
            padding: 0.75rem 1rem;
        }
        .stProgress > div > div > div > div {
            background-color: #2563eb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Persuasive Writing Coach")

    left, right = st.columns([2, 1])
    with left:
        writing = st.text_area(
            "Paste persuasive writing",
            height=360,
            placeholder="Paste an introduction, body paragraphs, or full persuasive essay here.",
            key="writing_text",
        )
    with right:
        topic = st.text_input("Topic", placeholder="Example: school uniforms", key="topic_text")
        audience = st.text_input("Audience", placeholder="Example: Year 8 students", key="audience_text")
        st.button("Load sample", on_click=load_sample)

    if not writing.strip():
        st.info("Paste a draft or load the sample to begin.")
        return

    analysis = analyse_text(writing)

    st.divider()
    metric_columns = st.columns(6)
    metric_columns[0].metric("Overall", f"{analysis.overall_score}/100", score_label(analysis.overall_score))
    metric_columns[1].metric("Reasoning", f"{analysis.reasoning.score}/100")
    metric_columns[2].metric("Level 8", f"{analysis.curriculum.score}/100")
    metric_columns[3].metric("Arguments", f"{analysis.arguments.score}/100")
    metric_columns[4].metric("Strong words", f"{analysis.strong_words.score}/100")
    metric_columns[5].metric("Techniques", f"{analysis.techniques.score}/100")

    tabs = st.tabs(["Feedback", "Improved draft", "Checklist", "Word bank"])

    with tabs[0]:
        col_a, col_b = st.columns(2)
        with col_a:
            render_score_card("1. Valid reasoning", analysis.reasoning)
            render_score_card("3. Strong arguments", analysis.arguments)
            render_score_card("5. Persuasive technique", analysis.techniques)
        with col_b:
            render_score_card("2. Level 8 Australia Curriculum", analysis.curriculum)
            render_score_card("4. Use of strong words", analysis.strong_words)

        st.subheader("Technique scan")
        render_technique_table(analysis)

        if analysis.overclaims:
            st.subheader("Claims to qualify")
            for sentence in analysis.overclaims:
                st.write(f"- {sentence}")

        if analysis.weak_word_hits:
            st.subheader("Weak words found")
            for word, count in analysis.weak_word_hits.items():
                replacements = ", ".join(WEAK_WORD_REPLACEMENTS[word])
                st.write(f"- **{word}** appeared {count} time(s). Try: {replacements}.")

    with tabs[1]:
        improved = build_improved_draft(writing, topic, audience)
        st.text_area("Improved draft", improved, height=420)
        report = build_feedback_report(analysis, writing, topic, audience)
        st.download_button(
            "Download feedback",
            data=report,
            file_name="persuasive_writing_feedback.txt",
            mime="text/plain",
        )

    with tabs[2]:
        render_checklist(analysis)

    with tabs[3]:
        render_word_bank()


if __name__ == "__main__":
    main()
