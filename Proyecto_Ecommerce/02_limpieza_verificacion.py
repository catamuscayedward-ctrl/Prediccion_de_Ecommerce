# -*- coding: utf-8 -*-
"""
Verificación de calidad / limpieza del dataset
E-Commerce Behavior Data from Multi Category Store (2019-Nov)
Procesamiento por lotes (chunks) para no agotar la memoria.
"""
import gc
import time
import pandas as pd
import numpy as np

FILE = r"D:\USUARIO NO BORRAR\Documentos\Trabajo_de_Grado\Proyecto_Ecommerce\Dataset\2019-Nov.csv"
CHUNKSIZE = 1_000_000

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

t0 = time.time()

total_rows = 0
nulls = None
event_type_counts = {}
price_min = np.inf
price_max = -np.inf
price_neg = 0
price_zero = 0
date_min = None
date_max = None
users = set()
sessions = set()
products = set()
brands = set()
category_codes = set()

reader = pd.read_csv(
    FILE,
    chunksize=CHUNKSIZE,
    dtype=dtype_dict,
    parse_dates=["event_time"],
)

for i, chunk in enumerate(reader):
    total_rows += len(chunk)

    # Nulos
    n = chunk.isnull().sum()
    if nulls is None:
        nulls = n
    else:
        nulls = nulls.add(n, fill_value=0)

    # Eventos
    vc = chunk["event_type"].value_counts(dropna=False)
    for k, v in vc.items():
        event_type_counts[k] = event_type_counts.get(k, 0) + int(v)

    # Precio
    p = chunk["price"]
    price_min = min(price_min, float(p.min()))
    price_max = max(price_max, float(p.max()))
    price_neg += int((p < 0).sum())
    price_zero += int((p == 0).sum())

    # Fechas
    if date_min is None:
        date_min = chunk["event_time"].min()
        date_max = chunk["event_time"].max()
    else:
        date_min = min(date_min, chunk["event_time"].min())
        date_max = max(date_max, chunk["event_time"].max())

    # Unicidad (sets)
    users.update(chunk["user_id"].dropna().unique().tolist())
    sessions.update(chunk["user_session"].dropna().unique().tolist())
    products.update(chunk["product_id"].dropna().unique().tolist())
    brands.update(chunk["brand"].dropna().unique().tolist())
    category_codes.update(chunk["category_code"].dropna().unique().tolist())

    if (i + 1) % 5 == 0:
        print(f"[{time.time()-t0:6.1f}s] chunk {i+1}: {total_rows:,} filas", flush=True)

print("\n" + "=" * 60)
print("RESULTADOS DE CALIDAD / LIMPIEZA DEL DATASET")
print("=" * 60)
print(f"\nTotal de registros (filas): {total_rows:,}")
print(f"Total de columnas: {len(dtype_dict) + 1}")

print("\n--- VALORES NULOS POR COLUMNA ---")
for col in ["event_time", "event_type", "product_id", "category_id",
            "category_code", "brand", "price", "user_id", "user_session"]:
    if col in nulls:
        nn = int(nulls[col])
        pct = 100 * nn / total_rows if total_rows else 0
        print(f"  {col:15s}: {nn:>12,}  ({pct:.4f}%)")

print("\n--- TIPOS DE EVENTO ---")
for k, v in sorted(event_type_counts.items(), key=lambda x: -x[1]):
    print(f"  {str(k):10s}: {v:>12,}  ({100*v/total_rows:.2f}%)")

print("\n--- PRECIO ---")
print(f"  Mínimo: {price_min:,.4f}")
print(f"  Máximo: {price_max:,.4f}")
print(f"  Registros con precio negativo: {price_neg:,}")
print(f"  Registros con precio igual a 0: {price_zero:,}")

print("\n--- RANGO DE FECHAS ---")
print(f"  Desde: {date_min}")
print(f"  Hasta: {date_max}")

print("\n--- UNICIDAD ---")
print(f"  Usuarios únicos (user_id): {len(users):,}")
print(f"  Sesiones únicas (user_session): {len(sessions):,}")
print(f"  Productos únicos (product_id): {len(products):,}")
print(f"  Marcas únicas (brand): {len(brands):,}")
print(f"  category_code únicos: {len(category_codes):,}")

print(f"\nTiempo total: {time.time()-t0:.1f} s")
print("=" * 60)
