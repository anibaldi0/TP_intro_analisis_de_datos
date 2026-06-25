# src/models/train_model.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

def entrenar_imputar_ingresos(input_pickle, output_pickle, output_figures="reports/figures"):
    os.makedirs(output_figures, exist_ok=True)
    df = pd.read_pickle(input_pickle)

    # Usar PONDIIO si existe, sino PONDERA
    pond_col = "PONDIIO" if "PONDIIO" in df.columns else "PONDERA"

    # Solo ocupados con horas trabajadas > 0
    df_modelo = df[(df["ESTADO"] == 1) & (df["horas_trabajadas"] > 0)].copy()

    # Separar con y sin ingreso
    df_con_ingreso = df_modelo[df_modelo["ingreso_real"] > 0].copy()
    df_sin_ingreso = df_modelo[df_modelo["ingreso_real"] <= 0].copy()

    if len(df_con_ingreso) < 100:
        raise ValueError("No hay suficientes casos con ingreso para entrenar.")

    # Crear variables predictoras
    df_con_ingreso["edad"] = pd.to_numeric(df_con_ingreso["CH06"], errors="coerce").fillna(0)
    df_con_ingreso["edad_cuadrado"] = df_con_ingreso["edad"] ** 2

    # Seleccion de variables
    X = df_con_ingreso[[
        "horas_trabajadas",
        "sexo",
        "nivel_educativo",
        "sector_actividad",
        "calificacion_tarea",
        "categoria_ocupacional",
        "registro",
        "AGLOMERADO",
        "ANO4",
        "TRIMESTRE",
        "edad",
        "edad_cuadrado"
    ]].copy()

    X = pd.get_dummies(X, drop_first=True)
    y = np.log(df_con_ingreso["ingreso_real"])

    # Division entrenamiento/prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modelo
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Metricas
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print("="*60)
    print("EVALUACION DEL MODELO DE IMPUTACION")
    print("="*60)
    print(f"R cuadrado: {r2:.4f}")
    print(f"RMSE (log): {rmse:.4f}")
    print("\nCoeficientes (interpretacion en log):")
    for col, coef in zip(X.columns, model.coef_):
        print(f"  {col}: {coef:.4f}")

    # Graficos de diagnostico
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 3, 1)
    plt.scatter(y_test, y_pred, alpha=0.3, s=10)
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--')
    plt.xlabel('Observado (log)')
    plt.ylabel('Predicho (log)')
    plt.title(f'Observados vs Predichos (R2 = {r2:.3f})')

    residuos = y_test - y_pred
    plt.subplot(1, 3, 2)
    plt.scatter(y_pred, residuos, alpha=0.3, s=10)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Predicho (log)')
    plt.ylabel('Residuo (log)')
    plt.title('Residuos vs Predichos')

    plt.subplot(1, 3, 3)
    stats.probplot(residuos, dist="norm", plot=plt)
    plt.title('Q-Q plot de residuos')

    plt.tight_layout()
    plt.savefig(os.path.join(output_figures, 'diagnostico_regresion.png'), dpi=300)
    plt.close()
    print(f"Grafico de diagnostico guardado en {output_figures}/diagnostico_regresion.png")

    # Imputacion para casos sin ingreso
    if len(df_sin_ingreso) > 0:
        df_sin_ingreso["edad"] = pd.to_numeric(df_sin_ingreso["CH06"], errors="coerce").fillna(0)
        df_sin_ingreso["edad_cuadrado"] = df_sin_ingreso["edad"] ** 2

        X_sin = df_sin_ingreso[[
            "horas_trabajadas",
            "sexo",
            "nivel_educativo",
            "sector_actividad",
            "calificacion_tarea",
            "categoria_ocupacional",
            "registro",
            "AGLOMERADO",
            "ANO4",
            "TRIMESTRE",
            "edad",
            "edad_cuadrado"
        ]].copy()

        X_sin = pd.get_dummies(X_sin, drop_first=True)
        X_sin = X_sin.reindex(columns=X.columns, fill_value=0)

        pred_log = model.predict(X_sin)
        df_sin_ingreso["ingreso_imputado"] = np.exp(pred_log)

        # Unir conjuntos
        df_con_ingreso["ingreso_final"] = df_con_ingreso["ingreso_real"]
        df_sin_ingreso["ingreso_final"] = df_sin_ingreso["ingreso_imputado"]
        df_final = pd.concat([df_con_ingreso, df_sin_ingreso], ignore_index=True)

        # Validacion con PONDIIO: mediana ponderada
        if pond_col in df_final.columns:
            df_valid = df_final[df_final["ingreso_final"] > 0].copy()
            sorted_valid = df_valid.sort_values("ingreso_final")
            cumsum = sorted_valid[pond_col].cumsum()
            total = sorted_valid[pond_col].sum()
            idx = (cumsum >= total/2).idxmax()
            mediana_ponderada = sorted_valid.loc[idx, "ingreso_final"]
            print(f"\nMediana ponderada con {pond_col}: ${mediana_ponderada:,.0f}".replace(",", "."))
        else:
            print("\nNo se encontro PONDIIO para validacion.")

        df_final.to_pickle(output_pickle)
        print(f"Imputacion completada. Guardado en {output_pickle}")
    else:
        print("No hay casos sin ingreso para imputar.")

    # Guardar coeficientes
    coef_df = pd.DataFrame({'variable': X.columns, 'coeficiente': model.coef_})
    coef_df.to_csv(os.path.join(output_figures, 'coeficientes_modelo.csv'), index=False)

if __name__ == "__main__":
    entrenar_imputar_ingresos(
        "data/processed/serie_individual_final.pkl",
        "data/processed/serie_individual_imputada.pkl"
    )