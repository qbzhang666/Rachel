import csv
import html
import io
import json
import random
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = (
    BASE_DIR
    / "French"
    / "Delf Junion Scolaire A1"
    / "Delf Junior Scolaire_A1_Comprehension Orale"
)

EXAM_COMPONENTS = [
    {
        "Skill": "Compréhension de l'oral",
        "What happens": "4 listening exercises; very short everyday recordings",
        "Time": "About 20 minutes",
        "Points": 25,
    },
    {
        "Skill": "Compréhension des écrits",
        "What happens": "4 reading exercises with everyday documents",
        "Time": "30 minutes",
        "Points": 25,
    },
    {
        "Skill": "Production écrite",
        "What happens": "Complete a form and write a message of at least 40 words",
        "Time": "30 minutes",
        "Points": 25,
    },
    {
        "Skill": "Production orale",
        "What happens": "Interview, information exchange and simulated dialogue",
        "Time": "5-7 minutes; 10 minutes preparation",
        "Points": 25,
    },
]

PRACTICE_MODES = ["Smart mix", "Review my mistakes", "Fresh practice"]


def audio_path(track: int) -> Path:
    return AUDIO_DIR / f"DELF_A1_JS_PISTE{track:03d}.mp3"


LISTENING_TASKS = [
    {
        "id": "co-tennis",
        "title": "Rendez-vous au tennis",
        "track": 55,
        "skill": "Invitations and events",
        "context": "Vous écoutez un message de Max au sujet d'une sortie.",
        "summary": "Max confirms a Saturday tennis meeting and explains what each person should bring.",
        "questions": [
            {
                "prompt": "Quelle activité est proposée ?",
                "choices": ["Le tennis", "Le football", "La natation"],
                "answer": "Le tennis",
                "explanation": "The activity named in the message is tennis.",
            },
            {
                "prompt": "Quel jour a lieu l'activité ?",
                "choices": ["Vendredi", "Samedi", "Dimanche"],
                "answer": "Samedi",
                "explanation": "Listen for the day immediately before the time of day.",
            },
            {
                "prompt": "Qu'est-ce que la personne doit apporter ?",
                "choices": ["Du jus de fruits", "Des biscuits", "Un ballon"],
                "answer": "Du jus de fruits",
                "explanation": "Max assigns juice to the listener; the other food is already organised.",
            },
            {
                "prompt": "Où et à quelle heure est le rendez-vous ?",
                "choices": ["À 10 h au stade", "À 11 h au parc", "À 10 h à l'école"],
                "answer": "À 10 h au stade",
                "explanation": "The key practical details are the time and meeting place.",
            },
        ],
    },
    {
        "id": "co-fleurs",
        "title": "Aux belles fleurs",
        "track": 56,
        "skill": "Numbers and practical details",
        "context": "Vous entendez une publicité pour un magasin de fleurs.",
        "summary": "A flower shop announces a limited discount and gives colours, hours and location.",
        "questions": [
            {
                "prompt": "Quel produit est en promotion ?",
                "choices": ["Les roses", "Les chocolats", "Les vêtements"],
                "answer": "Les roses",
                "explanation": "Identify the product before listening for the numerical details.",
            },
            {
                "prompt": "Quelle est la réduction ?",
                "choices": ["20 %", "30 %", "40 %"],
                "answer": "30 %",
                "explanation": "The advertisement clearly states a thirty-percent reduction.",
            },
            {
                "prompt": "Quelles couleurs sont disponibles ?",
                "choices": ["Blanc et rouge", "Jaune et rose", "Bleu et blanc"],
                "answer": "Blanc et rouge",
                "explanation": "Both rose colours are named after the discount.",
            },
            {
                "prompt": "Quand peut-on profiter de la réduction ?",
                "choices": ["Cette semaine, de 14 h à 20 h", "Samedi, de 9 h à 12 h", "Tous les jours, de 8 h à 18 h"],
                "answer": "Cette semaine, de 14 h à 20 h",
                "explanation": "Listen for both the period and the opening hours.",
            },
        ],
    },
    {
        "id": "co-trains",
        "title": "Annonce à la gare",
        "track": 57,
        "skill": "Numbers and practical details",
        "context": "Vous entendez une annonce dans une gare.",
        "summary": "Cold weather delays trains; passengers are told where to get information and what is offered.",
        "questions": [
            {
                "prompt": "Pourquoi les trains sont-ils en retard ?",
                "choices": ["À cause du froid", "À cause de la pluie", "À cause d'une grève"],
                "answer": "À cause du froid",
                "explanation": "The reason is given at the beginning of the announcement.",
            },
            {
                "prompt": "Quelle est la durée possible du retard ?",
                "choices": ["De 5 à 15 minutes", "De 15 à 45 minutes", "De 45 à 60 minutes"],
                "answer": "De 15 à 45 minutes",
                "explanation": "Two numbers define the range of possible delay.",
            },
            {
                "prompt": "Où peut-on demander des informations ?",
                "choices": ["Au bureau Informations", "Au café", "Sur le quai 2"],
                "answer": "Au bureau Informations",
                "explanation": "The station directs passengers to its information office.",
            },
            {
                "prompt": "Qu'est-ce qui est offert ?",
                "choices": ["Du thé chaud", "Un billet gratuit", "Un sandwich"],
                "answer": "Du thé chaud",
                "explanation": "The final detail is a hot drink at the main entrance.",
            },
        ],
    },
    {
        "id": "co-parc",
        "title": "Sortie au parc",
        "track": 58,
        "skill": "Invitations and events",
        "context": "Un ami vous parle d'une sortie prévue pour demain.",
        "summary": "The speaker describes tomorrow's weather, suitable clothes, what to bring and departure time.",
        "questions": [
            {
                "prompt": "Quel temps va-t-il faire ?",
                "choices": ["Il va faire beau", "Il va pleuvoir", "Il va faire froid"],
                "answer": "Il va faire beau",
                "explanation": "The weather forecast explains the suggested clothes.",
            },
            {
                "prompt": "Quels vêtements sont conseillés ?",
                "choices": ["Un short et un tee-shirt", "Un manteau et des bottes", "Un pull et un pantalon"],
                "answer": "Un short et un tee-shirt",
                "explanation": "Warm-weather clothes are named directly.",
            },
            {
                "prompt": "Qu'est-ce que vous devez prendre ?",
                "choices": ["Le sac avec le gâteau", "Le ballon de football", "Une bouteille de lait"],
                "answer": "Le sac avec le gâteau",
                "explanation": "The speaker takes the ball and asks the listener to carry the cake bag.",
            },
            {
                "prompt": "À quelle heure est le départ ?",
                "choices": ["À 10 h 30", "À 11 h 30", "À 12 h 30"],
                "answer": "À 11 h 30",
                "explanation": "The departure time comes near the end of the message.",
            },
        ],
    },
    {
        "id": "co-famille",
        "title": "Chez une famille française",
        "track": 59,
        "skill": "Everyday instructions",
        "context": "Votre famille d'accueil vous explique l'organisation de la journée.",
        "summary": "A host family explains breakfast, transport, dinner and bedtime routines.",
        "questions": [
            {
                "prompt": "À quelle heure est le petit déjeuner ?",
                "choices": ["À 7 h", "À 7 h 30", "À 8 h"],
                "answer": "À 7 h",
                "explanation": "The morning routine begins with the breakfast time.",
            },
            {
                "prompt": "Comment allez-vous à l'école de langues ?",
                "choices": ["En bus", "À pied", "En train"],
                "answer": "En bus",
                "explanation": "The listener travels with the family's son by bus.",
            },
            {
                "prompt": "Combien coûte le ticket ?",
                "choices": ["1,20 €", "1,50 €", "2,10 €"],
                "answer": "1,20 €",
                "explanation": "Take care with the order of the euros and cents.",
            },
            {
                "prompt": "À quelle heure la famille dîne-t-elle ?",
                "choices": ["À 18 h 30", "À 19 h 30", "À 22 h"],
                "answer": "À 19 h 30",
                "explanation": "Dinner and bedtime are two different evening times.",
            },
        ],
    },
    {
        "id": "co-lunettes",
        "title": "Les lunettes perdues",
        "track": 62,
        "skill": "Everyday instructions",
        "context": "Vous écoutez un message téléphonique au sujet d'objets à la maison.",
        "summary": "Someone asks for help finding glasses, gives a return time and mentions shopping for dinner.",
        "questions": [
            {
                "prompt": "Quel objet cherche la personne ?",
                "choices": ["Ses lunettes", "Ses clés", "Son téléphone"],
                "answer": "Ses lunettes",
                "explanation": "The missing object is named in the first request.",
            },
            {
                "prompt": "Où faut-il regarder ?",
                "choices": ["À côté de la télévision", "Sous le lit", "Dans la cuisine"],
                "answer": "À côté de la télévision",
                "explanation": "The message suggests a possible location beside the television.",
            },
            {
                "prompt": "À quelle heure la personne rentre-t-elle ?",
                "choices": ["À 17 h", "À 18 h", "À 19 h"],
                "answer": "À 18 h",
                "explanation": "Listen for the return time after the request to look around the house.",
            },
            {
                "prompt": "Qu'est-ce que la personne va acheter ?",
                "choices": ["Une baguette", "Du poisson", "Des lunettes"],
                "answer": "Une baguette",
                "explanation": "The baguette is planned; the fish is only a question for the listener.",
            },
        ],
    },
    {
        "id": "co-examen",
        "title": "Le dernier examen",
        "track": 63,
        "skill": "Everyday instructions",
        "context": "Un parent donne des conseils avant l'école.",
        "summary": "A parent reminds a student about an exam, a book, travel time and an upcoming diploma.",
        "questions": [
            {
                "prompt": "Quel examen l'élève passe-t-il ?",
                "choices": ["Un examen d'histoire", "Un examen de français", "Un examen de sciences"],
                "answer": "Un examen d'histoire",
                "explanation": "The school subject is stated at the start.",
            },
            {
                "prompt": "Où est le livre ?",
                "choices": ["Sur la table de la cuisine", "Dans le sac", "À l'école"],
                "answer": "Sur la table de la cuisine",
                "explanation": "The location includes both the object and the room.",
            },
            {
                "prompt": "Combien de temps dure le trajet ?",
                "choices": ["20 minutes", "30 minutes", "40 minutes"],
                "answer": "30 minutes",
                "explanation": "The travel duration explains why the student can read on the bus.",
            },
            {
                "prompt": "Quand l'école donne-t-elle le diplôme ?",
                "choices": ["Vendredi", "Samedi", "Dimanche"],
                "answer": "Samedi",
                "explanation": "The diploma is given on the day after the final exam period.",
            },
        ],
    },
    {
        "id": "co-fete-immeuble",
        "title": "Une fête dans l'immeuble",
        "track": 76,
        "skill": "Invitations and events",
        "context": "Votre voisin Pierre vous laisse un message.",
        "summary": "Pierre invites neighbours to a welcome party and gives the date, apartment and reply method.",
        "questions": [
            {
                "prompt": "Dans quel appartement habite Pierre ?",
                "choices": ["B", "D", "T"],
                "answer": "D",
                "explanation": "Pierre identifies himself as the neighbour from apartment D.",
            },
            {
                "prompt": "Pourquoi organise-t-il une fête ?",
                "choices": ["Pour accueillir les nouveaux voisins", "Pour son anniversaire", "Pour la fin des cours"],
                "answer": "Pour accueillir les nouveaux voisins",
                "explanation": "The purpose is to welcome new people in the building.",
            },
            {
                "prompt": "Quand est la fête ?",
                "choices": ["Vendredi soir après les cours", "Vendredi matin", "Samedi toute la journée"],
                "answer": "Vendredi soir après les cours",
                "explanation": "The message combines the day with a part of the day.",
            },
            {
                "prompt": "Où faut-il laisser une réponse ?",
                "choices": ["Sur la porte de Pierre", "Sur Internet", "À l'école"],
                "answer": "Sur la porte de Pierre",
                "explanation": "Pierre asks the listener to leave a message on his door.",
            },
        ],
    },
    {
        "id": "co-aeroport",
        "title": "À l'aéroport de Paris",
        "track": 77,
        "skill": "Numbers and practical details",
        "context": "Vous entendez une annonce à l'aéroport.",
        "summary": "An airport announcement gives a flight number, baggage hall instructions, information point and transport options.",
        "questions": [
            {
                "prompt": "Quel est le numéro du vol ?",
                "choices": ["1649", "1689", "1840"],
                "answer": "1649",
                "explanation": "Write the four-digit number as soon as you hear it.",
            },
            {
                "prompt": "Dans quel hall faut-il aller ?",
                "choices": ["Le hall 4", "Le hall 6", "Le hall 9"],
                "answer": "Le hall 6",
                "explanation": "The hall number follows the instruction about baggage.",
            },
            {
                "prompt": "Quel document faut-il montrer ?",
                "choices": ["Le billet", "Le passeport", "La carte de bus"],
                "answer": "Le billet",
                "explanation": "Passengers are told to present their ticket in the hall.",
            },
            {
                "prompt": "Quels transports sont à la sortie ?",
                "choices": ["Des taxis et des autobus", "Des trains et des vélos", "Le métro seulement"],
                "answer": "Des taxis et des autobus",
                "explanation": "Two types of transport are named at the end.",
            },
        ],
    },
    {
        "id": "co-malade",
        "title": "Tu es malade",
        "track": 78,
        "skill": "Everyday instructions",
        "context": "La mère de votre famille d'accueil vous donne des instructions.",
        "summary": "A host parent gives instructions about rest, medicine, food and making contact later.",
        "questions": [
            {
                "prompt": "Où devez-vous rester ?",
                "choices": ["Dans votre lit", "Dans la cuisine", "Dans le jardin"],
                "answer": "Dans votre lit",
                "explanation": "The first instruction is to go to the bedroom and remain in bed.",
            },
            {
                "prompt": "Où sont les médicaments ?",
                "choices": ["Dans la salle de bains", "Dans la chambre", "Dans le sac"],
                "answer": "Dans la salle de bains",
                "explanation": "The medicine location follows the instruction for a headache.",
            },
            {
                "prompt": "Combien de médicaments faut-il prendre ?",
                "choices": ["Un", "Deux", "Trois"],
                "answer": "Trois",
                "explanation": "The quantity is stated directly after the location.",
            },
            {
                "prompt": "Que faut-il faire dans une heure ?",
                "choices": ["Appeler la mère", "Manger des frites", "Aller à l'école"],
                "answer": "Appeler la mère",
                "explanation": "The final instruction is to call after one hour.",
            },
        ],
    },
]


