import pandas as pd
import numpy as np

df = pd.read_pickle("data/processed/serie_individual_final.pkl")

# Filtrar ocupados con horas > 0
df_modelo = df[(df["ESTADO"] == 1) & (df["horas_trabajadas"] > 0)].copy()
df_con_ingreso = df_modelo[df_modelo["ingreso_real"] > 0].copy()

print("=== Estadisticas de ingreso_real ===")
print(df_con_ingreso["ingreso_real"].describe())

print("\n=== Rango de valores ===")
print(f"Min: {df_con_ingreso['ingreso_real'].min():.2f}")
print(f"Max: {df_con_ingreso['ingreso_real'].max():.2f}")
print(f"Media: {df_con_ingreso['ingreso_real'].mean():.2f}")

# Ver distribucion de log
print("\n=== Estadisticas de log(ingreso_real) ===")
log_ingreso = np.log(df_con_ingreso["ingreso_real"])
print(log_ingreso.describe())
print(f"Rango de log: {log_ingreso.min():.2f} a {log_ingreso.max():.2f}")