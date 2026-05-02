import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
import shap
import os

MODEL_PATH = "model/xgboost_model.pkl"
EXPLAINER_PATH = "model/shap_explainer.pkl"

def generate_synthetic_data(num_samples=1000):
    np.random.seed(42)
    mood = np.random.randint(1, 11, num_samples) # 1-10
    sleep_duration = np.random.uniform(4.0, 11.0, num_samples) # 4 to 11 hours
    screen_time = np.random.uniform(0.5, 8.0, num_samples) # 0.5 to 8 hours
    activity_level = np.random.randint(1, 11, num_samples) # 1-10
    
    # Heuristic for stress score: lower mood, lower sleep, higher screen, lower activity -> higher stress
    # Normalizing all to roughly 0-1 range to create a score
    stress_score = (
        (11 - mood) * 0.3 + 
        (11 - sleep_duration) * 0.3 + 
        (screen_time) * 0.2 + 
        (11 - activity_level) * 0.2
    )
    
    # Add some noise
    stress_score += np.random.normal(0, 0.5, num_samples)
    
    # Scale to 0-100
    stress_score = (stress_score - stress_score.min()) / (stress_score.max() - stress_score.min()) * 100
    
    # Categorize
    stress_level = []
    for s in stress_score:
        if s < 33:
            stress_level.append("low")
        elif s < 66:
            stress_level.append("medium")
        else:
            stress_level.append("high")
            
    df = pd.DataFrame({
        "mood": mood,
        "sleep_duration": sleep_duration,
        "screen_time": screen_time,
        "activity_level": activity_level,
        "stress_score": stress_score,
        "stress_level": stress_level
    })
    return df

def train_and_save_model():
    if not os.path.exists("model"):
        os.makedirs("model")
        
    df = generate_synthetic_data(2000)
    X = df[['mood', 'sleep_duration', 'screen_time', 'activity_level']]
    y = df['stress_score'] # Training to predict continuous score
    
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X, y)
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
        
    explainer = shap.TreeExplainer(model)
    with open(EXPLAINER_PATH, "wb") as f:
        pickle.dump(explainer, f)
        
    print("Model and Explainer trained and saved successfully.")

def predict_stress(features_dict):
    """
    Takes a dict like: {'mood': 5, 'sleep_duration': 6.5, 'screen_time': 4.0, 'activity_level': 3}
    Returns score, level, and explanation.
    """
    if not os.path.exists(MODEL_PATH):
        train_and_save_model()
        
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(EXPLAINER_PATH, "rb") as f:
        explainer = pickle.load(f)
        
    # Order must match training
    X_pred = pd.DataFrame([features_dict])
    score = model.predict(X_pred)[0]
    
    if score < 33:
        level = "low"
    elif score < 66:
        level = "medium"
    else:
        level = "high"
        
    shap_values = explainer.shap_values(X_pred)
    
    # Map SHAP values to features to find top contributors
    feature_names = X_pred.columns
    contributions = dict(zip(feature_names, shap_values[0]))
    
    # Format explanation
    sorted_contributions = sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)
    top_feature, top_val = sorted_contributions[0]
    
    if top_val > 0:
        reason = f"High contribution from {top_feature}."
    else:
        reason = f"Low contribution from {top_feature}."
        
    return float(score), level, reason

if __name__ == "__main__":
    train_and_save_model()
