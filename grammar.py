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

QUIZ_SIZE = 10
YEAR_LEVELS = ["Year 7", "Year 8", "Year 9"]

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
YEAR_SKILLS["Year 9"] = {question["skill"] for question in QUESTIONS}


def available_indexes_for_level(level: str) -> list[int]:
    skills = YEAR_SKILLS.get(level, YEAR_SKILLS["Year 9"])
    return [
        index
        for index, question in enumerate(QUESTIONS)
        if question["skill"] in skills
    ]


def initialise_state() -> None:
    if "grammar_level" not in st.session_state:
        st.session_state.grammar_level = "Year 7"
    if "quiz_number" not in st.session_state:
        st.session_state.quiz_number = 0
        start_new_quiz()


def start_new_quiz() -> None:
    st.session_state.quiz_number = st.session_state.get("quiz_number", 0) + 1
    available_indexes = available_indexes_for_level(st.session_state.get("grammar_level", "Year 7"))
    quiz_size = min(QUIZ_SIZE, len(available_indexes))
    st.session_state.quiz_indexes = random.sample(available_indexes, quiz_size)
    st.session_state.choice_orders = {
        question_index: random.sample(
            QUESTIONS[question_index]["choices"],
            len(QUESTIONS[question_index]["choices"]),
        )
        for question_index in st.session_state.quiz_indexes
    }
    st.session_state.submitted = False
    st.session_state.answers = {}


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

    col_score, col_accuracy, col_bank = st.columns(3)
    col_score.metric("Score", f"{score}/{total}")
    col_accuracy.metric("Accuracy", f"{percentage}%")
    col_bank.metric("Question set", f"#{st.session_state.quiz_number}")
    st.progress(score / total)

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
    page_title="Year 7-9 Grammar Studio",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background:
            linear-gradient(90deg, rgba(37, 99, 235, 0.08), rgba(15, 118, 110, 0.08), rgba(245, 158, 11, 0.08)),
            #f8fafc;
    }
    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
    }
    .grammar-hero {
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-left: 10px solid #0f766e;
        border-radius: 8px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 24px rgba(23, 32, 51, 0.06);
    }
    .grammar-hero h1 {
        margin: 0 0 0.35rem 0;
        color: #172033;
        font-size: 2.25rem;
    }
    .grammar-hero p {
        margin: 0;
        color: #4b5563;
    }
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 8px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 24px rgba(23, 32, 51, 0.06);
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 8px;
        padding: 0.8rem;
    }
    div.stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
        min-height: 46px;
        font-weight: 700;
    }
    .skill-pill {
        display: inline-block;
        background: #ecfeff;
        color: #155e75;
        border: 1px solid #a5f3fc;
        border-radius: 999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
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

control_col, metric_col = st.columns([2, 1])
with control_col:
    st.selectbox(
        "Year level",
        YEAR_LEVELS,
        key="grammar_level",
        on_change=start_new_quiz,
    )
    st.button("Start fresh grammar challenge", type="primary", use_container_width=True, on_click=start_new_quiz)
with metric_col:
    level_bank = len(available_indexes_for_level(st.session_state.grammar_level))
    metric_1, metric_2 = st.columns(2)
    metric_1.metric("Questions", len(st.session_state.quiz_indexes))
    metric_2.metric("Level bank", level_bank)
    st.caption(f"Current set #{st.session_state.quiz_number} for {st.session_state.grammar_level}.")

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
