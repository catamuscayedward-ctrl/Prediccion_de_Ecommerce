# Despliegue en la nube (Streamlit Community Cloud)

La app ya fue **verificada localmente** (dashboard + predicción funcionando).
Para publicarla en línea solo faltan 2 pasos manuales (requieren tu cuenta de GitHub).

## Lo que ya está listo

- ✅ Repositorio git creado y con el primer commit (rama `master`).
- ✅ `.gitignore` que excluye el CSV completo (8.5 GB), el `.zip` y los PDFs.
- ✅ Muestra compacta del dataset: `Proyecto_Ecommerce/Dataset/2019-Nov-sample.csv` (40 MB).
- ✅ Modelo entrenado exportado: `mejor_modelo.joblib` (428 KB) + `scaler` + variables.
- ✅ `dashboard/app.py` lee la muestra si el archivo completo no está presente (portátil).
- ✅ `requirements.txt` con todas las dependencias.

## Paso 1 — Crear el repositorio en GitHub

1. Entra a https://github.com y crea un repositorio **nuevo y vacío** (sin README),
   por ejemplo `ecommerce-conversion`.
2. Copia la URL del repositorio (https://github.com/TU_USUARIO/ecommerce-conversion.git).

## Paso 2 — Subir el proyecto

Desde la carpeta raíz del proyecto, ejecuta:

```bash
git remote add origin https://github.com/TU_USUARIO/ecommerce-conversion.git
git branch -M main
git push -u origin main
```

## Paso 3 — Publicar en Streamlit Cloud

1. Entra a https://share.streamlit.io y entra con tu cuenta de GitHub.
2. Click en **"New app"** (o **"Create app"**).
3. Elige:
   - **Repository:** `ecommerce-conversion`
   - **Branch:** `main`
   - **Main file path:** `Proyecto_Ecommerce/dashboard/app.py`
4. Click **Deploy**. Streamlit instala `requirements.txt` automáticamente.

En unos minutos tendrás una URL pública (https://tu-app.streamlit.app) con el
dashboard y la predicción de conversión.

> **Nota:** el dashboard usa la muestra de 300,000 interacciones (suficiente para
> las gráficas de comportamiento). La predicción usa el modelo entrenado completo,
> así que da los mismos resultados que en local.

---

## Probar localmente (opcional, ya verificado)

```bash
cd Proyecto_Ecommerce/dashboard
pip install -r requirements.txt
streamlit run app.py
```
