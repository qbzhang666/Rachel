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
        "have to",
        "essential",
        "vital",
        "crucial",
        "necessary",
        "urgent",
        "unacceptable",
        "undeniably",
        "certainly",
    ],
    "Emotive language": [
        "harmful",
        "devastating",
        "urgent",
        "unfair",
        "alarming",
        "concerning",
        "damaging",
        "inspiring",
        "hopeful",
        "respectful",
        "powerful",
        "dangerous",
        "valuable",
        "vital",
        "responsible",
        "shocking",
    ],
    "Evidence appeal": [
        "research",
        "evidence",
        "data",
        "statistics",
        "facts",
        "findings",
        "expert",
        "experts",
        "study",
        "studies",
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
    "crucial",
    "unacceptable",
    "undeniable",
    "compelling",
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
    "alarming",
    "concerning",
    "avoidable",
    "preventable",
    "unjust",
    "inexcusable",
    "transformative",
    "inclusive",
    "respectful",
    "resilient",
    "accountable",
    "ethical",
    "constructive",
    "informed",
    "decisive",
    "balanced",
    "harmonious",
    "empowering",
    "protective",
    "lifelong",
]

WEAK_WORD_REPLACEMENTS = {
    "good": ["effective", "valuable", "beneficial", "worthwhile"],
    "bad": ["harmful", "damaging", "unfair", "unacceptable"],
    "very": ["extremely", "deeply", "significantly"],
    "really": ["genuinely", "clearly", "strongly"],
    "thing": ["issue", "reason", "factor"],
    "things": ["issues", "reasons", "factors"],
    "stuff": ["evidence", "details", "materials"],
    "nice": ["positive", "respectful", "encouraging"],
    "big": ["significant", "major", "substantial"],
    "small": ["minor", "limited", "manageable"],
    "sad": ["concerning", "distressing", "disheartening"],
    "happy": ["confident", "hopeful", "encouraged"],
    "hard": ["challenging", "demanding", "difficult"],
    "easy": ["simple", "practical", "manageable"],
    "important": ["essential", "vital", "crucial"],
    "better": ["more effective", "more responsible", "more beneficial"],
    "worse": ["more harmful", "less effective", "more damaging"],
    "help": ["support", "strengthen", "benefit"],
    "stop": ["prevent", "reduce", "discourage"],
    "make": ["encourage", "create", "produce"],
    "show": ["demonstrate", "reveal", "prove"],
    "say": ["argue", "claim", "suggest"],
    "get": ["gain", "receive", "achieve"],
    "use": ["apply", "adopt", "employ"],
    "a lot": ["many", "frequently", "a significant amount"],
    "I think": ["It is clear that", "The evidence suggests that"],
    "in my opinion": ["The evidence suggests that", "A reasonable conclusion is that"],
}

PERSUASIVE_WORD_BANK = {
    "High modality": [
        "must",
        "should",
        "need to",
        "cannot ignore",
        "it is essential that",
        "it is vital that",
        "there is no doubt that",
    ],
    "Emotive words": [
        "alarming",
        "unfair",
        "harmful",
        "damaging",
        "distressing",
        "hopeful",
        "empowering",
        "inspiring",
    ],
    "Evaluative words": [
        "effective",
        "responsible",
        "reasonable",
        "ethical",
        "sustainable",
        "practical",
        "beneficial",
        "constructive",
    ],
    "Evidence words": [
        "research shows",
        "evidence suggests",
        "statistics reveal",
        "experts argue",
        "studies indicate",
        "for example",
        "this demonstrates",
    ],
    "Cause and effect": [
        "therefore",
        "as a result",
        "consequently",
        "this leads to",
        "this creates",
        "this reduces",
        "this strengthens",
    ],
    "Counterargument": [
        "although",
        "however",
        "this overlooks",
        "this ignores",
        "in reality",
        "a stronger view is",
        "more importantly",
    ],
    "Call to action": [
        "we must act",
        "it is time to",
        "schools should",
        "the community needs to",
        "students deserve",
        "leaders must",
    ],
}

