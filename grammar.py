import csv
import io
import json
import random
from collections import Counter
from datetime import datetime

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
    {
        "skill": "Noun phrases",
        "prompt": "In the noun phrase 'the unusually detailed map of coastal erosion', which word is the head noun?",
        "choices": ["map", "detailed", "coastal", "erosion"],
        "answer": "map",
        "explanation": "The head noun is the main noun that the rest of the phrase describes or modifies.",
    },
    {
        "skill": "Noun phrases",
        "prompt": "Which sentence contains an expanded noun phrase?",
        "choices": [
            "The carefully annotated draft of the essay was submitted on time.",
            "The draft was submitted.",
            "Students submitted work.",
            "The essay arrived.",
        ],
        "answer": "The carefully annotated draft of the essay was submitted on time.",
        "explanation": "The noun phrase includes determiners, modifiers and a prepositional phrase built around the head noun draft.",
    },
    {
        "skill": "Determiners",
        "prompt": "In the sentence 'Several of the revised chapters include stronger evidence', what is the determiner?",
        "choices": ["Several", "revised", "include", "stronger"],
        "answer": "Several",
        "explanation": "Several is a determiner because it indicates quantity before the noun phrase.",
    },
    {
        "skill": "Determiners",
        "prompt": "Choose the sentence with the most precise determiner.",
        "choices": [
            "Each participant completed an individual reflection.",
            "Every participants completed an individual reflection.",
            "Much participants completed an individual reflection.",
            "Either participants completed an individual reflection.",
        ],
        "answer": "Each participant completed an individual reflection.",
        "explanation": "Each is used with a singular count noun when focusing on members of a group individually.",
    },
    {
        "skill": "Prepositional phrases",
        "prompt": "In the sentence 'The results from the second trial were more reliable', what does the phrase 'from the second trial' modify?",
        "choices": ["results", "were", "reliable", "second"],
        "answer": "results",
        "explanation": "The prepositional phrase tells us which results are being discussed.",
    },
    {
        "skill": "Prepositional phrases",
        "prompt": "Which sentence uses a prepositional phrase as an adverbial?",
        "choices": [
            "The class debated the issue after lunch.",
            "The after-lunch debate was lively.",
            "The issue after lunch was complex.",
            "Lunch was after the debate issue.",
        ],
        "answer": "The class debated the issue after lunch.",
        "explanation": "After lunch modifies the verb debated by telling when the action happened.",
    },
    {
        "skill": "Clause types",
        "prompt": "Which option is the main clause in this sentence: 'Although the evidence was limited, the conclusion was reasonable'?",
        "choices": [
            "the conclusion was reasonable",
            "Although the evidence was limited",
            "the evidence was limited",
            "Although the evidence",
        ],
        "answer": "the conclusion was reasonable",
        "explanation": "The main clause can stand alone as a complete sentence.",
    },
    {
        "skill": "Clause types",
        "prompt": "Which sentence contains a subordinate clause of concession?",
        "choices": [
            "Although the source was old, it remained useful.",
            "The source was old and useful.",
            "The source remained useful in the essay.",
            "The old source remained useful.",
        ],
        "answer": "Although the source was old, it remained useful.",
        "explanation": "Although introduces a concession: a contrast or unexpected condition.",
    },
    {
        "skill": "Noun clauses",
        "prompt": "Which sentence contains a noun clause functioning as the object of a verb?",
        "choices": [
            "I understand why the results changed.",
            "The results changed during the trial.",
            "Because the results changed, we repeated the trial.",
            "The changed results surprised the group.",
        ],
        "answer": "I understand why the results changed.",
        "explanation": "Why the results changed acts as the object of understand.",
    },
    {
        "skill": "Noun clauses",
        "prompt": "In the sentence 'What the witness remembered altered the timeline', what is the subject?",
        "choices": [
            "What the witness remembered",
            "the witness",
            "remembered",
            "the timeline",
        ],
        "answer": "What the witness remembered",
        "explanation": "The whole noun clause acts as the subject of the verb altered.",
    },
    {
        "skill": "Relative clauses",
        "prompt": "Which sentence uses a non-restrictive relative clause correctly?",
        "choices": [
            "The novel, which won several awards, explores migration.",
            "The novel which won several awards explores migration.",
            "The novel, that won several awards explores migration.",
            "The novel which, won several awards, explores migration.",
        ],
        "answer": "The novel, which won several awards, explores migration.",
        "explanation": "A non-restrictive clause adds extra information and is set off with commas.",
    },
    {
        "skill": "Relative clauses",
        "prompt": "Which sentence uses a restrictive relative clause correctly?",
        "choices": [
            "Students who submit the form by Friday will receive priority.",
            "Students, who submit the form by Friday, will receive priority.",
            "Students which submit the form by Friday will receive priority.",
            "Students, that submit the form by Friday will receive priority.",
        ],
        "answer": "Students who submit the form by Friday will receive priority.",
        "explanation": "The clause identifies which students, so it is restrictive and should not be separated by commas.",
    },
    {
        "skill": "Embedded clauses",
        "prompt": "Which sentence contains an embedded clause?",
        "choices": [
            "The claim that the policy improved attendance needs evidence.",
            "The policy improved attendance.",
            "Attendance improved after the policy changed.",
            "The claim needs evidence.",
        ],
        "answer": "The claim that the policy improved attendance needs evidence.",
        "explanation": "That the policy improved attendance is embedded inside the noun phrase beginning with claim.",
    },
    {
        "skill": "Embedded clauses",
        "prompt": "In 'The idea that language changes over time is widely accepted', what is the embedded clause?",
        "choices": [
            "that language changes over time",
            "The idea",
            "is widely accepted",
            "over time is widely",
        ],
        "answer": "that language changes over time",
        "explanation": "The that-clause is embedded inside the larger sentence as part of the subject noun phrase.",
    },
    {
        "skill": "Finite verbs",
        "prompt": "Which word is the finite verb in this sentence: 'The committee reviewing the proposal has requested revisions'?",
        "choices": ["has", "reviewing", "proposal", "requested"],
        "answer": "has",
        "explanation": "Has is finite because it shows tense and agrees with the subject. Requested is part of the perfect verb phrase.",
    },
    {
        "skill": "Non-finite clauses",
        "prompt": "Which sentence begins with a non-finite participle clause?",
        "choices": [
            "Having checked the data, Aisha revised her conclusion.",
            "Aisha checked the data before revising.",
            "Because Aisha checked the data, she revised her conclusion.",
            "Aisha has checked the data carefully.",
        ],
        "answer": "Having checked the data, Aisha revised her conclusion.",
        "explanation": "Having checked the data is a non-finite clause because it has no tense-marked finite verb.",
    },
    {
        "skill": "Perfect aspect",
        "prompt": "Which sentence uses the present perfect aspect?",
        "choices": [
            "The researchers have published their findings.",
            "The researchers published their findings.",
            "The researchers are publishing their findings.",
            "The researchers will publish their findings.",
        ],
        "answer": "The researchers have published their findings.",
        "explanation": "Have published uses the auxiliary have plus a past participle, forming the present perfect.",
    },
    {
        "skill": "Progressive aspect",
        "prompt": "Which sentence uses the past perfect progressive aspect?",
        "choices": [
            "The team had been testing the prototype for weeks.",
            "The team has tested the prototype for weeks.",
            "The team was testing the prototype.",
            "The team had tested the prototype.",
        ],
        "answer": "The team had been testing the prototype for weeks.",
        "explanation": "Had been testing combines perfect and progressive aspect in the past.",
    },
    {
        "skill": "Modal verbs",
        "prompt": "Which sentence uses a modal verb to express obligation?",
        "choices": [
            "Students must acknowledge their sources.",
            "Students might acknowledge their sources.",
            "Students could acknowledge their sources.",
            "Students would acknowledge their sources.",
        ],
        "answer": "Students must acknowledge their sources.",
        "explanation": "Must expresses obligation or necessity.",
    },
    {
        "skill": "Modal verbs",
        "prompt": "Which sentence expresses the strongest certainty?",
        "choices": [
            "The data must indicate a trend.",
            "The data might indicate a trend.",
            "The data could indicate a trend.",
            "The data may indicate a trend.",
        ],
        "answer": "The data must indicate a trend.",
        "explanation": "Must can express a strong logical conclusion, while might, could and may are less certain.",
    },
    {
        "skill": "Mood",
        "prompt": "Which sentence uses the subjunctive mood correctly in formal English?",
        "choices": [
            "The committee recommended that the policy be reviewed.",
            "The committee recommended that the policy is reviewed.",
            "The committee recommended that the policy was reviewed.",
            "The committee recommended that the policy being reviewed.",
        ],
        "answer": "The committee recommended that the policy be reviewed.",
        "explanation": "After verbs such as recommend, formal English can use the base form be in a subjunctive clause.",
    },
    {
        "skill": "Mood",
        "prompt": "Which sentence expresses a hypothetical situation correctly?",
        "choices": [
            "If I were responsible for the project, I would change the timeline.",
            "If I was responsible for the project, I will change the timeline.",
            "If I am responsible for the project, I would changed the timeline.",
            "If I were responsible for the project, I will changed the timeline.",
        ],
        "answer": "If I were responsible for the project, I would change the timeline.",
        "explanation": "Were and would change mark a hypothetical present situation and its result.",
    },
    {
        "skill": "Conditionals",
        "prompt": "Choose the correct third conditional sentence.",
        "choices": [
            "If the group had checked the source, they would have noticed the error.",
            "If the group checked the source, they would have notice the error.",
            "If the group had checked the source, they will notice the error.",
            "If the group has checked the source, they would noticed the error.",
        ],
        "answer": "If the group had checked the source, they would have noticed the error.",
        "explanation": "The third conditional uses had plus past participle and would have plus past participle.",
    },
    {
        "skill": "Conditionals",
        "prompt": "Choose the most accurate sentence using unless.",
        "choices": [
            "Unless the evidence is reliable, the claim should be revised.",
            "Unless the evidence is reliable, the claim should not be revised.",
            "Unless the evidence was reliable, the claim should revises.",
            "Unless the evidence reliable, the claim should be revised.",
        ],
        "answer": "Unless the evidence is reliable, the claim should be revised.",
        "explanation": "Unless means if not: if the evidence is not reliable, the claim should be revised.",
    },
    {
        "skill": "Subject-verb agreement",
        "prompt": "Choose the sentence with correct agreement.",
        "choices": [
            "The list of recommended readings is on the website.",
            "The list of recommended readings are on the website.",
            "The list of recommended readings have been on the website.",
            "The list of recommended readings were on the website.",
        ],
        "answer": "The list of recommended readings is on the website.",
        "explanation": "The subject is list, which is singular. The phrase of recommended readings does not control the verb.",
    },
    {
        "skill": "Subject-verb agreement",
        "prompt": "Choose the sentence with correct nearest-subject agreement.",
        "choices": [
            "Either the teachers or the principal is attending the forum.",
            "Either the teachers or the principal are attending the forum.",
            "Either the teachers nor the principal is attending the forum.",
            "Either the teachers and the principal is attending the forum.",
        ],
        "answer": "Either the teachers or the principal is attending the forum.",
        "explanation": "With either/or, the verb often agrees with the nearest subject. Principal is singular, so is is correct.",
    },
    {
        "skill": "Subject-verb agreement",
        "prompt": "Choose the sentence with correct collective noun agreement.",
        "choices": [
            "The jury has reached its decision.",
            "The jury have reached its decision.",
            "The jury has reached their decision.",
            "The jury were reached its decision.",
        ],
        "answer": "The jury has reached its decision.",
        "explanation": "When the group acts as one unit, a singular verb and singular pronoun are appropriate.",
    },
    {
        "skill": "Passive voice",
        "prompt": "Which sentence is in passive voice?",
        "choices": [
            "The final report was reviewed by the panel.",
            "The panel reviewed the final report.",
            "The panel carefully reviewed the report.",
            "The final report influenced the panel.",
        ],
        "answer": "The final report was reviewed by the panel.",
        "explanation": "Passive voice uses a form of be plus a past participle, and the receiver of the action becomes the subject.",
    },
    {
        "skill": "Passive voice",
        "prompt": "Which passive sentence is most appropriate when the actor is unknown or unimportant?",
        "choices": [
            "The window was broken during lunch.",
            "Someone broke the window during lunch.",
            "The window broke someone during lunch.",
            "During lunch, someone had broken the window by a window.",
        ],
        "answer": "The window was broken during lunch.",
        "explanation": "The passive can be useful when the action matters more than the person who performed it.",
    },
    {
        "skill": "Nominalisation",
        "prompt": "Which sentence uses nominalisation?",
        "choices": [
            "The investigation of the sample revealed contamination.",
            "The team investigated the sample and found contamination.",
            "The sample was contaminated.",
            "The team found that the sample was contaminated.",
        ],
        "answer": "The investigation of the sample revealed contamination.",
        "explanation": "Investigation turns the verb investigate into a noun, which is a nominalisation.",
    },
    {
        "skill": "Nominalisation",
        "prompt": "Choose the clearest revision of this sentence: 'The implementation of the rule by the council caused confusion.'",
        "choices": [
            "When the council implemented the rule, people became confused.",
            "The implementation rule by the council confusion caused.",
            "The council's implementation of the confusion caused the rule.",
            "People were confused by implementation from the rule of council.",
        ],
        "answer": "When the council implemented the rule, people became confused.",
        "explanation": "Changing heavy nominalisations back into verbs can make a sentence clearer.",
    },
    {
        "skill": "Cohesion",
        "prompt": "Which sentence uses a pronoun with the clearest antecedent?",
        "choices": [
            "After Mia spoke to Harper, Mia revised her argument.",
            "After Mia spoke to Harper, she revised her argument.",
            "Mia and Harper discussed her argument after she spoke.",
            "After the conversation, she changed it.",
        ],
        "answer": "After Mia spoke to Harper, Mia revised her argument.",
        "explanation": "Repeating Mia removes possible confusion about whether she refers to Mia or Harper.",
    },
    {
        "skill": "Cohesion",
        "prompt": "Choose the best transition to show contrast: 'The evidence is limited; ___, the pattern is still worth investigating.'",
        "choices": ["however", "therefore", "for example", "similarly"],
        "answer": "however",
        "explanation": "However signals contrast between limited evidence and continued value.",
    },
    {
        "skill": "Parallel structure",
        "prompt": "Choose the sentence with the strongest parallel structure.",
        "choices": [
            "The article is persuasive because it is concise, balanced and well researched.",
            "The article is persuasive because it is concise, balance and researching well.",
            "The article is persuasive because it is concision, balanced and well researched.",
            "The article is persuasive because it is concise, has balance and researching.",
        ],
        "answer": "The article is persuasive because it is concise, balanced and well researched.",
        "explanation": "Concise, balanced and well researched are parallel adjective phrases.",
    },
    {
        "skill": "Parallel structure",
        "prompt": "Which sentence avoids faulty comparison?",
        "choices": [
            "The themes in this poem are more complex than those in the first poem.",
            "The themes in this poem are more complex than the first poem.",
            "This poem's themes are more complex than the first poem.",
            "The themes in this poem are more complex than reading the first poem.",
        ],
        "answer": "The themes in this poem are more complex than those in the first poem.",
        "explanation": "The sentence compares themes with themes, not themes with a poem.",
    },
    {
        "skill": "Dangling modifiers",
        "prompt": "Choose the sentence that corrects the dangling modifier: 'After reading the article, the argument became clearer.'",
        "choices": [
            "After reading the article, I understood the argument more clearly.",
            "After reading the article, the argument understood me clearly.",
            "The argument became clearer after reading the article.",
            "Reading the article, the argument was clearer to understand.",
        ],
        "answer": "After reading the article, I understood the argument more clearly.",
        "explanation": "The introductory phrase needs to describe the person who did the reading.",
    },
    {
        "skill": "Misplaced modifiers",
        "prompt": "Which sentence places only most clearly?",
        "choices": [
            "The teacher only marked the essays that were submitted on time.",
            "Only the teacher marked the essays that were submitted on time.",
            "The teacher marked only the essays that were submitted on time.",
            "The teacher marked the essays that were submitted only on time.",
        ],
        "answer": "The teacher marked only the essays that were submitted on time.",
        "explanation": "Only should sit next to the words it limits: the essays submitted on time.",
    },
    {
        "skill": "Semicolons",
        "prompt": "Choose the sentence that correctly uses a semicolon with a conjunctive adverb.",
        "choices": [
            "The draft was detailed; however, it lacked a clear conclusion.",
            "The draft was detailed, however, it lacked a clear conclusion.",
            "The draft was detailed; however it lacked, a clear conclusion.",
            "The draft was detailed however; it lacked a clear conclusion.",
        ],
        "answer": "The draft was detailed; however, it lacked a clear conclusion.",
        "explanation": "A semicolon can join two independent clauses before a conjunctive adverb such as however.",
    },
    {
        "skill": "Colons",
        "prompt": "Choose the sentence that uses a colon correctly before an explanation.",
        "choices": [
            "The result was clear: the hypothesis needed revision.",
            "The result was: clear the hypothesis needed revision.",
            "The result: was clear the hypothesis needed revision.",
            "The result was clear the hypothesis: needed revision.",
        ],
        "answer": "The result was clear: the hypothesis needed revision.",
        "explanation": "A colon can introduce an explanation after a complete clause.",
    },
    {
        "skill": "Commas",
        "prompt": "Which sentence correctly punctuates an interrupter?",
        "choices": [
            "The solution, however, was more complicated than expected.",
            "The solution however, was more complicated than expected.",
            "The solution, however was more complicated than expected.",
            "The solution however was, more complicated than expected.",
        ],
        "answer": "The solution, however, was more complicated than expected.",
        "explanation": "An interrupting word such as however is usually set off with commas.",
    },
    {
        "skill": "Commas",
        "prompt": "Choose the sentence that avoids an unnecessary comma.",
        "choices": [
            "The student who designed the poster explained her choices.",
            "The student, who designed the poster, explained her choices.",
            "The student who designed the poster, explained her choices.",
            "The student, who designed the poster explained her choices.",
        ],
        "answer": "The student who designed the poster explained her choices.",
        "explanation": "When the relative clause identifies which student, it should not be set off with commas.",
    },
    {
        "skill": "Apostrophes",
        "prompt": "Choose the sentence with correct possession.",
        "choices": [
            "The head of English's announcement surprised the class.",
            "The head's of English announcement surprised the class.",
            "The head of Englishs' announcement surprised the class.",
            "The head of English announcement's surprised the class.",
        ],
        "answer": "The head of English's announcement surprised the class.",
        "explanation": "For a compound noun phrase, the possessive apostrophe is usually added to the final word.",
    },
    {
        "skill": "Apostrophes",
        "prompt": "Which sentence uses a plural possessive correctly?",
        "choices": [
            "The students' reflections showed careful thinking.",
            "The student's reflections showed careful thinking from all students.",
            "The students reflections' showed careful thinking.",
            "The student reflections's showed careful thinking.",
        ],
        "answer": "The students' reflections showed careful thinking.",
        "explanation": "Students' shows that the reflections belong to multiple students.",
    },
    {
        "skill": "Reported speech",
        "prompt": "Choose the best reported speech version of: 'I am revising my conclusion,' said Priya.",
        "choices": [
            "Priya said that she was revising her conclusion.",
            "Priya said that I am revising my conclusion.",
            "Priya said that she is revised her conclusion.",
            "Priya said that she had revise her conclusion.",
        ],
        "answer": "Priya said that she was revising her conclusion.",
        "explanation": "Reported speech usually changes first-person pronouns and may backshift the tense.",
    },
    {
        "skill": "Reported speech",
        "prompt": "Choose the correctly reported question.",
        "choices": [
            "The teacher asked whether the class had finished the task.",
            "The teacher asked had the class finished the task.",
            "The teacher asked whether had the class finished the task.",
            "The teacher asked did the class finish the task.",
        ],
        "answer": "The teacher asked whether the class had finished the task.",
        "explanation": "Reported questions use statement word order, not question word order.",
    },
    {
        "skill": "Articles",
        "prompt": "Choose the sentence with correct article use.",
        "choices": [
            "The report analyses the role of education in democracy.",
            "The report analyses role of education in the democracy.",
            "The report analyses a role of the education in democracy.",
            "The report analyses the role of the education in the democracy.",
        ],
        "answer": "The report analyses the role of education in democracy.",
        "explanation": "Abstract nouns such as education and democracy often take no article when used generally.",
    },
    {
        "skill": "Quantifiers",
        "prompt": "Choose the correct sentence.",
        "choices": [
            "Fewer students chose the extension task this week.",
            "Less students chose the extension task this week.",
            "A fewer number of students chose the extension task this week.",
            "Much students chose the extension task this week.",
        ],
        "answer": "Fewer students chose the extension task this week.",
        "explanation": "Use fewer with countable plural nouns such as students.",
    },
    {
        "skill": "Quantifiers",
        "prompt": "Choose the sentence with the correct quantifier.",
        "choices": [
            "There was less noise in the library after lunch.",
            "There were fewer noise in the library after lunch.",
            "There was fewer noise in the library after lunch.",
            "There were many noise in the library after lunch.",
        ],
        "answer": "There was less noise in the library after lunch.",
        "explanation": "Use less with uncountable nouns such as noise.",
    },
    {
        "skill": "Apposition",
        "prompt": "Which sentence correctly punctuates an appositive phrase?",
        "choices": [
            "Dr Patel, the guest speaker, discussed renewable energy.",
            "Dr Patel the guest speaker, discussed renewable energy.",
            "Dr Patel, the guest speaker discussed renewable energy.",
            "Dr Patel the guest speaker discussed, renewable energy.",
        ],
        "answer": "Dr Patel, the guest speaker, discussed renewable energy.",
        "explanation": "A non-essential appositive phrase is set off with commas.",
    },
    {
        "skill": "Ellipsis",
        "prompt": "Which sentence uses ellipsis correctly to avoid repetition?",
        "choices": [
            "Mia chose the poem; Noah, the short story.",
            "Mia chose the poem; Noah the short story chose.",
            "Mia chose the poem; Noah, chose the short story.",
            "Mia chose the poem; Noah, the short story chose.",
        ],
        "answer": "Mia chose the poem; Noah, the short story.",
        "explanation": "The verb chose is omitted in the second clause because it is understood from the first clause.",
    },
    {
        "skill": "Formal language",
        "prompt": "Choose the most concise academic sentence.",
        "choices": [
            "The findings indicate a correlation between sleep and concentration.",
            "The findings sort of show that sleep and concentration are linked in a way.",
            "Sleep and concentration, you know, connect heaps in the findings.",
            "The findings are basically about sleep doing things to concentration.",
        ],
        "answer": "The findings indicate a correlation between sleep and concentration.",
        "explanation": "Academic style values precise vocabulary, concision and an appropriate level of formality.",
    },
    {
        "skill": "Formal language",
        "prompt": "Which sentence best avoids wordiness?",
        "choices": [
            "The speaker repeated the claim to emphasise its importance.",
            "The speaker repeated the claim again to emphasise how important it was in importance.",
            "The speaker made a repetition of the claim again for importance.",
            "The claim was repeated again by the speaker due to its important importance.",
        ],
        "answer": "The speaker repeated the claim to emphasise its importance.",
        "explanation": "The best sentence avoids repeated again and other unnecessary wording.",
    },
]

