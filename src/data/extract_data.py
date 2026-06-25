# backend/app/data/extract_data.py
"""Modulo de extraccion y consolidacion de microdatos de la EPH."""
import os
import zipfile
import pandas as pd

def extraer_y_consolidar_eph(raw_dir, processed_dir):
    """Extrae y consolida microdatos filtrando aglomerados objetivo."""
    os.makedirs(processed_dir, exist_ok=True)
    registros = []
    aglomerados_objetivo = [10, 32]
    columnas_core = ["CODUSU", "ANO4", "TRIMESTRE", "AGLOMERADO", "CH04", "CH06", 
                     "NIVEL_ED", "ESTADO", "CAT_OCUP", "PONDERA", "P21", "PP03J", 
                     "PP04B_COD", "PP04D_COD"]

    for archivo in os.listdir(raw_dir):
        if archivo.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(raw_dir, archivo), "r") as z:
                for nombre in z.namelist():
                    if "individual" in nombre.lower():
                        with z.open(nombre) as f:
                            df = pd.read_csv(f, sep=";", low_memory=False)
                            df.columns = [c.upper() for c in df.columns]
                            df = df[df["AGLOMERADO"].isin(aglomerados_objetivo)]
                            registros.append(df[columnas_core.intersection(df.columns)])
    
    df_final = pd.concat(registros, ignore_index=True)
    df_final.to_pickle(os.path.join(processed_dir, "serie_consolidada.pkl"))
    print("Extraccion completada con exito.")

if __name__ == "__main__":
    extraer_y_consolidar_eph("data/raw", "data/processed")