import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import pickle

# Load dataset
df = pd.read_csv('../data/dataset.csv')

# Encode categorical data
le_mood = LabelEncoder()
le_activity = LabelEncoder()
le_stress = LabelEncoder()

df['mood'] = le_mood.fit_transform(df['mood'])
df['activity_level'] = le_activity.fit_transform(df['activity_level'])
df['stress_level'] = le_stress.fit_transform(df['stress_level'])

# Features and target
X = df[['mood', 'sleep_hours', 'screen_time', 'activity_level']]
y = df['stress_level']

# Train model
model = DecisionTreeClassifier()
model.fit(X, y)

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump((model, le_mood, le_activity, le_stress), f)

print("Model trained successfully!")