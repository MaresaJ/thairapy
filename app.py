from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# AI Model laden
chatbot = pipeline("text-generation", model="gpt2")

@app.route("/")
def home():
    return "Hello AI, de chatbot werkt!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    vraag = data["vraag"]
    antwoord = chatbot(vraag, max_length=50, num_return_sequences=1)
    return jsonify({"antwoord": antwoord[0]["generated_text"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
