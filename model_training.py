import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import pickle

# Load dataset
df = pd.read_csv("ghost_borrower_dataset.csv")

# Encode categorical columns
le_business_type = LabelEncoder()
le_loan_purpose = LabelEncoder()
le_address_type = LabelEncoder()

df["business_type"] = le_business_type.fit_transform(df["business_type"])
df["loan_purpose"] = le_loan_purpose.fit_transform(df["loan_purpose"])
df["address_type"] = le_address_type.fit_transform(df["address_type"])

# Drop non-feature columns
X = df.drop(columns=["business_id", "is_ghost"])
y = df["is_ghost"]

# Handle missing values — fill with median of each column
imputer = SimpleImputer(strategy="median")
X_imputed = imputer.fit_transform(X)
X_imputed = pd.DataFrame(X_imputed, columns=X.columns)

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y, test_size=0.2, random_state=42, stratify=y
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Adjusted threshold for better ghost recall
y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred_adjusted = (y_pred_proba >= 0.3).astype(int)
print("\nAdjusted Classification Report (threshold 0.3):")
print(classification_report(y_test, y_pred_adjusted))

# Feature importance
importances = pd.Series(
    model.feature_importances_, index=X.columns
).sort_values(ascending=False)
print("\nTop 10 Most Important Features:")
print(importances.head(10))

# Save everything needed for inference later
with open("ghost_borrower_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("ghost_borrower_imputer.pkl", "wb") as f:
    pickle.dump(imputer, f)

with open("ghost_borrower_encoders.pkl", "wb") as f:
    pickle.dump({
        "business_type": le_business_type,
        "loan_purpose": le_loan_purpose,
        "address_type": le_address_type
    }, f)

print("\nModel, imputer and encoders saved successfully")