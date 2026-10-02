# -*- coding: utf-8 -*-
"""Página 5 — Reflexiones sobre ACP, K-Means y la lectura de Saber Pro."""
import streamlit as st

from styles import apply_styles, render_hero
from utils import init_session, render_progress_sidebar

st.set_page_config(
    page_title="Reflexiones | Saber Pro",
    page_icon="💡",
    layout="wide",
)

init_session()
apply_styles()

with st.sidebar:
    render_progress_sidebar()

render_hero(
    "Reflexiones: segmentar sin clausurar el sentido",
    "Qué puede decir el ACP y K-Means sobre Saber Pro, y dónde tiene que entrar otra lectura",
    kicker="Cierre del recorrido",
)

steps = st.session_state.get("steps_done", {})
if steps.get("kmeans"):
    st.success(
        f"Análisis completo: **{st.session_state.n_components}** componentes, "
        f"**k = {st.session_state.k_selected}** grupos, "
        f"**{len(st.session_state.df_with_id):,}** programas."
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
<p>Las cinco competencias genéricas se mueven juntas: quien obtiene un puntaje alto
en lectura crítica suele obtenerlo también en las demás. El primer componente suele
recoger ese <strong>desempeño general</strong>. Los siguientes, si se conservan,
recogen <strong>contrastes</strong>: programas relativamente más cuantitativos que
escritores, o con un inglés que no sigue al resto del perfil. La desviación agrega
otra pregunta: no solo qué tan alto es el promedio, sino qué tan parejos son los
resultados dentro del programa.</p>
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
- Programas extremos jalan las primeras componentes.
- Cuántos componentes conservar es una decisión de lectura, no un umbral mágico.
- El agregado del programa esconde la desigualdad entre estudiantes.
"""
    )

st.markdown("---")
st.markdown("## Qué hace K-Means con esos perfiles")

st.markdown(
    """
<div class="reflection-box">
<h3>Grupos útiles, no grupos verdaderos</h3>
<p>No existe la etiqueta correcta de un programa. Un grupo sirve si se puede
contar con una frase precisa —en qué competencias se aparta del conjunto—
y si esa frase ayuda a elegir casos para una lectura más densa. Si el grupo
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
- Proponer un muestreo cualitativo por contraste: un programa de cada perfil, no diez del promedio.
- Cruzar el grupo con núcleo de conocimiento, departamento e institución y ver si el perfil “es” la carrera o la corta.
- Usar la dispersión interna como pista de experiencias desiguales dentro del mismo plan de estudios.
- Exportar la base con la etiqueta para seguir el análisis fuera de la app.
"""
    )
with col_d:
    st.markdown("### Lo que no alcanza")
    st.markdown(
        """
- K-Means prefiere grupos compactos y parecidos en tamaño; la realidad institucional no tiene esa forma.
- El número de grupos se elige: la silueta orienta, no decide.
- El resultado depende de cuántos componentes se hayan guardado antes.
- Un cluster no autoriza una política de calidad, un cierre de programa ni un ranking de universidades.
- La cohorte de 2025 no es la de 2024: el mapa hay que rehacerlo si cambia la prueba o la población.
"""
    )

st.markdown("---")
st.markdown("## Después de exportar")

st.markdown(
    """
1. Descarga `saber_pro_con_clusters.csv`.
2. Mira, dentro de cada grupo, la mezcla de núcleos de conocimiento, departamentos e instituciones.
3. Elige dos o tres programas cercanos al centro del grupo y dos en el borde. El centro ilustra el perfil; el borde muestra a quién le queda estrecha la etiqueta.
4. Para esos casos, abre el proyecto educativo, el plan de estudios y, si es posible, conversaciones con estudiantes y profesores.
5. Reescribe el nombre del grupo solo después de ese contraste. Hasta entonces es una descripción de puntajes, no una identidad formativa.

La segmentación cuantitativa vale como **mapa de diferencias**. La investigación cualitativa vale como **explicación situada** de algunas de esas diferencias. Ninguna de las dos sustituye a la otra.
"""
)

st.info("Sigue en **Preguntas** para las consignas de discusión.")
