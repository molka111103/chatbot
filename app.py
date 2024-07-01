from flask import Flask, render_template, request, jsonify
from fuzzywuzzy import fuzz
import random
import json
import os

app = Flask(__name__)
last_keyword_context = None  # Global variable to store the last detected keyword context

def load_chat_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Ensure the file path is correct
file_path = os.path.join(os.path.dirname(__file__), 'data.json')
chat_data = load_chat_data(file_path)

salutations = chat_data.get("salutations", [])
remerciements = chat_data.get("remerciements", {})

def get_temperature_response(user_input, specific_responses):
    try:
        words = user_input.split()
        for word in words:
            try:
                temperature = float(word)
                for condition in specific_responses:
                    if eval(condition["condition"], {"temperature": temperature}):
                        return condition["response"]
            except ValueError:
                continue
    except (ValueError, SyntaxError):
        pass
    return None

def get_response(user_input):
    global last_keyword_context
    user_input_lower = user_input.lower()

    # Salutations
    for salutation in salutations:
        if fuzz.partial_ratio(user_input_lower, salutation.lower()) > 80:
            return f"{salutation.capitalize()}, comment puis-je vous aider?"

    # Check for "oui" or "non" in the context of the last detected keyword
    if last_keyword_context:
        if "oui" in user_input_lower:
            response = random.choice(last_keyword_context['responses'].get("oui", last_keyword_context['responses'].get("default", [])))
            last_keyword_context = None  # Reset context after use
            return response
        elif "non" in user_input_lower:
            response = random.choice(last_keyword_context['responses'].get("non", last_keyword_context['responses'].get("default", [])))
            last_keyword_context = None  # Reset context after use
            return response

    # Détections de questions
    for detection in chat_data.get("questions_detections", []):
        if fuzz.partial_ratio(user_input_lower, detection["keyword"].lower()) > 80:
            last_keyword_context = detection  # Store the current context
            if detection["keyword"].lower() == "température":
                temperature_response = get_temperature_response(user_input, detection["responses"].get("specific", []))
                if temperature_response:
                    return temperature_response
            return random.choice(detection['responses'].get("default", []))

    # Informations complémentaires
    for info in chat_data.get("informations_complementaires", []):
        if fuzz.partial_ratio(user_input_lower, info["type"].lower()) > 80:
            details = random.choice(info["details"])
            return (f"Voici des informations supplémentaires:\n"
                    f"Type de sol: {details.get('type_de_sol', 'N/A')}\n"
                    f"Caractéristiques: {details.get('caracteristiques', 'N/A')}\n"
                    f"Conseils: {details.get('conseils', 'N/A')}")

    # Remerciements
    for key, responses in remerciements.items():
        if key in user_input_lower:
            return random.choice(responses)

    return "Désolé, mais nous n'avons pas compris votre demande! Pour assistance, veuillez nous contacter par téléphone au 55 221 722 ou par email à irwise@irwise.com."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form["user_input"]
    response = get_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
