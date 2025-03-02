from flask import Flask, request, jsonify
from transformers import pipeline
import random
import os
import PyPDF2

app = Flask(__name__)

# AI-model
chatbot = pipeline("text-generation", model="gpt2")

# Reacties in apart bestand (voorbeeld)
empathische_reacties = {
    "ik voel me verdrietig": [
        "Dat klinkt zwaar... Wil je er meer over vertellen?",
        "Je bent niet alleen. Hoe kan ik je het beste helpen?",
        "Het is helemaal oké om je zo te voelen. Wat helpt jou om troost te vinden?"
    ],
    "ik heb stress": [
        "Stress kan veel energie kosten. Wat geeft je normaal rust?",
        "Wil je delen wat je het meest bezighoudt?",
        "Kan ik je helpen met ademhalingsoefeningen of een positieve gedachte?"
    ],
    "ik ben eenzaam": [
        "Dat lijkt me moeilijk... Wat helpt jou om je minder eenzaam te voelen?",
        "Wil je praten over wat je mist in gezelschap?"
    ],
    "ik ben boos": [
        "Goed dat je dit deelt! Wat maakt je boos?",
        "Boosheid is normaal. Wat zou je helpen om wat rust te vinden?",
        "Soms helpt bewegen, zoals een wandeling maken, om boosheid los te laten."
    ],
    "compliment": [
        "Je doet het ontzettend goed, vergeet dat niet!",
        "Je bent sterker dan je denkt.",
        "Het is moedig dat je hierover praat."
    ]
}

# Opvolgvraag
opvolgvraag = [
    "En wat nog meer?",
    "Hoe voelt dat voor jou?",
    "Wil je daar iets meer over delen?",
    "Wat komt er verder in je op?"
]

# Complimenten geven op basis van toeval
def geef_compliment():
    if random.random() < 0.3:  # 30% kans op spontaan compliment
        return random.choice(empathische_reacties["compliment"])
    return ""

def lees_gespreksvoorbeelden(pdf_path):
    voorbeelden = []
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for pagina in reader.pages:
            tekst = pagina.extract_text()
            voorbeelden.append(tekst)
    return " ".join(voorbeelden)

def empathische_reactie(vraag):
    for keyword in empathische_reacties:
        if keyword in vraag:
            basisreactie = random.choice(empathische_reacties[keyword])
            extra_vraag = random.choice(opvolgvraag)
            afsluitboodschap = "Je mag trots op jezelf zijn dat je dit deelt! Wil je nog iets kwijt?"
            compliment = geef_compliment()
            return f"{basisreactie} {extra_vraag} {compliment} {afsluitboodschap}"
    return None

@app.route("/")
def home():
    return "Hoi, ik ben de therapiebot 🌿"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    vraag = data["vraag"].lower()

    # Gespreksvoorbeelden uit PDF laden
    pdf_path = "/app/data/gespreksvoorbeelden.pdf"
    if os.path.exists(pdf_path):
        gespreksvoorbeelden = lees_gespreksvoorbeelden(pdf_path)
        if vraag in gespreksvoorbeelden:
            return jsonify({"antwoord": "Dat lijkt op iets wat ik herken... Wil je daar meer over delen?"})

    reactie = empathische_reactie(vraag)
    if reactie:
        if "wat zijn opmerkingen die je ooit hebben geholpen?" in vraag:
            nieuwe_opmerking = vraag.replace("wat zijn opmerkingen die je ooit hebben geholpen?", "").strip()
            empathische_reacties["persoonlijk"] = empathische_reacties.get("persoonlijk", []) + [nieuwe_opmerking]
            return jsonify({"antwoord": "Dank je voor het delen! Ik zal dit onthouden."})
        return jsonify({"antwoord": reactie})

    # Geen match, gebruik AI-model
    antwoord = chatbot(vraag, max_length=50, num_return_sequences=1)
    return jsonify({"antwoord": antwoord[0]["generated_text"]})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