QUESTIONS.extend(
    [
        {
            "min_year": 7,
            "skill": "Apostrophes",
            "prompt": "Choose the sentence that correctly distinguishes its and it's.",
            "choices": [
                "The club changed its rules because it's growing quickly.",
                "The club changed it's rules because its growing quickly.",
                "The club changed its' rules because it's growing quickly.",
                "The club changed it's rules because its' growing quickly.",
            ],
            "answer": "The club changed its rules because it's growing quickly.",
            "explanation": "Its is possessive, while it's is the contraction of it is.",
        },
        {
            "min_year": 7,
            "skill": "Subject-verb agreement",
            "prompt": "Which sentence has correct subject-verb agreement?",
            "choices": [
                "The collection of old maps belongs in the library.",
                "The collection of old maps belong in the library.",
                "The collection of old maps belonging in the library.",
                "The collection of old maps have belong in the library.",
            ],
            "answer": "The collection of old maps belongs in the library.",
            "explanation": "The head noun collection is singular, so it takes the singular verb belongs.",
        },
        {
            "min_year": 7,
            "skill": "Commas",
            "prompt": "Choose the sentence with the introductory phrase punctuated correctly.",
            "choices": [
                "After the final bell, the team met in the gym.",
                "After the final bell the team, met in the gym.",
                "After, the final bell the team met in the gym.",
                "After the final, bell the team met in the gym.",
            ],
            "answer": "After the final bell, the team met in the gym.",
            "explanation": "A comma separates the introductory phrase from the main clause.",
        },
        {
            "min_year": 7,
            "skill": "Tense consistency",
            "prompt": "Which sentence keeps the past tense consistent?",
            "choices": [
                "Amir opened the gate and waited for the others.",
                "Amir opened the gate and waits for the others.",
                "Amir opens the gate and waited for the others.",
                "Amir had open the gate and waits for the others.",
            ],
            "answer": "Amir opened the gate and waited for the others.",
            "explanation": "Opened and waited are both in the simple past tense.",
        },
        {
            "min_year": 7,
            "skill": "Direct speech",
            "prompt": "Choose the correctly punctuated direct speech.",
            "choices": [
                "'Please bring your notes,' Ms Chen said.",
                "'Please bring your notes' Ms Chen said.",
                "'Please bring your notes', Ms Chen said.",
                "Please bring your notes, 'Ms Chen said.'",
            ],
            "answer": "'Please bring your notes,' Ms Chen said.",
            "explanation": "The comma belongs inside the closing quotation mark before the reporting clause.",
        },
        {
            "min_year": 7,
            "skill": "Commonly confused words",
            "prompt": "Choose the sentence that uses affect and effect correctly.",
            "choices": [
                "The new timetable may affect attendance, but its full effect is not yet known.",
                "The new timetable may effect attendance, but its full affect is not yet known.",
                "The new timetable may affect attendance, but its full affect is not yet known.",
                "The new timetable may effect attendance, but its full effect is not yet known.",
            ],
            "answer": "The new timetable may affect attendance, but its full effect is not yet known.",
            "explanation": "Affect is usually a verb meaning influence; effect is usually a noun meaning result.",
        },
        {
            "min_year": 7,
            "skill": "Pronouns",
            "prompt": "Which sentence has a clear pronoun reference?",
            "choices": [
                "When Leila spoke to Rosa, Leila explained the new rule.",
                "When Leila spoke to Rosa, she explained it to her.",
                "Leila told Rosa that she had changed her mind about her idea.",
                "After she met her, she explained what she meant.",
            ],
            "answer": "When Leila spoke to Rosa, Leila explained the new rule.",
            "explanation": "Repeating the name removes uncertainty about who explained the rule.",
        },
        {
            "min_year": 7,
            "skill": "Run-on sentences",
            "prompt": "Which option correctly repairs the run-on sentence: The rain stopped we continued the match?",
            "choices": [
                "The rain stopped, so we continued the match.",
                "The rain stopped, we continued the match.",
                "The rain stopped and, we continued the match.",
                "The rain stopped we, continued the match.",
            ],
            "answer": "The rain stopped, so we continued the match.",
            "explanation": "A comma plus the coordinating conjunction so correctly joins the two complete clauses.",
        },
        {
            "min_year": 8,
            "skill": "Semicolons",
            "prompt": "Choose the sentence that correctly joins two closely related independent clauses.",
            "choices": [
                "The evidence was convincing; the audience changed its view.",
                "The evidence was convincing; because the audience changed its view.",
                "The evidence; was convincing the audience changed its view.",
                "The evidence was; convincing, the audience changed its view.",
            ],
            "answer": "The evidence was convincing; the audience changed its view.",
            "explanation": "A semicolon can join two complete clauses that express closely connected ideas.",
        },
        {
            "min_year": 8,
            "skill": "Colons",
            "prompt": "Which sentence correctly introduces a list with a colon?",
            "choices": [
                "The proposal has three strengths: clarity, fairness and affordability.",
                "The proposal has: clarity, fairness and affordability.",
                "The proposal: has three strengths clarity, fairness and affordability.",
                "The proposal has three: strengths, clarity, fairness and affordability.",
            ],
            "answer": "The proposal has three strengths: clarity, fairness and affordability.",
            "explanation": "A colon may introduce a list after a complete clause.",
        },
        {
            "min_year": 8,
            "skill": "Relative clauses",
            "prompt": "Choose the sentence with a correctly punctuated non-essential relative clause.",
            "choices": [
                "The library, which reopened in May, now stays open later.",
                "The library which reopened in May, now stays open later.",
                "The library, which reopened in May now stays open later.",
                "The library which, reopened in May, now stays open later.",
            ],
            "answer": "The library, which reopened in May, now stays open later.",
            "explanation": "The extra information can be removed, so the clause is set off with a pair of commas.",
        },
        {
            "min_year": 8,
            "skill": "Active and passive voice",
            "prompt": "Which sentence uses active voice to make responsibility clearest?",
            "choices": [
                "The council approved the new crossing.",
                "The new crossing was approved.",
                "Approval was given to the new crossing.",
                "The new crossing had been being approved.",
            ],
            "answer": "The council approved the new crossing.",
            "explanation": "Active voice names the actor, the council, and gives the sentence a direct verb.",
        },
        {
            "min_year": 8,
            "skill": "Parallel structure",
            "prompt": "Which sentence uses parallel structure?",
            "choices": [
                "The program aims to reduce waste, improve safety and support students.",
                "The program aims to reduce waste, improving safety and student support.",
                "The program aims at reducing waste, to improve safety and supports students.",
                "The program aims to reduce waste, safety improvement and supporting students.",
            ],
            "answer": "The program aims to reduce waste, improve safety and support students.",
            "explanation": "Each item follows the same verb pattern: reduce, improve and support.",
        },
        {
            "min_year": 8,
            "skill": "Misplaced modifiers",
            "prompt": "Choose the sentence in which the modifier clearly describes the correct noun.",
            "choices": [
                "Wearing a bright vest, the cyclist was easy for drivers to see.",
                "Wearing a bright vest, drivers could easily see the cyclist.",
                "The cyclist was easy, wearing a bright vest, for drivers to see.",
                "Drivers wearing a bright vest could easily see the cyclist.",
            ],
            "answer": "Wearing a bright vest, the cyclist was easy for drivers to see.",
            "explanation": "The cyclist immediately follows the phrase wearing a bright vest, so the meaning is clear.",
        },
        {
            "min_year": 8,
            "skill": "Reported speech",
            "prompt": "Choose the best reported version of: 'Where did you put the survey?' the teacher asked Mia.",
            "choices": [
                "The teacher asked Mia where she had put the survey.",
                "The teacher asked Mia where did she put the survey.",
                "The teacher asked Mia where had she put the survey.",
                "The teacher asked Mia where she has putted the survey.",
            ],
            "answer": "The teacher asked Mia where she had put the survey.",
            "explanation": "Reported questions use statement word order and usually backshift the tense.",
        },
        {
            "min_year": 8,
            "skill": "Cohesion",
            "prompt": "Which transition best completes the contrast? The plan is affordable. ___, it may take months to organise.",
            "choices": ["However", "For example", "Therefore", "Similarly"],
            "answer": "However",
            "explanation": "However signals a contrast between affordability and the time needed to organise the plan.",
        },
        {
            "min_year": 9,
            "skill": "Nominalisation",
            "prompt": "Which sentence uses nominalisation to create a concise academic tone?",
            "choices": [
                "The committee's rejection of the proposal caused concern.",
                "The committee rejected the proposal and this made people concerned about it.",
                "The committee did a reject of the proposal, causing concernment.",
                "The proposal was rejectingly concerning to the committee.",
            ],
            "answer": "The committee's rejection of the proposal caused concern.",
            "explanation": "Rejection turns the process into a noun and creates a concise academic expression.",
        },
        {
            "min_year": 9,
            "skill": "Conditionals",
            "prompt": "Which sentence correctly uses the third conditional?",
            "choices": [
                "If the team had checked the data, it would have noticed the error.",
                "If the team checked the data, it would have noticed the error yesterday.",
                "If the team had checked the data, it will notice the error.",
                "If the team would have checked the data, it had noticed the error.",
            ],
            "answer": "If the team had checked the data, it would have noticed the error.",
            "explanation": "The third conditional uses if + past perfect and would have + past participle.",
        },
        {
            "min_year": 9,
            "skill": "Perfect aspect",
            "prompt": "Which sentence correctly uses the future perfect?",
            "choices": [
                "By Friday, we will have completed the investigation.",
                "By Friday, we will completed the investigation.",
                "By Friday, we have will complete the investigation.",
                "By Friday, we will had completed the investigation.",
            ],
            "answer": "By Friday, we will have completed the investigation.",
            "explanation": "The future perfect uses will have followed by the past participle.",
        },
        {
            "min_year": 9,
            "skill": "Dangling modifiers",
            "prompt": "Which sentence correctly repairs the dangling modifier?",
            "choices": [
                "After reviewing the evidence, the students revised their conclusion.",
                "After reviewing the evidence, the conclusion was revised.",
                "After reviewing the evidence, there was a revised conclusion.",
                "After reviewing the evidence, revision of the conclusion occurred.",
            ],
            "answer": "After reviewing the evidence, the students revised their conclusion.",
            "explanation": "The students are the people who reviewed the evidence, so they must follow the opening phrase.",
        },
        {
            "min_year": 9,
            "skill": "Embedded clauses",
            "prompt": "Choose the sentence that correctly embeds a clause as the object of the verb.",
            "choices": [
                "Researchers predict that the results will change over time.",
                "Researchers predict that will the results change over time.",
                "Researchers predict, that the results will change over time.",
                "Researchers predict the results that will change over time are.",
            ],
            "answer": "Researchers predict that the results will change over time.",
            "explanation": "The clause that the results will change over time functions as the object of predict.",
        },
        {
            "min_year": 9,
            "skill": "Mood",
            "prompt": "Which sentence uses the subjunctive mood correctly in formal English?",
            "choices": [
                "The principal recommended that every student be present.",
                "The principal recommended that every student is present.",
                "The principal recommended that every student was present tomorrow.",
                "The principal recommended every student to being present.",
            ],
            "answer": "The principal recommended that every student be present.",
            "explanation": "After a formal recommendation, the subjunctive uses the base form be.",
        },
        {
            "min_year": 9,
            "skill": "Apposition",
            "prompt": "Which sentence correctly punctuates a non-essential appositive?",
            "choices": [
                "Our captain, Maya Singh, addressed the assembly.",
                "Our captain Maya Singh, addressed the assembly.",
                "Our captain, Maya Singh addressed the assembly.",
                "Our, captain Maya Singh, addressed the assembly.",
            ],
            "answer": "Our captain, Maya Singh, addressed the assembly.",
            "explanation": "The name is extra identifying information and is set off with a pair of commas.",
        },
        {
            "min_year": 9,
            "skill": "Ellipsis",
            "prompt": "Which sentence correctly omits repeated words while keeping the meaning clear?",
            "choices": [
                "The Year 8 team chose solar power; the Year 9 team, wind power.",
                "The Year 8 team chose solar power; the Year 9 team wind power chose.",
                "The Year 8 team chose solar power, the Year 9 team, wind power.",
                "The Year 8 team chose solar power; chose the Year 9 team wind power.",
            ],
            "answer": "The Year 8 team chose solar power; the Year 9 team, wind power.",
            "explanation": "The repeated verb chose is omitted from the second clause and represented by a comma.",
        },
    ]
)

