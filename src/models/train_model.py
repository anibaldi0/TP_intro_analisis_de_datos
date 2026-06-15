# src/models/train_model.py
import os
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def preparar_datos_modelado(path_final):
    """
    Levanta el dataset final, filtra la no respuesta y codifica
    las variables categoricas en formato dummy para la regresion.
    """
    df = pd.read_pickle(path_final)

    # El modelo se calibra unicamente con quienes declararon ingresos validos
    df_modelo = df[df["ingreso_real"] > 0].copy()

    # Seleccion de predictores estructurales para el modelo
    predictores = ["ch04", "ch06", "nivel_ed", "aglomerado"]
    X = df_modelo[predictores].copy()

    # Aplicamos transformacion logaritmica a la variable dependiente
    # Esto estabiliza la varianza y mejora el rendimiento del R2
    y = np.log(df_modelo["ingreso_real"])

    # Convertimos variables categoricas a dummies de forma explicita
    X = pd.get_dummies(
        X, columns=["ch04", "nivel_ed", "aglomerado"], drop_first=True
    )

    return X, y


def entrenar_evaluar_regresion(X, y):
    """
    Divide el dataset, entrena el modelo de regresion lineal ordinaria
    y expone las metricas de rendimiento solicitadas por la catedra.
    """
    from sklearn.linear_model import LinearRegression

    # CORRECCION: Se cambio 'test_test_split' por el parametro nativo 'test_size'
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predicciones para evaluar rendimiento general
    y_pred = model.predict(X_test)

    # Calculo de metricas solicitadas en el Objetivo 4
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print("\n================ EVALUACION DEL MODELO ================")
    print(f"Coeficiente de Determinacion (R2 Score): {round(r2, 4)}")
    print(f"Error Cuadratico Medio (RMSE en log): {round(rmse, 4)}")
    print("=======================================================")

    print("\n================ INTERPRETACION DE COEFICIENTES ================")
    coef_df = pd.DataFrame(
        {"Variable": X.columns, "Coeficiente (Beta)": model.coef_}
    ).round(4)
    print(coef_df)
    print(f"Intercepto (Beta 0): {round(model.intercept_, 4)}")
    print("================================================================")

    return model


if __name__ == "__main__":
    final_input = "data/processed/serie_individual_final.pkl"

    if not os.path.exists(final_input):
        print(f"[ERROR] No se encontro el archivo final en {final_input}")
    else:
        print("Iniciando preparacion de matrices para modelado estadistico...")
        X, y = preparar_datos_modelado(final_input)

        print("Entrenando modelo de regresion lineal multiple...")
        modelo_ajustado = entrenar_evaluar_regresion(X, y)