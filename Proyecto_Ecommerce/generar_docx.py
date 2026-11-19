# -*- coding: utf-8 -*-
"""Genera la versión Word (.docx) de las secciones faltantes de la tesis."""
import re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

# Tipografía base
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)


def add_runs(paragraph, text):
    """Añade runs interpretando **negrita**, *cursiva* y `código`."""
    token_re = re.compile(r"(\*\*.*?\*\*|\*.*?\*|`.*?`)")
    for part in token_re.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = paragraph.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = paragraph.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(10)
        elif part.startswith("*") and part.endswith("*"):
            r = paragraph.add_run(part[1:-1])
            r.italic = True
        else:
            paragraph.add_run(part)


def p(text, align=None):
    par = doc.add_paragraph()
    add_runs(par, text)
    if align == "center":
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return par


def h1(text):
    return doc.add_heading(text, level=1)


def h2(text):
    return doc.add_heading(text, level=2)


def h3(text):
    return doc.add_heading(text, level=3)


def bullet(text):
    par = doc.add_paragraph(style="List Bullet")
    add_runs(par, text)
    return par


def caption(text):
    par = doc.add_paragraph()
    add_runs(par, text)
    par.paragraph_format.space_before = Pt(6)
    return par


def add_table(headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, htxt in enumerate(headers):
        hdr[i].text = ""
        run = hdr[i].paragraphs[0].add_run(htxt)
        run.bold = True
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
    return table


# ----------------------------------------------------------------------
# Título y nota
# ----------------------------------------------------------------------
titulo = doc.add_heading("Secciones faltantes de la tesis", level=0)
subt = doc.add_paragraph()
r = subt.add_run(
    "Predicción Inteligente de Conversión en E-commerce — borrador para "
    "copiar/pegar en Word. No se modificó el archivo del profesor."
)
r.italic = True
r.font.size = Pt(10)

# ======================================================================
# PREPARACIÓN Y PREPROCESAMIENTO
# ======================================================================
h1("Preparación y preprocesamiento de los datos")

p("Para garantizar la confiabilidad de los análisis y el desempeño de los modelos, se "
  "aplicó un proceso de limpieza y preparación orientado por las dimensiones de calidad "
  "de datos descritas por Al-Toq y Almaslukh (2025): completitud, consistencia, exactitud "
  "y confiabilidad. Dado el volumen del conjunto de datos (67,501,979 registros, equivalente "
  "a más de 8.5 GB en disco), la lectura y el procesamiento se realizaron por lotes "
  "(*chunks*), lo que permitió verificar la totalidad de los registros sin agotar la memoria "
  "principal de la máquina.")

p("En primer lugar, se verificó la estructura y los tipos de datos de las nueve variables "
  "originales (Tabla 1). La variable `event_time` fue convertida a formato de fecha y hora, "
  "las variables categóricas (`event_type`, `category_code` y `brand`) fueron declaradas "
  "como tal para reducir el consumo de memoria, y las variables numéricas (`price`, "
  "`product_id`, `category_id` y `user_id`) fueron ajustadas a tipos de menor precisión "
  "(`float32` e `int32`) sin pérdida de información.")

p("Posteriormente, se evaluó la completitud del conjunto mediante el conteo de valores "
  "nulos por columna. Se identificó que las variables `category_code` y `brand` presentan "
  "valores ausentes (21,898,171 y 9,224,078 registros, equivalentes al 32.4 % y al 13.7 % "
  "del total, respectivamente), lo cual es esperable porque no todos los productos de la "
  "tienda tienen categoría o marca registrada. La variable `user_session` presentó 10 "
  "registros nulos, los cuales fueron eliminados, ya que sin identificador de sesión no es "
  "posible construir la unidad de análisis del modelo. Las demás variables (`event_time`, "
  "`event_type`, `product_id`, `category_id`, `price` y `user_id`) no presentaron valores "
  "faltantes, lo que evidencia una alta completitud general del conjunto de datos.")

p("En cuanto a la exactitud y consistencia, se validó que la columna `event_type` contuviera "
  "únicamente las tres categorías esperadas —`view`, `cart` y `purchase`— con las siguientes "
  "frecuencias: view 63,556,110, cart 3,028,930 y purchase 916,939 (94.15 %, 4.49 % y "
  "1.36 %, respectivamente). Asimismo, se verificó el rango de fechas, el cual comprende "
  "únicamente el mes de noviembre de 2019 (desde el 1 hasta el 30 de noviembre), en "
  "concordancia con la descripción del repositorio. Respecto a la variable `price`, no se "
  "detectaron precios negativos y se identificaron 188,088 registros con precio igual a cero "
  "(0.28 % del total), mientras que los precios positivos oscilan entre 0.01 y 2,574.07 dólares. "
  "Finalmente, se verificó la unicidad de los identificadores, obteniendo 3,696,117 usuarios "
  "únicos, 13,776,050 sesiones únicas, 190,662 productos únicos, 4,200 marcas únicas y "
  "129 categorías (`category_code`) distintas.")

p("A partir de los datos limpios se construyó la unidad de análisis a nivel de sesión. Para "
  "cada `user_session` se agregaron las interacciones de navegación previas a la compra, "
  "generando las siguientes variables predictoras (Tabla 2): número total de eventos "
  "(`num_events`), número de vistas (`num_views`), número de productos añadidos al carrito "
  "(`num_cart`), precio promedio (`price_mean`), precio máximo (`price_max`), número de "
  "productos únicos (`num_unique_products`) y duración de la sesión en segundos "
  "(`session_duration_sec`). La variable objetivo (`target`) se definió como binaria, "
  "indicando si la sesión finalizó o no en una compra. Es importante señalar que la compra "
  "misma fue excluida de las variables predictoras para evitar fuga de información "
  "(*data leakage*), de modo que el modelo predice la conversión exclusivamente a partir "
  "del comportamiento previo del usuario. La distribución resultante de la variable objetivo "
  "evidencia un desequilibrio de clases característico de este dominio: de las 2,190,404 "
  "sesiones extraídas, el 94.22 % no terminó en compra y el 5.78 % sí lo hizo.")

caption("**Tabla 2. Variables derivadas a nivel de sesión (feature engineering).**")
add_table(
    ["Variable", "Tipo", "Descripción"],
    [
        ["num_events", "Numérica", "Cantidad total de eventos de navegación en la sesión"],
        ["num_views", "Numérica", "Cantidad de vistas de producto (view)"],
        ["num_cart", "Numérica", "Cantidad de productos añadidos al carrito (cart)"],
        ["price_mean", "Numérica", "Precio promedio de los productos vistos"],
        ["price_max", "Numérica", "Precio máximo de los productos vistos"],
        ["num_unique_products", "Numérica", "Cantidad de productos distintos vistos"],
        ["session_duration_sec", "Numérica", "Duración de la sesión en segundos"],
        ["target", "Binaria", "1 si la sesión terminó en compra, 0 en caso contrario"],
    ],
)
p("Fuente: elaboración propia.")

p("Finalmente, el conjunto de sesiones fue dividido en entrenamiento (80 %) y prueba "
  "(20 %) mediante un muestreo estratificado que preserva la proporción de la variable "
  "objetivo en ambos subconjuntos. Las variables numéricas fueron estandarizadas "
  "(media 0 y desviación estándar 1) mediante `StandardScaler`, ajustado únicamente sobre "
  "el conjunto de entrenamiento, dado que este es un requisito para el correcto "
  "entrenamiento de la red neuronal (MLP).")

# ======================================================================
# TÉCNICAS DE ANÁLISIS Y MINERÍA DE DATOS
# ======================================================================
h1("Técnicas de análisis y minería de datos")

p("Para predecir la conversión de los usuarios se seleccionaron cuatro algoritmos de "
  "clasificación supervisada que representan las principales familias de técnicas de "
  "aprendizaje automático y aprendizaje profundo exigidas en el planteamiento del proyecto:")

bullet("**Random Forest (bagging):** ensamble de múltiples árboles de decisión entrenados "
       "sobre subconjuntos aleatorios de datos y de características, cuyas predicciones se "
       "combinan por votación para reducir la varianza y el sobreajuste (Breiman, 2001).")
bullet("**XGBoost (boosting):** algoritmo de *gradient boosting* optimizado que construye "
       "árboles de forma secuencial, corrigiendo los errores de los árboles anteriores y "
       "minimizando una función objetivo con término de regularización (Chen & Guestrin, 2016).")
bullet("**LightGBM (boosting):** implementación de *gradient boosting* basada en histogramas "
       "y crecimiento de árboles por hojas (*leaf-wise*), diseñada para alta velocidad y "
       "eficiencia en conjuntos de datos grandes (Ke et al., 2017).")
bullet("**Red Neuronal Artificial (MLP):** perceptrón multicapa con dos capas ocultas "
       "(64 y 32 neuronas), que aprende representaciones no lineales de las variables mediante "
       "retropropagación del error, representando la componente de *Deep Learning* del proyecto.")

p("Los modelos fueron configurados con hiperparámetros equivalentes en términos de "
  "capacidad (100 estimadores, profundidad máxima 6–10 y tasa de aprendizaje 0.1 para "
  "los métodos de ensamble), lo que permite una comparación justa entre algoritmos. "
  "Para todos ellos se utilizó una semilla aleatoria fija (`random_state=42`) con el fin de "
  "garantizar la reproducibilidad de los resultados.")

p("La evaluación del desempeño se realizó sobre el conjunto de prueba mediante cinco "
  "métricas: exactitud (*accuracy*), precisión (*precision*), sensibilidad (*recall*), medida F1 "
  "(*F1-score*) y área bajo la curva ROC (*ROC-AUC*). Dado el desequilibrio de clases del "
  "problema, la exactitud por sí sola resulta insuficiente para discriminar el mejor modelo, "
  "por lo que se dio mayor peso a la medida F1 y al ROC-AUC, que consideran de forma "
  "conjunta los falsos positivos y los falsos negativos.")

p("Adicionalmente, se aplicó la técnica de interpretabilidad SHAP (*SHapley Additive "
  "exPlanations*) sobre el modelo de mejor desempeño, con el propósito de cuantificar la "
  "contribución de cada variable a la probabilidad de conversión y dar soporte a la toma "
  "de decisiones de marketing digital (Lundberg & Lee, 2017).")

p("La implementación se llevó a cabo en Python 3.13, empleando las bibliotecas `pandas` "
  "para el procesamiento de datos, `scikit-learn` para Random Forest y la red neuronal, "
  "`xgboost` y `lightgbm` para los métodos de boosting, y `shap` para la interpretabilidad.")

# ======================================================================
# RESULTADOS Y DISCUSIÓN
# ======================================================================
h1("Resultados y discusión")

h2("Caracterización del conjunto de datos")
p("El conjunto de datos *E-Commerce Behavior Data from Multi Category Store* está "
  "compuesto por 67,501,979 interacciones correspondientes a la actividad de 3,696,117 "
  "usuarios únicos distribuidos en 13,776,050 sesiones de navegación durante noviembre "
  "de 2019. La Figura 2 presenta la distribución de los tipos de evento, en la que se observa "
  "un claro predominio de las vistas de producto (`view`, 94.15 %) frente a la adición al "
  "carrito (`cart`, 4.49 %) y la compra (`purchase`, 1.36 %). Esta marcada asimetría confirma "
  "la naturaleza del problema de conversión: solo una fracción reducida de las sesiones de "
  "navegación finaliza en una compra.")

h2("Comparación de los modelos")
p("La Tabla 3 resume el desempeño de los cuatro algoritmos evaluados sobre el conjunto "
  "de prueba.")

caption("**Tabla 3. Desempeño comparativo de los modelos de clasificación.**")
add_table(
    ["Algoritmo", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "Tiempo (s)"],
    [
        ["Random Forest", "0.9476", "0.6183", "0.2455", "0.3514", "0.8295", "260.3"],
        ["XGBoost", "0.9478", "0.6181", "0.2525", "0.3585", "0.8388", "47.8"],
        ["LightGBM", "0.9476", "0.6145", "0.2509", "0.3563", "0.8383", "27.7"],
        ["MLP (Red Neuronal)", "0.9474", "0.6205", "0.2320", "0.3377", "0.8345", "661.8"],
    ],
)
p("Fuente: elaboración propia.")

p("Como se observa en la Tabla 3, los cuatro modelos alcanzan una exactitud prácticamente "
  "idéntica (≈0.947), resultado esperable dado el marcado desequilibrio de clases: al "
  "predecir siempre la clase mayoritaria se obtendría una exactitud de 94.2 %, por lo que "
  "este indicador no permite discriminar entre los algoritmos. Por esta razón, el análisis se "
  "centra en la medida F1 y el ROC-AUC. En estos términos, **XGBoost obtuvo el mejor "
  "desempeño global (F1 = 0.3585 y ROC-AUC = 0.8388)**, seguido de cerca por LightGBM "
  "(F1 = 0.3563 y ROC-AUC = 0.8383), mientras que Random Forest (F1 = 0.3514) y la red "
  "neuronal MLP (F1 = 0.3377) quedaron por detrás.")

p("Los valores de precisión (≈0.62) y sensibilidad (≈0.25) reflejan el comportamiento típico "
  "de los modelos de conversión con clases desbalanceadas: cuando el modelo predice una "
  "compra, acierta en aproximadamente el 62 % de los casos, pero solo logra identificar "
  "alrededor del 25 % de las compras reales. Esta baja sensibilidad constituye una "
  "limitación natural del enfoque y un punto de mejora explícito para trabajos futuros, "
  "mediante técnicas de balanceo de clases.")

p("En términos de eficiencia, los métodos de boosting resultaron considerablemente más "
  "rápidos que el resto: LightGBM entrenó en 27.7 segundos y XGBoost en 47.8 segundos, "
  "frente a los 260.3 segundos de Random Forest y los 661.8 segundos de la red neuronal. "
  "Es decir, la red neuronal —representante del enfoque de *Deep Learning*— no solo "
  "obtuvo el menor desempeño en medida F1, sino que demandó el mayor tiempo de "
  "entrenamiento, lo que evidencia que, para este problema tabular con un número reducido "
  "de variables, los modelos de ensamble basados en árboles resultan más adecuados.")

h2("Interpretabilidad con SHAP")
p("La Figura 3 presenta la importancia global de las variables según los valores SHAP del "
  "modelo de mejor desempeño (XGBoost), y la Figura 4 muestra la distribución del impacto "
  "de cada variable sobre la probabilidad de conversión. El análisis revela que la variable "
  "**`num_cart` (número de productos añadidos al carrito) concentra aproximadamente el "
  "82 % de la importancia total**, lo que resulta intuitivo: añadir productos al carrito es la "
  "señal más directa de intención de compra. Le siguen, con una contribución mucho menor, "
  "el número de productos únicos vistos (`num_unique_products`, ≈8.5 %), la duración de la "
  "sesión (`session_duration_sec`, ≈4.6 %) y el número total de eventos (`num_events`, ≈2.2 %). "
  "Las variables de precio (`price_max` y `price_mean`) y el número de vistas (`num_views`) "
  "tuvieron un impacto marginal. Este hallazgo tiene una implicación práctica relevante "
  "para el marketing digital: las estrategias orientadas a la recuperación de carritos "
  "abandonados tendrían el mayor potencial para incrementar la conversión.")

p("**Figura 2.** Distribución de los tipos de evento del conjunto de datos.")
p("**Figura 3.** Importancia global de variables (SHAP Bar Plot).")
p("**Figura 4.** Impacto de cada variable en la conversión (SHAP Beeswarm).")

h2("Discusión y comparación con trabajos previos")
p("Los resultados obtenidos se contrastan con el trabajo de Satu e Islam (2023), quienes "
  "aplicaron diferentes técnicas de transformación de características, selección de variables "
  "y clasificación para predecir la intención de compra de consumidores en línea. En su "
  "estudio, el algoritmo Random Forest se identificó como el clasificador más estable, "
  "alcanzando una exactitud máxima de 92.39 %, una medida F de 0.924 y un AUROC de "
  "0.975 sobre el conjunto de datos *Online Shoppers' Purchasing Intention* del repositorio "
  "UCI (12,330 sesiones, 17 variables y una tasa de compra del 15.5 %).")

p("Aunque la exactitud alcanzada en este trabajo (≈94.8 %) es numéricamente superior, "
  "esta comparación no es directa, pues la exactitud está condicionada por el desequilibrio "
  "de clases: el conjunto de datos aquí utilizado presenta una tasa de compra mucho menor "
  "(5.78 %), de modo que una exactitud alta resulta engañosa. En los indicadores "
  "comparables que penalizan los errores sobre la clase minoritaria —medida F1 y "
  "ROC-AUC— los valores de este trabajo (F1 ≈ 0.36 y ROC-AUC ≈ 0.84) son inferiores a los "
  "reportados por Satu e Islam. Esta diferencia se explica por tres factores: (1) un "
  "desequilibrio de clases más acentuado; (2) una menor cantidad de variables utilizadas "
  "(7 derivadas a nivel de sesión frente a 17 originales); y (3) la ausencia en este trabajo de "
  "técnicas de balanceo (SMOTE), de eliminación de valores atípicos y de selección de "
  "características, que los autores citados sí aplicaron y que mejoran el desempeño sobre la "
  "clase minoritaria.")

p("En cuanto a las coincidencias, ambos estudios confirman que los métodos basados en "
  "árboles de ensamble son los más adecuados para predecir la intención de compra. No "
  "obstante, existe una diferencia relevante: mientras Satu e Islam identificaron a Random "
  "Forest como el clasificador más estable, en este trabajo los métodos de boosting (XGBoost "
  "y LightGBM) superaron ligeramente a Random Forest. Este resultado es coherente con la "
  "mayor escala del conjunto de datos empleado, en la que la corrección secuencial de "
  "errores propia del boosting aprovecha mejor el volumen de información disponible.")

p("En relación con la calidad de los datos, los hallazgos de este trabajo son consistentes "
  "con lo planteado por Al-Toq y Almaslukh (2025), quienes sostienen que la completitud, "
  "la consistencia, la exactitud y la confiabilidad de los datos inciden directamente en el "
  "desempeño de los modelos de aprendizaje automático, y con la perspectiva de Cai y Zhu "
  "(2015) sobre la necesidad de evaluar la calidad de los datos como condición previa al "
  "análisis en entornos de grandes volúmenes de información.")

# ======================================================================
# CONCLUSIONES
# ======================================================================
h1("Conclusiones")

p("El desarrollo de este trabajo permitió cumplir el objetivo general planteado, al construir "
  "un sistema capaz de predecir la probabilidad de conversión de los usuarios en una "
  "plataforma de comercio electrónico a partir del análisis de sus datos de comportamiento. "
  "Para ello se cumplieron los objetivos específicos de manera secuencial, siguiendo la "
  "metodología CRISP-DM.")

p("En primer lugar, se cumplió el objetivo de caracterizar y preparar los datos mediante un "
  "proceso de limpieza y transformación, en el que se verificó la completitud, consistencia "
  "y exactitud del conjunto de datos, se eliminaron los registros sin identificador de sesión "
  "y se construyó una unidad de análisis a nivel de sesión mediante la creación de variables "
  "predictoras libres de fuga de información. Este proceso evidenció que el conjunto de "
  "datos, pese a su gran volumen, se encontraba en condiciones adecuadas para el modelado "
  "una vez aplicadas las transformaciones descritas.")

p("En segundo lugar, se aplicaron cuatro técnicas de aprendizaje automático y aprendizaje "
  "profundo —Random Forest, XGBoost, LightGBM y una red neuronal MLP—, evaluadas con "
  "métricas de exactitud, precisión, sensibilidad, medida F1 y ROC-AUC. El modelo XGBoost "
  "presentó el mejor desempeño global, con una medida F1 de 0.3585 y un ROC-AUC de "
  "0.8388, seguido de cerca por LightGBM, mientras que la red neuronal obtuvo el menor "
  "desempeño y el mayor costo computacional. El análisis de interpretabilidad SHAP "
  "permitió, además, identificar la variable `num_cart` (productos añadidos al carrito) como "
  "el factor más influyente en la conversión, lo que aporta información útil para orientar "
  "estrategias de marketing digital enfocadas en la recuperación de carritos abandonados.")

p("Desde el punto de vista comparativo, los resultados obtenidos son coherentes con los "
  "reportados por Satu e Islam (2023) en cuanto a la pertinencia de los métodos de ensamble "
  "basados en árboles para la predicción de la intención de compra, aunque difieren en el "
  "algoritmo ganador y en la magnitud de la medida F1 y del ROC-AUC, diferencias "
  "atribuibles al mayor desequilibrio de clases y a la menor cantidad de variables del "
  "conjunto de datos utilizado en este trabajo.")

p("Finalmente, como trabajo futuro se plantea la incorporación de variables contextuales y "
  "temporales adicionales (por ejemplo, día de la semana, hora del día o campañas activas), "
  "la aplicación de técnicas de balanceo de clases (como SMOTE) y de selección de "
  "características para mejorar la sensibilidad del modelo sobre la clase minoritaria, así como "
  "la exploración de técnicas de aprendizaje profundo más avanzado (redes recurrentes o "
  "modelos basados en atención) que capturen la secuencia temporal de las interacciones. "
  "Asimismo, se propone el despliegue del sistema en un entorno productivo con monitoreo "
  "continuo del desempeño del modelo.")

# ======================================================================
# REFERENCIAS
# ======================================================================
h1("Referencias (adicionales a las ya citadas)")

p("Al-Toq, R., & Almaslukh, A. (2025). DQMAF—Data Quality Modeling and Assessment "
  "Framework. *Information, 16*(9), 911.")
p("Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32.")
p("Cai, L., & Zhu, Y. (2015). The Challenges of Data Quality and Data Quality Assessment "
  "in the Big Data Era. *Data Science Journal, 14*, 2.")
p("Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings "
  "of the 22nd ACM SIGKDD*, 785–794.")
p("Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). "
  "LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural "
  "Information Processing Systems, 30*.")
p("Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model "
  "predictions. *Advances in Neural Information Processing Systems, 30*.")
p("Satu, M. S., & Islam, S. F. (2023). Modeling online customer purchase intention behavior "
  "applying different feature engineering and classification techniques. *Discover "
  "Artificial Intelligence, 3*(36).")

out = r"D:\USUARIO NO BORRAR\Documentos\Trabajo_de_Grado\Secciones_faltantes_tesis.docx"
doc.save(out)
print("Guardado:", out)
