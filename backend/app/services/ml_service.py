import json
import math
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.core.config import settings

NUMERIC_FEATURES = [
    "amount",
    "hour",
    "day_of_week",
    "transaction_frequency",
]
CATEGORICAL_FEATURES = ["merchant_category", "device_type", "location"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def transaction_to_frame(payload: dict[str, Any]) -> pd.DataFrame:
    transaction_time: datetime = payload["time"]
    return pd.DataFrame(
        [
            {
                "amount": payload["amount"],
                "hour": transaction_time.hour,
                "day_of_week": transaction_time.weekday(),
                "transaction_frequency": payload["transaction_frequency"],
                "merchant_category": payload["merchant_category"].lower(),
                "device_type": payload["device_type"].lower(),
                "location": payload["location"].lower(),
            }
        ],
        columns=FEATURES,
    )


class FraudPredictor:
    def __init__(self) -> None:
        self.preprocessor = None
        self.model = None
        self.explainer = None
        self.feature_names: list[str] = []
        self.threshold = 0.5
        self.model_version = "heuristic-fallback-v1"
        self.metadata: dict[str, Any] = {}
        self._lock = Lock()
        self._load_artifact()

    @property
    def is_trained(self) -> bool:
        return self.model is not None and self.preprocessor is not None

    def _load_artifact(self) -> None:
        model_path = Path(settings.model_path)
        if not model_path.exists():
            return
        artifact = joblib.load(model_path)
        self.preprocessor = artifact["preprocessor"]
        self.model = artifact["model"]
        self.threshold = float(artifact.get("threshold", 0.5))
        self.feature_names = list(artifact.get("feature_names", []))
        self.model_version = artifact.get("model_version", model_path.stem)
        metadata_path = Path(settings.model_metadata_path)
        if metadata_path.exists():
            self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    def reload(self) -> None:
        with self._lock:
            self.preprocessor = None
            self.model = None
            self.explainer = None
            self._load_artifact()

    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        frame = transaction_to_frame(payload)
        if not self.is_trained:
            return self._fallback_predict(frame.iloc[0].to_dict())

        transformed = self.preprocessor.transform(frame)
        probability = float(self.model.predict_proba(transformed)[0, 1])
        explanation = self._explain(transformed, frame.iloc[0].to_dict())
        return {
            "is_fraud": probability >= self.threshold,
            "probability": probability,
            "threshold": self.threshold,
            "explanation": explanation,
            "model_version": self.model_version,
        }

    def _get_explainer(self):
        if self.explainer is not None:
            return self.explainer
        import shap

        model_name = self.model.__class__.__name__.lower()
        if "logistic" in model_name:
            self.explainer = shap.LinearExplainer(self.model, np.zeros((1, len(self.feature_names))))
        else:
            self.explainer = shap.TreeExplainer(self.model)
        return self.explainer

    def _explain(self, transformed: Any, raw: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            explainer = self._get_explainer()
            dense = transformed.toarray() if hasattr(transformed, "toarray") else np.asarray(transformed)
            values = explainer.shap_values(dense)
            if isinstance(values, list):
                values = values[-1]
            values = np.asarray(values)
            if values.ndim == 3:
                values = values[:, :, -1]
            row = values[0]
            names = self.feature_names or [f"feature_{i}" for i in range(len(row))]
            ranked = sorted(zip(names, row), key=lambda item: abs(float(item[1])), reverse=True)[:6]
            return [
                {
                    "feature": self._friendly_feature(name),
                    "impact": round(float(value), 5),
                    "direction": "increases risk" if value > 0 else "decreases risk",
                }
                for name, value in ranked
            ]
        except Exception:
            return self._fallback_explanation(raw)

    @staticmethod
    def _friendly_feature(name: str) -> str:
        cleaned = name.split("__", 1)[-1].replace("_", " ")
        return cleaned.title()

    def _fallback_predict(self, row: dict[str, Any]) -> dict[str, Any]:
        hour = int(row["hour"])
        amount = float(row["amount"])
        frequency = int(row["transaction_frequency"])
        risky_category = row["merchant_category"] in {"gaming", "crypto", "cash withdrawal"}
        new_device = row["device_type"] in {"emulator", "unknown", "rooted"}

        logit = -4.0
        logit += min(amount / 25_000, 2.5)
        logit += min(frequency / 12, 2.0)
        logit += 1.1 if hour < 5 else 0.0
        logit += 1.0 if risky_category else 0.0
        logit += 1.4 if new_device else 0.0
        probability = 1 / (1 + math.exp(-logit))
        return {
            "is_fraud": probability >= 0.5,
            "probability": probability,
            "threshold": 0.5,
            "explanation": self._fallback_explanation(row),
            "model_version": self.model_version,
        }

    @staticmethod
    def _fallback_explanation(row: dict[str, Any]) -> list[dict[str, Any]]:
        impacts = [
            ("Transaction amount", min(float(row["amount"]) / 25_000, 2.5)),
            ("Transaction frequency", min(int(row["transaction_frequency"]) / 12, 2.0)),
            ("Unusual hour", 1.1 if int(row["hour"]) < 5 else -0.25),
            (
                "Merchant category",
                1.0 if row["merchant_category"] in {"gaming", "crypto", "cash withdrawal"} else -0.2,
            ),
            (
                "Device type",
                1.4 if row["device_type"] in {"emulator", "unknown", "rooted"} else -0.3,
            ),
        ]
        return [
            {
                "feature": feature,
                "impact": round(impact, 5),
                "direction": "increases risk" if impact > 0 else "decreases risk",
            }
            for feature, impact in sorted(impacts, key=lambda item: abs(item[1]), reverse=True)
        ]


predictor = FraudPredictor()

