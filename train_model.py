import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Load data
df = pd.read_csv(r"C:\Users\Nikhil\loan_project\loan_project\loan_data (2).csv")

# Drop ID
df.drop("Loan_ID", axis=1, inplace=True)

# Fill missing
df.fillna(method='ffill', inplace=True)

# Feature Engineering
df['Total_Income'] = df['ApplicantIncome'] + df['CoapplicantIncome']

# Encode
categorical_cols = [
    'Gender', 'Married', 'Dependents', 'Education',
    'Self_Employed', 'Property_Area', 'Loan_Type', 'Loan_Status'
]

encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# Split
X = df.drop("Loan_Status", axis=1)
y = df["Loan_Status"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier(n_estimators=200))
])

pipeline.fit(X_train, y_train)

print("Accuracy:", pipeline.score(X_test, y_test))

# Save
joblib.dump(pipeline, "model.pkl")
joblib.dump(encoders, "encoders.pkl")

print("✅ Model saved")