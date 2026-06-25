# src/analysis/income_analysis.py
import os
import pandas as pd

def calcular_ingresos_medianos(input_pickle, output_pickle):
    df = pd.read_pickle(input_pickle)

    # Usar PONDIIO si existe; si no, PONDERA
    pond_col = "PONDIIO" if "PONDIIO" in df.columns else "PONDERA"

    # Solo ocupados con ingreso positivo
    df_ocup = df[(df["ESTADO"] == 1) & (df["ingreso_real"] > 0)].copy()

    def weighted_median(group):
        sorted_group = group.sort_values("ingreso_real")
        cumsum = sorted_group[pond_col].cumsum()
        total = sorted_group[pond_col].sum()
        idx = (cumsum >= total/2).idxmax()
        return sorted_group.loc[idx, "ingreso_real"]

    medianas = df_ocup.groupby(["ANO4", "TRIMESTRE", "AGLOMERADO"]).apply(weighted_median).reset_index()
    medianas.columns = ["ANO4", "TRIMESTRE", "AGLOMERADO", "ingreso_mediano_pond"]
    medianas["periodo"] = medianas["ANO4"].astype(str) + "-T" + medianas["TRIMESTRE"].astype(str)

    medianas.to_pickle(output_pickle)
    print(f"Medianas de ingreso guardadas en {output_pickle}")
    return medianas

if __name__ == "__main__":
    calcular_ingresos_medianos(
        "data/processed/serie_individual_final.pkl",
        "data/processed/evolucion_ingresos.pkl"
    )