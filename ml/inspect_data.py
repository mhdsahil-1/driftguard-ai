
from pathlib import Path

import pandas as pd

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "PS_20174392719_1491204439457_log.csv"
)


def main():
    if not DATA_FILE.exists():
        print(f"Dataset not found: {DATA_FILE}")
        print("Download the PaySim CSV and place it in the data folder.")
        return

    df = pd.read_csv(DATA_FILE, nrows=20_000)

    print("\n--- DATASET PREVIEW ---")
    print(df.head())

    print("\n--- SHAPE (ROWS LOADED, COLUMNS) ---")
    print(df.shape)

    print("\n--- COLUMN NAMES ---")
    print(df.columns.tolist())

    print("\n--- DATA TYPES ---")
    print(df.dtypes)

    print("\n--- MISSING VALUES ---")
    print(df.isna().sum())

    if "isFraud" in df.columns:
        print("\n--- FRAUD LABEL COUNTS ---")
        print(df["isFraud"].value_counts(dropna=False))


if __name__ == "__main__":
    main()

