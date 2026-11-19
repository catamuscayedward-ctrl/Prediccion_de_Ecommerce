import pandas as pd
import os

ruta = "dataset/2019-Nov.csv"

print("=" * 60)
print("CARGANDO DATASET")
print("=" * 60)

df = pd.read_csv(ruta)

print("\n1. DIMENSIONES DEL DATASET")
print(f"Filas: {df.shape[0]:,}")
print(f"Columnas: {df.shape[1]}")

print("\n2. NOMBRES DE LAS COLUMNAS")
for columna in df.columns:
    print(f"- {columna}")

print("\n3. TIPOS DE DATOS")
print(df.dtypes)

print("\n4. VALORES NULOS")
print(df.isnull().sum())

print("\n5. PRIMEROS 5 REGISTROS")
print(df.head())

print("\n6. TIPOS DE EVENTOS")
if "event_type" in df.columns:
    print(df["event_type"].value_counts())

print("\n7. USUARIOS")
if "user_id" in df.columns:
    print(f"Usuarios únicos: {df['user_id'].nunique():,}")

print("\n8. SESIONES")
if "user_session" in df.columns:
    print(f"Sesiones únicas: {df['user_session'].nunique():,}")

print("\n" + "=" * 60)
print("EXPLORACIÓN TERMINADA")
print("=" * 60)