READING_TASKS = [
    {
        "id": "ce-voyage",
        "title": "Voyage scolaire à Lyon",
        "skill": "Dates and practical information",
        "document": (
            "VOYAGE SCOLAIRE À LYON\n"
            "Du lundi 14 au mercredi 16 octobre\n"
            "Départ devant le collège à 7 h 15. Retour à 18 h mercredi.\n"
            "Prix : 35 euros. Apportez un petit sac, une bouteille d'eau et un manteau.\n"
            "Donnez l'autorisation signée à Mme Robert avant le 30 septembre."
        ),
        "questions": [
            {"prompt": "Combien de jours dure le voyage ?", "choices": ["Deux jours", "Trois jours", "Quatre jours"], "answer": "Trois jours", "explanation": "Count Monday, Tuesday and Wednesday."},
            {"prompt": "À quelle heure est le départ ?", "choices": ["À 7 h 15", "À 18 h", "À 14 h"], "answer": "À 7 h 15", "explanation": "The early time is the departure; 18 h is the return."},
            {"prompt": "Qu'est-ce que les élèves doivent apporter ?", "choices": ["Une bouteille d'eau", "Un ordinateur", "Des bottes de ski"], "answer": "Une bouteille d'eau", "explanation": "Water is one of the three items on the packing list."},
            {"prompt": "Que faut-il donner à Mme Robert ?", "choices": ["L'autorisation signée", "35 bouteilles", "Un billet de train"], "answer": "L'autorisation signée", "explanation": "The final instruction concerns the signed permission form."},
        ],
    },
    {
        "id": "ce-sms",
        "title": "Un après-midi chez Chloé",
        "skill": "Invitations and directions",
        "document": (
            "Salut ! Tu veux venir chez moi samedi à 15 h ? On peut préparer des crêpes "
            "et regarder un film. Prends le bus 24 et descends à l'arrêt Mairie. Continue tout droit, "
            "puis tourne à gauche après la pharmacie. J'habite au 8, rue des Lilas. Réponds-moi avant vendredi ! Chloé"
        ),
        "questions": [
            {"prompt": "Quand Chloé invite-t-elle son ami ?", "choices": ["Samedi à 15 h", "Vendredi à 15 h", "Samedi à 14 h"], "answer": "Samedi à 15 h", "explanation": "The invitation time is in the first sentence."},
            {"prompt": "Quelles activités sont proposées ?", "choices": ["Faire des crêpes et regarder un film", "Jouer au tennis", "Visiter un musée"], "answer": "Faire des crêpes et regarder un film", "explanation": "Two activities follow the invitation."},
            {"prompt": "Quel bus faut-il prendre ?", "choices": ["Le bus 8", "Le bus 15", "Le bus 24"], "answer": "Le bus 24", "explanation": "The transport number comes before the stop name."},
            {"prompt": "Où faut-il tourner à gauche ?", "choices": ["Après la pharmacie", "Avant la mairie", "Devant le cinéma"], "answer": "Après la pharmacie", "explanation": "Follow the sequence: straight ahead, then left after the pharmacy."},
        ],
    },
    {
        "id": "ce-cantine",
        "title": "Menu de la cantine",
        "skill": "Schedules and menus",
        "document": (
            "CANTINE - JEUDI\n"
            "Entrée : salade de tomates\n"
            "Plat : poulet avec riz ou poisson avec légumes\n"
            "Dessert : yaourt ou fruit\n"
            "Service de 12 h à 13 h 20. Prix élève : 4,20 €.\n"
            "Attention : vendredi, la cantine est fermée."
        ),
        "questions": [
            {"prompt": "Quelle est l'entrée ?", "choices": ["Une salade de tomates", "Du poulet", "Un yaourt"], "answer": "Une salade de tomates", "explanation": "Read the category heading before choosing the food."},
            {"prompt": "Quel plat est servi avec des légumes ?", "choices": ["Le poisson", "Le poulet", "Le riz"], "answer": "Le poisson", "explanation": "The menu pairs fish with vegetables."},
            {"prompt": "Combien coûte le repas ?", "choices": ["4,02 €", "4,20 €", "5,20 €"], "answer": "4,20 €", "explanation": "Check the order of euros and cents."},
            {"prompt": "Quel jour la cantine est-elle fermée ?", "choices": ["Jeudi", "Vendredi", "Samedi"], "answer": "Vendredi", "explanation": "The closure is in the warning at the end."},
        ],
    },
    {
        "id": "ce-bibliotheque",
        "title": "Bibliothèque Victor-Hugo",
        "skill": "Rules and opening hours",
        "document": (
            "BIBLIOTHÈQUE VICTOR-HUGO\n"
            "Mardi-vendredi : 10 h-18 h\nSamedi : 9 h-16 h\nFermée dimanche et lundi\n"
            "Carte gratuite pour les moins de 18 ans. Trois livres maximum pendant 21 jours.\n"
            "Les boissons et les appels téléphoniques sont interdits."
        ),
        "questions": [
            {"prompt": "À quelle heure ouvre la bibliothèque samedi ?", "choices": ["À 9 h", "À 10 h", "À 16 h"], "answer": "À 9 h", "explanation": "Saturday has different hours from weekdays."},
            {"prompt": "Quand est-elle fermée ?", "choices": ["Dimanche et lundi", "Lundi et mardi", "Samedi et dimanche"], "answer": "Dimanche et lundi", "explanation": "Both closed days are listed together."},
            {"prompt": "Combien de livres peut-on emprunter ?", "choices": ["Deux", "Trois", "Vingt et un"], "answer": "Trois", "explanation": "Three is the quantity; 21 is the number of days."},
            {"prompt": "Qu'est-ce qui est interdit ?", "choices": ["Les boissons", "Les livres", "Les cartes gratuites"], "answer": "Les boissons", "explanation": "The rules prohibit drinks and phone calls."},
        ],
    },
    {
        "id": "ce-cinema",
        "title": "Programme du cinéma",
        "skill": "Schedules and menus",
        "document": (
            "CINÉMA LUMIÈRE - SAMEDI\n"
            "Le Secret du lac : 14 h 00 - aventure - 7 €\n"
            "Planète Rouge : 16 h 30 - science-fiction - 8 €\n"
            "Les Musiciens : 19 h 15 - comédie - 8 €\n"
            "Tarif jeune : 5 € avant 17 h. Réservation sur Internet ou à la caisse."
        ),
        "questions": [
            {"prompt": "Quel film commence à 16 h 30 ?", "choices": ["Le Secret du lac", "Planète Rouge", "Les Musiciens"], "answer": "Planète Rouge", "explanation": "Match the film title with its start time."},
            {"prompt": "Quel genre de film est Les Musiciens ?", "choices": ["Une comédie", "Un film d'aventure", "Un film de science-fiction"], "answer": "Une comédie", "explanation": "The genre appears after the start time."},
            {"prompt": "Combien paie un jeune pour la séance de 14 h ?", "choices": ["5 €", "7 €", "8 €"], "answer": "5 €", "explanation": "The youth price applies before 17 h."},
            {"prompt": "Où peut-on réserver ?", "choices": ["Sur Internet ou à la caisse", "À la bibliothèque", "Au collège"], "answer": "Sur Internet ou à la caisse", "explanation": "The final line gives two reservation methods."},
        ],
    },
    {
        "id": "ce-annonces",
        "title": "Petites annonces au collège",
        "skill": "Finding specific information",
        "document": (
            "1. Lina vend un dictionnaire français-anglais, 6 €. SMS : 06 22 14 80 31.\n"
            "2. Hugo cherche un livre de géographie pour lundi. Écrivez à hugo.ecole@mail.fr.\n"
            "3. Sara donne deux places pour le concert de vendredi. Appelez après 18 h.\n"
            "4. Mehdi vend un sac de sport bleu, 10 €. Disponible mercredi après-midi."
        ),
        "questions": [
            {"prompt": "Qui vend un dictionnaire ?", "choices": ["Lina", "Hugo", "Mehdi"], "answer": "Lina", "explanation": "Scan for the object, then read the name at the start of that notice."},
            {"prompt": "Comment contacter Hugo ?", "choices": ["Par courriel", "Par téléphone", "À la bibliothèque"], "answer": "Par courriel", "explanation": "Hugo's notice gives an email address."},
            {"prompt": "À partir de quelle heure peut-on appeler Sara ?", "choices": ["Après 16 h", "Après 18 h", "Après 20 h"], "answer": "Après 18 h", "explanation": "The contact time is at the end of Sara's notice."},
            {"prompt": "De quelle couleur est le sac ?", "choices": ["Rouge", "Bleu", "Noir"], "answer": "Bleu", "explanation": "The colour follows the item in Mehdi's notice."},
        ],
    },
    {
        "id": "ce-sport",
        "title": "Club Sports Jeunes",
        "skill": "Dates and practical information",
        "document": (
            "CLUB SPORTS JEUNES\n"
            "Natation : mardi 17 h\nBadminton : mercredi 16 h 30\nBasket : samedi 10 h\n"
            "Inscription : 12 € par mois. Première séance gratuite.\n"
            "Apportez une tenue de sport et une bouteille d'eau. Contact : Mme Lopez, bureau 12."
        ),
        "questions": [
            {"prompt": "Quel sport a lieu mercredi ?", "choices": ["La natation", "Le badminton", "Le basket"], "answer": "Le badminton", "explanation": "Match each activity to its day."},
            {"prompt": "À quelle heure commence le basket ?", "choices": ["À 10 h", "À 12 h", "À 16 h 30"], "answer": "À 10 h", "explanation": "Basket is the Saturday activity."},
            {"prompt": "Combien coûte la première séance ?", "choices": ["0 €", "10 €", "12 €"], "answer": "0 €", "explanation": "Gratuite means free."},
            {"prompt": "Que faut-il apporter ?", "choices": ["Une tenue de sport", "Un dictionnaire", "Un billet de train"], "answer": "Une tenue de sport", "explanation": "The equipment list follows the price information."},
        ],
    },
    {
        "id": "ce-carte",
        "title": "Carte postale de Nice",
        "skill": "Understanding a personal message",
        "document": (
            "Coucou Emma ! Je passe une semaine à Nice avec mes cousins. Il fait chaud et nous allons à la plage tous les matins. "
            "Hier, nous avons visité un musée. Demain, nous allons prendre le bateau. Je rentre dimanche soir. "
            "J'ai un petit cadeau pour toi ! Bisous, Nora"
        ),
        "questions": [
            {"prompt": "Avec qui Nora est-elle à Nice ?", "choices": ["Avec ses cousins", "Avec sa classe", "Avec Emma"], "answer": "Avec ses cousins", "explanation": "The companions are named in the first sentence."},
            {"prompt": "Que fait-elle tous les matins ?", "choices": ["Elle va à la plage", "Elle visite un musée", "Elle prend le bateau"], "answer": "Elle va à la plage", "explanation": "The phrase tous les matins marks a regular activity."},
            {"prompt": "Qu'est-ce qui est prévu demain ?", "choices": ["Une sortie en bateau", "Le retour", "Une visite au musée"], "answer": "Une sortie en bateau", "explanation": "Separate yesterday's museum visit from tomorrow's boat trip."},
            {"prompt": "Quand Nora rentre-t-elle ?", "choices": ["Samedi matin", "Dimanche soir", "Lundi"], "answer": "Dimanche soir", "explanation": "The return day and part of day are both stated."},
        ],
    },
    {
        "id": "ce-ecole",
        "title": "Journée portes ouvertes",
        "skill": "Finding specific information",
        "document": (
            "PORTES OUVERTES - COLLÈGE JEAN-MOULIN\nSamedi 6 avril, de 9 h à 13 h\n"
            "Sciences : salle 105 - Langues : salle 210 - Sport : gymnase\n"
            "Visite de la bibliothèque toutes les 30 minutes.\n"
            "Pour parler avec des élèves, inscrivez-vous d'abord à l'accueil. Café gratuit pour les familles."
        ),
        "questions": [
            {"prompt": "Quel jour a lieu la visite ?", "choices": ["Samedi 6 avril", "Dimanche 6 avril", "Samedi 13 avril"], "answer": "Samedi 6 avril", "explanation": "The date is directly under the heading."},
            {"prompt": "Où faut-il aller pour les langues ?", "choices": ["Salle 105", "Salle 210", "Au gymnase"], "answer": "Salle 210", "explanation": "Each subject is paired with a place."},
            {"prompt": "Quand commencent les visites de la bibliothèque ?", "choices": ["Toutes les 30 minutes", "À 13 h seulement", "Toutes les deux heures"], "answer": "Toutes les 30 minutes", "explanation": "This is a frequency, not a single start time."},
            {"prompt": "Que faut-il faire avant de parler avec des élèves ?", "choices": ["S'inscrire à l'accueil", "Payer le café", "Aller au gymnase"], "answer": "S'inscrire à l'accueil", "explanation": "The instruction uses d'abord to mark the first step."},
        ],
    },
    {
        "id": "ce-anniversaire",
        "title": "Invitation d'anniversaire",
        "skill": "Understanding a personal message",
        "document": (
            "INVITATION\nJe fête mes 14 ans dimanche 12 mai, de 14 h à 18 h, dans le jardin de mes grands-parents. "
            "Nous allons jouer au volley et faire un grand goûter. Apporte une casquette s'il fait beau. "
            "Mes grands-parents habitent 5, avenue des Roses, en face du parc. Confirme avant mercredi. - Lucas"
        ),
        "questions": [
            {"prompt": "Quel âge va avoir Lucas ?", "choices": ["12 ans", "14 ans", "18 ans"], "answer": "14 ans", "explanation": "The age comes immediately after the purpose of the invitation."},
            {"prompt": "Où est la fête ?", "choices": ["Dans le jardin de ses grands-parents", "Au collège", "Dans un parc"], "answer": "Dans le jardin de ses grands-parents", "explanation": "The park is only opposite the address; it is not the party location."},
            {"prompt": "Quelle activité sportive est prévue ?", "choices": ["Le volley", "Le tennis", "La natation"], "answer": "Le volley", "explanation": "The planned sport appears before the snack."},
            {"prompt": "Quand faut-il répondre ?", "choices": ["Avant mercredi", "Le 12 mai", "Après dimanche"], "answer": "Avant mercredi", "explanation": "The confirmation deadline is the final instruction."},
        ],
    },
]


