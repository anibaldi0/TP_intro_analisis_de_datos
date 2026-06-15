# README.md

# Pipeline de Ingenieria de Datos - Procesamiento de la EPH (2016-2025)

Este proyecto contiene la infraestructura de codigo desarrollada en Python para la ingesta, extraccion, limpieza, consolidacion y transformacion economica de los microdatos de la Encuesta Permanente de Hogares (EPH) del INDEC, cubriendo la serie historica de los segundos trimestres del periodo 2016-2025.

El objetivo final del set de datos procesado es abastecer un analisis socioeconomico comparativo entre dos aglomerados urbanos y entrenar un modelo estadistico predictivo para la imputacion de la no respuesta a ingresos.

## 1. Arquitectura del Proyecto

El repositorio mantiene un diseno modular y predictivo basado en las mejores practicas de ingenieria de software:

```text
eph_project/
├── data/
│   ├── interim/          # Archivos .txt individuales extraidos programaticamente
│   ├── processed/        # Datasets consolidados, transformados y metricas en formato pickle (.pkl)
│   └── raw/              # Archivos fuentes ZIP descargados a mano del INDEC
├── reports/
│   └── figures/          # Graficos de alta definicion exportados para el informe (.png)
└── src/
    ├── data/
    │   └── extract_data.py       # Extractor selectivo de microdatos individuales
    ├── features/
    │   ├── build_feature.py      # Consolidador de serie filtrado por aglomerado
    │   └── transform_income.py   # Modulo de deflacion e ingenieria economica
    ├── analysis/
    │   └── stats_analysis.py     # Procesador de tasas del mercado de trabajo e ingresos ponderados
    ├── visualization/
    │   └── plots_visualization.py # Generador sistematico de graficos y boxplots
    └── models/
        └── train_model.py        # Modulo de entrenamiento y evaluacion de la regresion lineal

## 2. Etapas del Pipeline de Datos (Que hicimos y Por que)
    Etapa 1: Ingesta y Extraccion Selectiva (src/data/)
    Que se hizo: Se almacenaron las bases de datos crudas empaquetadas en .zip dentro de data/raw/ y se desarrollo un script extractor selectivo utilizando la libreria nativa zipfile.

    Por que: Cada paquete del INDEC contiene multiples tablas (Hogares e Individuales) en formatos redundantes. El script extrae unicamente los archivos con patron individual o personas en formato .txt, descartando las bases de hogares para optimizar el espacio en disco, reducir el uso de memoria RAM y acelerar la velocidad de lectura nativa de Pandas.

    Etapa 2: Consolidacion y Filtrado Geografico (src/features/build_feature.py)
    Que se hizo: Se unificaron las 39 bases de datos individuales en un unico dataframe indexado de Pandas (306.608 registros totales), tipificando las columnas en minusculas y filtrando exclusivamente por los codigos de aglomerado elegidos por el grupo.

    Aglomerados Seleccionados:
        33: Partidos del Gran Buenos Aires (GBA)
        5: Gran Mendoza

    Por que: El procesamiento de datos masivos a nivel nacional desborda los recursos de hardware locales de forma innecesaria. El filtrado temprano por claves foraneas numericas (aglomerado) reduce la dimensionalidad del dataset, aisla las muestras de estudio requeridas por el parcial y unifica las discrepancias estructurales que el INDEC introdujo en los disenos de registro a lo largo de la decada.

    Etapa 3: Ingenieria Economica - Deflacion por IPC (src/features/transform_income.py)
    Que se hizo: Se creo la variable sintetica ingreso_real sanitizando primero la columna p21 de forma numerica y multiplicando el ingreso nominal declarado de la ocupacion principal por un vector homogeneo de factores de ajuste basados en el Indice de Precios al Consumidor (IPC) del INDEC, tomando como base el ano 2025.

    Por que: Debido al regimen inflacionario del periodo 2016-2025, una comparacion directa sobre los valores nominales destruye la validez de cualquier analisis temporal o modelo predictivo (sesgo por distorsion de precios relativos). Transformar los datos a pesos constantes de poder adquisitivo homogeneo permite evaluar la evolucion real de los ingresos y calibrar un modelo de regresion lineal donde los coeficientes estimen impactos socioeconomicos veridicos.

## 3. Tratamiento Proximo de Datos (Preparacion para el Modelo Predictivo)
    El dataset definitivo generado en data/processed/serie_individual_final.pkl aisla las variables demograficas clave (ch04 Sexo, ch06 Edad, nivel_ed Nivel Educativo) y laborales (estado Condicion de actividad, cat_ocup Categorizacion, pp04b_cod Rama de actividad, pp04d_cod Ocupacion).

    Para el cumplimiento del Objetivo 4 (Aprobacion Directa), la estrategia de modelado consistira en:
    
    Segmentacion: Aislar los registros con valores mayores a cero en ingreso_real para conformar los conjuntos de entrenamiento y testeo (Train/Test Split).
    
    Filtrado de Blancos: Separar las filas donde la variable presente "No Respuesta" (codigo -9 o valores de no declaracion de ingresos iguales a 0) para constituir el set de aplicacion final de las predicciones del modelo.

######################################
## Detalle Funcional de los Scripts ##
######################################

#### python src/data/extract_data.py

    Proposito: Automatiza la apertura y extraccion limpia de los archivos comprimidos .zip de la base cruda.

    Logica: Utiliza la libreria nativa zipfile para escanear de forma dinamica el contenido e identificar unicamente los archivos de microdatos de personas (filtrando por patrones como "individual" o "personas" en minusculas), ignorando las tablas de hogares para optimizar espacio en disco y acelerar procesos subsiguientes. Estandariza los nombres extraidos en la carpeta data/interim/.

#### python src/features/build_feature.py

    Proposito: Unifica el historico atomizado en un unico corpus de datos indexado y realiza el filtrado geografico temprano.

    Logica: Lee secuencialmente las 39 bases individuales crudas (manejando un total de 306.608 registros). Sanea inconsistencias temporales forzando las columnas a minusculas de forma nativa y aisla los aglomerados de estudio seleccionados: 33 (Partidos del Gran Buenos Aires) y 5 (Gran Mendoza). Conserva estrictamente las variables demograficas, laborales y de ingresos exigidas por la catedra, incluyendo pp04b_cod y pp04d_cod. Exporta el DataFrame intermedio en formato binario Pickle.

#### python src/features/transform_income.py

    Proposito: Ejecuta la ingenieria de caracteristicas de indole economica para neutralizar la distorsion de precios relativos.

    Logica: Sanitiza la columna de ingreso de la ocupacion principal (p21) forzando tipos numericos con Pandas y normalizando valores corruptos o vacios a 0. Aplica un diccionario de factores de deflacion basados en el Indice de Precios al Consumidor (IPC) del INDEC para mapear los ingresos nominales a pesos constantes con base en el ano 2025 bajo la variable sintetica ingreso_real.

#### python src/analysis/stats_analysis.py

    Proposito: Computa de forma vectorizada los macro-indicadores del mercado laboral y la evolucion de ingresos reales.

    Logica: Reemplaza iteraciones costosas de Python por operaciones booleanas vectorizadas de alta performance para aislar la PEA, Ocupados y Desocupados. Implementa algoritmos matematicos con numpy para obtener la media ponderada y los percentiles ponderados (Q1​, Mediana, Q3​) utilizando de forma estricta el factor de expansion poblacional (pondera), garantizando precision estadistica e inmunidad ante sesgos metodologicos. Almacena las matrices resultantes en data/processed/.

#### python src/visualization/plots_visualization.py

    Proposito: Resuelve el pipeline visual de analisis multivariado generando graficos con calidad de publicacion.

    Logica: Utiliza matplotlib y seaborn alimentandose de las metricas consolidadas. Exporta a reports/figures/ las curvas de evolucion temporal de las Tasas de Actividad, Empleo y Desocupacion segmentadas por aglomerado. Adicionalmente, genera un diagrama de cajas (boxplot) en escala logaritmica para mapear la dispersion de ingresos cruzando el Sexo y el Nivel Educativo del ultimo periodo disponible.

#### python src/models/train_model.py

    Proposito: Desarrolla, entrena y evalua el modelo estadistico ordinario para la futura imputacion de la no respuesta a ingresos.

    Logica: Filtra el dataset aislando unicamente a la poblacion que declaro ingresos validos (ingreso_real > 0). Aplica transformacion logaritmica a la variable dependiente para mitigar la heterocedasticidad. Convierte los predictores categoricos (ch04, nivel_ed, aglomerado) en variables Dummy numericas. Divide la muestra metodologicamente utilizando un esquema Train/Test Split (80/20) mediante scikit-learn y entrena una Regresion Lineal Multiple.

## Metricas y Resultados del Modelo de Regresion

El modelo de regresion para el Objetivo 4 arrojo las siguientes metricas de control en la consola de evaluacion:

    Coeficiente de Determinacion (R2 Score): 0.1754 (Explica el 17.54% de la variabilidad del ingreso real, un rango consistente y valido para microdatos de ciencias sociales).

    Error Cuadratico Medio (RMSE en log): 0.8797

Impacto de los Coeficientes Estimados (β):

    Edad (ch06): Incremento promedio del 0.68% en el ingreso real por cada ano de experiencia.

    Genero (ch04_2): Penalizacion critica para el sexo femenino, evidenciando una brecha de ingresos real aproximada del 42.5% a igual nivel educativo y edad frente a los varones.

    Educacion (nivel_ed_6): Rendimiento incremental de la formacion profesional. Un graduado universitario superior completo percibe, en promedio, un 257% mas de ingresos reales respecto a la categoria sin instruccion.

    Aglomerado (aglomerado_33): Los trabajadores del GBA perciben, bajo condiciones homogeneas de perfil, un 9.28% mas de ingresos reales frente a los del Gran Mendoza.


