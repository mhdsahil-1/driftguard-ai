
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "PS_20174392719_1491204439457_log.csv"

df = pd.read_csv(DATA_FILE)

# Sort transactions chronologically.
df = df.sort_values("step").reset_index(drop=True)

# Inspect the available time range.
print("Total transactions:", len(df))
print("First step:", df["step"].min())
print("Last step:", df["step"].max())
print("Unique time steps:", df["step"].nunique())

# Split by chronological row position.
n = len(df)
train_end = int(n * 0.70)
val_end = int(n * 0.85)

train = df.iloc[:train_end].copy()
validation = df.iloc[train_end:val_end].copy()
test = df.iloc[val_end:].copy()

# Save each split for the next stage.
output_dir = BASE_DIR / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

train.to_csv(output_dir / "train.csv", index=False)
validation.to_csv(output_dir / "validation.csv", index=False)
test.to_csv(output_dir / "test.csv", index=False)

for name, part in [
    ("Train", train),
    ("Validation", validation),
    ("Test", test),
]:
    print(f"\n{name}: {len(part)} transactions")
    print("Fraud cases:", int(part["isFraud"].sum()))
    print("Fraud rate:", round(part["isFraud"].mean() * 100, 4), "%")
    print("Steps:", part["step"].min(), "to", part["step"].max())

print("\nChronological splits saved successfully.")