QUIZ_SIZE = 10
YEAR_LEVELS = ["Year 7", "Year 8", "Year 9"]
GRAMMAR_PRACTICE_MODES = ["Smart mix", "Review my mistakes", "Fresh questions"]

YEAR_SKILLS = {
    "Year 7": {
        "Apostrophes",
        "Articles",
        "Capitalisation",
        "Commas",
        "Commonly confused words",
        "Comparatives",
        "Conjunctions",
        "Direct speech",
        "Prepositions",
        "Pronouns",
        "Quantifiers",
        "Run-on sentences",
        "Sentence fragments",
        "Subject-verb agreement",
        "Tense consistency",
        "Their, there, they're",
        "Your and you're",
    },
    "Year 8": {
        "Active and passive voice",
        "Apostrophes",
        "Articles",
        "Capitalisation",
        "Clause types",
        "Cohesion",
        "Colons",
        "Commas",
        "Commonly confused words",
        "Comparatives",
        "Conjunctions",
        "Determiners",
        "Direct speech",
        "Formal language",
        "Misplaced modifiers",
        "Modal verbs",
        "Modifiers",
        "Noun phrases",
        "Parallel structure",
        "Prepositional phrases",
        "Prepositions",
        "Pronouns",
        "Quantifiers",
        "Relative clauses",
        "Reported speech",
        "Run-on sentences",
        "Semicolons",
        "Sentence fragments",
        "Subject-verb agreement",
        "Tense consistency",
    },
}

