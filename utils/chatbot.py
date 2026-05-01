def ai_chat(user_input, history=None):
    text = user_input.lower()

    if "sad" in text:
        return "I'm here for you 💙 Maybe try drawing or talking to someone you trust."

    elif "angry" in text:
        return "Take a deep breath 😌 Try counting to 10 or going for a short walk."

    elif "happy" in text:
        return "That's awesome 😄 Keep doing what makes you happy!"

    elif "stress" in text:
        return "Try relaxing activities like music, breathing, or playing outside 🎧"

    else:
        return "Tell me more about how you're feeling 😊"