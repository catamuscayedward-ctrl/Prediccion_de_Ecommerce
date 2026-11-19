# -*- coding: utf-8 -*-
"""
Aplicación web de despliegue — Predicción Inteligente de Conversión en E-commerce.
Proyecto #13 (Minería de Datos / CRISP-DM - Fase de Despliegue).

Ejecutar con:  streamlit run app.py
"""
import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Predicción de Conversión E-commerce", layout="wide")

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
CSV_PATH = os.path.join(ROOT, "Dataset", "2019-Nov.csv")
SAMPLE_CSV_PATH = os.path.join(ROOT, "Dataset", "2019-Nov-sample.csv")

MODEL_PATH = os.path.join(ROOT, "mejor_modelo.joblib")
SCALER_PATH = os.path.join(ROOT, "scaler.joblib")
FEATURES_PATH = os.path.join(ROOT, "feature_names.joblib")

FEATURES_ORDER = [
    "num_events",
    "num_views",
    "num_cart",
    "price_mean",
    "price_max",
    "num_unique_products",
    "session_duration_sec",
]

FEATURE_LABELS = {
    "num_events": "Número de eventos en la sesión",
    "num_views": "Número de vistas (view)",
    "num_cart": "Número de productos añadidos al carrito",
    "price_mean": "Precio promedio de los productos vistos",
    "price_max": "Precio máximo visto",
    "num_unique_products": "Productos únicos vistos",
    "session_duration_sec": "Duración de la sesión (segundos)",
}


@st.cache_resource(show_spinner=False)
def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        return None, None, None
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH) if os.path.exists(SCALER_PATH) else None
    feats = joblib.load(FEATURES_PATH) if os.path.exists(FEATURES_PATH) else FEATURES_ORDER
    return model, scaler, feats


@st.cache_data(show_spinner=False)
def cargar_muestra(nrows=300_000):
    path = SAMPLE_CSV_PATH if os.path.exists(SAMPLE_CSV_PATH) else CSV_PATH
    if not os.path.exists(path):
        return None
    df = pd.read_csv(
        path,
        nrows=nrows,
        dtype={
            "event_type": "category",
            "category_code": "category",
            "brand": "category",
            "price": "float32",
        },
    )
    return df


def main():
    st.title("🛒 Predicción Inteligente de Conversión en E-commerce")
    st.caption(
        "Sistema predictivo basado en Machine Learning y Deep Learning para estimar "
        "la probabilidad de conversión de usuarios en una tienda en línea multicategoría."
    )

    menu = st.sidebar.radio(
        "Navegación",
        ["🏠 Inicio", "📊 Dashboard de comportamiento", "🎯 Predicción de conversión"],
    )

    if menu == "🏠 Inicio":
        inicio()
    elif menu == "📊 Dashboard de comportamiento":
        dashboard()
    else:
        prediccion()


def inicio():
    st.header("Bienvenida")
    st.markdown(
        """
Este sistema corresponde a la **fase de Despliegue** de la metodología CRISP-DM del
proyecto *"Predicción Inteligente de Conversión en E-commerce"*.

**Objetivo:** predecir la probabilidad de que un usuario realice una compra
(conversión) a partir de su comportamiento de navegación.

**Dataset:** *E-Commerce Behavior Data from Multi Category Store* (noviembre de 2019),
con 67,501,979 interacciones.

**Modelos evaluados:** Random Forest, XGBoost, LightGBM y Red Neuronal (MLP).

**Métricas:** Accuracy, Precision, Recall, F1-Score y ROC-AUC, con interpretabilidad SHAP.

Utilice el menú lateral para explorar el comportamiento de los usuarios o para
realizar una predicción con una sesión nueva.
        """
    )
    st.info(
        "Si los artefactos del modelo no están cargados, ejecute primero "
        "`python 03_ejecucion_modelos.py` en la carpeta del proyecto."
    )