for question in QUESTIONS:
    if "min_year" not in question:
        if question["skill"] in YEAR_SKILLS["Year 7"]:
            question["min_year"] = 7
        elif question["skill"] in YEAR_SKILLS["Year 8"]:
            question["min_year"] = 8
        else:
            question["min_year"] = 9

YEAR_SKILLS["Year 9"] = {question["skill"] for question in QUESTIONS}

SKILL_TIPS = {
    "Apostrophes": "Decide whether the word shows possession, a contraction or a simple plural before adding an apostrophe.",
    "Commas": "Read the sentence aloud and identify introductions, extra information and clause boundaries.",
    "Subject-verb agreement": "Ignore words between the subject and verb, then match the verb to the head noun.",
    "Tense consistency": "Mark the time frame first, then check that every main verb stays in that frame.",
    "Direct speech": "Keep spoken punctuation inside the quotation marks and separate the reporting clause correctly.",
    "Commonly confused words": "Substitute a short definition for each option and choose the word whose meaning fits.",
    "Run-on sentences": "Find each complete thought, then join them with a full stop, semicolon or comma plus conjunction.",
    "Semicolons": "Check that the words on both sides could stand as complete sentences.",
    "Colons": "Make sure the words before the colon form a complete clause that introduces what follows.",
    "Relative clauses": "Ask whether the clause identifies the noun or only adds extra information.",
    "Parallel structure": "Make every item in a list follow the same grammatical pattern.",
    "Reported speech": "Change pronouns and time references, then use statement word order.",
    "Conditionals": "Identify whether the condition is real, imagined now or imagined in the past before choosing verb forms.",
    "Dangling modifiers": "Place the person or thing doing the opening action immediately after the comma.",
    "Formal language": "Prefer precise verbs and nouns; remove slang, repetition and vague fillers.",
}


