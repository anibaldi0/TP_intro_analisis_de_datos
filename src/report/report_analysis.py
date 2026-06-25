# src/report/report_analysis.py
import os
import pandas as pd

def generar_reporte(tasas_pkl, ingresos_pkl, output_txt):
    df_tasas = pd.read_pickle(tasas_pkl)
    df_ingresos = pd.read_pickle(ingresos_pkl)

    # Encontrar primer y último período
    primer_periodo = df_tasas["periodo"].min()
    ultimo_periodo = df_tasas["periodo"].max()

    mapa_aglom = {33: "Gran Buenos Aires (GBA)", 5: "Gran Mendoza"}

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("      REPORTE DE EVOLUCIÓN SOCIOECONÓMICA (2016-2025)\n")
        f.write("="*60 + "\n\n")

        # --- Tasas ---
        f.write("1. MERCADO LABORAL\n")
        f.write("-"*60 + "\n")
        for aglom_id, aglom_nom in mapa_aglom.items():
            f.write(f"* {aglom_nom}:\n")
            for col, nombre in [("tasa_actividad", "Actividad"),
                                ("tasa_empleo", "Empleo"),
                                ("tasa_desocupacion", "Desocupación")]:
                val_ini = df_tasas[(df_tasas["periodo"] == primer_periodo) & (df_tasas["AGLOMERADO"] == aglom_id)][col].mean()
                val_fin = df_tasas[(df_tasas["periodo"] == ultimo_periodo) & (df_tasas["AGLOMERADO"] == aglom_id)][col].mean()
                diff = val_fin - val_ini
                direccion = "subió" if diff > 0 else "bajó"
                f.write(f"  - {nombre}: {val_ini:.1f}% → {val_fin:.1f}% ({direccion} {abs(diff):.1f} pp)\n")
            f.write("\n")

        # --- Ingresos ---
        f.write("2. EVOLUCIÓN DEL INGRESO MEDIANO (PESOS CONSTANTES)\n")
        f.write("-"*60 + "\n")
        f.write("(Ingreso mediano ponderado, ajustado por inflación)\n\n")
        for aglom_id, aglom_nom in mapa_aglom.items():
            ing_ini = df_ingresos[(df_ingresos["periodo"] == primer_periodo) & (df_ingresos["AGLOMERADO"] == aglom_id)]["ingreso_mediano_pond"].mean()
            ing_fin = df_ingresos[(df_ingresos["periodo"] == ultimo_periodo) & (df_ingresos["AGLOMERADO"] == aglom_id)]["ingreso_mediano_pond"].mean()
            variacion = ((ing_fin - ing_ini) / ing_ini) * 100 if ing_ini > 0 else 0
            f.write(f"* {aglom_nom}:\n")
            f.write(f"  - Mediana inicial ({primer_periodo}): ${ing_ini:,.0f}\n".replace(",", "."))
            f.write(f"  - Mediana final ({ultimo_periodo}): ${ing_fin:,.0f}\n".replace(",", "."))
            f.write(f"  - Variación real: {variacion:+.1f}%\n\n")

        f.write("="*60 + "\n")
        f.write("FIN DEL REPORTE\n")
        f.write("="*60 + "\n")

    print(f"Reporte guardado en {output_txt}")

if __name__ == "__main__":
    generar_reporte(
        "data/processed/tasas_mercado_trabajo.pkl",
        "data/processed/evolucion_ingresos.pkl",
        "reports/reporte_humano.txt"
    )