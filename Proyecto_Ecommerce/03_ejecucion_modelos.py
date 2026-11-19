# -*- coding: utf-8 -*-
"""
Ejecución de los 4 modelos de clasificación (mismo enfoque de modelo_conversion.py)
con 10,000,000 de filas. Guarda los resultados en un .csv/.txt y las figuras SHAP
en la carpeta imagenes/, para usarlas en el documento de la tesis.
"""
import gc
import time
import warnings
import os
import joblib

import matplotlib
matplotlib.use("Agg")  # sin GUI, para guardar figuras en disco
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(os.path.dirname(BASE), "imagenes")
os.makedirs(IMG_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. CARGA (10,000,000 filas, ~2M sesiones)
# ---------------------------------------------------------
FILE_PATH = os.path.join(BASE, "Dataset", "2019-Nov.csv")
N_ROWS = 10_000_000

dtype_dict = {
    "event_type": "category",
    "product_id": "int32",
    "category_id": "int64",
    "category_code": "category",
    "brand": "category",
    "price": "float32",
    "user_id": "int32",
    "user_session": "str",
}

print("Leyendo 10,000,000 de filas...", flush=True)
t0 = time.time()
df = pd.read_csv(FILE_PATH, nrows=N_ROWS, dtype=dtype_dict)
df["event_time"] = pd.to_datetime(
    df["event_time"], format="%Y-%m-%d %H:%M:%S %Z", errors="coerce"
)
df = df.dropna(subset=["user_session"])
print(f"Filas cargadas: {len(df):,}  ({time.time()-t0:.1f}s)", flush=True)

# ---------------------------------------------------------
# 2. FEATURE ENGINEERING (SIN LEAKAGE)
# ---------------------------------------------------------
df["is_purchase"] = (df["event_type"] == "purchase").astype("int8")
df_nav = df[df["event_type"] != "purchase"].copy()
df_nav["is_view"] = (df_nav["event_type"] == "view").astype("int8")
df_nav["is_cart"] = (df_nav["event_type"] == "cart").astype("int8")

features = df_nav.groupby("user_session").agg(
    num_events=("event_type", "count"),
    num_views=("is_view", "sum"),
    num_cart=("is_cart", "sum"),
    price_mean=("price", "mean"),
    price_max=("price", "max"),
    num_unique_products=("product_id", "nunique"),
    session_duration_sec=("event_time", lambda x: (x.max() - x.min()).total_seconds()),
).reset_index()

targets = (
    df.groupby("user_session")["is_purchase"]
    .max()
    .reset_index()
    .rename(columns={"is_purchase": "target"})
)
features = pd.merge(features, targets, on="user_session", how="inner").fillna(0)
del df
gc.collect()
features = features.fillna(0)

print(f"Sesiones extraídas: {len(features):,}", flush=True)
print("Distribución del target (conversión):", flush=True)
print(features["target"].value_counts(normalize=True), flush=True)

# ---------------------------------------------------------
# 3. SPLIT Y ESCALADO
# ---------------------------------------------------------
X = features.drop(columns=["user_session", "target"])
y = features["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---------------------------------------------------------
# 4. MODELOS
# ---------------------------------------------------------
models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
    ),
    "XGBoost": XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss",
        n_jobs=-1,
    ),
    "LightGBM": LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        verbose=-1,
        n_jobs=-1,
    ),
    "MLP (Red Neuronal)": MLPClassifier(
        hidden_layer_sizes=(64, 32), max_iter=150, random_state=42
    ),
}

results = []
trained = {}

for name, model in models.items():
    print(f"\nEntrenando {name}...", flush=True)
    ts = time.time()
    if name == "MLP (Red Neuronal)":
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
    train_time = time.time() - ts
    trained[name] = model

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_proba)

    results.append(
        {
            "Algoritmo": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1-Score": round(f1, 4),
            "ROC-AUC": round(roc_auc, 4),
            "Tiempo_entrenamiento_s": round(train_time, 1),
        }
    )
    print(f"  {name}: Acc={acc:.4f} Prec={prec:.4f} Rec={rec:.4f} "
          f"F1={f1:.4f} AUC={roc_auc:.4f} ({train_time:.1f}s)", flush=True)

df_results = pd.DataFrame(results)
print("\n=== TABLA COMPARATIVA ===")
print(df_results.to_string(index=False))

out_csv = os.path.join(BASE, "resultados_modelos.csv")
out_txt = os.path.join(BASE, "resultados_modelos.txt")
df_results.to_csv(out_csv, index=False)
with open(out_txt, "w", encoding="utf-8") as fh:
    fh.write("RESULTADOS DE LOS 4 MODELOS (10M filas)\n")
    fh.write(df_results.to_string(index=False))
    fh.write("\n\nDistribución del target:\n")
    fh.write(features["target"].value_counts(normalize=True).to_string())
print(f"\nResultados guardados en: {out_csv} y {out_txt}", flush=True)

# ---------------------------------------------------------
# 5. SHAP (mejor modelo por ROC-AUC)
# ---------------------------------------------------------
best_name = df_results.sort_values("ROC-AUC", ascending=False).iloc[0]["Algoritmo"]
best_model = trained[best_name]
print(f"\nModelo con mejor ROC-AUC: {best_name}. Calculando SHAP...", flush=True)

# Guardar el mejor modelo + escalador + nombres de variables para el despliegue
modelo_path = os.path.join(BASE, "mejor_modelo.joblib")
scaler_path = os.path.join(BASE, "scaler.joblib")
features_path = os.path.join(BASE, "feature_names.joblib")
joblib.dump(best_model, modelo_path)
joblib.dump(scaler, scaler_path)
joblib.dump(list(X.columns), features_path)
print(f"Modelo guardado en: {modelo_path}", flush=True)

explainer = shap.TreeExplainer(best_model)
X_test_sample = X_test.sample(n=1000, random_state=42)
shap_values = explainer(X_test_sample)

plt.figure(figsize=(10, 6))
shap.plots.bar(shap_values, show=False)
plt.title("Importancia Global de Variables (SHAP Bar Plot)")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "SHAP_bar.png"), dpi=150, bbox_inches="tight")
plt.close()

plt.figure(figsize=(10, 6))
shap.plots.beeswarm(shap_values, show=False)
plt.title("Impacto de cada Variable en la Conversión (SHAP Beeswarm)")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "SHAP_beeswarm.png"), dpi=150, bbox_inches="tight")
plt.close()

print("Figuras SHAP guardadas en", IMG_DIR, flush=True)
print("\nDONE", flush=True)
