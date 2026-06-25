# src/analysis/stats_analysis.py
import os
import pandas as pd

def calcular_tasas_laborales(input_pickle, output_pickle):
    df = pd.read_pickle(input_pickle)

    # Asegurar tipos
    df["PONDERA"] = pd.to_numeric(df["PONDERA"], errors="coerce").fillna(0)
    df["ESTADO"] = pd.to_numeric(df["ESTADO"], errors="coerce").fillna(0).astype(int)

    # Crear columnas ponderadas
    df["pob_total"] = df["PONDERA"]
    df["pob_activa"] = df.apply(lambda r: r["PONDERA"] if r["ESTADO"] in [1, 2] else 0, axis=1)
    df["pob_ocupada"] = df.apply(lambda r: r["PONDERA"] if r["ESTADO"] == 1 else 0, axis=1)
    df["pob_desocupada"] = df.apply(lambda r: r["PONDERA"] if r["ESTADO"] == 2 else 0, axis=1)

    # Agrupar por año, trimestre y aglomerado
    grouped = df.groupby(["ANO4", "TRIMESTRE", "AGLOMERADO"], as_index=False)[
        ["pob_total", "pob_activa", "pob_ocupada", "pob_desocupada"]
    ].sum()

    # Calcular tasas
    grouped["tasa_actividad"] = (grouped["pob_activa"] / grouped["pob_total"]) * 100
    grouped["tasa_empleo"] = (grouped["pob_ocupada"] / grouped["pob_total"]) * 100
    grouped["tasa_desocupacion"] = (grouped["pob_desocupada"] / grouped["pob_activa"]) * 100

    # Crear período como string
    grouped["periodo"] = grouped["ANO4"].astype(str) + "-T" + grouped["TRIMESTRE"].astype(str)

    grouped.to_pickle(output_pickle)
    print(f"Tasas laborales guardadas en {output_pickle}")
    return grouped

if __name__ == "__main__":
    calcular_tasas_laborales(
        "data/processed/serie_individual_final.pkl",
        "data/processed/tasas_mercado_trabajo.pkl"
    )