import pandas as pd
import numpy as np

np.random.seed(42)

# ==========================================
# STEP 1: LOAD LENDING CLUB DATASET
# ==========================================

INPUT_FILE = "lending_club_loan_two.csv"
OUTPUT_FILE = "document_correlation_dataset.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

# ==========================================
# STEP 2: KEEP ONLY RELEVANT COLUMNS
# ==========================================

required_cols = [
    "annual_inc",
    "emp_title",
    "verification_status",
    "address",
    "application_type",
    "dti",
    "loan_amnt",
    "installment",
    "loan_status"
]

df = df[required_cols].copy()

# ==========================================
# STEP 3: REMOVE IMPORTANT NULLS
# ==========================================

df.dropna(
    subset=[
        "annual_inc",
        "emp_title",
        "address"
    ],
    inplace=True
)

# ==========================================
# STEP 4: RANDOM SAMPLE
# ==========================================

sample_size = min(10000, len(df))

df = df.sample(
    n=sample_size,
    random_state=42
).reset_index(drop=True)

n = len(df)

# ==========================================
# STEP 5: SYNTHETIC DOCUMENT FEATURES
# ==========================================

# Identity checks

df["pan_match"] = np.random.choice(
    [0, 1],
    size=n,
    p=[0.08, 0.92]
)

df["aadhaar_name_match"] = np.random.choice(
    [0, 1],
    size=n,
    p=[0.07, 0.93]
)

# Address consistency

df["address_match"] = np.random.choice(
    [0, 1],
    size=n,
    p=[0.10, 0.90]
)

# Employment consistency

df["employer_match"] = np.random.choice(
    [0, 1],
    size=n,
    p=[0.12, 0.88]
)

# Salary Slip vs ITR

df["salary_itr_match"] = np.random.choice(
    [0, 1],
    size=n,
    p=[0.10, 0.90]
)

# Bank Statement vs Salary

df["bank_salary_match"] = np.random.choice(
    [0, 1],
    size=n,
    p=[0.12, 0.88]
)

# Metadata tampering

df["metadata_suspicious"] = np.random.choice(
    [0, 1],
    size=n,
    p=[0.93, 0.07]
)

# Photoshop edited document

df["edited_in_photoshop"] = np.random.choice(
    [0, 1],
    size=n,
    p=[0.95, 0.05]
)

# OCR confidence score

df["ocr_confidence"] = np.random.uniform(
    70,
    100,
    size=n
).round(2)

# ==========================================
# STEP 6: INCOME DIFFERENCE %
# ==========================================

salary_multiplier = np.random.uniform(
    0.5,
    1.5,
    size=n
)

salary_slip_income = (
    df["annual_inc"] * salary_multiplier
)

df["income_difference_pct"] = (
    abs(
        salary_slip_income - df["annual_inc"]
    )
    / df["annual_inc"]
) * 100

df["income_difference_pct"] = (
    df["income_difference_pct"]
    .round(2)
)

# ==========================================
# STEP 7: WEIGHTED FRAUD SCORE
# ==========================================

fraud_score = (
      (df["pan_match"] == 0).astype(int) * 3
    + (df["aadhaar_name_match"] == 0).astype(int) * 3
    + (df["address_match"] == 0).astype(int) * 2
    + (df["employer_match"] == 0).astype(int) * 2
    + (df["salary_itr_match"] == 0).astype(int) * 2
    + (df["bank_salary_match"] == 0).astype(int) * 2
    + (df["metadata_suspicious"] == 1).astype(int) * 3
    + (df["edited_in_photoshop"] == 1).astype(int) * 3
    + (df["income_difference_pct"] > 35).astype(int) * 2
)

df["is_document_fraud"] = (
    fraud_score >= 6
).astype(int)

# ==========================================
# STEP 8: ADD LABEL NOISE
# ==========================================

noise_size = int(0.05 * n)

noise_indices = np.random.choice(
    df.index,
    noise_size,
    replace=False
)

df.loc[
    noise_indices,
    "is_document_fraud"
] = 1 - df.loc[
    noise_indices,
    "is_document_fraud"
]

# ==========================================
# STEP 9: ADD MISSING VALUES
# ==========================================

null_rows = np.random.choice(
    df.index,
    int(0.05 * n),
    replace=False
)

df.loc[
    null_rows,
    "income_difference_pct"
] = np.nan

# ==========================================
# STEP 10: SAVE DATASET
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================
# STEP 11: REPORT
# ==========================================

print("\nDataset Created Successfully")

print("\nShape:")
print(df.shape)

print("\nClass Distribution:")
print(
    df["is_document_fraud"]
    .value_counts()
)

print("\nFraud Percentage:")
print(
    round(
        df["is_document_fraud"].mean() * 100,
        2
    ),
    "%"
)

print("\nMissing Values:")
print(
    df.isnull().sum()[
        df.isnull().sum() > 0
    ]
)

print("\nVerification Status Distribution:")
print(
    df["verification_status"]
    .value_counts()
)

print("\nApplication Type Distribution:")
print(
    df["application_type"]
    .value_counts()
)

print("\nMetadata Suspicious Distribution:")
print(
    df["metadata_suspicious"]
    .value_counts()
)

print("\nSample Rows:")
print(df.head())

print("\nNumerical Summary:")
print(df.describe())