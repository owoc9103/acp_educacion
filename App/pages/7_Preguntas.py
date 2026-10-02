# -*- coding: utf-8 -*-
"""Página 6 — Preguntas de cierre sobre la segmentación de Saber Pro."""
import streamlit as st

from styles import apply_styles, render_hero
from utils import init_session, render_progress_sidebar

st.set_page_config(
    page_title="Preguntas | Saber 11",
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
    kicker="Saber 11 · 2022-2",
)

st.markdown(
    """
<div class="reflection-box">
<p>Responde con lo que muestra la app: la base de programas, el ACP, las cargas,
el diagnóstico de <em>k</em>, el heatmap de medias y, si ya lo descargaste,
<code>sb11_con_clusters.csv</code> y la página <strong>Perfiles</strong>.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown("## Preguntas")

st.markdown(
    """
1. ¿Por qué el ACP usa solo los **cinco puntajes de área** y deja por fuera el
   puntaje global, el NSE y el estrato?

2. ¿Por qué estandarizar esos puntajes si ya vienen en una escala parecida?

3. Al mirar las cargas, ¿cuál componente se parece más a un **desempeño general**
   y cuál a un **contraste** entre pruebas?

4. Si un estudiante tiene un score alto en PC1, ¿qué puntajes lo empujan hacia
   ese lado?

5. ¿Qué criterio usarías para conservar componentes: varianza acumulada,
   la posibilidad de contar el eje en palabras, o la nitidez del gráfico?

6. Si el codo sugiere un *k* y la silueta sugiere otro, ¿cuál elegirías para
   comparar condiciones de origen? ¿La mejor métrica es siempre la más útil?

7. ¿Qué significa que dos clusters se solapen en el plano PC1–PC2?

8. Elige **dos clusters**. Describe el perfil de puntajes y, con la página
   **Perfiles**, di si ese perfil coincide con el NSE, la naturaleza del colegio
   o la zona.

9. Propón **una pregunta cualitativa** que el puntaje no puede responder para
   uno de esos grupos, y qué decisión **no** debería tomarse solo con esta
   segmentación.
"""
)

st.info("En **Reflexiones** está el marco para distinguir el mapa de puntajes de la explicación del caso.")
