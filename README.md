# Aplicación de Optimización: Programación Lineal 📐

## Descripción
Esta herramienta interactiva permite resolver problemas de optimización mediante los métodos **Gráfico** (para 2 variables) y **Simplex** (para N variables). Ha sido diseñada como un recurso de apoyo para la materia de **Investigación de Operaciones** de la **Licenciatura en Informática** en la **Universidad del Istmo (UNISTMO)**, campus Ixtepec.

## Características Principales
*   **Método Gráfico:** Visualización dinámica de la región factible, vértices evaluados y la línea de nivel óptima utilizando **Plotly**.
*   **Método Simplex:** Resolución paso a paso con animaciones que muestran la evolución de las tablas, selección de pivotes y análisis de variables básicas.
*   **Gestión de Resultados:**
    *   Soporte para visualización en **fracciones exactas** o decimales.
    *   Generación automática de **reportes detallados en PDF** con el planteamiento, resultados e interpretación.
*   **Interfaz Adaptativa:** Incluye un glosario de términos técnicos y soporte para modo claro y oscuro.

## Tecnologías Utilizadas
*   **Streamlit:** Framework para la interfaz de usuario web.
*   **Plotly:** Generación de gráficas interactivas.
*   **NumPy & SciPy:** Cálculos matriciales y optimización numérica.
*   **ReportLab:** Creación de documentos PDF para reportes.

## Instalación y Uso
1.  Clona este repositorio.
2.  Instala las dependencias:
    ```bash
    pip install streamlit numpy plotly scipy reportlab
    ```
3.  Ejecuta la aplicación:
    ```bash
    streamlit run app.py
    ```

Link a app web
https://programacion-lineal-nashe.streamlit.app/

## Créditos y Desarrollo
*   **Desarrolladora:** Brenda Nashelly Gómez Reyes.
*   **Institución:** Universidad del Istmo (UNISTMO), Campus Ixtepec.
*   **Colaboradores Técnicos:** Yahir Antonio Bautista Ramirez y Ulises Diaz Antonio.
*   **Versión:** 1.0.
