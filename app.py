from flask import Flask, request, jsonify
from transformers import pipeline
import random

app = Flask(__name__)

# AI-model
chatbot = pipeline("text-generation", model="gpt2")

# 🔥 Hier kun je zelf de standaard antwoorden aanpassen
empathische_reacties = {
    "ik voel me verdrietig": [
        "Dat klinkt zwaar... Wil je er meer over vertellen?",
        "Je bent niet alleen. Hoe kan ik je het beste helpen?",
        "Het is helemaal oké om je zo te voelen. Al is het natuurlijk prut. Wat maakt dat je het hier deelt? Hoe hoop je dat ik je kan helpen? Want dat doe ik graag."
    ],
    "ik heb stress": [
        "Stress kan veel energie kosten. Wat helpt jou om te ontspannen?",
        "Wil je iets delen over wat je stress geeft?"
    ],
    "ik ben eenzaam": [
        "Dat lijkt me moeilijk... Met wie/wat voor persoon zou je willen praten, of van wie zou je gezelschap willen hebben? En hoe zou diegene je minder eenzaam doen voelen?"

    ],
    "ik ben boos": [
        "Goed dat je het deelt! Wil je er meer over kwijt? Wat maakt je boos?",
        "Boosheid is normaal. Wat zou je helpen om wat rust te vinden?",
        "Soms helpt bewegen, zoals een wandeling maken, om boosheid los te laten."
    ]
}


# Opvolgvraag
opvolgvraag = [
    "En wat nog meer?",
    "Hoe voelt dat voor jou?",
    "Wil je daar iets meer over delen?",
    "Wat komt er verder in je op?"
]

def empathische_reactie(vraag):
    for keyword in empathische_reacties:
        if keyword in vraag:
            basisreactie = random.choice(empathische_reacties[keyword])
            extra_vraag = random.choice(opvolgvraag)
            return f"{basisreactie} {extra_vraag}"
    return None

@app.route("/")
def home():
    return "Therapiebot is actief 🌿"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    vraag = data["vraag"].lower()

    reactie = empathische_reactie(vraag)
    if reactie:
        return jsonify({"antwoord": reactie})

    # Geen match, gebruik AI-model
    antwoord = chatbot(vraag, max_length=50, num_return_sequences=1)
    return jsonify({"antwoord": antwoord[0]["generated_text"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
