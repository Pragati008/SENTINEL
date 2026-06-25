import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    roc_auc_score
)

# ==========================================
# LOAD DATASET
# ==========================================

DATA_FILE = "document_correlation_dataset.csv"

df = pd.read_csv(DATA_FILE)

print("Dataset Shape:", df.shape)

# ==========================================
# TARGET
# ==========================================

TARGET = "is_document_fraud"

X = df.drop(columns=[TARGET])
y = df[TARGET]

# ==========================================
# FEATURE TYPES
# ==========================================

categorical_features = [
    "emp_title",
    "verification_status",
    "address",
    "application_type",
    "loan_status"
]

numerical_features = [
    "annual_inc",
    "dti",
    "loan_amnt",
    "installment",
    "pan_match",
    "aadhaar_name_match",
    "address_match",
    "employer_match",
    "salary_itr_match",
    "bank_salary_match",
    "metadata_suspicious",
    "edited_in_photoshop",
    "ocr_confidence",
    "income_difference_pct"
]

# ==========================================
# PREPROCESSORS
# ==========================================

numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numerical_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# ==========================================
# MODEL
# ==========================================

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    scale_pos_weight=7.65,
    eval_metric="logloss"
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

# ==========================================
# TRAIN
# ==========================================

print("\nTraining Model...")

pipeline.fit(X_train, y_train)

# ==========================================
# PREDICT
# ==========================================

predictions = pipeline.predict(X_test)

probabilities = pipeline.predict_proba(X_test)[:,1]
probabilities = pipeline.predict_proba(X_test)[:, 1]
adjusted_predictions = (probabilities >= 0.3).astype(int)

print("\nAdjusted Classification Report (threshold 0.3):")
print(classification_report(y_test, adjusted_predictions))

# ==========================================
# EVALUATION
# ==========================================

print("\nAccuracy:")
print(accuracy_score(y_test, predictions))

print("\nROC AUC:")
print(roc_auc_score(y_test, probabilities))

print("\nClassification Report:")
print(classification_report(y_test, predictions))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    pipeline,
    "document_fraud_model_xgb.pkl"
)

print("\nModel Saved:")
print("document_fraud_model_xgb.pkl")