def level_number(level: str) -> int:
    return int(level.split()[-1])


def skills_for_level(level: str) -> list[str]:
    return sorted(
        {
            question["skill"]
            for question in QUESTIONS
            if question["min_year"] <= level_number(level)
            and question["skill"] in YEAR_SKILLS.get(level, YEAR_SKILLS["Year 9"])
        }
    )


def available_indexes_for_level(level: str, focus: str = "All skills") -> list[int]:
    skills = YEAR_SKILLS.get(level, YEAR_SKILLS["Year 9"])
    return [
        index
        for index, question in enumerate(QUESTIONS)
        if question["skill"] in skills
        and question["min_year"] <= level_number(level)
        and (focus == "All skills" or question["skill"] == focus)
    ]


def choose_grammar_indexes(
    level: str,
    quiz_size: int,
    focus: str = "All skills",
    review_skills: list[str] | None = None,
    review_ratio: float = 0.4,
    exclude_indexes: list[int] | None = None,
    seed: int | None = None,
) -> list[int]:
    rng = random.Random(seed)
    available = available_indexes_for_level(level, focus)
    quiz_size = min(quiz_size, len(available))
    if quiz_size <= 0:
        return []

    excluded = set(exclude_indexes or [])
    fresh = [index for index in available if index not in excluded]
    pool = fresh if len(fresh) >= quiz_size else available
    review_set = set(review_skills or [])
    priority = [index for index in pool if QUESTIONS[index]["skill"] in review_set]
    target_count = min(len(priority), round(quiz_size * review_ratio)) if review_set else 0
    if review_set and priority and target_count == 0:
        target_count = 1
    selected = rng.sample(priority, target_count) if target_count else []
    remaining = [index for index in pool if index not in set(selected)]
    selected.extend(rng.sample(remaining, min(quiz_size - len(selected), len(remaining))))
    rng.shuffle(selected)
    return selected


