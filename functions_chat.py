from fuzzywuzzy import fuzz
import time
import random
from tkinter import END

def envoie(user_input, e, txt, salutations, chat_data, remerciements):
    envoie = "moi: " + user_input
    txt.insert(END, "\n" + envoie)
    txt.yview_moveto(1.0)
    e.delete(0, END)

    responded = False 

    # Gestion des salutations
    for salutation in salutations:
        if fuzz.partial_ratio(user_input.lower(), salutation) > 80:
            show_message(txt, f"\nIrrigoBot: {salutation.capitalize()}, comment puis-je vous aider?")
            return

    # Gestion des questions détectées
    for detection in chat_data.get("questions_detections", []):
        if fuzz.partial_ratio(user_input.lower(), detection["keyword"].lower()) > 80:
            if "oui" in user_input.lower():
                response = random.choice(detection['responses'].get("oui", detection['responses'].get("default", [])))
            elif "non" in user_input.lower():
                response = random.choice(detection['responses'].get("non", detection['responses'].get("default", [])))
            elif "température" in user_input.lower():
                temperature_response = get_temperature_response(user_input, detection["responses"].get("specific", []))
                if temperature_response:
                    response = temperature_response
                else:
                    response = random.choice(detection['responses'].get("default", []))
            else:
                response = random.choice(detection['responses'].get("default", []))
            show_message(txt, f"\nIrrigoBot: {response}")
            responded = True

    # Gestion des informations complémentaires
    for info in chat_data.get("informations_complementaires", []):
        if fuzz.partial_ratio(user_input.lower(), info["type"].lower()) > 80:
            details = random.choice(info["details"])
            show_message(txt, f"\nIrrigoBot: Voici des informations supplémentaires:\nType de sol: {details['type_de_sol']}\nCaractéristiques: {details['caracteristiques']}\nConseils: {details['conseils']}")
            responded = True 

    # Gestion des remerciements
    for key, responses in remerciements.items():
        if key in user_input.lower():
            response = random.choice(responses)
            show_message(txt, f"\nIrrigoBot: {response}")
            responded = True
            break 
    
    if not responded:  
        show_message(txt, "\nIrrigoBot: Désolé, mais nous n'avons pas compris votre demande! Pour assistance, veuillez nous contacter par téléphone au 55 221 722 ou par email à irwise@irwise.com.")
        print("No match found. Default response given.")  # Debug message

def get_temperature_response(user_input, specific_responses):
    try:
        temperature = float(user_input.split()[-1])  # Assuming the temperature is the last word in the input
        for condition in specific_responses:
            if eval(condition["condition"]):
                return condition["response"]
    except ValueError:
        pass
    return None

def show_message(txt, message):
    for char in message:
        txt.insert(END, char)
        txt.update()
        time.sleep(0.05)

def on_text_scroll(txt, event):
    y = event.y
    height = txt.winfo_height()
    if y >= height - 20:  # Si le curseur est près du bas de la zone de texte
        txt.yview_moveto(1.0)  # Faire défiler automatiquement vers le bas