LANGUAGE_QUESTION_DATA = [
    ("lg01", "Se présenter", "Complétez : Je ___ quatorze ans.", ["suis", "ai", "vais"], "ai", "Age is expressed with avoir: j'ai quatorze ans."),
    ("lg02", "Se présenter", "Quelle phrase est correcte ?", ["Je m'appelle Lina.", "Je appelle Lina.", "Je suis appelle Lina."], "Je m'appelle Lina.", "Use the reflexive form je m'appelle to give your name."),
    ("lg03", "Se présenter", "Complétez : Maria est ___ . Elle habite en Italie.", ["italien", "italienne", "Italie"], "italienne", "The nationality adjective agrees with Maria: italienne."),
    ("lg04", "Se présenter", "Quelle question demande l'adresse ?", ["Où habitez-vous ?", "Quel âge avez-vous ?", "Comment vous appelez-vous ?"], "Où habitez-vous ?", "Où asks about a place."),
    ("lg05", "Être et avoir", "Complétez : Nous ___ au collège.", ["sommes", "avons", "êtes"], "sommes", "The nous form of être is sommes."),
    ("lg06", "Être et avoir", "Complétez : Ils ___ deux frères.", ["sont", "ont", "avez"], "ont", "The ils form of avoir is ont."),
    ("lg07", "Être et avoir", "Complétez : Tu ___ très sympathique.", ["es", "as", "est"], "es", "The tu form of être is es."),
    ("lg08", "Être et avoir", "Complétez : Vous ___ une carte de bus ?", ["êtes", "avez", "ont"], "avez", "The vous form of avoir is avez."),
    ("lg09", "Aller et faire", "Complétez : Je ___ à la bibliothèque.", ["vais", "va", "allez"], "vais", "The je form of aller is vais."),
    ("lg10", "Aller et faire", "Complétez : Nous ___ du sport le samedi.", ["fait", "faisons", "font"], "faisons", "The nous form of faire is faisons."),
    ("lg11", "Aller et faire", "Complétez : Mes amis ___ du tennis.", ["faites", "fais", "font"], "font", "The ils/elles form of faire is font."),
    ("lg12", "Aller et faire", "Complétez : Vous ___ au cinéma ce soir ?", ["allez", "allons", "vas"], "allez", "The vous form of aller is allez."),
    ("lg13", "Articles et nourriture", "Complétez : Je mange ___ pomme.", ["un", "une", "du"], "une", "Pomme is feminine singular, so use une."),
    ("lg14", "Articles et nourriture", "Complétez : Nous achetons ___ pain.", ["du", "de la", "des"], "du", "Use du with the masculine mass noun pain."),
    ("lg15", "Articles et nourriture", "Complétez : Elle boit ___ eau.", ["du", "de la", "de l'"], "de l'", "Use de l' before a vowel sound."),
    ("lg16", "Articles et nourriture", "Complétez : Il prend ___ frites.", ["du", "de la", "des"], "des", "Frites is plural, so use des."),
    ("lg17", "Accord des adjectifs", "Complétez : Ma sœur est très ___ .", ["sportif", "sportive", "sportifs"], "sportive", "The adjective agrees with the feminine noun sœur."),
    ("lg18", "Accord des adjectifs", "Complétez : Ce sont des garçons ___ .", ["français", "française", "françaises"], "français", "The masculine plural form is français."),
    ("lg19", "Accord des adjectifs", "Complétez : J'aime cette robe ___ .", ["bleu", "bleue", "bleus"], "bleue", "Robe is feminine singular, so bleu becomes bleue."),
    ("lg20", "Accord des adjectifs", "Complétez : Il a les cheveux ___ .", ["brun", "brune", "bruns"], "bruns", "Cheveux is masculine plural, so add s."),
    ("lg21", "La négation", "Choisissez la phrase correcte.", ["Je ne mange pas de viande.", "Je mange ne pas de viande.", "Je ne pas mange de viande."], "Je ne mange pas de viande.", "Ne and pas surround the conjugated verb."),
    ("lg22", "La négation", "Complétez : Elle ___ va ___ au cinéma.", ["ne / jamais", "jamais / ne", "pas / ne"], "ne / jamais", "Ne... jamais means never."),
    ("lg23", "La négation", "Transformez : J'ai un vélo.", ["Je n'ai pas de vélo.", "Je ne ai pas un vélo.", "Je n'ai de pas vélo."], "Je n'ai pas de vélo.", "After negation, un becomes de; ne contracts before a vowel."),
    ("lg24", "La négation", "Complétez : Nous ___ sommes ___ en retard.", ["ne / pas", "pas / ne", "n' / jamais pas"], "ne / pas", "Place ne before sommes and pas after it."),
    ("lg25", "Poser des questions", "___ vous appelez-vous ?", ["Comment", "Combien", "Quand"], "Comment", "Comment asks for a name or manner."),
    ("lg26", "Poser des questions", "___ est la gare ?", ["Qui", "Où", "Pourquoi"], "Où", "Où asks for a location."),
    ("lg27", "Poser des questions", "___ coûte ce sandwich ?", ["Combien", "Quel", "Comment"], "Combien", "Combien asks about price or quantity."),
    ("lg28", "Poser des questions", "___ est votre sport préféré ?", ["Quelle", "Quel", "Quels"], "Quel", "Sport is masculine singular, so use quel."),
    ("lg29", "Se repérer", "La pharmacie est ___ la boulangerie.", ["à côté de", "demain", "souvent"], "à côté de", "À côté de expresses a nearby location."),
    ("lg30", "Se repérer", "Pour continuer sans tourner, allez ___ .", ["tout droit", "à gauche", "derrière"], "tout droit", "Tout droit means straight ahead."),
    ("lg31", "Se repérer", "Tournez ___ après la banque.", ["à gauche", "le lundi", "en bus"], "à gauche", "À gauche gives a direction."),
    ("lg32", "Se repérer", "Je vais ___ mon ami après l'école.", ["chez", "au", "à la"], "chez", "Chez is used for going to a person's home."),
    ("lg33", "Dates et heures", "Quel jour vient après mercredi ?", ["Mardi", "Jeudi", "Vendredi"], "Jeudi", "The sequence is mercredi, jeudi, vendredi."),
    ("lg34", "Dates et heures", "14 h 30, c'est...", ["deux heures et demie de l'après-midi", "quatre heures trente du matin", "midi et demi"], "deux heures et demie de l'après-midi", "14:30 is 2:30 pm."),
    ("lg35", "Dates et heures", "Quel mois vient avant septembre ?", ["Juillet", "Août", "Octobre"], "Août", "August comes immediately before September."),
    ("lg36", "Dates et heures", "Complétez : Mon anniversaire est ___ 5 juin.", ["le", "à", "en"], "le", "Use le before a specific date."),
    ("lg37", "Futur proche", "Complétez : Demain, je ___ visiter Paris.", ["vais", "suis", "ai"], "vais", "The near future uses aller + infinitive."),
    ("lg38", "Futur proche", "Complétez : Nous allons ___ du vélo.", ["faisons", "faire", "fait"], "faire", "After allons, use the infinitive faire."),
    ("lg39", "Futur proche", "Quelle phrase parle du futur ?", ["Elle va partir samedi.", "Elle part tous les samedis.", "Elle est partie samedi."], "Elle va partir samedi.", "Va + infinitive indicates a planned future action."),
    ("lg40", "Futur proche", "Complétez : Ils ___ regarder un film.", ["vont", "font", "ont"], "vont", "The ils form of aller is vont."),
    ("lg41", "Politesse", "Au café, quelle demande est polie ?", ["Je voudrais un jus d'orange, s'il vous plaît.", "Donne un jus !", "Je veux ça."], "Je voudrais un jus d'orange, s'il vous plaît.", "Je voudrais and s'il vous plaît make a polite request."),
    ("lg42", "Politesse", "Comment demander le prix ?", ["Combien ça coûte ?", "Où ça mange ?", "Quand ça parle ?"], "Combien ça coûte ?", "This is the standard A1 price question."),
    ("lg43", "Politesse", "Le vendeur vous donne votre achat. Vous dites...", ["Merci beaucoup.", "Je m'appelle Zoé.", "Il est huit heures."], "Merci beaucoup.", "Thank the seller after receiving the item."),
    ("lg44", "Politesse", "Pour terminer un dialogue, vous dites...", ["Au revoir, bonne journée.", "Quel âge avez-vous ?", "Je n'ai pas de frère."], "Au revoir, bonne journée.", "A closing formula ends the interaction politely."),
    ("lg45", "Vocabulaire quotidien", "Où prend-on le train ?", ["À la gare", "À la piscine", "À la boulangerie"], "À la gare", "A train leaves from a station: la gare."),
    ("lg46", "Vocabulaire quotidien", "Quel objet utilise-t-on pour téléphoner ?", ["Un téléphone portable", "Une fourchette", "Un manteau"], "Un téléphone portable", "A mobile phone is used for calls."),
    ("lg47", "Vocabulaire quotidien", "Qui est le frère de votre mère ?", ["Votre oncle", "Votre cousin", "Votre grand-père"], "Votre oncle", "A parent's brother is an uncle."),
    ("lg48", "Vocabulaire quotidien", "Quelle matière étudie les nombres et les calculs ?", ["Les mathématiques", "L'histoire", "La musique"], "Les mathématiques", "Numbers and calculations belong to mathematics."),
]

LANGUAGE_QUESTIONS = [
    {
        "id": item[0],
        "topic": item[1],
        "prompt": item[2],
        "choices": item[3],
        "answer": item[4],
        "explanation": item[5],
    }
    for item in LANGUAGE_QUESTION_DATA
]

