def get_recommendation(stress_level):
    if stress_level == "high":
        return "Try deep breathing 🧘 or talk to a parent."
    elif stress_level == "medium":
        return "Take a short break or play a game 🎮"
    else:
        return "Great! Keep doing what you love 😊"