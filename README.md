# Aplicación de Optimización: Programación Lineal 📐

## Descripción
Esta herramienta interactiva permite resolver problemas de optimización mediante los métodos **Gráfico** (para 2 variables) y **Simplex** (para N variables)[cite: 1]. Ha sido diseñada como un recurso de apoyo para la materia de **Investigación de Operaciones** de la **Licenciatura en Informática** en la **Universidad del Istmo (UNISTMO)**, campus Ixtepec[cite: 1, 4].

## Características Principales
*   **Método Gráfico:** Visualización dinámica de la región factible, vértices evaluados y la línea de nivel óptima utilizando **Plotly**[cite: 1, 2].
*   **Método Simplex:** Resolución paso a paso con animaciones que muestran la evolución de las tablas, selección de pivotes y análisis de variables básicas[cite: 1, 3].
*   **Gestión de Resultados:**
    *   Soporte para visualización en **fracciones exactas** o decimales[cite: 1].
    *   Generación automática de **reportes detallados en PDF** con el planteamiento, resultados e interpretación[cite: 1].
*   **Interfaz Adaptativa:** Incluye un glosario de términos técnicos y soporte para modo claro y oscuro[cite: 1].

## Tecnologías Utilizadas
*   **Streamlit:** Framework para la interfaz de usuario web[cite: 1].
*   **Plotly:** Generación de gráficas interactivas[cite: 1, 2].
*   **NumPy & SciPy:** Cálculos matriciales y optimización numérica[cite: 2, 3].
*   **ReportLab:** Creación de documentos PDF para reportes[cite: 1].

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

## Créditos y Desarrollo
*   **Desarrolladora:** Brenda Nashelly Gómez Reyes[cite: 4].
*   **Institución:** Universidad del Istmo (UNISTMO), Campus Ixtepec[cite: 4].
*   **Colaboradores Técnicos:** Yahir Antonio Bautista Ramirez y Ulises Diaz Antonio[cite: 4].
*   **Versión:** 4.0[cite: 1].