def grammar_rank(xp: int) -> str:
    if xp >= 1200:
        return "Editor"
    if xp >= 700:
        return "Sentence Architect"
    if xp >= 350:
        return "Rule Detective"
    if xp >= 150:
        return "Proofreader"
    return "Starter"


def initialise_state() -> None:
    if "grammar_level" not in st.session_state:
        st.session_state.grammar_level = "Year 7"
    if "grammar_focus" not in st.session_state:
        st.session_state.grammar_focus = "All skills"
    if "grammar_size" not in st.session_state:
        st.session_state.grammar_size = QUIZ_SIZE
    if "grammar_practice_mode" not in st.session_state:
        st.session_state.grammar_practice_mode = "Smart mix"
    if "grammar_review_queue" not in st.session_state:
        st.session_state.grammar_review_queue = {}
    if "grammar_history" not in st.session_state:
        st.session_state.grammar_history = []
    if "grammar_xp" not in st.session_state:
        st.session_state.grammar_xp = 0
    if "grammar_best" not in st.session_state:
        st.session_state.grammar_best = 0
    if "grammar_completed" not in st.session_state:
        st.session_state.grammar_completed = 0
    if "quiz_number" not in st.session_state:
        st.session_state.quiz_number = 0
        start_new_quiz()


def start_new_quiz() -> None:
    st.session_state.quiz_number = st.session_state.get("quiz_number", 0) + 1
    level = st.session_state.get("grammar_level", "Year 7")
    focus = st.session_state.get("grammar_focus", "All skills")
    if focus != "All skills" and focus not in skills_for_level(level):
        focus = "All skills"
        st.session_state.grammar_focus = focus
    mode = st.session_state.get("grammar_practice_mode", "Smart mix")
    review_ratio = {
        "Smart mix": 0.4,
        "Review my mistakes": 0.75,
        "Fresh questions": 0.0,
    }[mode]
    st.session_state.quiz_indexes = choose_grammar_indexes(
        level,
        st.session_state.get("grammar_size", QUIZ_SIZE),
        focus=focus,
        review_skills=list(st.session_state.get("grammar_review_queue", {})) if review_ratio else [],
        review_ratio=review_ratio,
        exclude_indexes=st.session_state.get("quiz_indexes", []),
    )
    st.session_state.choice_orders = {
        question_index: random.sample(
            QUESTIONS[question_index]["choices"],
            len(QUESTIONS[question_index]["choices"]),
        )
        for question_index in st.session_state.quiz_indexes
    }
    st.session_state.submitted = False
    st.session_state.answers = {}


