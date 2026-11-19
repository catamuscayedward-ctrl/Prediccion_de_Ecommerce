# Dashboard — Predicción de Conversión en E-commerce

Aplicación web de **despliegue** (fase 6 de CRISP-DM) del proyecto de grado.

## Requisitos

- Python 3.10+
- Dataset `2019-Nov.csv` en `../Dataset/`
- Modelo entrenado (`mejor_modelo.joblib`, `scaler.joblib`, `feature_names.joblib`)
  en la carpeta raíz del proyecto.

## Pasos

### 1. Entrenar y exportar el modelo

Desde la carpeta `Proyecto_Ecommerce/`:

```bash
python 03_ejecucion_modelos.py
```

Esto entrena los 4 modelos (Random Forest, XGBoost, LightGBM y MLP), guarda la
tabla de resultados (`resultados_modelos.csv`), las figuras SHAP en `imagenes/` y
exporta el mejor modelo para el despliegue.

### 2. Instalar dependencias

```bash
cd dashboard
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```bash
streamlit run app.py
```

Se abrirá en `http://localhost:8501`.

## Despliegue en la nube (Streamlit Community Cloud)

1. Sube el proyecto a un repositorio de GitHub (incluye el `.joblib` del modelo y
   el dataset, o usa un subconjunto).
2. En [share.streamlit.io](https://share.streamlit.io) elige el repositorio y como
   archivo principal `dashboard/app.py`.
3. Publica la app. Streamlit instalará `requirements.txt` automáticamente.

> Nota: el dataset completo pesa ~8.5 GB; para la demo del dashboard solo se lee
> una muestra de 300 000 filas, así que puedes subir únicamente esa porción.
