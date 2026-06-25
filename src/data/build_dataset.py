# src/data/build_dataset.py
import os
import zipfile
import pandas as pd

def build_dataset(raw_dir, processed_dir, aglomerados=[33, 5]):
    """
    Lee todos los archivos .zip de raw_dir, extrae los microdatos individuales,
    filtra por aglomerados y guarda un único DataFrame en processed_dir.
    """
    os.makedirs(processed_dir, exist_ok=True)
    registros = []

    # Columnas requeridas (incluyendo las que se usarán en el modelo)
    columnas_necesarias = [
        "CODUSU", "NRO_HOGAR", "COMPONENTE", "ANO4", "TRIMESTRE",
        "AGLOMERADO", "CH04", "CH06", "NIVEL_ED", "ESTADO",
        "CAT_OCUP", "PONDERA", "P21", "PP03J", "PP04B_COD", "PP04D_COD"
    ]

    archivos_zip = [f for f in os.listdir(raw_dir) if f.endswith(".zip")]
    print(f"Encontrados {len(archivos_zip)} archivos .zip")

    for zip_name in archivos_zip:
        zip_path = os.path.join(raw_dir, zip_name)
        with zipfile.ZipFile(zip_path, "r") as z:
            for inner_file in z.namelist():
                # Buscar archivo de individuos (suele contener "individual" o "ind")
                if "individual" in inner_file.lower() or "ind" in inner_file.lower():
                    print(f"Procesando {zip_name} -> {inner_file}")
                    with z.open(inner_file) as f:
                        df = pd.read_csv(f, sep=";", low_memory=False,
                                         usecols=lambda c: c.upper() in columnas_necesarias)
                        # Normalizar nombres
                        df.columns = df.columns.str.upper()
                        # Filtrar aglomerados
                        df["AGLOMERADO"] = pd.to_numeric(df["AGLOMERADO"], errors="coerce")
                        df = df[df["AGLOMERADO"].isin(aglomerados)].copy()
                        registros.append(df)

    if not registros:
        raise ValueError("No se encontraron datos para los aglomerados especificados.")

    df_consolidado = pd.concat(registros, ignore_index=True)
    # Guardar
    output_path = os.path.join(processed_dir, "serie_individual_raw.pkl")
    df_consolidado.to_pickle(output_path)
    print(f"Dataset guardado en {output_path}")
    print(f"Dimensiones: {df_consolidado.shape}")
    return df_consolidado

if __name__ == "__main__":
    build_dataset("data/raw", "data/processed")