def change_grammar_level() -> None:
    st.session_state.grammar_focus = "All skills"
    start_new_quiz()


def start_review_round() -> None:
    st.session_state.grammar_focus = "All skills"
    st.session_state.grammar_practice_mode = "Review my mistakes"
    start_new_quiz()


def answer_key(question_index: int) -> str:
    return f"quiz_{st.session_state.quiz_number}_question_{question_index}"


def collect_answers() -> dict[int, str | None]:
    return {
        question_index: st.session_state.get(answer_key(question_index))
        for question_index in st.session_state.quiz_indexes
    }


def get_choices(question_index: int) -> list[str]:
    if "choice_orders" not in st.session_state:
        st.session_state.choice_orders = {}
    if question_index not in st.session_state.choice_orders:
        st.session_state.choice_orders[question_index] = random.sample(
            QUESTIONS[question_index]["choices"],
            len(QUESTIONS[question_index]["choices"]),
        )
    return st.session_state.choice_orders[question_index]


def get_score(answers: dict[int, str | None]) -> int:
    return sum(
        answers.get(question_index) == QUESTIONS[question_index]["answer"]
        for question_index in st.session_state.quiz_indexes
    )


def update_grammar_progress(answers: dict[int, str | None]) -> None:
    score = get_score(answers)
    total = len(st.session_state.quiz_indexes)
    percentage = round(score / total * 100) if total else 0
    previous = st.session_state.grammar_history[-1]["accuracy"] if st.session_state.grammar_history else None
    outcomes = {}
    for question_index in st.session_state.quiz_indexes:
        skill = QUESTIONS[question_index]["skill"]
        outcomes.setdefault(skill, {"correct": 0, "wrong": 0})
        result_key = "correct" if answers.get(question_index) == QUESTIONS[question_index]["answer"] else "wrong"
        outcomes[skill][result_key] += 1

    queue = dict(st.session_state.grammar_review_queue)
    for skill, result in outcomes.items():
        if result["wrong"]:
            queue[skill] = min(5, queue.get(skill, 0) + result["wrong"])
        elif result["correct"] and skill in queue:
            queue[skill] -= 1
            if queue[skill] <= 0:
                queue.pop(skill)

    st.session_state.grammar_review_queue = queue
    st.session_state.grammar_xp += 20 + score * 8
    st.session_state.grammar_completed += 1
    st.session_state.grammar_best = max(st.session_state.grammar_best, percentage)
    st.session_state.grammar_history.append(
        {
            "date": datetime.now().astimezone().isoformat(timespec="seconds"),
            "level": st.session_state.grammar_level,
            "focus": st.session_state.grammar_focus,
            "score": score,
            "total": total,
            "accuracy": percentage,
            "change": None if previous is None else percentage - previous,
        }
    )


def grammar_results_csv(answers: dict[int, str | None]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["Question", "Year", "Skill", "Prompt", "Your answer", "Correct answer", "Result", "Rule", "Practice tip"],
    )
    writer.writeheader()
    for display_number, question_index in enumerate(st.session_state.quiz_indexes, start=1):
        question = QUESTIONS[question_index]
        selected = answers.get(question_index)
        writer.writerow(
            {
                "Question": display_number,
                "Year": st.session_state.grammar_level,
                "Skill": question["skill"],
                "Prompt": question["prompt"],
                "Your answer": selected or "Not answered",
                "Correct answer": question["answer"],
                "Result": "Correct" if selected == question["answer"] else "Review",
                "Rule": question["explanation"],
                "Practice tip": SKILL_TIPS.get(question["skill"], "Compare the answer choices one feature at a time and explain why each incorrect option fails."),
            }
        )
    return output.getvalue()


