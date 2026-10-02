# -*- coding: utf-8 -*-
"""Página 5 — Reflexiones sobre ACP, K-Means y la lectura de Saber Pro."""
import streamlit as st

from styles import apply_styles, render_hero
from utils import init_session, render_progress_sidebar

st.set_page_config(
    page_title="Reflexiones | Saber 11",
    page_icon="💡",
    layout="wide",
)

init_session()
apply_styles()

with st.sidebar:
    render_progress_sidebar()

render_hero(
    "Reflexiones: segmentar sin clausurar el sentido",
    "Qué puede decir el ACP y K-Means sobre Saber 11, y dónde tiene que entrar otra lectura",
    kicker="Cierre del recorrido",
)

steps = st.session_state.get("steps_done", {})
if steps.get("kmeans"):
    st.success(
        f"Análisis completo: **{st.session_state.n_components}** componentes, "
        f"**k = {st.session_state.k_selected}** grupos, "
        f"**{len(st.session_state.df_with_id):,}** estudiantes."
    )
elif steps.get("pca"):
    st.info("El ACP ya está hecho. Falta correr K-Means para cerrar la segmentación.")
else:
    st.info("Esta página se puede leer en cualquier momento. Gana precisión cuando ya hay grupos.")

st.markdown("---")
st.markdown("## Qué hace el ACP con estas competencias")

st.markdown(
    """
<div class="reflection-box">
<h3>Una forma, no un ranking</h3>
<p>Los cinco puntajes de área se mueven juntos: quien obtiene un puntaje alto
en lectura crítica suele obtenerlo también en las demás. El primer componente suele
recoger ese <strong>desempeño general</strong>. Los siguientes, si se conservan,
recogen <strong>contrastes</strong>: estudiantes relativamente más fuertes en
matemáticas que en lectura, o con un inglés que no sigue al resto del perfil.</p>
</div>
""",
    unsafe_allow_html=True,
)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("### Lo que sí permite")
    st.markdown(
        """
- Ver la redundancia entre competencias en lugar de comentar cada promedio por separado.
- Separar el “van bien en todo” del “van bien en una cosa y no en otra”.
- Dejar un espacio corto y comparable donde K-Means no se pierde entre escalas distintas.
- Volver de cada componente a las competencias que lo definen, mediante las cargas.
"""
    )
with col_b:
    st.markdown("### Lo que no alcanza")
    st.markdown(
        """
- El componente es una combinación lineal: hay que traducirlo, no bautizarlo de una vez.
- Relaciones no lineales entre competencias pueden quedar aplanadas.
- Estudiantes con puntajes extremos jalan las primeras componentes.
- Cuántos componentes conservar es una decisión de lectura, no un umbral mágico.
- El puntaje no dice en qué condiciones estudió esa persona. Eso se mira en **Perfiles**.
"""
    )

st.markdown("---")
st.markdown("## Qué hace K-Means con esos perfiles")

st.markdown(
    """
<div class="reflection-box">
<h3>Grupos útiles, no grupos verdaderos</h3>
<p>No existe la etiqueta correcta de un estudiante. Un grupo sirve si se puede
contar con una frase precisa —en qué puntajes se aparta del conjunto—
y si esa frase ayuda a mirar el origen social del grupo. Si el grupo
solo repite “alto, medio, bajo”, el puntaje global bastaba y el clustering
no aportó una forma.</p>
</div>
""",
    unsafe_allow_html=True,
)

col_c, col_d = st.columns(2)
with col_c:
    st.markdown("### Lo que sí permite")
    st.markdown(
        """
- Comparar, en **Perfiles**, si el grupo de puntajes coincide con el NSE, el estrato o el tipo de colegio.
- Ver si un mismo perfil aparece en varios departamentos o se concentra en unos pocos.
- Exportar la base con la etiqueta para seguir el análisis fuera de la app.
"""
    )
with col_d:
    st.markdown("### Lo que no alcanza")
    st.markdown(
        """
- K-Means prefiere grupos compactos y parecidos en tamaño; la población estudiantil no tiene esa forma.
- El número de grupos se elige: la silueta orienta, no decide.
- El resultado depende de cuántos componentes se hayan guardado antes.
- Un cluster no autoriza un ranking de colegios ni una decisión sobre una persona.
- Esta cohorte es la de 2022-2. Otra aplicación del examen puede ordenarse distinto.
"""
    )

st.markdown("---")
st.markdown("## Después de exportar")

st.markdown(
    """
1. Descarga `sb11_con_clusters.csv` o revisa la página **Perfiles**.
2. Mira, dentro de cada grupo, la mezcla de NSE, estrato, naturaleza del colegio y departamento.
3. El grupo se nombra por sus puntajes. El cruce con el origen dice si ese nombre también es social.

La segmentación cuantitativa vale como **mapa de diferencias**. La lectura del contexto vale como **pista**, no como causa. Ninguna de las dos sustituye a la otra.
"""
)

st.info("Sigue en **Preguntas** para las consignas de discusión.")
