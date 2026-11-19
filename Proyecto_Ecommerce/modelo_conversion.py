import gc
import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
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

# ---------------------------------------------------------
# 1. CARGA OPTIMIZADA POR CHUNKS (REDUCCIÓN DE MEMORIA)
# ---------------------------------------------------------
FILE_PATH = "Dataset\\2019-Nov.csv"  # Reemplaza por tu archivo local

print("Iniciando lectura optimizada por lotes...")

# Cargar solo las primeras N filas si deseas una prueba ultra rápida,
# o procesar por lotes si deseas incluir más datos.
# Para este ejemplo procesaremos 10,000,000 de filas que generan ~2M de sesiones.
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

df = pd.read_csv(
    FILE_PATH,
    nrows=N_ROWS,
    dtype=dtype_dict,
)
# 2. Convertimos la columna event_time a datetime de forma explícita
df["event_time"] = pd.to_datetime(df["event_time"], format="%Y-%m-%d %H:%M:%S %Z", errors="coerce")

# Eliminar nulos en la sesión
df = df.dropna(subset=["user_session"])

print(f"Filas cargadas y procesadas: {len(df):,}")

# Eliminar nulos en la sesión
df = df.dropna(subset=["user_session"])

print(f"Filas cargadas y procesadas: {len(df):,}")

# ---------------------------------------------------------
# 2. FEATURE ENGINEERING (SIN LEAKAGE)
# ---------------------------------------------------------
print("Generando variables a nivel de Sesión (sin leakage)...")

# Identificar compra primero
df['is_purchase'] = (df['event_type'] == 'purchase').astype('int8')

# Filtrar eventos de navegación previa (excluyendo la compra misma de los features)
df_nav = df[df['event_type'] != 'purchase'].copy()

# Banderas de navegación
df_nav['is_view'] = (df_nav['event_type'] == 'view').astype('int8')
df_nav['is_cart'] = (df_nav['event_type'] == 'cart').astype('int8')

# Agregación por sesión previa
features = df_nav.groupby('user_session').agg(
    num_events=('event_type', 'count'),
    num_views=('is_view', 'sum'),
    num_cart=('is_cart', 'sum'),
    price_mean=('price', 'mean'),
    price_max=('price', 'max'),
    num_unique_products=('product_id', 'nunique'),
    session_duration_sec=('event_time', lambda x: (x.max() - x.min()).total_seconds())
).reset_index()

# Obtener si la sesión terminó en compra (Target)
targets = df.groupby('user_session')['is_purchase'].max().reset_index().rename(columns={'is_purchase': 'target'})

# Unir features con el target
features = pd.merge(features, targets, on='user_session', how='inner').fillna(0)

# Liberar memoria RAM del dataframe original masivo
del df
gc.collect()

# Rellenar valores nulos residuales
features = features.fillna(0)

print(f"Total de sesiones extraídas: {len(features):,}")
print("Distribución de la Variable Objetivo (Conversión):")
print(features["target"].value_counts(normalize=True))

# ---------------------------------------------------------
# 3. PREPARACIÓN DE DATOS Y SAMPLING PARA MODELADO
# ---------------------------------------------------------
# Si hay demasiadas sesiones, tomamos un subconjunto representativo balanceado
# para entrenar los modelos eficientemente
X = features.drop(columns=["user_session", "target"])
y = features["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Escalamiento de características para la Red Neuronal (MLP)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---------------------------------------------------------
# 4. ENTRENAMIENTO Y EVALUACIÓN DE LOS 4 ALGORITMOS
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

print("\n============================================================")
print("ENTRENANDO MODELOS Y EVALUANDO MÉTRICAS")
print("============================================================")

for name, model in models.items():
    print(f"Entrenando {name}...")

    if name == "MLP (Red Neuronal)":
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

    # Cálculo de las 4 métricas obligatorias
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
        }
    )

# Mostrar resultados tabulados
df_results = pd.DataFrame(results)
print("\n=== TABLA COMPARATIVA DE RENDIMIENTO ===")
print(df_results.to_string(index=False))

# ---------------------------------------------------------
# 5. INTERPRETABILIDAD CON SHAP
# ---------------------------------------------------------
print("\nCalculando valores SHAP con el modelo de mejor desempeño (LightGBM)...")

best_model = models["LightGBM"]
explainer = shap.TreeExplainer(best_model)

# Muestra de prueba para SHAP (1000 instancias para velocidad)
X_test_sample = X_test.sample(n=1000, random_state=42)
shap_values = explainer(X_test_sample)

# Gráfico 1: Importancia global de características
plt.figure(figsize=(10, 6))
shap.plots.bar(shap_values, show=False)
plt.title("Importancia Global de Variables (SHAP Bar Plot)")
plt.tight_layout()
plt.show()

# Gráfico 2: Impacto directo en la conversión
plt.figure(figsize=(10, 6))
shap.plots.beeswarm(shap_values, show=False)
plt.title("Distribución del Impacto de cada Variable en la Conversión (SHAP Beeswarm)")
plt.tight_layout()
plt.show()