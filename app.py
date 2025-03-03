from flask import Flask, request, jsonify
from transformers import pipeline
import random
import os
import PyPDF2

app = Flask(__name__)

# AI-model
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model_name = "t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs.input_ids, max_length=50, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Reacties in apart bestand (voorbeeld)
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
        "Je bent sterker dan je denkt, al voelt dat misschien niet altijd zo.",
        "Goed dat je hierover praat."
    ]
}

# Complimenten geven op basis van toeval
def geef_compliment():
    if random.random() < 0.3:  # 30% kans op spontaan compliment
        return random.choice(empathische_reacties["compliment"])
    return ""

# Gespreksvoorbeelden uit PDF uitlezen
def lees_gespreksvoorbeelden(pdf_path):
    voorbeelden = []
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for pagina in reader.pages:
            tekst = pagina.extract_text()
            if tekst:
                voorbeelden.extend(tekst.splitlines())
    return voorbeelden

pdf_path = "/app/data/gespreksvoorbeelden.pdf"
gespreksvoorbeelden = lees_gespreksvoorbeelden(pdf_path) if os.path.exists(pdf_path) else []

# Empathische reactie functie
def empathische_reactie(vraag):
    for keyword in empathische_reacties:
        if keyword in vraag:
            basisreactie = random.choice(empathische_reacties[keyword])
            compliment = geef_compliment()
            return f"{basisreactie} {compliment}".strip()
    for voorbeeld in gespreksvoorbeelden:
        if voorbeeld.lower() in vraag:
            return f"{voorbeeld}"
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
    antwoord = generate_response(vraag)
    return jsonify({"antwoord": antwoord})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