PERSUASIVE_SENTENCE_STARTERS = [
    "It is clear that...",
    "The evidence suggests that...",
    "A responsible solution would be...",
    "This issue matters because...",
    "We cannot ignore the fact that...",
    "Although some people argue that..., this overlooks...",
    "This demonstrates that...",
    "For this reason, we must...",
    "Ultimately, the most reasonable choice is...",
]

TOPIC_IDEAS = {
    "School life": [
        "School uniforms should be compulsory",
        "Homework should be limited",
        "Mobile phones should be restricted during class",
        "Students should read every day",
        "School sport should be protected",
        "School lunches should be healthier",
        "Students should have more choice in subjects",
    ],
    "Technology": [
        "Social media should have stronger age limits",
        "AI tools should be used carefully in schools",
        "Video games can be beneficial when balanced",
        "Screen time should be reduced before bedtime",
        "Cyberbullying needs stronger consequences",
    ],
    "Environment": [
        "Schools should reduce plastic waste",
        "Public transport should be cheaper for students",
        "Every school should plant more trees",
        "Food waste should be reduced in canteens",
        "Communities should protect local wildlife habitats",
    ],
    "Community": [
        "Volunteering should be encouraged for teenagers",
        "Libraries remain essential in modern communities",
        "Local parks should receive more funding",
        "Students should learn basic first aid",
        "Public spaces should be safer and more inclusive",
    ],
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

SAMPLE_LIBRARY = [
    {
        "key": "school-uniforms",
        "label": "School uniforms",
        "topic": "school uniforms",
        "audience": "Year 8 students",
        "writing": (
            "I think school uniforms are good because they make students look the same. "
            "Uniforms can stop people from showing off expensive clothes. This is important because some students feel left out.\n\n"
            "Another reason is that uniforms save time in the morning. Students do not need to choose what to wear, so they can focus on school.\n\n"
            "Some people say uniforms are bad because they stop students from showing personality. However, students can still show personality through their actions, ideas and friendships.\n\n"
            "In conclusion, school uniforms should stay because they are fair and useful."
        ),
    },
    {
        "key": "homework-limits",
        "label": "Homework limits",
        "topic": "homework limits",
        "audience": "school leaders",
        "writing": (
            "Schools should limit homework because students need time to rest, practise hobbies and connect with their families. "
            "When homework becomes excessive, it can create stress instead of meaningful learning.\n\n"
            "Firstly, balanced homework is more effective than large amounts of repetitive tasks. For example, a short revision activity can help students remember key ideas, while hours of worksheets may only make them tired. "
            "This shows that quality matters more than quantity.\n\n"
            "Furthermore, students who have time for sport, music and reading often return to class with better focus. "
            "If schools want students to be responsible and motivated, they must protect time for wellbeing.\n\n"
            "Although some people argue that more homework always leads to better results, this ignores the importance of sleep and mental health. "
            "Ultimately, schools should set reasonable homework limits so learning remains useful, fair and sustainable."
        ),
    },
    {
        "key": "phones-at-school",
        "label": "Phones at school",
        "topic": "mobile phones at school",
        "audience": "parents and teachers",
        "writing": (
            "Mobile phones should be restricted during class because learning requires attention. "
            "How can students fully listen, think and contribute if notifications are constantly pulling their focus away?\n\n"
            "Firstly, phones can interrupt concentration. According to many classroom observations, even a quick message can distract not only one student but also the people around them. "
            "This means phone use affects the whole learning environment, not just the individual.\n\n"
            "Secondly, a clear phone rule can make school fairer. Students who feel pressured to reply online deserve a break from that stress during lessons. "
            "We need classrooms that are calm, respectful and focused.\n\n"
            "Some people argue that phones are necessary for safety. However, schools can still provide office phones and emergency contact systems. "
            "Therefore, restricting phones in class is a responsible choice that protects learning while still keeping students safe."
        ),
    },
    {
        "key": "daily-reading",
        "label": "Daily reading",
        "topic": "daily reading",
        "audience": "Year 8 students",
        "writing": (
            "Every student should read for at least ten minutes each day. "
            "Reading is not just a school task; it is a powerful habit that builds vocabulary, imagination and confidence.\n\n"
            "Firstly, daily reading helps students become stronger writers. For example, students who regularly read novels, articles and essays see more sentence patterns and persuasive techniques. "
            "This evidence matters because writers improve when they notice how language works.\n\n"
            "Secondly, reading can improve focus. In a world filled with fast videos and constant alerts, quiet reading trains the mind to stay with one idea for longer. "
            "That skill is valuable in every subject.\n\n"
            "Although some students say they are too busy, ten minutes is realistic and practical. "
            "Ultimately, daily reading is a small action with lasting benefits, so we should make it a normal part of student life."
        ),
    },
    {
        "key": "school-sport",
        "label": "School sport",
        "topic": "school sport",
        "audience": "the school community",
        "writing": (
            "School sport must remain an important part of education because healthy bodies support healthy minds. "
            "It is unfair to treat sport as a break from learning when it teaches discipline, teamwork and resilience.\n\n"
            "To begin with, regular physical activity can improve student wellbeing. For instance, exercise can reduce stress and help students return to class more alert. "
            "This shows that sport supports academic learning instead of competing with it.\n\n"
            "In addition, sport gives students a chance to practise leadership and cooperation. "
            "A team succeeds when players communicate, encourage each other and keep trying after setbacks.\n\n"
            "Critics may argue that sport takes time away from core subjects. However, this view overlooks the fact that students learn best when their routines include movement, challenge and belonging. "
            "For this reason, schools should protect sport as a vital part of a balanced education."
        ),
    },
    {
        "key": "healthy-school-lunches",
        "label": "Healthy school lunches",
        "topic": "healthy school lunches",
        "audience": "school leaders",
        "writing": (
            "Schools should provide healthier lunch options because students deserve food that supports their learning and wellbeing. "
            "It is concerning when canteens offer mostly sugary snacks instead of balanced, nourishing meals.\n\n"
            "Firstly, healthy food can improve concentration. For example, students who eat a balanced lunch are more likely to feel alert in afternoon classes. "
            "This demonstrates that food choices affect learning, not just hunger.\n\n"
            "Furthermore, schools have a responsibility to encourage lifelong habits. "
            "If students regularly see practical, affordable and appealing healthy choices, they are more likely to make responsible decisions outside school.\n\n"
            "Although some people argue that unhealthy food is more popular, this overlooks the power of creative menus and student feedback. "
            "Ultimately, healthier school lunches are a fair and beneficial step towards a stronger school community."
        ),
    },
    {
        "key": "plastic-waste",
        "label": "Plastic waste",
        "topic": "plastic waste at school",
        "audience": "students and teachers",
        "writing": (
            "Our school must reduce plastic waste because the current amount of rubbish is unnecessary and harmful. "
            "Every wrapper, bottle and container that is thrown away creates a problem that does not disappear when the bell rings.\n\n"
            "To begin with, reducing plastic waste is a practical way to protect the environment. "
            "For example, reusable bottles and lunch containers can prevent hundreds of single-use items from entering bins each week. "
            "This shows that small daily choices can create meaningful change.\n\n"
            "In addition, a cleaner school environment builds pride and responsibility. "
            "Students are more likely to respect shared spaces when we all contribute to keeping them tidy.\n\n"
            "Some people may argue that reducing plastic is inconvenient. However, this ignores the long-term cost of waste and pollution. "
            "For this reason, our school should adopt a stronger, clearer and more sustainable waste policy."
        ),
    },
    {
        "key": "social-media-age-limits",
        "label": "Social media age limits",
        "topic": "social media age limits",
        "audience": "parents and policymakers",
        "writing": (
            "Social media platforms should have stronger age limits because young people need safer online spaces. "
            "It is unacceptable for children to face harmful content, pressure and cyberbullying without enough protection.\n\n"
            "Firstly, stronger age limits can reduce exposure to damaging online behaviour. "
            "Research suggests that constant comparison and negative comments can affect confidence and wellbeing. "
            "This evidence shows why safety should be more important than convenience.\n\n"
            "Secondly, clear rules support parents and schools. "
            "When expectations are consistent, adults can guide students more effectively and reduce conflict about online access.\n\n"
            "Although critics may claim that age limits are difficult to enforce, this overlooks the value of better platform design and education. "
            "Ultimately, stronger age limits are a responsible step towards protecting young people."
        ),
    },
    {
        "key": "ai-in-schools",
        "label": "AI in schools",
        "topic": "AI tools in schools",
        "audience": "teachers and students",
        "writing": (
            "AI tools should be used carefully in schools because they can support learning while also creating serious risks. "
            "The most responsible approach is not to ban AI completely, but to teach students how to use it ethically.\n\n"
            "Firstly, AI can help students plan, revise and practise skills. "
            "For instance, a student might use feedback from an AI tool to improve sentence clarity before writing their own final response. "
            "This demonstrates that technology can strengthen learning when students remain active thinkers.\n\n"
            "However, AI can also weaken learning if students copy answers without understanding them. "
            "This is why schools need clear expectations, honest discussion and practical guidance.\n\n"
            "Some people argue that AI should be removed from classrooms entirely. Nevertheless, this ignores the fact that students will meet AI in future workplaces. "
            "Ultimately, schools must teach careful, informed and ethical AI use."
        ),
    },
    {
        "key": "student-volunteering",
        "label": "Student volunteering",
        "topic": "student volunteering",
        "audience": "Year 8 students",
        "writing": (
            "Students should be encouraged to volunteer because service builds empathy, confidence and responsibility. "
            "Helping others is not only generous; it is a powerful way to become more connected to the community.\n\n"
            "Firstly, volunteering teaches students to understand different experiences. "
            "For example, helping at a local food drive can reveal how many families rely on community support. "
            "This shows that volunteering can make students more thoughtful and compassionate.\n\n"
            "Furthermore, volunteering develops practical skills such as communication, teamwork and organisation. "
            "These skills are valuable in school, sport, friendships and future work.\n\n"
            "Although some students may feel too busy, even one hour a month can make a meaningful difference. "
            "Ultimately, volunteering should be encouraged because it creates stronger students and a kinder community."
        ),
    },
    {
        "key": "public-transport",
        "label": "Cheaper public transport",
        "topic": "cheaper public transport for students",
        "audience": "local government",
        "writing": (
            "Public transport should be cheaper for students because travel costs can unfairly limit opportunities. "
            "When transport is affordable, students can reach school, sport, libraries and community activities more easily.\n\n"
            "Firstly, cheaper transport supports fairness. "
            "For example, families with several children may spend a significant amount each week on buses or trains. "
            "This evidence demonstrates that transport costs can become a real barrier.\n\n"
            "In addition, affordable public transport can reduce traffic and pollution. "
            "If more students use buses and trains, fewer cars are needed around schools during busy times.\n\n"
            "Some people may argue that discounts cost too much. However, this ignores the long-term benefits of safer roads, cleaner air and stronger student participation. "
            "Therefore, cheaper public transport is a practical and responsible investment."
        ),
    },
    {
        "key": "school-libraries",
        "label": "School libraries",
        "topic": "school libraries",
        "audience": "school leaders",
        "writing": (
            "School libraries remain essential because they give students a calm, inclusive and resource-rich place to learn. "
            "In a world full of screens and distractions, libraries offer something valuable: focus.\n\n"
            "Firstly, libraries support reading, research and independent learning. "
            "For instance, students can access books, databases and expert help when preparing assignments. "
            "This demonstrates that a library is more than a room of books; it is a learning centre.\n\n"
            "Secondly, libraries create a safe space for students who need quiet at lunch or before school. "
            "That matters because every student deserves somewhere respectful and welcoming.\n\n"
            "Although some people claim that online information makes libraries unnecessary, this overlooks the importance of guidance and reliable sources. "
            "Ultimately, school libraries should be protected because they strengthen literacy, wellbeing and fairness."
        ),
    },
    {
        "key": "later-school-start",
        "label": "Later school start",
        "topic": "later school start times",
        "audience": "school leaders and parents",
        "writing": (
            "Schools should consider later start times because tired students cannot learn as effectively as rested students. "
            "Sleep is not a luxury; it is essential for memory, concentration and emotional health.\n\n"
            "Firstly, a later start could improve focus in morning classes. "
            "Research often shows that teenagers need substantial sleep, yet many struggle to get enough when school begins early. "
            "This suggests that timetable design can directly affect learning.\n\n"
            "Furthermore, rested students are more likely to manage stress and participate positively. "
            "A small change in routine could create a more alert, respectful and productive classroom environment.\n\n"
            "Some people argue that later starts would inconvenience families. However, this concern can be addressed through careful planning and before-school supervision. "
            "Ultimately, later start times deserve serious consideration because student wellbeing must be a priority."
        ),
    },
    {
        "key": "first-aid",
        "label": "First aid lessons",
        "topic": "first aid lessons",
        "audience": "school leaders",
        "writing": (
            "Every student should learn basic first aid because emergency skills can save lives. "
            "It is alarming that many young people would not know how to respond confidently if someone was injured or unwell.\n\n"
            "Firstly, first aid lessons build practical confidence. "
            "For example, students could learn how to call for help, treat minor injuries and respond safely in urgent situations. "
            "This knowledge is valuable because emergencies can happen anywhere.\n\n"
            "In addition, first aid education encourages responsibility. "
            "Students who understand how to help others are more prepared, calm and useful in difficult moments.\n\n"
            "Although some people may argue that the curriculum is already crowded, first aid does not need to take many lessons. "
            "Ultimately, teaching first aid is a sensible and ethical choice for every school."
        ),
    },
    {
        "key": "screen-time",
        "label": "Screen time",
        "topic": "screen time before bed",
        "audience": "teenagers",
        "writing": (
            "Teenagers should reduce screen time before bed because sleep is too important to sacrifice. "
            "Endless scrolling may feel relaxing, but it can become a harmful habit that leaves students tired the next day.\n\n"
            "Firstly, reducing screen time can improve rest. "
            "Studies often suggest that bright screens and late notifications make it harder for the brain to switch off. "
            "This shows why a phone-free routine before sleep can be beneficial.\n\n"
            "Secondly, better sleep supports learning, mood and motivation. "
            "Students who wake up refreshed are more likely to listen carefully, remember information and treat others respectfully.\n\n"
            "Although some teenagers argue that phones help them relax, this ignores the way apps are designed to hold attention. "
            "For this reason, reducing screen time before bed is a practical step towards healthier routines."
        ),
    },
]

SAMPLE_WRITING = SAMPLE_LIBRARY[0]["writing"]


def get_sample(sample_key: str | None = None) -> dict[str, str]:
    for sample in SAMPLE_LIBRARY:
        if sample["key"] == sample_key:
            return sample
    return SAMPLE_LIBRARY[0]


def get_sample_labels() -> list[str]:
    return [sample["label"] for sample in SAMPLE_LIBRARY]


def get_sample_by_label(label: str) -> dict[str, str]:
    for sample in SAMPLE_LIBRARY:
        if sample["label"] == label:
            return sample
    return SAMPLE_LIBRARY[0]


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


def get_word_bank_hits(text: str) -> dict[str, list[str]]:
    return {
        category: unique_terms_found(text, words)
        for category, words in PERSUASIVE_WORD_BANK.items()
    }


def get_missing_word_categories(text: str) -> list[str]:
    hits = get_word_bank_hits(text)
    return [category for category, found in hits.items() if not found]


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
    score = 15
    strengths = []
    improvements = []

    strong_hits = unique_terms_found(text, STRONG_WORDS)
    if len(strong_hits) >= 14:
        score += 25
        strengths.append("Strong vocabulary is used frequently.")
    elif len(strong_hits) >= 7:
        score += 18
        strengths.append("There is some strong vocabulary.")
        improvements.append("Add more precise high-impact words to key claims.")
    elif len(strong_hits) >= 3:
        score += 10
        improvements.append("Use more strong, specific words in the topic sentences and conclusion.")
    else:
        improvements.append("Replace simple words with stronger persuasive vocabulary.")

    word_bank_hits = get_word_bank_hits(text)
    category_count = len([hits for hits in word_bank_hits.values() if hits])
    if category_count >= 6:
        score += 35
        strengths.append("Persuasive word choices are varied across several purposes.")
    elif category_count >= 4:
        score += 25
        strengths.append("The writing uses several types of persuasive language.")
        improvements.append("Add one or two missing word types, such as evidence language or a call to action.")
    elif category_count >= 2:
        score += 15
        improvements.append("Use a wider mix of persuasive words, not only general strong adjectives.")
    else:
        improvements.append("Add high modality, emotive, evidence, and cause-and-effect language.")

    high_modality_count = len(word_bank_hits["High modality"])
    if high_modality_count >= 3:
        score += 15
        strengths.append("High modality words make the stance confident.")
    elif high_modality_count >= 1:
        score += 8
        improvements.append("Use more high modality words such as must, should, cannot ignore, essential, and vital.")
    else:
        improvements.append("Add high modality language to sound more decisive.")

    if word_bank_hits["Emotive words"] and word_bank_hits["Evaluative words"]:
        score += 10
        strengths.append("Emotive and evaluative words help shape the reader's judgement.")
    else:
        improvements.append("Combine emotive words with evaluative words so the reader feels and judges the issue clearly.")

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
            reasoning.score * 0.2
            + curriculum.score * 0.15
            + arguments.score * 0.2
            + strong_words.score * 0.3
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
        "nice": "encouraging",
        "big": "significant",
        "sad": "concerning",
        "happy": "hopeful",
        "hard": "challenging",
        "easy": "practical",
        "important": "essential",
        "better": "more effective",
        "worse": "more harmful",
        "help": "support",
        "stop": "prevent",
        "show": "demonstrate",
        "say": "argue",
        "get": "gain",
        "use": "apply",
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

    word_bank_hits = get_word_bank_hits(text)
    lines.append("Persuasive word choice scan:")
    for category, hits in word_bank_hits.items():
        if hits:
            lines.append(f"  - {category}: {', '.join(hits[:6])}")
        else:
            lines.append(f"  - {category}: add one or two phrases from this category")
    lines.append("")

    lines.append("Useful sentence starters:")
    for starter in PERSUASIVE_SENTENCE_STARTERS:
        lines.append(f"  - {starter}")
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


def render_word_choice_scan(text: str, weak_word_hits: dict[str, int]) -> None:
    word_bank_hits = get_word_bank_hits(text)
    rows = []
    for category, hits in word_bank_hits.items():
        rows.append(
            {
                "Word purpose": category,
                "Detected": ", ".join(hits[:6]) if hits else "Not detected",
                "Try adding": ", ".join(PERSUASIVE_WORD_BANK[category][:4]),
            }
        )
    st.dataframe(rows, hide_index=True, use_container_width=True)

    if weak_word_hits:
        st.markdown("**Weak-to-strong upgrades found in this draft**")
        upgrade_rows = []
        for weak, count in weak_word_hits.items():
            upgrade_rows.append(
                {
                    "Weak word": weak,
                    "Count": count,
                    "Stronger options": ", ".join(WEAK_WORD_REPLACEMENTS[weak]),
                }
            )
        st.dataframe(upgrade_rows, hide_index=True, use_container_width=True)


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

    st.markdown("**Persuasive words by purpose**")
    bank_rows = []
    for category, phrases in PERSUASIVE_WORD_BANK.items():
        bank_rows.append(
            {
                "Purpose": category,
                "Words and phrases": ", ".join(phrases),
            }
        )
    st.dataframe(bank_rows, hide_index=True, use_container_width=True)

    st.markdown("**Sentence starters**")
    for starter in PERSUASIVE_SENTENCE_STARTERS:
        st.write(f"- {starter}")

    st.markdown("**Strong persuasive words**")
    columns = st.columns(5)
    for index, word in enumerate(STRONG_WORDS):
        columns[index % 5].write(f"- {word}")


def render_topic_ideas() -> None:
    for category, topics in TOPIC_IDEAS.items():
        st.markdown(f"**{category}**")
        for topic in topics:
            st.write(f"- {topic}")


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


def render_html_word_bank() -> str:
    bank_rows = "".join(
        "<tr>"
        f"<td>{escape_html(category)}</td>"
        f"<td>{escape_html(', '.join(phrases))}</td>"
        "</tr>"
        for category, phrases in PERSUASIVE_WORD_BANK.items()
    )
    starters = "".join(f"<li>{escape_html(starter)}</li>" for starter in PERSUASIVE_SENTENCE_STARTERS)
    return f"""
    <section class="panel full">
        <h2>Persuasive word bank</h2>
        <table>
            <thead><tr><th>Purpose</th><th>Words and phrases</th></tr></thead>
            <tbody>{bank_rows}</tbody>
        </table>
        <h3>Sentence starters</h3>
        <ul>{starters}</ul>
    </section>
    """


def render_html_topic_ideas() -> str:
    category_blocks = []
    for category, topics in TOPIC_IDEAS.items():
        topic_items = "".join(f"<li>{escape_html(topic)}</li>" for topic in topics)
        category_blocks.append(f"<div class=\"panel\"><h2>{escape_html(category)}</h2><ul>{topic_items}</ul></div>")
    return f"""
    <section class="panel full">
        <h2>Topic ideas</h2>
    </section>
    <section class="topic-grid">
        {''.join(category_blocks)}
    </section>
    """


def render_html_word_choice_scan(text: str, weak_word_hits: dict[str, int]) -> str:
    word_rows = "".join(
        "<tr>"
        f"<td>{escape_html(category)}</td>"
        f"<td>{escape_html(', '.join(hits[:6]) if hits else 'Not detected')}</td>"
        f"<td>{escape_html(', '.join(PERSUASIVE_WORD_BANK[category][:4]))}</td>"
        "</tr>"
        for category, hits in get_word_bank_hits(text).items()
    )
    weak_rows = "".join(
        "<tr>"
        f"<td>{escape_html(word)}</td>"
        f"<td>{count}</td>"
        f"<td>{escape_html(', '.join(WEAK_WORD_REPLACEMENTS[word]))}</td>"
        "</tr>"
        for word, count in weak_word_hits.items()
    )
    if not weak_rows:
        weak_rows = "<tr><td colspan=\"3\">No common weak words detected.</td></tr>"
    return f"""
    <section class="panel full">
        <h2>Persuasive use of words</h2>
        <table>
            <thead><tr><th>Word purpose</th><th>Detected</th><th>Try adding</th></tr></thead>
            <tbody>{word_rows}</tbody>
        </table>
        <h3>Weak-to-strong upgrades</h3>
        <table>
            <thead><tr><th>Weak word</th><th>Count</th><th>Stronger options</th></tr></thead>
            <tbody>{weak_rows}</tbody>
        </table>
    </section>
    """


def render_http_page(
    writing: str = "",
    topic: str = "",
    audience: str = "",
    analysis: Analysis | None = None,
    selected_sample_key: str | None = None,
) -> str:
    report = ""
    improved = ""
    scores = ""
    technique_rows = ""
    weak_words = ""
    overclaims = ""
    selected_sample = get_sample(selected_sample_key)
    sample_options = "".join(
        f"<option value=\"{escape_html(sample['key'])}\""
        f"{' selected' if sample['key'] == selected_sample['key'] else ''}>"
        f"{escape_html(sample['label'])}</option>"
        for sample in SAMPLE_LIBRARY
    )

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

        {render_html_word_choice_scan(writing, analysis.weak_word_hits)}

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
        textarea, input, select {{
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
        .side label + input, .side label + select {{ margin-bottom: 14px; }}
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
        .topic-grid {{
            width: min(1180px, calc(100% - 32px));
            margin: 20px auto;
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
            form, .grid, .two-col, .summary, .topic-grid {{
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
            <label for="sample_key">Example</label>
            <select id="sample_key" name="sample_key">{sample_options}</select>
            <div class="actions">
                <button type="submit">Analyse writing</button>
                <button class="sample-link" type="submit" formaction="/sample">Load selected sample</button>
            </div>
        </div>
    </form>

    {results_html}
    {render_html_word_bank()}
    {render_html_topic_ideas()}
</body>
</html>"""


class WritingCoachHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/sample":
            fields = parse_qs(parsed.query)
            sample = get_sample(fields.get("sample_key", [""])[0])
            self.send_html(
                render_http_page(
                    writing=sample["writing"],
                    topic=sample["topic"],
                    audience=sample["audience"],
                    analysis=analyse_text(sample["writing"]),
                    selected_sample_key=sample["key"],
                )
            )
            return
        self.send_html(render_http_page())

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in {"/analyse", "/sample"}:
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        fields = parse_qs(body)

        if path == "/sample":
            sample = get_sample(fields.get("sample_key", [""])[0])
            self.send_html(
                render_http_page(
                    writing=sample["writing"],
                    topic=sample["topic"],
                    audience=sample["audience"],
                    analysis=analyse_text(sample["writing"]),
                    selected_sample_key=sample["key"],
                )
            )
            return

        writing = fields.get("writing", [""])[0]
        topic = fields.get("topic", [""])[0]
        audience = fields.get("audience", [""])[0]
        sample_key = fields.get("sample_key", [""])[0]
        analysis = analyse_text(writing) if writing.strip() else None
        self.send_html(render_http_page(writing, topic, audience, analysis, sample_key))

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
    sample = get_sample_by_label(st.session_state.get("sample_label", SAMPLE_LIBRARY[0]["label"]))
    st.session_state["writing_text"] = sample["writing"]
    st.session_state["topic_text"] = sample["topic"]
    st.session_state["audience_text"] = sample["audience"]
    st.session_state["submitted_writing"] = sample["writing"]
    st.session_state["submitted_topic"] = sample["topic"]
    st.session_state["submitted_audience"] = sample["audience"]


def submit_writing() -> None:
    st.session_state["submitted_writing"] = st.session_state.get("writing_text", "")
    st.session_state["submitted_topic"] = st.session_state.get("topic_text", "")
    st.session_state["submitted_audience"] = st.session_state.get("audience_text", "")


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
        st.button("Submit writing", type="primary", use_container_width=True, on_click=submit_writing)
    with right:
        topic = st.text_input("Topic", placeholder="Example: school uniforms", key="topic_text")
        audience = st.text_input("Audience", placeholder="Example: Year 8 students", key="audience_text")
        st.selectbox("Example", get_sample_labels(), key="sample_label")
        st.button("Load selected sample", on_click=load_sample)

    submitted_writing = st.session_state.get("submitted_writing", "")
    submitted_topic = st.session_state.get("submitted_topic", "")
    submitted_audience = st.session_state.get("submitted_audience", "")

    if not submitted_writing.strip():
        st.info("Paste a draft or load a sample, then click Submit writing.")
        return

    if writing.strip() and writing != submitted_writing:
        st.warning("Draft changed since the last submission. Click Submit writing to refresh the feedback.")

    analysis = analyse_text(submitted_writing)

    st.divider()
    metric_columns = st.columns(6)
    metric_columns[0].metric("Overall", f"{analysis.overall_score}/100", score_label(analysis.overall_score))
    metric_columns[1].metric("Reasoning", f"{analysis.reasoning.score}/100")
    metric_columns[2].metric("Level 8", f"{analysis.curriculum.score}/100")
    metric_columns[3].metric("Arguments", f"{analysis.arguments.score}/100")
    metric_columns[4].metric("Strong words", f"{analysis.strong_words.score}/100")
    metric_columns[5].metric("Techniques", f"{analysis.techniques.score}/100")

    tabs = st.tabs(["Feedback", "Word choice", "Improved draft", "Checklist", "Word bank", "Topic ideas"])

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
        render_score_card("Persuasive use of words", analysis.strong_words)
        render_word_choice_scan(submitted_writing, analysis.weak_word_hits)

    with tabs[2]:
        improved = build_improved_draft(submitted_writing, submitted_topic, submitted_audience)
        st.text_area("Improved draft", improved, height=420)
        report = build_feedback_report(analysis, submitted_writing, submitted_topic, submitted_audience)
        st.download_button(
            "Download feedback",
            data=report,
            file_name="persuasive_writing_feedback.txt",
            mime="text/plain",
        )

    with tabs[3]:
        render_checklist(analysis)

    with tabs[4]:
        render_word_bank()

    with tabs[5]:
        render_topic_ideas()


if __name__ == "__main__":
    main()
