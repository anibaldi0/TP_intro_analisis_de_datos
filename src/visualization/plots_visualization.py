# src/visualization/plots_visualization.py
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

def generar_graficos(tasas_pkl, ingresos_pkl, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid")

    # ------------------------------------------------------------------
    # 1. Graficos de evolucion de tasas laborales
    # ------------------------------------------------------------------
    df_tasas = pd.read_pickle(tasas_pkl)
    mapa_aglom = {33: "GBA", 5: "Gran Mendoza"}
    df_tasas["Aglomerado"] = df_tasas["AGLOMERADO"].map(mapa_aglom)

    tasas = ["tasa_actividad", "tasa_empleo", "tasa_desocupacion"]
    titulos = ["Tasa de Actividad", "Tasa de Empleo", "Tasa de Desocupacion"]

    for tasa, titulo in zip(tasas, titulos):
        plt.figure(figsize=(12, 5))
        sns.lineplot(
            data=df_tasas,
            x="periodo",
            y=tasa,
            hue="Aglomerado",
            marker="o",
            linewidth=2,
            palette="Set1"
        )
        plt.title(f"Evolucion de la {titulo} (2016-2025)", fontweight="bold")
        plt.xlabel("Periodo (Anio-Trimestre)")
        plt.ylabel("Porcentaje (%)")
        plt.xticks(rotation=45, ha="right", fontsize=9)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"evolucion_{tasa}.png"), dpi=300)
        plt.close()

    # ------------------------------------------------------------------
    # 2. Boxplot de ingresos por nivel educativo y sexo (ultimo anio)
    # ------------------------------------------------------------------
    df_ing = pd.read_pickle(ingresos_pkl)
    ultimo_ano = df_ing["ANO4"].max()
    df_plot = df_ing[(df_ing["ANO4"] == ultimo_ano) & (df_ing["ingreso_real"] > 0)].copy()
    df_plot["Sexo"] = df_plot["sexo"]
    df_plot["Educacion"] = df_plot["nivel_educativo"]

    plt.figure(figsize=(14, 7))
    sns.boxplot(
        data=df_plot,
        x="Educacion",
        y="ingreso_real",
        hue="Sexo",
        palette="pastel",
        order=[
            "Sin instruccion",
            "Primaria incompleta",
            "Primaria completa",
            "Secundaria incompleta",
            "Secundaria completa",
            "Superior incompleta",
            "Superior completa"
        ]
    )
    plt.title(f"Distribucion de Ingresos Reales por Nivel Educativo y Sexo ({ultimo_ano})", fontweight="bold")
    plt.xlabel("Nivel Educativo")
    plt.ylabel("Ingreso Real (pesos constantes)")
    plt.xticks(rotation=30, ha="right")
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "boxplot_ingresos_multivariado.png"), dpi=300)
    plt.close()

    # ------------------------------------------------------------------
    # 3. Histograma de la distribucion del ingreso real (log) - nuevo
    # ------------------------------------------------------------------
    df_ing_pos = df_ing[df_ing["ingreso_real"] > 0].copy()
    df_ing_pos["log_ingreso"] = np.log(df_ing_pos["ingreso_real"])

    plt.figure(figsize=(10, 6))
    sns.histplot(
        data=df_ing_pos,
        x="log_ingreso",
        hue="AGLOMERADO",
        kde=True,
        bins=40,
        alpha=0.5,
        palette="Set2"
    )
    plt.title("Distribucion del log(Ingreso Real) por Aglomerado (todos los anios)")
    plt.xlabel("Log(Ingreso Real)")
    plt.ylabel("Frecuencia")
    plt.legend(title="Aglomerado", labels=["GBA", "Gran Mendoza"])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "histograma_log_ingreso.png"), dpi=300)
    plt.close()

    # ------------------------------------------------------------------
    # 4. Grafico de evolucion de la mediana de ingresos reales
    # ------------------------------------------------------------------
    # Para esto necesitamos los datos de ingresos medianos por periodo.
    # Usamos el archivo de evolucion de ingresos generado por income_analysis.py
    # Pero ese archivo no se pasa como parametro, asi que lo leemos directamente.
    # Si no existe, se omite este grafico.
    evol_path = "data/processed/evolucion_ingresos.pkl"
    if os.path.exists(evol_path):
        df_evol = pd.read_pickle(evol_path)
        df_evol["Aglomerado"] = df_evol["AGLOMERADO"].map(mapa_aglom)
        plt.figure(figsize=(12, 5))
        sns.lineplot(
            data=df_evol,
            x="periodo",
            y="ingreso_mediano_pond",
            hue="Aglomerado",
            marker="o",
            linewidth=2,
            palette="Set1"
        )
        plt.title("Evolucion del Ingreso Mediano Real (pesos constantes de 2025)")
        plt.xlabel("Periodo (Anio-Trimestre)")
        plt.ylabel("Ingreso Mediano (pesos)")
        plt.xticks(rotation=45, ha="right", fontsize=9)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "evolucion_ingreso_mediano.png"), dpi=300)
        plt.close()
    else:
        print("No se encontro evolucion_ingresos.pkl, se omite el grafico de evolucion de ingreso mediano.")

    print(f"Graficos guardados en {output_dir}")

if __name__ == "__main__":
    generar_graficos(
        "data/processed/tasas_mercado_trabajo.pkl",
        "data/processed/serie_individual_final.pkl",
        "reports/figures"
    )