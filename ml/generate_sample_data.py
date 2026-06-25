import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate(rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    categories = np.array(
        ["grocery", "utilities", "food", "travel", "shopping", "gaming", "crypto"]
    )
    devices = np.array(["android", "ios", "web", "emulator", "rooted"])
    locations = np.array(["Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Unknown"])
    frame = pd.DataFrame(
        {
            "amount": np.round(rng.lognormal(mean=7.0, sigma=1.0, size=rows), 2),
            "hour": rng.integers(0, 24, rows),
            "day_of_week": rng.integers(0, 7, rows),
            "transaction_frequency": rng.poisson(4, rows),
            "merchant_category": rng.choice(
                categories, rows, p=[0.25, 0.15, 0.2, 0.1, 0.2, 0.07, 0.03]
            ),
            "device_type": rng.choice(
                devices, rows, p=[0.55, 0.3, 0.1, 0.03, 0.02]
            ),
            "location": rng.choice(
                locations, rows, p=[0.25, 0.2, 0.18, 0.15, 0.17, 0.05]
            ),
        }
    )
    risk = (
        -6.0
        + frame["amount"] / 20_000
        + frame["transaction_frequency"] / 8
        + frame["hour"].isin([0, 1, 2, 3, 4]).astype(float) * 1.4
        + frame["merchant_category"].isin(["gaming", "crypto"]).astype(float) * 1.5
        + frame["device_type"].isin(["emulator", "rooted"]).astype(float) * 2.2
        + frame["location"].eq("Unknown").astype(float) * 1.2
    )
    probability = 1 / (1 + np.exp(-risk.clip(-15, 15)))
    frame["is_fraud"] = rng.binomial(1, probability)
    return frame


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/sample_upi_transactions.csv"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data = generate(args.rows, args.seed)
    data.to_csv(args.output, index=False)
    print(f"Saved {len(data):,} rows to {args.output}; fraud rate={data.is_fraud.mean():.2%}")

