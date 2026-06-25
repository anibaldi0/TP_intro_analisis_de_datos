# README.md

# Pipeline de Ingeniería de Datos - Procesamiento de la EPH (2016-2025)

Este proyecto contiene la infraestructura de código desarrollada en Python para la ingesta, extracción, limpieza, consolidación y transformación económica de los microdatos de la Encuesta Permanente de Hogares (EPH) del INDEC, cubriendo la serie histórica de **todos los trimestres** del período 2016-2025.

El objetivo final del conjunto de datos procesado es abastecer un análisis socioeconómico comparativo entre dos aglomerados urbanos y entrenar un modelo estadístico predictivo para la imputación de la no respuesta a ingresos.

## 1. Arquitectura del Proyecto

El repositorio mantiene un diseño modular basado en las mejores prácticas de ingeniería de software:

```text
eph_project/
├── data/
│   ├── raw/                     # Archivos fuente ZIP descargados del INDEC
│   └── processed/               # Datasets consolidados y métricas en formato pickle (.pkl)
├── reports/
│   ├── figures/                 # Gráficos de alta definición para el informe (.png)
│   └── reporte.txt              # Reporte en lenguaje natural generado automáticamente
└── src/
    ├── data/
    │   └── build_dataset.py     # Extracción y consolidación de microdatos desde los ZIP
    ├── features/
    │   └── build_features.py    # Deflación de ingresos, creación de variables y ponderadores
    ├── analysis/
    │   ├── stats_analysis.py    # Cálculo de tasas de actividad, empleo y desocupación
    │   └── income_analysis.py   # Mediana ponderada de ingresos con PONDERA/PONDIIO
    ├── models/
    │   └── train_model.py       # Entrenamiento y evaluación del modelo de imputación
    ├── visualization/
    │   └── plots_visualization.py # Generación de gráficos de evolución y distribución
    ├── report/
    │   └── report_analysis.py   # Generación del reporte en lenguaje natural
    ├── run_pipeline.py          # Orquestador principal del pipeline
    ├── check_data.py            # Script de verificación rápida de datos
    └── __init__.py              # (marcador de paquete)

2. Etapas del Pipeline de Datos
Etapa 1: Ingesta y Extracción Selectiva (src/data/build_dataset.py)

Qué se hizo: Se almacenaron las bases de datos crudas empaquetadas en .zip dentro de data/raw/ y se desarrolló un script extractor selectivo utilizando la librería nativa zipfile.

Por qué: Cada paquete del INDEC contiene múltiples tablas (hogares e individuales) en formatos redundantes. El script extrae únicamente los archivos con patrón individual o ind en formato .txt, descartando las bases de hogares para optimizar el espacio en disco, reducir el uso de memoria RAM y acelerar la lectura con Pandas. Además, filtra por los aglomerados de interés (33 = GBA, 5 = Gran Mendoza) desde el primer momento.
Etapa 2: Construcción de Features y Deflación (src/features/build_features.py)

Qué se hizo: Este script unifica y transforma el dataset crudo:

    Aplica factores de deflación para expresar todos los ingresos en pesos constantes del segundo trimestre de 2025 (usando el IPC nacional con base diciembre 2016 = 100).

    Crea variables categóricas: sexo, nivel_educativo, sector_actividad, calificacion_tarea, categoria_ocupacional y registro (formal/informal).

    Asegura la existencia de los ponderadores PONDERA (para población general) y PONDIIO (para ingresos, con corrección de no respuesta). Si PONDIIO no está disponible, se utiliza PONDERA como fallback.

Por qué: La deflación es imprescindible para eliminar el efecto de la inflación acumulada del período (+10.000%). Las variables categóricas permiten el análisis multivariado y la segmentación de los ingresos.
Etapa 3: Cálculo de Tasas Laborales (src/analysis/stats_analysis.py)

Qué se hizo: Se calculan de forma vectorizada las tasas de actividad, empleo y desocupación utilizando el factor de expansión PONDERA. Se agrupa por año, trimestre y aglomerado.

Por qué: Las tasas oficiales del INDEC se calculan con ponderación muestral. Ignorar PONDERA introduciría sesgos significativos en las estimaciones.
Etapa 4: Evolución de Ingresos Medianos (src/analysis/income_analysis.py)

Qué se hizo: Se calcula la mediana ponderada del ingreso real de la ocupación principal (P21) para cada año, trimestre y aglomerado, utilizando PONDIIO (o PONDERA en su defecto).

Por qué: La mediana es robusta frente a outliers, y la ponderación asegura que la muestra represente a la población. PONDIIO corrige la no respuesta de ingresos, mejorando la precisión.
Etapa 5: Modelo de Imputación por Regresión (src/models/train_model.py)

Qué se hizo: Se entrena un modelo de regresión lineal múltiple sobre el logaritmo del ingreso real para imputar los valores faltantes (no respuesta). Las variables predictoras incluyen: horas trabajadas, sexo, nivel educativo, sector, calificación, categoría ocupacional, registro, aglomerado, año, trimestre, edad y edad al cuadrado. Se evalúa con R² y RMSE, y se generan gráficos de diagnóstico (observados vs predichos, residuos, Q-Q plot).

Por qué: La transformación logarítmica estabiliza la varianza. El modelo permite estimar el ingreso de los ocupados que no lo declararon (≈26% de la muestra), cumpliendo el Objetivo 4 del TP.
Etapa 6: Visualización y Reporte (src/visualization/plots_visualization.py y src/report/report_analysis.py)

Qué se hizo: Se generan gráficos de líneas para las tres tasas, boxplots de ingresos por educación y sexo, histograma de log-ingreso y evolución de la mediana. Finalmente, se produce un reporte en texto plano con las variaciones de tasas e ingresos entre el primer y último período.

Por qué: La visualización permite interpretar rápidamente las tendencias, y el reporte automatiza la extracción de conclusiones numéricas.
3. Instrucciones de Ejecución
3.1. Requisitos Previos
bash

# Crear y activar entorno virtual
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)
# o
source venv/bin/activate       # Linux/Mac

# Instalar dependencias
pip install pandas numpy scikit-learn matplotlib seaborn openpyxl xlrd

3.2. Estructura de Carpetas

Asegurar la siguiente estructura antes de ejecutar:
text

eph_project/
├── data/
│   ├── raw/           # Colocar los 39 archivos .zip aquí
│   └── processed/     # (se creará automáticamente)
├── reports/
│   └── figures/       # (se creará automáticamente)
└── src/               # Todo el código fuente (ver árbol arriba)

3.3. Ejecutar el Pipeline Completo
bash

# Desde la raíz del proyecto
python src/run_pipeline.py

3.4. Ejecutar Módulos Individuales (para depuración)
bash

# Solo extracción y consolidación
python src/data/build_dataset.py

# Solo construcción de features y deflación
python src/features/build_features.py

# Solo cálculo de tasas
python src/analysis/stats_analysis.py

# Solo análisis de ingresos
python src/analysis/income_analysis.py

# Solo modelo de imputación
python src/models/train_model.py

# Solo generación de gráficos
python src/visualization/plots_visualization.py

# Solo generación de reporte
python src/report/report_analysis.py

