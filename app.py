from flask import Flask, request, jsonify
from transformers import pipeline
import random
import os

app = Flask(__name__)

# AI-model
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model_name = "t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

empathische_reacties = {
    "ik voel me verdrietig": [
        "Dat klinkt zwaar... Wil je er meer over vertellen?",
        "Je bent niet alleen. Wat gaat er op dit moment door je heen?",
        "Het is helemaal oké om je zo te voelen. Wat maakt dit moment extra moeilijk voor je?"
    ],
    "ik heb stress": [
        "Stress kan veel energie kosten. Wat houdt je op dit moment het meest bezig?",
        "Wil je iets delen over wat je nu voelt in je lichaam?",
        "Wat helpt jou normaal om rust te vinden?"
    ],
    "ik ben eenzaam": [
        "Dat lijkt me moeilijk... Wanneer voel je je het minst alleen?",
        "Wat heb je nodig om je meer verbonden te voelen?"
    ],
    "ik ben boos": [
        "Goed dat je dit deelt! Wat maakt je precies boos?",
        "Welke gedachten komen er in je op als je boos bent?",
        "Wat zou je op dit moment nodig hebben om je rustiger te voelen?"
    ],
    "compliment": [
        "Je doet het ontzettend goed, vergeet dat niet!",
        "Je bent sterker dan je denkt, ook al voel je dat nu misschien niet zo.",
        "Goed dat je hierover praat, echt!"
    ]
}

opvolgvraag = [
    "Hoe voelt dat voor jou?",
    "Wil je daar iets meer over delen?",
    "Wat komt er verder in je op?",
    "Wat zou je willen dat er nu verandert?"
]

persoonlijke_opmerkingen = []

def geef_compliment():
    if random.random() < 0.3:  # 30% kans op spontaan compliment
        return random.choice(empathische_reacties["compliment"])
    return ""

def empathische_reactie(vraag):
    for keyword in empathische_reacties:
        if keyword in vraag:
            basisreactie = random.choice(empathische_reacties[keyword])
            extra_vraag = random.choice(opvolgvraag)
            compliment = geef_compliment()
            return f"{basisreactie} {extra_vraag} {compliment}"
    return None

@app.route("/")
def home():
    return "Therapiebot actief 🌿"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    vraag = data.get("vraag", "").lower()

    if "opmerkingen die je ooit hebben geholpen" in vraag:
        nieuwe_opmerking = vraag.replace("opmerkingen die je ooit hebben geholpen", "").strip()
        persoonlijke_opmerkingen.append(nieuwe_opmerking)
        return jsonify({"antwoord": "Dank je voor het delen! Ik zal dit onthouden."})

    reactie = empathische_reactie(vraag)
    if reactie:
        return jsonify({"antwoord": reactie})

    if persoonlijke_opmerkingen:
        eerder_geholpen = random.choice(persoonlijke_opmerkingen)
        return jsonify({"antwoord": f"Eerder gaf je aan dat '{eerder_geholpen}' je geholpen heeft. Zou dat nu ook steun kunnen bieden?"})

    return jsonify({"antwoord": "Ik hoor je... Wil je iets meer vertellen over wat je voelt?"})

if __name__ == "__main__":
    port = int(os.getenv("PORT"))  # Geen fallback
    app.run(host="0.0.0.0", port=port)
