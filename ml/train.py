import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

NUMERIC = ["amount", "hour", "day_of_week", "transaction_frequency"]
CATEGORICAL = ["merchant_category", "device_type", "location"]
TARGET = "is_fraud"


def adapt_public_credit_card_dataset(frame: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Adapt Kaggle/ULB creditcard.csv to the contextual API feature contract."""
    if {"Time", "Amount", "Class"}.issubset(frame.columns):
        rng = np.random.default_rng(seed)
        adapted = pd.DataFrame(
            {
                "amount": frame["Amount"].astype(float),
                "hour": ((frame["Time"] // 3600) % 24).astype(int),
                "day_of_week": ((frame["Time"] // 86400) % 7).astype(int),
                "transaction_frequency": np.clip(
                    np.abs(frame.get("V1", 0)).astype(float).round().astype(int) + 1, 0, 50
                ),
                "merchant_category": rng.choice(
                    ["grocery", "utilities", "food", "travel", "shopping", "gaming"],
                    len(frame),
                ),
                "device_type": rng.choice(["android", "ios", "web"], len(frame)),
                "location": rng.choice(
                    ["Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad"], len(frame)
                ),
                TARGET: frame["Class"].astype(int),
            }
        )
        return adapted
    aliases = {"class": TARGET, "fraud": TARGET, "label": TARGET}
    frame = frame.rename(columns={name: aliases.get(name.lower(), name) for name in frame.columns})
    missing = set(NUMERIC + CATEGORICAL + [TARGET]) - set(frame.columns)
    if missing:
        raise ValueError(
            "Dataset is missing columns: "
            + ", ".join(sorted(missing))
            + ". See ml/README.md for the accepted schema."
        )
    return frame[NUMERIC + CATEGORICAL + [TARGET]].copy()


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    return ColumnTransformer(
        [("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)]
    )


def metrics_for(model, x_test, y_test, threshold: float = 0.5) -> dict:
    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)
    return {
        "roc_auc": round(roc_auc_score(y_test, probabilities), 6),
        "average_precision": round(average_precision_score(y_test, probabilities), 6),
        "precision": round(precision_score(y_test, predictions, zero_division=0), 6),
        "recall": round(recall_score(y_test, predictions, zero_division=0), 6),
        "f1": round(f1_score(y_test, predictions, zero_division=0), 6),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "classification_report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
    }


def main(args) -> None:
    frame = adapt_public_credit_card_dataset(pd.read_csv(args.data), args.seed)
    x = frame[NUMERIC + CATEGORICAL]
    y = frame[TARGET].astype(int)
    if y.nunique() != 2:
        raise ValueError("Target must contain both legitimate (0) and fraud (1) samples")

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )
    preprocessor = build_preprocessor()
    x_train_transformed = preprocessor.fit_transform(x_train)
    x_test_transformed = preprocessor.transform(x_test)

    minority_count = int(y_train.value_counts().min())
    if minority_count < 2:
        raise ValueError("At least two fraud samples are required for SMOTE")
    smote = SMOTE(random_state=args.seed, k_neighbors=min(5, minority_count - 1))
    x_balanced, y_balanced = smote.fit_resample(x_train_transformed, y_train)

    models = {
        "logistic_regression": LogisticRegression(max_iter=1500, random_state=args.seed),
        "random_forest": RandomForestClassifier(
            n_estimators=350,
            max_depth=18,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=args.seed,
            class_weight="balanced_subsample",
        ),
        "xgboost": XGBClassifier(
            n_estimators=350,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="binary:logistic",
            eval_metric="aucpr",
            n_jobs=-1,
            random_state=args.seed,
        ),
    }

    results = {}
    trained = {}
    for name, model in models.items():
        model.fit(x_balanced, y_balanced)
        trained[name] = model
        results[name] = metrics_for(model, x_test_transformed, y_test, args.threshold)
        print(
            f"{name}: AP={results[name]['average_precision']:.4f} "
            f"ROC-AUC={results[name]['roc_auc']:.4f} F1={results[name]['f1']:.4f}"
        )

    best_name = max(results, key=lambda name: results[name]["average_precision"])
    best_model = trained[best_name]
    feature_names = preprocessor.get_feature_names_out().tolist()
    model_version = f"{best_name}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    artifact = {
        "preprocessor": preprocessor,
        "model": best_model,
        "threshold": args.threshold,
        "feature_names": feature_names,
        "model_version": model_version,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, args.output)

    metadata = {
        "model_version": model_version,
        "selected_model": best_name,
        "selection_metric": "average_precision",
        "trained_at": datetime.now(UTC).isoformat(),
        "training_rows": len(x_train),
        "test_rows": len(x_test),
        "original_fraud_rate": float(y.mean()),
        "threshold": args.threshold,
        "features": NUMERIC + CATEGORICAL,
        "results": results,
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved best model ({best_name}) to {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and compare Secure UPI fraud models")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/fraud_model.joblib")
    )
    parser.add_argument(
        "--metadata", type=Path, default=Path("artifacts/model_metadata.json")
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    main(parser.parse_args())
