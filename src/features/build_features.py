# src/features/build_features.py
import os
import pandas as pd

def build_features(raw_pickle, output_pickle):
    """
    Carga el dataset crudo, aplica deflación (pesos de 2025),
    y agrega variables categóricas y ponderadores.
    """
    df = pd.read_pickle(raw_pickle)
    df.columns = df.columns.str.upper()

    # --- DEFLACIÓN DE INGRESOS (pesos constantes de 2025) ---
    factores_inflacion = {
        2016: 107.15,
        2017: 85.82,
        2018: 58.13,
        2019: 37.80,
        2020: 27.76,
        2021: 18.39,
        2022: 9.44,
        2023: 3.80,
        2024: 1.39,
        2025: 1.00,
    }

    df["ANO4"] = df["ANO4"].astype(int)
    df["P21"] = pd.to_numeric(df["P21"], errors="coerce").fillna(0)
    df["factor_deflacion"] = df["ANO4"].map(factores_inflacion)
    df["ingreso_real"] = df["P21"] * df["factor_deflacion"]
    df.loc[df["P21"] <= 0, "ingreso_real"] = 0

    # --- PONDERADORES ---
    # Asegurar que PONDIIO exista; si no, usar PONDERA como fallback
    if "PONDIIO" not in df.columns:
        df["PONDIIO"] = df["PONDERA"]
        print("PONDIIO no encontrado. Se usará PONDERA para ingresos.")
    else:
        df["PONDIIO"] = pd.to_numeric(df["PONDIIO"], errors="coerce").fillna(df["PONDERA"])

    df["PONDERA"] = pd.to_numeric(df["PONDERA"], errors="coerce").fillna(0)

    # --- VARIABLES CATEGÓRICAS ---
    df["sexo"] = df["CH04"].map({1: "Varón", 2: "Mujer"})

    mapa_edu = {
        1: "Sin instrucción",
        2: "Primaria incompleta",
        3: "Primaria completa",
        4: "Secundaria incompleta",
        5: "Secundaria completa",
        6: "Superior incompleta",
        7: "Superior completa"
    }
    df["nivel_educativo"] = df["NIVEL_ED"].map(mapa_edu).fillna("Sin instrucción")

    df["horas_trabajadas"] = pd.to_numeric(df["PP03J"], errors="coerce").fillna(0)

    def sector_from_cod(cod):
        if cod < 10:
            return "Primario"
        elif cod < 46:
            return "Secundario"
        else:
            return "Terciario"
    df["sector_actividad"] = df["PP04B_COD"].apply(sector_from_cod)

    def calif_from_cod(cod):
        if cod in [1, 2, 3]:
            return "Profesional"
        elif cod in [4, 5, 6]:
            return "Técnico"
        else:
            return "Operario"
    df["calificacion_tarea"] = df["PP04D_COD"].apply(calif_from_cod)

    # --- NUEVAS VARIABLES (como el Trabajo 2) ---
    # Categoría ocupacional (CAT_OCUP)
    mapa_cat = {
        1: "Patrón/Empleador",
        2: "Cuenta propia",
        3: "Asalariado",
        4: "Trabajador familiar"
    }
    df["categoria_ocupacional"] = df["CAT_OCUP"].map(mapa_cat).fillna("Asalariado")

    # Registro del empleo (PP07H: 1 = tiene descuento jubilatorio, 2 = no)
    if "PP07H" in df.columns:
        df["registro"] = df["PP07H"].map({1: "Registrado", 2: "No registrado"}).fillna("No registrado")
    else:
        df["registro"] = "No registrado"  # fallback

    # Guardar
    df.to_pickle(output_pickle)
    print(f"Dataset final guardado en {output_pickle}")
    print(f"Dimensiones: {df.shape}")
    return df

if __name__ == "__main__":
    build_features(
        "data/processed/serie_individual_raw.pkl",
        "data/processed/serie_individual_final.pkl"
    )