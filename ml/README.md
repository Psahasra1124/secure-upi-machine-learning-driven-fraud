# Dataset and training

The trainer accepts either:

1. A UPI-style CSV with `amount`, `hour`, `day_of_week`,
   `transaction_frequency`, `merchant_category`, `device_type`, `location`,
   and binary `is_fraud` columns.
2. The public ULB/Kaggle Credit Card Fraud Detection `creditcard.csv`, with
   `Time`, `Amount`, and `Class` columns. The adapter derives time fields and
   adds reproducible contextual categories so the resulting artifact matches
   the real-time API contract. The anonymized `V1`-`V28` values are not sent by
   the product API and therefore are not model inputs.

For a quick local demonstration:

```bash
cd ml
python generate_sample_data.py
python train.py --data data/sample_upi_transactions.csv
```

For the public dataset, download `creditcard.csv` from the Kaggle
"Credit Card Fraud Detection" dataset, place it in `ml/data/`, and run:

```bash
python train.py --data data/creditcard.csv
```

Model selection uses average precision, which is more informative than raw
accuracy for severely imbalanced fraud data. SMOTE is applied only to the
training split, after preprocessing, to prevent test-set leakage.
