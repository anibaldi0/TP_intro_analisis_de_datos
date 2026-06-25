# src/run_pipeline.py
import os
import sys

src_path = os.path.dirname(os.path.abspath(__file__))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from data.build_dataset import build_dataset
from features.build_features import build_features
from analysis.stats_analysis import calcular_tasas_laborales
from analysis.income_analysis import calcular_ingresos_medianos
from models.train_model import entrenar_imputar_ingresos
from visualization.plots_visualization import generar_graficos
from report.report_analysis import generar_reporte

def verificar_archivos():
    required = ["data/raw"]
    for r in required:
        if not os.path.exists(r):
            print(f"[ERROR] No se encuentra: {r}")
            return False
    return True

def run_pipeline():
    print("=== INICIANDO PIPELINE DEL TP ===")
    if not verificar_archivos():
        sys.exit(1)

    print("\n[1/6] Construyendo dataset crudo...")
    build_dataset("data/raw", "data/processed")

    print("\n[2/6] Construyendo features y deflactando ingresos...")
    build_features(
        "data/processed/serie_individual_raw.pkl",
        "data/processed/serie_individual_final.pkl"
    )

    print("\n[3/6] Calculando tasas laborales...")
    calcular_tasas_laborales(
        "data/processed/serie_individual_final.pkl",
        "data/processed/tasas_mercado_trabajo.pkl"
    )

    print("\n[4/6] Calculando evolución de ingresos...")
    calcular_ingresos_medianos(
        "data/processed/serie_individual_final.pkl",
        "data/processed/evolucion_ingresos.pkl"
    )

    print("\n[5/6] Entrenando modelo de imputación...")
    entrenar_imputar_ingresos(
        "data/processed/serie_individual_final.pkl",
        "data/processed/serie_individual_imputada.pkl"
    )

    print("\n[6/6] Generando gráficos y reporte...")
    generar_graficos(
        "data/processed/tasas_mercado_trabajo.pkl",
        "data/processed/serie_individual_final.pkl",
        "reports/figures"
    )
    generar_reporte(
        "data/processed/tasas_mercado_trabajo.pkl",
        "data/processed/evolucion_ingresos.pkl",
        "reports/reporte.txt"
    )

    print("\n=== PIPELINE COMPLETADO CON ÉXITO ===")

if __name__ == "__main__":
    run_pipeline()