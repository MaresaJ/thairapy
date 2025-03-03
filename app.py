from flask import Flask, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import random
import os
import PyPDF2

app = Flask(__name__)

# AI-model
model_name = "t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs.input_ids, max_length=50, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Empathische reacties
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
        "Wil je even spuien? Helpt dat?"
    ],
    "compliment": [
        "Je doet het ontzettend goed, vergeet dat niet!",
        "Je bent sterker dan je denkt.",
        "Het is moedig dat je hierover praat."
    ]
}

opvolgvraag = [
    "En wat nog meer?",
    "Hoe voelt dat voor jou?",
    "Wil je daar iets meer over delen?",
    "Wat komt er verder in je op?",
    "Wat zou je willen dat er nu verandert?"
]

def geef_compliment():
    if random.random() < 0.3:
        return random.choice(empathische_reacties["compliment"])
    return ""

def lees_gespreksvoorbeelden(pdf_path):
    voorbeelden = []
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for pagina in reader.pages:
            tekst = pagina.extract_text()
            if tekst:
                voorbeelden.append(tekst)
    return " ".join(voorbeelden)

@app.route("/")
def home():
    return "Therapiebot is actief 🌿"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    vraag = data["vraag"].lower()

    # PDF voorbeelden uitlezen
    pdf_path = "/app/data/gespreksvoorbeelden.pdf"
    if os.path.exists(pdf_path):
        gespreksvoorbeelden = lees_gespreksvoorbeelden(pdf_path)
        if vraag in gespreksvoorbeelden:
            return jsonify({"antwoord": "Dat lijkt op iets wat ik herken... Wil je daar meer over delen?"})

    for keyword in empathische_reacties:
        if keyword in vraag:
            basisreactie = random.choice(empathische_reacties[keyword])
            extra_vraag = random.choice(opvolgvraag)
            compliment = geef_compliment()
            afsluitboodschap = "Goed dat je dit deelt! Wil je nog iets kwijt?"
            return jsonify({"antwoord": f"{basisreactie} {extra_vraag} {compliment} {afsluitboodschap}"})

    if "wat zijn opmerkingen die je ooit hebben geholpen?" in vraag:
        nieuwe_opmerking = vraag.replace("wat zijn opmerkingen die je ooit hebben geholpen?", "").strip()
        empathische_reacties["persoonlijk"] = empathische_reacties.get("persoonlijk", []) + [nieuwe_opmerking]
        return jsonify({"antwoord": "Dank je voor het delen! Ik zal dit onthouden."})

    antwoord = generate_response(vraag)
    return jsonify({"antwoord": antwoord})

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
