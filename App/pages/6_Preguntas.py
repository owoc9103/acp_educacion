# -*- coding: utf-8 -*-
"""Página 6 — Preguntas de cierre sobre la segmentación de Saber Pro."""
import streamlit as st

from styles import apply_styles, render_hero
from utils import init_session, render_progress_sidebar

st.set_page_config(
    page_title="Preguntas | Saber Pro",
    page_icon="❓",
    layout="wide",
)

init_session()
apply_styles()

with st.sidebar:
    render_progress_sidebar()

render_hero(
    "Preguntas para discutir la segmentación",
    "Consignas sobre el ACP, K-Means y el paso de un perfil de puntajes a una pregunta cualitativa",
    kicker="Saber Pro 2025",
)

st.markdown(
    """
<div class="reflection-box">
<p>Responde con lo que muestra la app: la base de programas, el ACP, las cargas,
el diagnóstico de <em>k</em>, el heatmap de medias y, si ya lo descargaste,
<code>saber_pro_con_clusters.csv</code>.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown("## Preguntas")

st.markdown(
    """
1. ¿Por qué esta base usa el **programa académico** como unidad, y no al estudiante?
   ¿Qué se gana y qué desigualdad queda invisible?

2. ¿Por qué estandarizar promedios y desviaciones antes del ACP, si todas las
   competencias genéricas se reportan en una escala parecida?

3. El puntaje global no entra al modelo. ¿Qué pasaría con la interpretación de PC1
   si se incluyera? ¿Por qué dejarlo solo como columna de lectura?

4. Al mirar las cargas de PC1 y PC2, ¿cuál componente se parece más a un
   **desempeño general** y cuál a un **contraste** entre competencias?
   Nómbralos con una frase que alguien ajeno al modelo pueda entender.

5. Si un programa tiene un score alto en PC1, ¿qué competencias lo empujan hacia
   ese lado y cuáles lo empujarían al lado contrario?

6. ¿Qué criterio usarías para conservar componentes antes de clusterizar:
   la varianza acumulada, la posibilidad de contar el eje en palabras, o la
   nitidez del gráfico? Justifica con tus números.

7. Si el codo sugiere un *k* y la silueta sugiere otro, ¿cuál elegirías para
   armar una muestra cualitativa de programas? ¿La mejor métrica es siempre
   la más útil para comparar casos?

8. ¿Qué significa que dos clusters se solapen en el plano PC1–PC2? ¿Eso invalida
   la segmentación o indica que esos programas comparten una parte del perfil?

9. Elige **dos clusters**. Para cada uno describe el perfil con el heatmap
   (qué está por encima y qué por debajo del conjunto, incluyendo la dispersión).
   Después cruza el grupo con el núcleo de conocimiento y el departamento:
   ¿el perfil coincide con el tipo de carrera o lo atraviesa?

10. Propón, para uno de esos grupos, **una pregunta cualitativa** que el puntaje
    no puede responder. Indica qué materiales usarías (plan de estudios, entrevistas,
    observación, documentos institucionales) y qué decisión **no** debería tomarse
    solo con esta segmentación.
"""
)

st.info("En **Reflexiones** está el marco para distinguir el mapa de puntajes de la explicación del caso.")