def encouragement(score: int, total: int) -> tuple[str, str]:
    if score == total:
        return (
            "Outstanding work.",
            "You handled every grammar point in this set. Try another round and see if you can keep the streak going.",
        )
    if score >= total * 0.8:
        return (
            "Great effort.",
            "You have strong control of these skills. Review the feedback for the couple of items that need polishing.",
        )
    if score >= total * 0.6:
        return (
            "Good progress.",
            "You are building solid habits. Focus on the skill areas listed below, then try a fresh set.",
        )
    if score >= total * 0.4:
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
    total = len(st.session_state.quiz_indexes)
    percentage = round(score / total * 100)
    title, message = encouragement(score, total)
    missed_skills = Counter(
        QUESTIONS[question_index]["skill"]
        for question_index in st.session_state.quiz_indexes
        if answers.get(question_index) != QUESTIONS[question_index]["answer"]
    )

    st.divider()
    st.subheader("Results")
    st.success(f"{title} {message}")

    col_score, col_accuracy, col_best, col_xp = st.columns(4)
    col_score.metric("Score", f"{score}/{total}")
    col_accuracy.metric("Accuracy", f"{percentage}%")
    col_best.metric("Personal best", f"{st.session_state.grammar_best}%")
    col_xp.metric("Practice XP", st.session_state.grammar_xp)
    st.progress(score / total)

    latest = st.session_state.grammar_history[-1] if st.session_state.grammar_history else None
    if latest and latest["change"] is not None and latest["change"] > 0:
        st.success(f"You improved by {latest['change']} percentage points from the previous challenge.")

    if missed_skills:
        focus = ", ".join(skill for skill, _ in missed_skills.most_common(3))
        st.info(f"Focus for your next round: {focus}. Fresh examples from these skills are in your review queue.")
    else:
        st.info("No missed skills in this round. Try a fresh set or move up to a more advanced skill.")

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
                st.markdown(f"**Your answer:** {selected or 'Not answered'}")
                st.markdown(f"**Correct answer:** {question['answer']}")
            st.markdown(f"**Rule:** {question['explanation']}")
            st.caption(
                "Try next time: "
                + SKILL_TIPS.get(
                    question["skill"],
                    "Compare one grammar feature at a time and explain why the other choices do not work.",
                )
            )

    if missed_skills:
        st.button(
            "Practise my mistakes now",
            type="primary",
            width="stretch",
            on_click=start_review_round,
        )

    export_left, export_right = st.columns(2)
    export_left.download_button(
        "Export this result (CSV)",
        data=grammar_results_csv(answers),
        file_name=f"grammar_result_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        width="stretch",
    )
    progress_payload = {
        "app": "Year 7-9 Grammar Studio",
        "exported": datetime.now().astimezone().isoformat(timespec="seconds"),
        "xp": st.session_state.grammar_xp,
        "rank": grammar_rank(st.session_state.grammar_xp),
        "best_accuracy": st.session_state.grammar_best,
        "review_queue": st.session_state.grammar_review_queue,
        "history": st.session_state.grammar_history,
    }
    export_right.download_button(
        "Export progress (JSON)",
        data=json.dumps(progress_payload, indent=2),
        file_name="grammar_progress.json",
        mime="application/json",
        width="stretch",
    )


st.set_page_config(
    page_title="Year 7-9 Grammar Studio",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: #f5f7fa;
    }
    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
    }
    .grammar-hero {
        background: #143a3a;
        border-bottom: 6px solid #f0b84b;
        border-radius: 6px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 12px 28px rgba(20, 58, 58, 0.15);
    }
    .grammar-hero h1 {
        margin: 0 0 0.35rem 0;
        color: #ffffff;
        font-size: 2.15rem;
        letter-spacing: 0;
    }
    .grammar-hero p {
        margin: 0;
        color: #d8eded;
    }
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #d7e0e8;
        border-left: 4px solid #2d8e8b;
        border-radius: 6px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 24px rgba(23, 32, 51, 0.05);
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d7e0e8;
        border-top: 4px solid #d85b45;
        border-radius: 6px;
        padding: 0.8rem;
    }
    div.stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
        min-height: 46px;
        font-weight: 800;
        background: #d85b45;
        border: 1px solid #bd4633;
        color: #ffffff;
        box-shadow: 0 8px 16px rgba(189, 70, 51, 0.16);
    }
    .skill-pill {
        display: inline-block;
        background: #e9f7f5;
        color: #175f5d;
        border: 1px solid #a9d9d5;
        border-radius: 999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    @media (max-width: 700px) {
        .grammar-hero h1 { font-size: 1.75rem; }
        .block-container { padding-top: 0.75rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

initialise_state()

st.markdown(
    """
    <div class="grammar-hero">
        <h1>Year 7-9 Grammar Studio</h1>
        <p>Targeted Australian English practice with instant feedback after submission.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

control_col, metric_col = st.columns([3, 1])
with control_col:
    control_1, control_2, control_3, control_4 = st.columns(4)
    with control_1:
        st.selectbox(
            "Year level",
            YEAR_LEVELS,
            key="grammar_level",
            on_change=change_grammar_level,
        )
    with control_2:
        focus_options = ["All skills", *skills_for_level(st.session_state.grammar_level)]
        if st.session_state.grammar_focus not in focus_options:
            st.session_state.grammar_focus = "All skills"
        st.selectbox("Skill focus", focus_options, key="grammar_focus", on_change=start_new_quiz)
    with control_3:
        st.selectbox("Questions", [5, 10, 15, 20], key="grammar_size", on_change=start_new_quiz)
    with control_4:
        st.selectbox(
            "Practice mode",
            GRAMMAR_PRACTICE_MODES,
            key="grammar_practice_mode",
            on_change=start_new_quiz,
            help="Smart mix adds fresh examples from skills missed earlier.",
        )
    st.button("Start fresh grammar challenge", type="primary", width="stretch", on_click=start_new_quiz)
with metric_col:
    level_bank = len(available_indexes_for_level(st.session_state.grammar_level, st.session_state.grammar_focus))
    metric_1, metric_2 = st.columns(2)
    metric_1.metric("Questions", len(st.session_state.quiz_indexes))
    metric_2.metric("Level bank", level_bank)
    st.caption(f"Current set #{st.session_state.quiz_number} for {st.session_state.grammar_level}.")

progress_1, progress_2, progress_3, progress_4 = st.columns(4)
progress_1.metric("Rank", grammar_rank(st.session_state.grammar_xp))
progress_2.metric("Practice XP", st.session_state.grammar_xp)
progress_3.metric("Completed", st.session_state.grammar_completed)
progress_4.metric("Review queue", sum(st.session_state.grammar_review_queue.values()))

if st.session_state.submitted:
    st.info("This challenge has been submitted. Start a fresh grammar challenge when you are ready for another set.")

with st.form("grammar_quiz"):
    for display_number, question_index in enumerate(st.session_state.quiz_indexes, start=1):
        question = QUESTIONS[question_index]
        st.markdown(f"<span class='skill-pill'>{question['skill']}</span>", unsafe_allow_html=True)
        st.markdown(f"**{display_number}. {question['prompt']}**")
        st.radio(
            label=f"Question {display_number} options",
            options=get_choices(question_index),
            key=answer_key(question_index),
            index=None,
            disabled=st.session_state.submitted,
            label_visibility="collapsed",
        )
        st.divider()

    submitted = st.form_submit_button(
        "Submit grammar challenge",
        width="stretch",
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
        update_grammar_progress(answers)
        st.session_state.submitted = True
        st.rerun()

if st.session_state.submitted:
    show_results(st.session_state.answers)