WRITING_PROMPTS = [
    {
        "id": "pe-anniversaire",
        "title": "Inviter à un anniversaire",
        "instruction": "Vous organisez votre anniversaire. Écrivez à un ami : invitez-le, donnez la date, l'heure et le lieu, présentez deux activités et demandez une réponse.",
        "required": [["anniversaire", "fête"], ["samedi", "dimanche", "date", "heure", " h"], ["chez", "maison", "adresse", "parc"], ["répond", "réponse", "disponible", "venir"]],
        "useful": ["Je t'invite", "On se retrouve", "Nous allons", "Est-ce que tu peux répondre ?"],
        "model": "Salut Inès ! Je t'invite à ma fête d'anniversaire samedi à 15 h chez moi. Nous allons écouter de la musique, jouer au volley et manger un grand gâteau. Est-ce que tu es disponible ? Réponds-moi avant jeudi, s'il te plaît. À bientôt !",
    },
    {
        "id": "pe-vacances",
        "title": "Donner des nouvelles de vacances",
        "instruction": "Vous êtes en vacances. Écrivez une carte à un ami : dites où vous êtes, avec qui, quel temps il fait, deux activités et votre date de retour.",
        "required": [["vacances", "suis à", "suis en"], ["avec"], ["temps", "chaud", "beau", "froid", "pluie"], ["rentre", "retour"]],
        "useful": ["Je suis en vacances à", "Il fait", "Hier, j'ai", "Je rentre"],
        "model": "Coucou Tom ! Je suis en vacances à Marseille avec mes cousins. Il fait beau et très chaud. Le matin, nous allons à la plage et l'après-midi, nous visitons la ville. Hier, j'ai pris le bateau. Je rentre dimanche soir. À bientôt !",
    },
    {
        "id": "pe-cinema",
        "title": "Proposer une sortie au cinéma",
        "instruction": "Vous proposez une sortie au cinéma à un ami. Donnez le film, le jour, l'heure et le lieu du rendez-vous. Demandez à votre ami de confirmer.",
        "required": [["cinéma", "film"], ["samedi", "dimanche", "vendredi", " h"], ["rendez-vous", "devant", "à côté", "retrouve"], ["confirm", "répond", "disponible"]],
        "useful": ["Tu veux venir", "Le film commence", "Rendez-vous devant", "Tu peux confirmer ?"],
        "model": "Salut Louis ! Tu veux venir au cinéma avec moi vendredi ? Le film Planète Rouge commence à 18 h. On se retrouve devant le cinéma à 17 h 45. Après, nous pouvons manger une glace. Tu es disponible ? Merci de me répondre ce soir. À plus !",
    },
    {
        "id": "pe-sport",
        "title": "S'inscrire à une activité sportive",
        "instruction": "Vous écrivez à un club de sport. Présentez-vous, dites quel sport vous voulez faire, vos jours disponibles et posez deux questions pratiques.",
        "required": [["m'appelle", "ans"], ["sport", "natation", "tennis", "basket", "judo"], ["disponible", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"], ["combien", "heure", "coûte", "prix"]],
        "useful": ["Je voudrais m'inscrire", "Je suis disponible", "À quelle heure", "Combien coûte"],
        "model": "Bonjour, je m'appelle Rachel et j'ai 14 ans. Je voudrais m'inscrire au cours de badminton. Je suis disponible le mercredi et le samedi. À quelle heure commence le cours ? Combien coûte l'inscription par mois ? Merci beaucoup pour votre réponse. Au revoir.",
    },
    {
        "id": "pe-ecole",
        "title": "Présenter sa nouvelle école",
        "instruction": "Vous écrivez à un ami francophone. Présentez votre nouvelle école, vos matières préférées, votre emploi du temps et une activité après les cours.",
        "required": [["école", "collège", "classe"], ["matière", "français", "math", "sport", "histoire", "sciences"], ["cours", "matin", "après-midi", " h"], ["après", "club", "activité"]],
        "useful": ["Ma nouvelle école", "Ma matière préférée", "Les cours commencent", "Après les cours"],
        "model": "Salut Mia ! Ma nouvelle école est grande et moderne. Ma matière préférée est le français, mais j'aime aussi les sciences. Les cours commencent à 8 h 30 et finissent à 15 h 30. Après les cours, je fais du basket avec mes amis. Et ton école ? Bisous !",
    },
    {
        "id": "pe-musique",
        "title": "Inviter à la fête de la musique",
        "instruction": "Vous invitez un ami à la fête de la musique. Donnez le jour, l'heure et le lieu du rendez-vous, puis expliquez les activités prévues.",
        "required": [["musique", "concert"], ["samedi", "dimanche", "vendredi", " h"], ["rendez-vous", "retrouve", "devant"], ["écouter", "danser", "chanter", "manger"]],
        "useful": ["Tu veux venir", "On se retrouve", "Nous allons écouter", "Réponds-moi"],
        "model": "Coucou Ana ! Tu veux venir à la fête de la musique samedi ? On se retrouve à 17 h devant la mairie. Nous allons écouter deux concerts, chanter et manger des crêpes. Le dernier concert finit à 21 h. Tu peux venir ? Réponds-moi demain. Bises !",
    },
    {
        "id": "pe-remerciement",
        "title": "Remercier une famille d'accueil",
        "instruction": "Votre séjour en France est terminé. Remerciez votre famille d'accueil, mentionnez deux bons souvenirs et donnez de vos nouvelles.",
        "required": [["merci", "remerc"], ["souvenir", "aimé", "adoré"], ["visite", "repas", "sortie", "famille", "école"], ["maintenant", "rentré", "chez moi", "nouvelles"]],
        "useful": ["Merci pour", "J'ai beaucoup aimé", "Mon meilleur souvenir", "À bientôt"],
        "model": "Bonjour Madame Martin, merci beaucoup pour mon séjour chez vous. J'ai adoré nos repas en famille et la visite du château. Mon meilleur souvenir est notre sortie à vélo. Maintenant, je suis rentré chez moi et je montre mes photos à mes parents. À bientôt !",
    },
    {
        "id": "pe-weekend",
        "title": "Raconter son week-end",
        "instruction": "Écrivez à un ami pour raconter votre week-end : dites où vous êtes allé, avec qui, deux activités et votre opinion.",
        "required": [["week-end", "samedi", "dimanche"], ["avec"], ["visité", "joué", "regardé", "fait", "mangé"], ["super", "génial", "aimé", "content"]],
        "useful": ["Samedi, je suis allé", "avec", "Ensuite", "C'était"],
        "model": "Salut Hugo ! Ce week-end, je suis allé à la campagne avec ma famille. Samedi, nous avons fait une promenade et pris beaucoup de photos. Dimanche, j'ai joué au football avec mes cousins. Nous avons aussi mangé un grand gâteau. C'était vraiment super ! À lundi.",
    },
    {
        "id": "pe-devoirs",
        "title": "Demander les devoirs",
        "instruction": "Vous êtes malade et absent de l'école. Écrivez à un camarade : expliquez la situation, demandez les devoirs et proposez une façon de les recevoir.",
        "required": [["malade", "absent", "école"], ["devoir", "exercice", "leçon"], ["envoie", "photo", "mail", "message"], ["merci", "répond"]],
        "useful": ["Je suis malade", "Quels sont les devoirs ?", "Tu peux m'envoyer", "Merci pour ton aide"],
        "model": "Salut Adam, je suis malade et je ne vais pas à l'école aujourd'hui. Quels sont les devoirs de français et de mathématiques ? Tu peux prendre une photo du tableau et me l'envoyer par message, s'il te plaît ? Merci beaucoup pour ton aide. À demain, j'espère !",
    },
    {
        "id": "pe-cadeau",
        "title": "Choisir un cadeau",
        "instruction": "Vous demandez conseil à un ami pour acheter un cadeau. Présentez la personne, ses goûts, votre budget et demandez une idée.",
        "required": [["cadeau", "anniversaire"], ["aime", "adore", "préfère"], ["euro", "budget", "coûte"], ["idée", "conseil", "propose"]],
        "useful": ["Je cherche un cadeau", "Elle aime", "J'ai un budget de", "Tu as une idée ?"],
        "model": "Coucou Léa ! Je cherche un cadeau pour l'anniversaire de ma sœur. Elle a 16 ans et elle adore la musique et les romans. J'ai un budget de 20 euros. Je pense à un livre ou à des écouteurs. Tu as une autre idée ? Réponds-moi vite !",
    },
]

INTERVIEW_QUESTIONS = [
    "Comment vous appelez-vous ?",
    "Quel âge avez-vous ?",
    "Quelle est votre nationalité ?",
    "Où habitez-vous ?",
    "Pouvez-vous épeler votre nom ?",
    "Parlez-moi de votre famille.",
    "Avez-vous des frères et sœurs ?",
    "Quel est votre sport préféré ?",
    "Qu'est-ce que vous faites après l'école ?",
    "Quelle est votre matière préférée ? Pourquoi ?",
    "Qu'est-ce que vous aimez manger ?",
    "Que faites-vous le week-end ?",
    "Aimez-vous la musique ?",
    "Comment allez-vous à l'école ?",
    "À quelle heure commencent vos cours ?",
    "Parlez-moi de votre meilleur ami ou de votre meilleure amie.",
    "Quel temps préférez-vous ?",
    "Qu'est-ce que vous allez faire pendant les prochaines vacances ?",
]

INFORMATION_CARDS = [
    ("Dimanche", "Qu'est-ce que vous faites le dimanche ?"),
    ("Famille", "Combien de personnes y a-t-il dans votre famille ?"),
    ("Sport", "Quel sport est-ce que vous faites ?"),
    ("Film", "Quel est votre film préféré ?"),
    ("École", "Où est votre école ?"),
    ("Musique", "Quel genre de musique aimez-vous ?"),
    ("Anniversaire", "Quelle est la date de votre anniversaire ?"),
    ("Vacances", "Où allez-vous pendant les vacances ?"),
    ("Internet", "Qu'est-ce que vous faites sur Internet ?"),
    ("Transport", "Comment venez-vous à l'école ?"),
    ("Livre", "Quel livre est-ce que vous aimez ?"),
    ("Cuisine", "Qu'est-ce que vous aimez cuisiner ?"),
    ("Ville", "Dans quelle ville habitez-vous ?"),
    ("Téléphone", "Combien de temps utilisez-vous votre téléphone ?"),
    ("Saison", "Quelle est votre saison préférée ?"),
    ("Animal", "Est-ce que vous avez un animal ?"),
    ("Français", "Pourquoi apprenez-vous le français ?"),
    ("Matin", "À quelle heure vous levez-vous le matin ?"),
    ("Restaurant", "Quel est votre restaurant préféré ?"),
    ("Vêtement", "Quel vêtement portez-vous souvent ?"),
    ("Ami", "Comment s'appelle votre meilleur ami ?"),
    ("Chambre", "Comment est votre chambre ?"),
    ("Boisson", "Quelle boisson préférez-vous ?"),
    ("Week-end", "Qu'est-ce que vous allez faire ce week-end ?"),
]

ROLEPLAY_SCENARIOS = [
    {
        "id": "cafe",
        "title": "Dans une cafétéria",
        "brief": "Commandez un plat, une boisson et un dessert. Demandez les prix et payez.",
        "role": "serveur",
        "items": {"sandwich": 4.5, "poulet": 6.0, "salade": 5.0, "jus": 2.0, "eau": 1.5, "gâteau": 2.5},
    },
    {
        "id": "boulangerie",
        "title": "À la boulangerie",
        "brief": "Achetez du pain et des pâtisseries. Demandez les quantités, les prix et payez.",
        "role": "boulangère",
        "items": {"baguette": 1.2, "croissant": 1.3, "pain au chocolat": 1.5, "tarte": 3.0, "sandwich": 4.0},
    },
    {
        "id": "librairie",
        "title": "Dans une librairie",
        "brief": "Cherchez un cadeau pour un ami. Demandez des informations, choisissez et payez.",
        "role": "libraire",
        "items": {"roman": 9.0, "manga": 7.5, "dictionnaire": 12.0, "carnet": 4.0, "stylo": 2.0},
    },
    {
        "id": "sport",
        "title": "Dans un club de sport",
        "brief": "Demandez des informations sur deux activités, les horaires et le prix, puis inscrivez-vous.",
        "role": "employé du club",
        "items": {"natation": 15.0, "tennis": 18.0, "badminton": 12.0, "basket": 10.0, "judo": 14.0},
    },
    {
        "id": "marche",
        "title": "Au marché",
        "brief": "Achetez des fruits et des légumes. Demandez les prix et les quantités, puis payez.",
        "role": "vendeuse",
        "items": {"pommes": 2.5, "bananes": 2.0, "oranges": 3.0, "tomates": 2.8, "carottes": 2.2},
    },
    {
        "id": "gare",
        "title": "À la gare",
        "brief": "Achetez un billet. Demandez l'heure, le quai, le prix et choisissez un aller simple ou un aller-retour.",
        "role": "agent",
        "items": {"billet pour Lyon": 18.0, "billet pour Lille": 16.0, "billet pour Nantes": 22.0, "aller-retour": 30.0},
    },
]

CURATED_WORD_BANK = {
    "Se présenter": ["Je m'appelle...", "J'ai ... ans.", "J'habite à...", "Je suis australien(ne)."],
    "Inviter": ["Tu veux venir ?", "Je t'invite...", "On se retrouve à...", "Réponds-moi, s'il te plaît."],
    "Se repérer": ["tout droit", "à gauche", "à droite", "en face de", "à côté de", "au bout de la rue"],
    "Acheter": ["Je voudrais...", "Combien ça coûte ?", "C'est combien au total ?", "Voilà l'argent."],
    "Donner son avis": ["J'aime...", "Je préfère...", "C'est super.", "Je n'aime pas...", "À mon avis..."],
    "Temps": ["aujourd'hui", "demain", "hier", "le matin", "l'après-midi", "le soir", "la semaine prochaine"],
}


def get_by_id(items: list[dict], item_id: str) -> dict:
    return next(item for item in items if item["id"] == item_id)


def rows_to_csv(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def initialise_state() -> None:
    defaults = {
        "delf_progress": {
            "xp": 0,
            "attempts": 0,
            "questions": 0,
            "correct": 0,
            "best": {},
            "review": {},
            "history": [],
        },
        "delf_listening_id": random.choice(LISTENING_TASKS)["id"],
        "delf_listening_round": 1,
        "delf_listening_submitted": False,
        "delf_listening_pending": False,
        "delf_listening_results": [],
        "delf_reading_id": random.choice(READING_TASKS)["id"],
        "delf_reading_round": 1,
        "delf_reading_submitted": False,
        "delf_reading_pending": False,
        "delf_reading_results": [],
        "delf_language_round": 1,
        "delf_language_ids": [],
        "delf_language_orders": {},
        "delf_language_submitted": False,
        "delf_language_pending": False,
        "delf_language_results": [],
        "delf_writing_result": None,
        "delf_writing_round": 1,
        "delf_writing_prompt_id": random.choice(WRITING_PROMPTS)["id"],
        "delf_interview_round": 1,
        "delf_interview_questions": random.sample(INTERVIEW_QUESTIONS, 6),
        "delf_interview_submitted": False,
        "delf_interview_result": None,
        "delf_cards_round": 1,
        "delf_cards": random.sample(INFORMATION_CARDS, 6),
        "delf_cards_results": None,
        "delf_roleplay_id": ROLEPLAY_SCENARIOS[0]["id"],
        "delf_roleplay_round": 1,
        "delf_roleplay_messages": [
            {
                "role": "Examinateur",
                "content": "Bonjour ! Je vous écoute. Que puis-je faire pour vous ?",
            }
        ],
        "delf_roleplay_cart": {},
        "delf_roleplay_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def rank_name(xp: int) -> str:
    if xp >= 900:
        return "Candidat prêt"
    if xp >= 450:
        return "Communicant"
    if xp >= 180:
        return "Explorateur"
    return "Débutant courageux"


def record_attempt(
    section: str,
    label: str,
    score: int,
    total: int,
    wrong_skills: list[str],
    correct_skills: list[str],
) -> None:
    progress = st.session_state.delf_progress
    percentage = round((score / total) * 100) if total else 0
    progress["attempts"] += 1
    progress["questions"] += total
    progress["correct"] += score
    progress["xp"] += 15 + score * 5
    progress["best"][section] = max(percentage, progress["best"].get(section, 0))

    for skill in wrong_skills:
        key = f"{section}|{skill}"
        progress["review"][key] = min(8, progress["review"].get(key, 0) + 2)
    for skill in correct_skills:
        key = f"{section}|{skill}"
        if key in progress["review"]:
            progress["review"][key] = max(0, progress["review"][key] - 1)

    progress["history"].append(
        {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Section": section,
            "Activity": label,
            "Score": score,
            "Total": total,
            "Percent": percentage,
        }
    )


def choose_task(
    tasks: list[dict],
    section: str,
    mode: str,
    skill_filter: str,
    current_id: str | None,
) -> dict:
    candidates = [
        task for task in tasks if skill_filter == "All skills" or task["skill"] == skill_filter
    ]
    alternatives = [task for task in candidates if task["id"] != current_id]
    if alternatives:
        candidates = alternatives

    review = st.session_state.delf_progress["review"]
    if mode == "Review my mistakes":
        review_candidates = [
            task for task in candidates if review.get(f"{section}|{task['skill']}", 0) > 0
        ]
        if review_candidates:
            candidates = review_candidates

    if mode in {"Smart mix", "Review my mistakes"}:
        weights = [1 + review.get(f"{section}|{task['skill']}", 0) * 3 for task in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]
    return random.choice(candidates)


def new_objective_task(section: str) -> None:
    if section == "Listening":
        task = choose_task(
            LISTENING_TASKS,
            section,
            st.session_state.get("delf_listening_mode", PRACTICE_MODES[0]),
            st.session_state.get("delf_listening_skill", "All skills"),
            st.session_state.delf_listening_id,
        )
        prefix = "delf_listening"
    else:
        task = choose_task(
            READING_TASKS,
            section,
            st.session_state.get("delf_reading_mode", PRACTICE_MODES[0]),
            st.session_state.get("delf_reading_skill", "All skills"),
            st.session_state.delf_reading_id,
        )
        prefix = "delf_reading"
    st.session_state[f"{prefix}_id"] = task["id"]
    st.session_state[f"{prefix}_round"] += 1
    st.session_state[f"{prefix}_submitted"] = False
    st.session_state[f"{prefix}_pending"] = False
    st.session_state[f"{prefix}_results"] = []


def submit_objective_task(section: str, task: dict) -> None:
    prefix = "delf_listening" if section == "Listening" else "delf_reading"
    round_no = st.session_state[f"{prefix}_round"]
    results = []
    wrong_skills = []
    correct_skills = []
    for index, question in enumerate(task["questions"]):
        selected = st.session_state.get(f"{prefix}_{round_no}_{index}")
        correct = selected == question["answer"]
        results.append(
            {
                "Question": index + 1,
                "Your answer": selected,
                "Correct answer": question["answer"],
                "Result": "Correct" if correct else "Review",
                "Why": question["explanation"],
            }
        )
        (correct_skills if correct else wrong_skills).append(task["skill"])
    score = sum(row["Result"] == "Correct" for row in results)
    st.session_state[f"{prefix}_results"] = results
    st.session_state[f"{prefix}_submitted"] = True
    st.session_state[f"{prefix}_pending"] = False
    record_attempt(section, task["title"], score, len(results), wrong_skills, correct_skills)


def tokenise_french(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?", text.lower())


def normalise_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower().replace("’", "'"))
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def count_required_groups(text: str, groups: list[list[str]]) -> tuple[int, list[str]]:
    lowered = normalise_text(text)
    missing = []
    hits = 0
    for group in groups:
        if any(normalise_text(word) in lowered for word in group):
            hits += 1
        else:
            missing.append(" / ".join(group[:3]))
    return hits, missing


def common_language_errors(text: str) -> list[str]:
    checks = [
        (r"\bje suis\s+\d+\s+ans\b", "Use avoir for age: j'ai ... ans."),
        (r"\bje ai\b", "Contract je + ai: write j'ai."),
        (r"\btu est\b", "With tu, use tu es."),
        (r"\bnous va\b", "With nous, use nous allons."),
        (r"\bils va\b", "With ils, use ils vont."),
        (r"\bje aller\b", "Conjugate aller: je vais."),
        (r"\bje ne [a-zà-ÿ']+\b(?!\s+(?:pas|jamais|plus))", "Check that a negative sentence includes pas, jamais or plus."),
    ]
    return [message for pattern, message in checks if re.search(pattern, normalise_text(text))]


def score_form_fields(fields: dict[str, str]) -> tuple[int, list[dict]]:
    rows = []
    for label, value in fields.items():
        valid = bool(value.strip())
        note = "Completed" if valid else "Add this information"
        if valid and label == "Courriel" and ("@" not in value or "." not in value):
            valid = False
            note = "Use an email format such as lea@example.fr"
        if valid and label == "Âge" and not re.search(r"\d", value):
            valid = False
            note = "Write an age using a number"
        rows.append({"Field": label, "Point": 1 if valid else 0, "Feedback": note})
    return sum(row["Point"] for row in rows), rows


def score_message(text: str, prompt: dict) -> dict:
    words = tokenise_french(text)
    word_count = len(words)
    unique_count = len(set(words))
    required_hits, missing = count_required_groups(text, prompt["required"])
    errors = common_language_errors(text)
    lowered = normalise_text(text)

    if required_hits == len(prompt["required"]) and word_count >= 40:
        task_score = 3
    elif required_hits >= max(2, len(prompt["required"]) - 1) and word_count >= 30:
        task_score = 2
    elif required_hits or word_count >= 15:
        task_score = 1
    else:
        task_score = 0

    connector_count = sum(
        marker in lowered
        for marker in [" et ", " mais ", " parce que ", " ensuite", " puis ", " aussi", " enfin"]
    )
    sentence_count = len(re.findall(r"[.!?]+", text))
    coherence_score = min(3, int(word_count >= 20) + int(sentence_count >= 3) + int(connector_count >= 2))

    greeting = any(lowered.strip().startswith(item) for item in ["bonjour", "salut", "coucou", "cher", "chere"])
    closing = any(item in lowered for item in ["a bientot", "au revoir", "bisous", "bises", "a plus", "merci"])
    polite = any(item in lowered for item in ["s'il te plait", "s'il vous plait", "merci", "je voudrais"])
    social_score = int(greeting) + int(closing) + int(polite)

    useful_hits = sum(normalise_text(phrase) in lowered for phrase in prompt["useful"])
    lexical_score = min(3, int(unique_count >= 18) + int(unique_count >= 28) + int(useful_hits >= 1))

    verb_markers = re.findall(
        r"\b(?:je|j'|tu|il|elle|on|nous|vous|ils|elles)\s+(?:[a-zà-ÿ']+)", lowered
    )
    grammar_score = min(3, int(len(verb_markers) >= 2) + int(len(verb_markers) >= 4) + int(not errors and word_count >= 30))

    criteria = [
        {
            "Criterion": "Completing the task",
            "Score": task_score,
            "Out of": 3,
            "Feedback": (
                "All key details are present." if not missing else "Still cover: " + "; ".join(missing)
            ),
        },
        {
            "Criterion": "Coherence and linking",
            "Score": coherence_score,
            "Out of": 3,
            "Feedback": (
                "The message is organised into connected ideas."
                if coherence_score == 3
                else "Use short sentences and links such as et, mais, ensuite and parce que."
            ),
        },
        {
            "Criterion": "Appropriate greeting and tone",
            "Score": social_score,
            "Out of": 3,
            "Feedback": "Include a greeting, an appropriate polite phrase and a closing.",
        },
        {
            "Criterion": "Vocabulary",
            "Score": lexical_score,
            "Out of": 3,
            "Feedback": (
                "Good range for A1." if lexical_score == 3 else "Add precise words for time, place, people and activities."
            ),
        },
        {
            "Criterion": "Grammar and sentence control",
            "Score": grammar_score,
            "Out of": 3,
            "Feedback": errors[0] if errors else "Keep checking subject-verb forms and agreements.",
        },
    ]
    return {
        "word_count": word_count,
        "criteria": criteria,
        "score": sum(row["Score"] for row in criteria),
        "missing": missing,
        "errors": errors,
    }


def build_writing_text_report(result: dict) -> str:
    lines = [
        "DELF Junior A1 - Writing practice report",
        f"Created: {result['created']}",
        f"Topic: {result['prompt_title']}",
        "",
        f"Form practice: {result['form_score']}/10",
        f"Message practice estimate: {result['message']['score']}/15",
        f"Combined practice estimate: {result['total']}/25",
        f"Message length: {result['message']['word_count']} words",
        "",
        "Message:",
        result["text"],
        "",
        "Feedback:",
    ]
    for row in result["message"]["criteria"]:
        lines.append(f"- {row['Criterion']}: {row['Score']}/{row['Out of']} - {row['Feedback']}")
    lines.extend(["", "This is an automatic practice estimate, not an official examiner result."])
    return "\n".join(lines)


def build_writing_html_report(result: dict) -> bytes:
    criteria_html = "".join(
        "<tr>"
        f"<td>{html.escape(row['Criterion'])}</td>"
        f"<td>{row['Score']}/{row['Out of']}</td>"
        f"<td>{html.escape(row['Feedback'])}</td>"
        "</tr>"
        for row in result["message"]["criteria"]
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>DELF A1 writing report</title>
<style>body{{font:16px Arial,sans-serif;max-width:850px;margin:36px auto;color:#17233c;line-height:1.5}}
h1{{border-bottom:5px solid #e23d4f;padding-bottom:10px}}table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ccd4e0;padding:9px;text-align:left;vertical-align:top}}th{{background:#eef3f8}}
.score{{font-size:24px;font-weight:700;color:#0b5cab}}.note{{color:#5c667a}}</style></head>
<body><h1>DELF Junior A1 - Writing practice</h1><p>{html.escape(result['prompt_title'])}</p>
<p class="score">Practice estimate: {result['total']}/25</p>
<p><strong>Message ({result['message']['word_count']} words)</strong><br>{html.escape(result['text']).replace(chr(10), '<br>')}</p>
<h2>Feedback</h2><table><thead><tr><th>Criterion</th><th>Score</th><th>Next step</th></tr></thead>
<tbody>{criteria_html}</tbody></table><p class="note">Automatic practice estimate, not an official examiner result.</p></body></html>"""
    return document.encode("utf-8")


APP_CSS = """
<style>
    :root { --ink:#18233b; --blue:#1769aa; --red:#d83b50; --gold:#f3b63f; --paper:#ffffff; --line:#d9e1eb; }
    .stApp { background:#f5f7fa; color:var(--ink); }
    .block-container { max-width:1240px; padding-top:1.4rem; padding-bottom:3rem; }
    .delf-hero { background:#13233f; color:white; border-left:8px solid var(--red); border-radius:6px;
        padding:1.35rem 1.5rem; margin-bottom:1rem; box-shadow:0 7px 20px rgba(22,35,61,.10); }
    .delf-hero h1 { font-size:clamp(1.8rem,4vw,3rem); margin:0 0 .25rem; letter-spacing:0; color:white; }
    .delf-hero p { margin:0; color:#e9eef7; font-size:1.03rem; }
    .section-kicker { color:var(--red); font-weight:800; text-transform:uppercase; font-size:.76rem; margin-bottom:.15rem; }
    .document-sheet { background:var(--paper); border:1px solid var(--line); border-left:5px solid var(--blue);
        padding:1.1rem 1.2rem; border-radius:5px; white-space:pre-wrap; line-height:1.65; margin:.6rem 0 1rem; }
    .audio-panel { background:#eaf3fb; border:1px solid #bed5ea; border-radius:6px; padding:.8rem 1rem; margin:.5rem 0 1rem; }
    .score-strip { border-top:5px solid var(--gold); background:white; padding:.9rem 1rem; border-radius:4px; margin:.7rem 0; }
    .small-note { color:#5b6578; font-size:.9rem; }
    div[data-testid="stMetric"] { background:white; border:1px solid var(--line); border-top:4px solid var(--blue); padding:.7rem; border-radius:5px; }
    div[data-testid="stRadio"] { background:white; border:1px solid #e1e6ee; border-radius:5px; padding:.55rem .75rem;
        width:100%; box-sizing:border-box; }
    .stButton > button[kind="primary"] { background:var(--red); border-color:var(--red); font-weight:750; }
    .stButton > button { border-radius:5px; min-height:2.7rem; }
    .stDownloadButton > button { border-radius:5px; }
    div[data-baseweb="tab-list"] { gap:.25rem; overflow-x:auto; }
    div[data-baseweb="tab"] { min-width:max-content; }
    @media (max-width:700px) {
        .block-container { padding:1rem .8rem 2rem; }
        .delf-hero { padding:1rem; }
        .delf-hero h1 { font-size:1.8rem; }
        .document-sheet { padding:.9rem; }
    }
</style>
"""


def start_similar_objective_task(section: str, current_task: dict) -> None:
    tasks = LISTENING_TASKS if section == "Listening" else READING_TASKS
    task = choose_task(tasks, section, "Review my mistakes", current_task["skill"], current_task["id"])
    prefix = "delf_listening" if section == "Listening" else "delf_reading"
    st.session_state[f"{prefix}_id"] = task["id"]
    st.session_state[f"{prefix}_round"] += 1
    st.session_state[f"{prefix}_submitted"] = False
    st.session_state[f"{prefix}_pending"] = False
    st.session_state[f"{prefix}_results"] = []


def render_objective_practice(section: str) -> None:
    is_listening = section == "Listening"
    tasks = LISTENING_TASKS if is_listening else READING_TASKS
    prefix = "delf_listening" if is_listening else "delf_reading"
    title = "Compréhension de l'oral" if is_listening else "Compréhension des écrits"
    subtitle = (
        "Listen for purpose, people, times and practical details."
        if is_listening
        else "Scan the document first, then find evidence for every answer."
    )

    st.markdown(f'<div class="section-kicker">{html.escape(section)} practice</div>', unsafe_allow_html=True)
    st.header(title)
    st.write(subtitle)

    control_1, control_2, control_3 = st.columns([1, 1.2, 1])
    with control_1:
        st.selectbox("Practice mode", PRACTICE_MODES, key=f"{prefix}_mode")
    skills = ["All skills"] + sorted({task["skill"] for task in tasks})
    with control_2:
        st.selectbox("Focus", skills, key=f"{prefix}_skill")
    with control_3:
        st.write("")
        st.button(
            "New listening challenge" if is_listening else "New reading challenge",
            key=f"{prefix}_new",
            type="primary",
            width="stretch",
            on_click=new_objective_task,
            args=(section,),
        )

    task = get_by_id(tasks, st.session_state[f"{prefix}_id"])
    round_no = st.session_state[f"{prefix}_round"]
    submitted = st.session_state[f"{prefix}_submitted"]
    pending = st.session_state[f"{prefix}_pending"]

    st.subheader(task["title"])
    st.caption(f"Focus skill: {task['skill']} · 4 questions · all answers begin unticked")

    if is_listening:
        media = audio_path(task["track"])
        st.markdown(
            f'<div class="audio-panel"><strong>Situation</strong><br>{html.escape(task["context"])}</div>',
            unsafe_allow_html=True,
        )
        if media.exists():
            st.audio(str(media), format="audio/mp3")
        else:
            st.error(f"The local audio file could not be found: {media.name}")
        st.caption("Exam habit: listen once for the situation, then again for exact details.")
    else:
        st.markdown(
            f'<div class="document-sheet">{html.escape(task["document"])}</div>',
            unsafe_allow_html=True,
        )

    for index, question in enumerate(task["questions"]):
        st.radio(
            f"{index + 1}. {question['prompt']}",
            question["choices"],
            index=None,
            key=f"{prefix}_{round_no}_{index}",
            disabled=submitted or pending,
            width="stretch",
        )

    answer_keys = [f"{prefix}_{round_no}_{index}" for index in range(len(task["questions"]))]
    unanswered = [index + 1 for index, key in enumerate(answer_keys) if st.session_state.get(key) is None]

    if not submitted and not pending:
        if st.button("Submit my answers", key=f"{prefix}_submit_{round_no}", type="primary", width="stretch"):
            if unanswered:
                st.error("Answer every question before submitting. Still blank: " + ", ".join(map(str, unanswered)))
            else:
                st.session_state[f"{prefix}_pending"] = True
                st.rerun()

    if pending and not submitted:
        st.warning("Ready to submit? You will see the answers and will not be able to change this attempt.")
        confirm_col, edit_col = st.columns(2)
        with confirm_col:
            if st.button("Yes, submit now", key=f"{prefix}_confirm_{round_no}", type="primary", width="stretch"):
                submit_objective_task(section, task)
                st.rerun()
        with edit_col:
            if st.button("Keep editing", key=f"{prefix}_edit_{round_no}", width="stretch"):
                st.session_state[f"{prefix}_pending"] = False
                st.rerun()

    if submitted:
        results = st.session_state[f"{prefix}_results"]
        score = sum(row["Result"] == "Correct" for row in results)
        st.markdown('<div class="score-strip">', unsafe_allow_html=True)
        if score == len(results):
            st.success(f"Excellent listening! {score}/{len(results)} correct." if is_listening else f"Excellent reading! {score}/{len(results)} correct.")
        elif score >= len(results) / 2:
            st.info(f"Good progress: {score}/{len(results)} correct. Review the evidence below.")
        else:
            st.warning(f"You scored {score}/{len(results)}. This task is now in your smart review queue.")
        st.progress(score / len(results))
        st.markdown("</div>", unsafe_allow_html=True)

        for row in results:
            symbol = "Correct" if row["Result"] == "Correct" else "Try this clue"
            with st.expander(f"Question {row['Question']}: {symbol}", expanded=row["Result"] != "Correct"):
                st.write(f"**Your answer:** {row['Your answer']}")
                st.write(f"**Correct answer:** {row['Correct answer']}")
                st.write(f"**Why:** {row['Why']}")
        if is_listening:
            st.info(f"After listening, the whole message can be summarised as: {task['summary']}")

        export_col, similar_col = st.columns([1, 1.35])
        with export_col:
            st.download_button(
                "Export this result",
                data=rows_to_csv(results),
                file_name=f"delf_a1_{section.lower()}_{datetime.now():%Y%m%d_%H%M}.csv",
                mime="text/csv",
                key=f"{prefix}_download_{round_no}",
                width="stretch",
            )
        with similar_col:
            st.button(
                "Practise another task like this",
                key=f"{prefix}_similar_{round_no}",
                type="primary",
                width="stretch",
                on_click=start_similar_objective_task,
                args=(section, task),
            )


def choose_language_questions(topic: str, mode: str, count: int) -> list[dict]:
    candidates = [
        question for question in LANGUAGE_QUESTIONS if topic == "All topics" or question["topic"] == topic
    ]
    review = st.session_state.delf_progress["review"]
    if mode == "Review my mistakes":
        weak = [question for question in candidates if review.get(f"Language|{question['topic']}", 0) > 0]
        if weak:
            candidates = weak
    count = min(count, len(candidates))
    selected = []
    pool = candidates.copy()
    while pool and len(selected) < count:
        if mode in {"Smart mix", "Review my mistakes"}:
            weights = [1 + review.get(f"Language|{question['topic']}", 0) * 3 for question in pool]
            choice = random.choices(pool, weights=weights, k=1)[0]
        else:
            choice = random.choice(pool)
        selected.append(choice)
        pool.remove(choice)
    return selected


def new_language_quiz() -> None:
    selected = choose_language_questions(
        st.session_state.get("delf_language_topic", "All topics"),
        st.session_state.get("delf_language_mode", PRACTICE_MODES[0]),
        st.session_state.get("delf_language_count", 5),
    )
    st.session_state.delf_language_ids = [question["id"] for question in selected]
    st.session_state.delf_language_orders = {
        question["id"]: random.sample(question["choices"], len(question["choices"])) for question in selected
    }
    st.session_state.delf_language_round += 1
    st.session_state.delf_language_submitted = False
    st.session_state.delf_language_pending = False
    st.session_state.delf_language_results = []


def submit_language_quiz(questions: list[dict]) -> None:
    round_no = st.session_state.delf_language_round
    results = []
    wrong_skills = []
    correct_skills = []
    for index, question in enumerate(questions):
        selected = st.session_state.get(f"delf_language_{round_no}_{index}")
        correct = selected == question["answer"]
        results.append(
            {
                "Question": index + 1,
                "Topic": question["topic"],
                "Your answer": selected,
                "Correct answer": question["answer"],
                "Result": "Correct" if correct else "Review",
                "Why": question["explanation"],
            }
        )
        (correct_skills if correct else wrong_skills).append(question["topic"])
    score = sum(row["Result"] == "Correct" for row in results)
    st.session_state.delf_language_results = results
    st.session_state.delf_language_submitted = True
    st.session_state.delf_language_pending = False
    record_attempt("Language", "A1 language lab", score, len(results), wrong_skills, correct_skills)


def render_language_lab() -> None:
    st.markdown('<div class="section-kicker">Accuracy builder</div>', unsafe_allow_html=True)
    st.header("Language lab")
    st.write("Build the grammar and everyday vocabulary that support all four exam skills.")

    topics = ["All topics"] + sorted({question["topic"] for question in LANGUAGE_QUESTIONS})
    col_1, col_2, col_3, col_4 = st.columns([1.35, 1, .8, 1])
    with col_1:
        st.selectbox("Topic", topics, key="delf_language_topic")
    with col_2:
        st.selectbox("Practice mode", PRACTICE_MODES, key="delf_language_mode")
    with col_3:
        st.selectbox("Questions", [5, 10, 15], key="delf_language_count")
    with col_4:
        st.write("")
        st.button(
            "New language challenge",
            key="delf_language_new",
            type="primary",
            width="stretch",
            on_click=new_language_quiz,
        )

    if not st.session_state.delf_language_ids:
        new_language_quiz()
        st.rerun()

    questions = [get_by_id(LANGUAGE_QUESTIONS, item_id) for item_id in st.session_state.delf_language_ids]
    round_no = st.session_state.delf_language_round
    submitted = st.session_state.delf_language_submitted
    pending = st.session_state.delf_language_pending
    st.caption(f"{len(questions)} questions · no answer is selected for you")

    for index, question in enumerate(questions):
        st.radio(
            f"{index + 1}. {question['prompt']}",
            st.session_state.delf_language_orders[question["id"]],
            index=None,
            key=f"delf_language_{round_no}_{index}",
            disabled=submitted or pending,
            width="stretch",
        )

    answer_keys = [f"delf_language_{round_no}_{index}" for index in range(len(questions))]
    unanswered = [index + 1 for index, key in enumerate(answer_keys) if st.session_state.get(key) is None]
    if not submitted and not pending:
        if st.button("Submit my language answers", key=f"delf_language_submit_{round_no}", type="primary", width="stretch"):
            if unanswered:
                st.error("Answer every question before submitting. Still blank: " + ", ".join(map(str, unanswered)))
            else:
                st.session_state.delf_language_pending = True
                st.rerun()

    if pending and not submitted:
        st.warning("Submit this language challenge and reveal the explanations?")
        confirm_col, edit_col = st.columns(2)
        with confirm_col:
            if st.button("Yes, submit now", key=f"delf_language_confirm_{round_no}", type="primary", width="stretch"):
                submit_language_quiz(questions)
                st.rerun()
        with edit_col:
            if st.button("Keep editing", key=f"delf_language_edit_{round_no}", width="stretch"):
                st.session_state.delf_language_pending = False
                st.rerun()

    if submitted:
        results = st.session_state.delf_language_results
        score = sum(row["Result"] == "Correct" for row in results)
        st.subheader(f"Result: {score}/{len(results)}")
        st.progress(score / len(results))
        for row in results:
            with st.expander(
                f"Question {row['Question']} · {row['Topic']} · {row['Result']}",
                expanded=row["Result"] != "Correct",
            ):
                st.write(f"**Your answer:** {row['Your answer']}")
                st.write(f"**Correct answer:** {row['Correct answer']}")
                st.write(f"**Rule:** {row['Why']}")
        st.download_button(
            "Export language result",
            data=rows_to_csv(results),
            file_name=f"delf_a1_language_{datetime.now():%Y%m%d_%H%M}.csv",
            mime="text/csv",
            key=f"delf_language_download_{round_no}",
        )


def new_writing_prompt() -> None:
    current = st.session_state.delf_writing_prompt_id
    choices = [prompt for prompt in WRITING_PROMPTS if prompt["id"] != current]
    st.session_state.delf_writing_prompt_id = random.choice(choices)["id"]
    st.session_state.delf_writing_round += 1
    st.session_state.delf_writing_result = None


def render_writing_practice() -> None:
    st.markdown('<div class="section-kicker">Production écrite</div>', unsafe_allow_html=True)
    st.header("Writing studio")
    st.write("Complete both DELF-style tasks, then use the feedback to rewrite more precisely.")

    prompt_options = [prompt["id"] for prompt in WRITING_PROMPTS]
    prompt_col, button_col = st.columns([2.3, 1])
    with prompt_col:
        st.selectbox(
            "Message topic",
            prompt_options,
            key="delf_writing_prompt_id",
            format_func=lambda item_id: get_by_id(WRITING_PROMPTS, item_id)["title"],
        )
    with button_col:
        st.write("")
        st.button(
            "New writing mission",
            key="delf_writing_new",
            type="primary",
            width="stretch",
            on_click=new_writing_prompt,
        )

    prompt = get_by_id(WRITING_PROMPTS, st.session_state.delf_writing_prompt_id)
    round_no = st.session_state.delf_writing_round
    st.subheader("Task 1 · Complete a form")
    st.caption("Use imaginary details for practice. Do not enter a real home address, phone number or personal email.")

    with st.form(f"delf_writing_form_{round_no}"):
        field_col_1, field_col_2 = st.columns(2)
        with field_col_1:
            surname = st.text_input("Nom", key=f"delf_form_surname_{round_no}")
            first_name = st.text_input("Prénom", key=f"delf_form_first_{round_no}")
            age = st.text_input("Âge", key=f"delf_form_age_{round_no}")
            nationality = st.text_input("Nationalité", key=f"delf_form_nationality_{round_no}")
            fake_address = st.text_input("Adresse imaginaire", key=f"delf_form_address_{round_no}")
        with field_col_2:
            fake_email = st.text_input("Courriel imaginaire", key=f"delf_form_email_{round_no}")
            date = st.text_input("Date", key=f"delf_form_date_{round_no}")
            activity = st.text_input("Activité préférée", key=f"delf_form_activity_{round_no}")
            available_days = st.text_input("Jours disponibles", key=f"delf_form_days_{round_no}")
            signature = st.text_input("Signature", key=f"delf_form_signature_{round_no}")

        st.subheader("Task 2 · Write a message of at least 40 words")
        st.markdown(
            f'<div class="document-sheet"><strong>Consigne</strong><br>{html.escape(prompt["instruction"])}</div>',
            unsafe_allow_html=True,
        )
        message = st.text_area(
            "Votre message",
            height=260,
            placeholder="Écrivez votre message ici...",
            key=f"delf_writing_text_{round_no}",
        )
        submitted = st.form_submit_button("Analyse my writing", type="primary", width="stretch")

    if submitted:
        fields = {
            "Nom": surname,
            "Prénom": first_name,
            "Âge": age,
            "Nationalité": nationality,
            "Adresse": fake_address,
            "Courriel": fake_email,
            "Date": date,
            "Activité": activity,
            "Jours disponibles": available_days,
            "Signature": signature,
        }
        form_score, form_rows = score_form_fields(fields)
        message_result = score_message(message, prompt)
        total = form_score + message_result["score"]
        result = {
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "prompt_title": prompt["title"],
            "prompt_id": prompt["id"],
            "form_score": form_score,
            "form_rows": form_rows,
            "message": message_result,
            "text": message,
            "total": total,
        }
        st.session_state.delf_writing_result = result
        wrong = [row["Criterion"] for row in message_result["criteria"] if row["Score"] < 2]
        correct = [row["Criterion"] for row in message_result["criteria"] if row["Score"] >= 2]
        record_attempt("Writing", prompt["title"], total, 25, wrong, correct)
        st.rerun()

    result = st.session_state.delf_writing_result
    if result:
        st.divider()
        st.subheader("Writing feedback")
        st.caption("Automatic practice estimate only. An official DELF examiner may score the work differently.")
        metric_1, metric_2, metric_3, metric_4 = st.columns(4)
        metric_1.metric("Form", f"{result['form_score']}/10")
        metric_2.metric("Message", f"{result['message']['score']}/15")
        metric_3.metric("Practice total", f"{result['total']}/25")
        metric_4.metric("Message length", f"{result['message']['word_count']} words")

        if result["message"]["word_count"] < 40:
            st.warning(
                f"The DELF task asks for at least 40 words. Add {40 - result['message']['word_count']} or more words before your next attempt."
            )
        elif result["total"] >= 20:
            st.success("Strong A1 practice: the message is complete, clear and appropriately organised.")
        else:
            st.info("Choose the two lowest criteria below and improve those first. Small, precise revisions work best.")

        st.dataframe(result["message"]["criteria"], hide_index=True, width="stretch")
        with st.expander("Form field check"):
            st.dataframe(result["form_rows"], hide_index=True, width="stretch")
        with st.expander("Useful language and a model response"):
            st.write("**Useful phrases:** " + " · ".join(prompt["useful"]))
            st.write("**Model response:**")
            st.write(prompt["model"])
            st.caption("Compare the structure and required details; do not memorise the model word for word.")

        rubric_rows = [
            {
                "Criterion": row["Criterion"],
                "Score": row["Score"],
                "Out of": row["Out of"],
                "Feedback": row["Feedback"],
            }
            for row in result["message"]["criteria"]
        ]
        export_1, export_2, export_3 = st.columns(3)
        with export_1:
            st.download_button(
                "Download text report",
                build_writing_text_report(result).encode("utf-8-sig"),
                file_name=f"delf_a1_writing_{datetime.now():%Y%m%d_%H%M}.txt",
                mime="text/plain",
                key=f"delf_writing_text_export_{round_no}",
                width="stretch",
            )
        with export_2:
            st.download_button(
                "Download feedback CSV",
                rows_to_csv(rubric_rows),
                file_name=f"delf_a1_writing_feedback_{datetime.now():%Y%m%d_%H%M}.csv",
                mime="text/csv",
                key=f"delf_writing_csv_export_{round_no}",
                width="stretch",
            )
        with export_3:
            st.download_button(
                "Download printable HTML",
                build_writing_html_report(result),
                file_name=f"delf_a1_writing_report_{datetime.now():%Y%m%d_%H%M}.html",
                mime="text/html",
                key=f"delf_writing_html_export_{round_no}",
                width="stretch",
            )


def draw_interview_questions() -> None:
    st.session_state.delf_interview_questions = random.sample(INTERVIEW_QUESTIONS, 6)
    st.session_state.delf_interview_round += 1
    st.session_state.delf_interview_submitted = False
    st.session_state.delf_interview_result = None


def draw_information_cards() -> None:
    st.session_state.delf_cards = random.sample(INFORMATION_CARDS, 6)
    st.session_state.delf_cards_round += 1
    st.session_state.delf_cards_results = None


def question_is_formed(text: str) -> bool:
    lowered = normalise_text(text.strip())
    starters = (
        "qui ", "que ", "qu'est-ce", "quel", "quelle", "quels", "quelles", "ou ", "quand ",
        "comment ", "combien ", "pourquoi ", "est-ce que", "avez-vous", "êtes-vous", "pouvez-vous",
    )
    return len(tokenise_french(text)) >= 3 and (text.strip().endswith("?") or lowered.startswith(starters))


def reset_roleplay() -> None:
    st.session_state.delf_roleplay_round += 1
    st.session_state.delf_roleplay_messages = [
        {"role": "Examinateur", "content": "Bonjour ! Je vous écoute. Que puis-je faire pour vous ?"}
    ]
    st.session_state.delf_roleplay_cart = {}
    st.session_state.delf_roleplay_result = None


def quantity_from_line(line: str) -> int:
    lowered = normalise_text(line)
    quantities = {"quatre": 4, "trois": 3, "deux": 2, "une": 1, "un": 1}
    digit = re.search(r"\b([1-4])\b", lowered)
    if digit:
        return int(digit.group(1))
    return next((number for word, number in quantities.items() if re.search(rf"\b{word}\b", lowered)), 1)


def examiner_reply(line: str, scenario: dict) -> str:
    lowered = normalise_text(line)
    mentioned = [item for item in scenario["items"] if normalise_text(item) in lowered]
    wants_item = any(word in lowered for word in ["voudrais", "prends", "prendre", "achete", "acheter", "je veux"])
    asks_price = any(word in lowered for word in ["combien", "prix", "coute", "coutent"])
    asks_total = any(word in lowered for word in ["total", "payer", "paie", "voila"])

    if mentioned and wants_item:
        quantity = min(4, quantity_from_line(line))
        for item in mentioned:
            st.session_state.delf_roleplay_cart[item] = st.session_state.delf_roleplay_cart.get(item, 0) + quantity
        names = " et ".join(mentioned)
        return f"Très bien, {quantity} {names}. Vous désirez autre chose ?"
    if mentioned and asks_price:
        prices = [f"{item} : {scenario['items'][item]:.2f} €" for item in mentioned]
        return "Bien sûr. " + " ; ".join(prices) + "."
    if asks_total and st.session_state.delf_roleplay_cart:
        total = sum(
            scenario["items"][item] * quantity for item, quantity in st.session_state.delf_roleplay_cart.items()
        )
        return f"Cela fait {total:.2f} € au total, s'il vous plaît."
    if "heure" in lowered or "quai" in lowered:
        return "Le prochain départ est à 15 h 20, quai 4."
    if asks_price:
        return "De quel article voulez-vous connaître le prix ?"
    if any(word in lowered for word in ["bonjour", "bonsoir", "salut"]):
        return "Bonjour ! Qu'est-ce que vous souhaitez ?"
    if any(word in lowered for word in ["merci", "au revoir", "bonne journee"]):
        return "Merci à vous. Au revoir et bonne journée !"
    return "D'accord. Pouvez-vous préciser votre demande, s'il vous plaît ?"


def evaluate_roleplay(scenario: dict) -> tuple[int, list[dict]]:
    learner_text = normalise_text(" ".join(
        message["content"]
        for message in st.session_state.delf_roleplay_messages
        if message["role"] == "Candidat"
    ))
    checks = [
        ("Open the exchange", any(word in learner_text for word in ["bonjour", "bonsoir", "salut"]), "Begin with bonjour or bonsoir."),
        ("Make a polite request", any(word in learner_text for word in ["je voudrais", "s'il vous plait"]), "Use je voudrais... s'il vous plaît."),
        ("Ask for information", any(word in learner_text for word in ["combien", "coute", "prix", "heure", "quai", "quel"]), "Ask at least one relevant question."),
        ("Choose an item or service", any(normalise_text(item) in learner_text for item in scenario["items"]), "Name exactly what you want."),
        ("Give a quantity", bool(re.search(r"\b(?:1|2|3|4|un|une|deux|trois|quatre)\b", learner_text)), "Say the number or quantity."),
        ("Close politely", any(word in learner_text for word in ["merci", "au revoir", "bonne journee"]), "Finish with thanks and a goodbye."),
    ]
    rows = [
        {"Communication step": label, "Point": 1 if passed else 0, "Next time": "Achieved" if passed else advice}
        for label, passed, advice in checks
    ]
    return sum(row["Point"] for row in rows), rows


def render_speaking_practice() -> None:
    st.markdown('<div class="section-kicker">Production orale</div>', unsafe_allow_html=True)
    st.header("Speaking room")
    st.write("Practise the three parts of the A1 oral exam. Speak aloud before using the self-check.")

    interview_tab, cards_tab, roleplay_tab = st.tabs(
        ["1 · Guided interview", "2 · Information exchange", "3 · Roleplay"]
    )

    with interview_tab:
        st.subheader("Entretien dirigé")
        st.write("Answer each question aloud in two or three short French sentences.")
        st.button(
            "Draw six new questions",
            key="delf_interview_new",
            on_click=draw_interview_questions,
            type="primary",
        )
        round_no = st.session_state.delf_interview_round
        checked = []
        for index, question in enumerate(st.session_state.delf_interview_questions):
            st.markdown(f"**{index + 1}. {question}**")
            checked.append(
                st.checkbox(
                    "I answered aloud with a complete sentence",
                    value=False,
                    key=f"delf_interview_check_{round_no}_{index}",
                    disabled=st.session_state.delf_interview_submitted,
                )
            )
        if not st.session_state.delf_interview_submitted:
            if st.button(
                "Finish my interview check",
                key=f"delf_interview_submit_{round_no}",
                type="primary",
                width="stretch",
            ):
                score = sum(checked)
                st.session_state.delf_interview_result = score
                st.session_state.delf_interview_submitted = True
                record_attempt(
                    "Speaking",
                    "Guided interview",
                    score,
                    6,
                    ["Complete spoken answers"] * (6 - score),
                    ["Complete spoken answers"] * score,
                )
                st.rerun()
        if st.session_state.delf_interview_submitted:
            score = st.session_state.delf_interview_result
            st.info(f"Self-check: {score}/6 complete answers. Add a reason or example to any answer that felt too short.")

    with cards_tab:
        st.subheader("Échange d'informations")
        st.write("For each card, type the question you would ask the examiner. Say it aloud as well.")
        st.button(
            "Draw six new cards",
            key="delf_cards_new",
            on_click=draw_information_cards,
            type="primary",
        )
        round_no = st.session_state.delf_cards_round
        answers = []
        for index, (keyword, _) in enumerate(st.session_state.delf_cards):
            answers.append(
                st.text_input(
                    f"Card {index + 1}: {keyword}",
                    key=f"delf_card_answer_{round_no}_{index}",
                    disabled=st.session_state.delf_cards_results is not None,
                    placeholder="Écrivez une question complète...",
                )
            )
        if st.session_state.delf_cards_results is None:
            if st.button(
                "Check my six questions",
                key=f"delf_cards_submit_{round_no}",
                type="primary",
                width="stretch",
            ):
                if any(not answer.strip() for answer in answers):
                    st.error("Write a question for every card before checking.")
                else:
                    results = []
                    for (keyword, model), answer in zip(st.session_state.delf_cards, answers):
                        formed = question_is_formed(answer)
                        results.append(
                            {
                                "Card": keyword,
                                "Your question": answer,
                                "Point": 1 if formed else 0,
                                "Example": model,
                            }
                        )
                    st.session_state.delf_cards_results = results
                    score = sum(row["Point"] for row in results)
                    record_attempt(
                        "Speaking",
                        "Information exchange",
                        score,
                        6,
                        ["Forming questions"] * (6 - score),
                        ["Forming questions"] * score,
                    )
                    st.rerun()
        if st.session_state.delf_cards_results is not None:
            results = st.session_state.delf_cards_results
            score = sum(row["Point"] for row in results)
            st.subheader(f"Question check: {score}/6")
            st.dataframe(results, hide_index=True, width="stretch")
            st.caption("Many questions can be correct. The examples show one natural A1 possibility.")

    with roleplay_tab:
        st.subheader("Dialogue simulé")
        scenario_ids = [scenario["id"] for scenario in ROLEPLAY_SCENARIOS]
        st.selectbox(
            "Situation",
            scenario_ids,
            key="delf_roleplay_id",
            format_func=lambda scenario_id: get_by_id(ROLEPLAY_SCENARIOS, scenario_id)["title"],
            on_change=reset_roleplay,
        )
        scenario = get_by_id(ROLEPLAY_SCENARIOS, st.session_state.delf_roleplay_id)
        st.markdown(
            f'<div class="document-sheet"><strong>Votre mission</strong><br>{html.escape(scenario["brief"])}</div>',
            unsafe_allow_html=True,
        )
        catalogue = [
            {"Article ou service": item, "Prix": f"{price:.2f} €"} for item, price in scenario["items"].items()
        ]
        st.dataframe(catalogue, hide_index=True, width="stretch")

        for message in st.session_state.delf_roleplay_messages:
            role = "assistant" if message["role"] == "Examinateur" else "user"
            with st.chat_message(role):
                st.write(f"**{message['role']} :** {message['content']}")

        if st.session_state.delf_roleplay_result is None:
            turn = len(st.session_state.delf_roleplay_messages)
            with st.form(
                f"delf_roleplay_form_{st.session_state.delf_roleplay_round}_{turn}",
                clear_on_submit=True,
            ):
                line = st.text_input(
                    "Votre phrase",
                    placeholder="Parlez à voix haute, puis écrivez votre phrase...",
                )
                sent = st.form_submit_button("Send to the examiner", type="primary", width="stretch")
            if sent:
                if not line.strip():
                    st.error("Say and write one French sentence before sending.")
                else:
                    st.session_state.delf_roleplay_messages.append(
                        {"role": "Candidat", "content": line.strip()}
                    )
                    st.session_state.delf_roleplay_messages.append(
                        {"role": "Examinateur", "content": examiner_reply(line, scenario)}
                    )
                    st.rerun()

            if len(st.session_state.delf_roleplay_messages) >= 5:
                if st.button(
                    "Finish and assess this roleplay",
                    key=f"delf_roleplay_assess_{st.session_state.delf_roleplay_round}",
                    type="primary",
                    width="stretch",
                ):
                    score, rows = evaluate_roleplay(scenario)
                    st.session_state.delf_roleplay_result = {"score": score, "rows": rows}
                    record_attempt(
                        "Speaking",
                        scenario["title"],
                        score,
                        6,
                        [row["Communication step"] for row in rows if not row["Point"]],
                        [row["Communication step"] for row in rows if row["Point"]],
                    )
                    st.rerun()

        if st.session_state.delf_roleplay_result is not None:
            result = st.session_state.delf_roleplay_result
            st.subheader(f"Communication check: {result['score']}/6")
            st.dataframe(result["rows"], hide_index=True, width="stretch")
            st.button(
                "Start a new roleplay",
                key=f"delf_roleplay_reset_{st.session_state.delf_roleplay_round}",
                type="primary",
                on_click=reset_roleplay,
            )


def encouragement(progress: dict) -> str:
    if progress["attempts"] == 0:
        return "Start with one short challenge. Finishing a small task is the first win."
    accuracy = progress["correct"] / progress["questions"] if progress["questions"] else 0
    if progress["attempts"] >= 10 and accuracy >= 0.8:
        return "Your accuracy is becoming consistent. Add one timed exam-style session next."
    if accuracy < 0.55:
        return "Mistakes are useful data here. Smart mix will bring the difficult patterns back in a new context."
    if progress["attempts"] >= 5:
        return "You are building real exam stamina. Keep alternating listening, reading and speaking."
    return "Good momentum. One more different skill today will make the session balanced."


def render_dashboard() -> None:
    progress = st.session_state.delf_progress
    accuracy = round(progress["correct"] / progress["questions"] * 100) if progress["questions"] else 0
    st.markdown('<div class="section-kicker">Your preparation</div>', unsafe_allow_html=True)
    st.header("Mission control")
    st.write(encouragement(progress))

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Practice XP", progress["xp"])
    metric_2.metric("Challenges finished", progress["attempts"])
    metric_3.metric("Question accuracy", f"{accuracy}%")
    metric_4.metric("Current rank", rank_name(progress["xp"]))

    st.subheader("Exam readiness")
    readiness = []
    for section, exam_name in [
        ("Listening", "Listening"),
        ("Reading", "Reading"),
        ("Writing", "Writing"),
        ("Speaking", "Speaking"),
    ]:
        best = progress["best"].get(section)
        readiness.append(
            {
                "Exam skill": exam_name,
                "Best practice result": f"{best}%" if best is not None else "Not attempted",
                "Next target": "Mix in timed practice" if best is not None and best >= 80 else "Reach 80% twice",
            }
        )
    st.dataframe(readiness, hide_index=True, width="stretch")

    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Smart review queue")
        review_items = sorted(
            [(key, value) for key, value in progress["review"].items() if value > 0],
            key=lambda item: item[1],
            reverse=True,
        )
        if review_items:
            queue_rows = [
                {
                    "Area": key.split("|", 1)[0],
                    "Focus": key.split("|", 1)[1],
                    "Priority": "High" if value >= 4 else "Next",
                }
                for key, value in review_items[:6]
            ]
            st.dataframe(queue_rows, hide_index=True, width="stretch")
        else:
            st.info("The queue will fill automatically when an answer needs more practice.")
    with right:
        st.subheader("Milestones")
        milestones = [
            (1, "First challenge"),
            (5, "Five-task streak"),
            (10, "Ten challenges"),
            (20, "Exam explorer"),
        ]
        for target, label in milestones:
            reached = progress["attempts"] >= target
            st.write(f"{'Completed' if reached else 'Locked'} · {label} ({target})")

    st.subheader("Practice record")
    if progress["history"]:
        st.dataframe(list(reversed(progress["history"][-10:])), hide_index=True, width="stretch")
        download_1, download_2 = st.columns(2)
        with download_1:
            st.download_button(
                "Export progress CSV",
                rows_to_csv(progress["history"]),
                file_name=f"delf_a1_progress_{datetime.now():%Y%m%d}.csv",
                mime="text/csv",
                key="delf_progress_csv",
                width="stretch",
            )
        with download_2:
            st.download_button(
                "Back up this session",
                json.dumps(progress, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=f"delf_a1_session_{datetime.now():%Y%m%d}.json",
                mime="application/json",
                key="delf_progress_json",
                width="stretch",
            )
    else:
        st.caption("Completed practice will appear here. Progress is remembered during this browser session.")


def render_exam_guide() -> None:
    st.markdown('<div class="section-kicker">Know the challenge</div>', unsafe_allow_html=True)
    st.header("DELF Junior A1 exam guide")
    st.write(
        "The four skills are marked out of 25. To earn the diploma, a candidate needs at least 50/100 overall "
        "and at least 5/25 in every skill."
    )
    st.dataframe(EXAM_COMPONENTS, hide_index=True, width="stretch")
    st.caption("Timings and task counts follow the current France Éducation international A1 junior/scolaire overview.")

    st.subheader("A simple exam routine")
    routine_rows = [
        {"Skill": "Listening", "Before answering": "Identify who is speaking and why.", "Final check": "Check numbers, times, places and negatives."},
        {"Skill": "Reading", "Before answering": "Look at the document type, title and layout.", "Final check": "Point to the exact words that prove each answer."},
        {"Skill": "Writing", "Before answering": "Underline every required detail.", "Final check": "Count 40+ words; check greeting, verbs and closing."},
        {"Skill": "Speaking", "Before answering": "Prepare short reusable sentence patterns.", "Final check": "Ask, respond and close politely; keep communicating."},
    ]
    st.dataframe(routine_rows, hide_index=True, width="stretch")

    st.subheader("A1 phrase bank")
    st.caption("Use this area for revision after a practice attempt, not while answering a challenge.")
    for purpose, phrases in CURATED_WORD_BANK.items():
        with st.expander(purpose):
            st.write(" · ".join(phrases))

    audio_count = len(list(AUDIO_DIR.glob("*.mp3"))) if AUDIO_DIR.exists() else 0
    st.subheader("Rachel's local learning resources")
    st.write(
        f"The app uses selected recordings from the completed local course library ({audio_count} audio tracks available) "
        "and adds original questions for fresh practice. Source PDFs remain unchanged in the French folder."
    )
    st.link_button(
        "Official DELF Junior A1 information",
        "https://france-education-international.fr/article/delf-juniorscolaire-niveau-a1",
    )


def main() -> None:
    st.set_page_config(page_title="DELF Junior A1 Prep", layout="wide")
    initialise_state()
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="delf-hero">
            <h1>DELF Junior A1 Prep</h1>
            <p>Listen, read, write and speak with focused practice built around Rachel's completed French course.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    dashboard_tab, listening_tab, reading_tab, writing_tab, speaking_tab, language_tab, guide_tab = st.tabs(
        ["Dashboard", "Listening", "Reading", "Writing", "Speaking", "Language lab", "Exam guide"]
    )
    with dashboard_tab:
        render_dashboard()
    with listening_tab:
        render_objective_practice("Listening")
    with reading_tab:
        render_objective_practice("Reading")
    with writing_tab:
        render_writing_practice()
    with speaking_tab:
        render_speaking_practice()
    with language_tab:
        render_language_lab()
    with guide_tab:
        render_exam_guide()

    st.divider()
    st.caption("DELF Junior A1 Prep · independent practice tool · automatic feedback is not an official DELF result")


if __name__ == "__main__":
    main()