def dashboard():
    st.header("Dashboard de comportamiento de usuarios")
    df = cargar_muestra()
    if df is None:
        st.error("No se encontró el dataset. Verifique la ruta del archivo CSV.")
        return

    st.markdown(f"Análisis sobre una muestra de **{len(df):,}** interacciones.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribución de tipos de evento")
        vc = df["event_type"].value_counts()
        fig, ax = plt.subplots()
        ax.bar(vc.index.astype(str), vc.values, color=["#4C72B0", "#DD8452", "#55A868"])
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.subheader("Embudo de conversión")
        views = int((df["event_type"] == "view").sum())
        carts = int((df["event_type"] == "cart").sum())
        purchases = int((df["event_type"] == "purchase").sum())
        fig, ax = plt.subplots()
        stages = ["Vistas (view)", "Carrito (cart)", "Compra (purchase)"]
        vals = [views, carts, purchases]
        ax.barh(stages, vals, color=["#4C72B0", "#DD8452", "#55A868"])
        ax.set_xlabel("Cantidad")
        for i, v in enumerate(vals):
            ax.text(v, i, f" {v:,}", va="center")
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Categorías más visitadas (top 10)")
    top_cat = df["category_code"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top_cat.index.astype(str)[::-1], top_cat.values[::-1])
    ax.set_xlabel("Vistas")
    st.pyplot(fig)
    plt.close(fig)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Marcas más vistas (top 10)")
        top_brand = df["brand"].value_counts().head(10)
        fig, ax = plt.subplots()
        ax.barh(top_brand.index.astype(str)[::-1], top_brand.values[::-1])
        ax.set_xlabel("Vistas")
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        st.subheader("Distribución de precios")
        fig, ax = plt.subplots()
        ax.hist(df["price"].dropna().clip(0, 1000), bins=40, color="#4C72B0")
        ax.set_xlabel("Precio (USD)")
        ax.set_ylabel("Frecuencia")
        st.pyplot(fig)
        plt.close(fig)


def prediccion():
    st.header("Predicción de conversión")
    model, scaler, feats = cargar_modelo()

    if model is None:
        st.error(
            "No se encontró el modelo entrenado (`mejor_modelo.joblib`). "
            "Ejecute primero `python 03_ejecucion_modelos.py`."
        )
        return

    st.markdown(
        "Ingrese las características de la sesión de navegación para estimar la "
        "probabilidad de que el usuario realice una compra."
    )

    with st.form("form_pred"):
        c1, c2, c3 = st.columns(3)
        with c1:
            num_events = st.number_input(FEATURE_LABELS["num_events"], 1, 10_000, 20)
            num_views = st.number_input(FEATURE_LABELS["num_views"], 0, 10_000, 15)
            num_cart = st.number_input(FEATURE_LABELS["num_cart"], 0, 100, 1)
        with c2:
            price_mean = st.number_input(FEATURE_LABELS["price_mean"], 0.0, 10_000.0, 100.0)
            price_max = st.number_input(FEATURE_LABELS["price_max"], 0.0, 20_000.0, 200.0)
        with c3:
            num_unique_products = st.number_input(
                FEATURE_LABELS["num_unique_products"], 0, 1_000, 10
            )
            session_duration_sec = st.number_input(
                FEATURE_LABELS["session_duration_sec"], 0.0, 100_000.0, 600.0
            )
        submitted = st.form_submit_button("🔮 Predecir probabilidad de conversión")

    if submitted:
        entrada = pd.DataFrame(
            [[num_events, num_views, num_cart, price_mean, price_max,
              num_unique_products, session_duration_sec]],
            columns=FEATURES_ORDER,
        )
        entrada = entrada[feats]  # respetar el orden de las variables del modelo

        if scaler is not None:
            X = scaler.transform(entrada)
        else:
            X = entrada.values

        try:
            proba = model.predict_proba(X)[0][1]
        except Exception:
            proba = float(model.predict(X)[0])

        pred = "Sí (compra)" if proba >= 0.5 else "No (sin compra)"
        st.success(f"**Probabilidad de conversión: {proba:.1%}**")
        st.metric("Predicción (umbral 0.5)", pred)
        st.progress(min(max(proba, 0.0), 1.0))


if __name__ == "__main__":
    main()
