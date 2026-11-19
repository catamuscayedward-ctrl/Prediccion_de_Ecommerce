# Predicción Inteligente de Conversión en E-commerce

Proyecto de grado basado en **Minería de Datos** (metodología **CRISP-DM**) que aplica
técnicas de **Machine Learning** y **Deep Learning** para predecir la probabilidad de
conversión (compra) de los usuarios de una tienda en línea multicategoría.

- **Dataset:** *E-Commerce Behavior Data from Multi Category Store* (noviembre de 2019, Kaggle).
- **Volumen:** 67,501,979 interacciones · 3,696,117 usuarios · 13,776,050 sesiones (~8.5 GB).
- **Modelos:** Random Forest, XGBoost, LightGBM y Red Neuronal (MLP).
- **Resultado:** **XGBoost** obtuvo el mejor desempeño (F1 = 0.3585, ROC-AUC = 0.8388).

---

## Estructura del proyecto

```
Trabajo_de_Grado/
├── Proyecto_Ecommerce/
│   ├── Dataset/
│   │   └── 2019-Nov.csv               # Dataset (8.5 GB)
│   ├── 01_exploracion.py              # Análisis exploratorio inicial
│   ├── 02_limpieza_verificacion.py    # Verificación de calidad/limpieza (por lotes)
│   ├── 03_ejecucion_modelos.py        # Entrena los 4 modelos y exporta resultados
│   ├── modelo_conversion.py           # Script original de modelado
│   ├── generar_docx.py                # Genera el .docx con las secciones de la tesis
│   ├── resultados_modelos.csv/.txt    # Tabla de métricas de los 4 modelos
│   ├── mejor_modelo.joblib            # Mejor modelo entrenado (para el dashboard)
│   ├── scaler.joblib                  # Escalador ajustado
│   ├── feature_names.joblib           # Orden de las variables del modelo
│   └── dashboard/
│       ├── app.py                     # Aplicación web Streamlit (despliegue)
│       ├── requirements.txt
│       └── README.md
├── articulos/                         # Artículos de referencia (PDFs)
├── imagenes/                          # Figuras (CRISP-DM, distribución, SHAP)
├── Secciones_faltantes_tesis.md       # Borrador de secciones (Markdown)
├── Secciones_faltantes_tesis.docx     # Borrador de secciones (Word)
├── trabajo.docx                       # Documento de trabajo del estudiante
└── 7_Edward_David_Catam_VC_CM.docx    # Documento corregido por el profesor
```

---

## Flujo de trabajo (CRISP-DM)

1. **Comprensión del negocio** — predecir la conversión para orientar decisiones de marketing.
2. **Comprensión de los datos** — `01_exploracion.py`.
3. **Preparación de los datos** — `02_limpieza_verificacion.py` + *feature engineering* a nivel de sesión.
4. **Modelado** — `03_ejecucion_modelos.py` (Random Forest, XGBoost, LightGBM, MLP).
5. **Evaluación** — Accuracy, Precision, Recall, F1 y ROC-AUC + interpretabilidad SHAP.
6. **Despliegue** — `dashboard/app.py`.

---

## Requisitos

- Python 3.10+ (probado en 3.13).
- El dataset `2019-Nov.csv` debe estar en `Proyecto_Ecommerce/Dataset/`.

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

---

## Uso

### 1. Verificar la limpieza del dataset

```bash
cd Proyecto_Ecommerce
python 02_limpieza_verificacion.py
```

Procesa los 67.5M de filas por lotes y reporta nulos, tipos de evento, precios
anómalos, rango de fechas y unicidad. Tarda ~25 minutos.

### 2. Entrenar los 4 modelos

```bash
cd Proyecto_Ecommerce
python 03_ejecucion_modelos.py
```

Lee 10M de filas (~2.19M de sesiones), entrena los 4 modelos y genera:
- `resultados_modelos.csv/.txt` — tabla de métricas.
- `mejor_modelo.joblib`, `scaler.joblib`, `feature_names.joblib` — artefactos para el despliegue.
- `../imagenes/SHAP_bar.png` y `../imagenes/SHAP_beeswarm.png` — figuras de interpretabilidad.

> El MLP (red neuronal) es el paso más lento (~11 min). El total ronda ~15–20 min.

### 3. Ejecutar el dashboard (despliegue)

```bash
cd Proyecto_Ecommerce/dashboard
streamlit run app.py
```

Abre la app en `http://localhost:8501` con dashboard de comportamiento y
predicción de conversión. Ver `Proyecto_Ecommerce/dashboard/README.md` para
instrucciones de despliegue en la nube.

---

## Resultados

| Algoritmo | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Tiempo (s) |
|---|---|---|---|---|---|---|
| Random Forest | 0.9476 | 0.6183 | 0.2455 | 0.3514 | 0.8295 | 260.3 |
| **XGBoost** | **0.9478** | 0.6181 | 0.2525 | **0.3585** | **0.8388** | 47.8 |
| LightGBM | 0.9476 | 0.6145 | 0.2509 | 0.3563 | 0.8383 | 27.7 |
| MLP (Red Neuronal) | 0.9474 | 0.6205 | 0.2320 | 0.3377 | 0.8345 | 661.8 |

**Nota:** la exactitud (~0.947) es engañosa por el desequilibrio de clases
(94.2 % de sesiones sin compra). Las métricas relevantes son F1 y ROC-AUC, donde
**XGBoost** es el mejor modelo.

**Interpretabilidad (SHAP):** la variable `num_cart` (productos añadidos al carrito)
concentra ~82 % de la importancia — clave para estrategias de recuperación de carritos.
