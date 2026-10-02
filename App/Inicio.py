# -*- coding: utf-8 -*-
"""
Página inicial — contexto de la segmentación de Saber Pro
y del diálogo entre lectura cuantitativa y cualitativa.
"""
import streamlit as st

from styles import apply_styles, render_hero
from utils import init_session, render_progress_sidebar

st.set_page_config(
    page_title="Inicio | Saber 11",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
apply_styles()

with st.sidebar:
    render_progress_sidebar()
    st.markdown("---")
    st.caption(
        "Facultad de Ciencias Sociales y Económicas · "
        "Universidad del Valle"
    )

render_hero(
    "Segmentación de estudiantes en Saber 11",
    "ACP y K-Means sobre los puntajes de área, periodo 2022-2",
    kicker="Laboratorio de Analítica · Sociología",
)

st.markdown(
    """
<div class="context-box">
<h3>De un puntaje a una pregunta sociológica</h3>
<p>Saber 11 es el examen de Estado al cierre de la educación media en Colombia.
Esta base corresponde al periodo <strong>2022-2</strong>. El ICFES resume el
desempeño en cinco puntajes: lectura crítica, matemáticas, ciencias naturales,
sociales y ciudadanas, e inglés. La aplicación no clasifica “buenos” y “malos”
estudiantes. Busca <strong>perfiles</strong>: grupos que se parecen en la forma
del resultado, no solo en el puntaje global.</p>
<p>La base ya está conectada. No hay que cargarla. Cada fila es un estudiante
de <code>SB11_20222.xlsx</code>.</p>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### Qué se observa")
    st.markdown(
        """
Cada fila es un **estudiante**. Al modelo entran solo los cinco puntajes de área.

El puntaje global, el INSE, el estrato, el NSE y las características del colegio
se guardan para la página **Perfiles**. No participan en el ACP ni en K-Means.
"""
    )
with c2:
    st.markdown("### Para qué segmentar")
    st.markdown(
        """
Con cinco puntajes correlacionados, el global esconde la forma del perfil.
Dos estudiantes pueden tener un global parecido y, aun así, uno apoyarse en
lectura y el otro en matemáticas.

El ACP comprime esa estructura. K-Means propone grupos. La segmentación sirve
para **comparar perfiles**, no para producir un ranking.
"""
    )
with c3:
    st.markdown("### Qué no dice el examen")
    st.markdown(
        """
Un cluster no mide el mérito de quien presenta la prueba ni la calidad de un colegio.
El puntaje mezcla aprendizaje, condiciones de origen y la propia forma del examen.

Por eso el resultado cuantitativo se trata como una **hipótesis**: describe una
regularidad y deja abierta la pregunta de por qué ese perfil existe.
"""
    )

st.markdown("---")
st.markdown("## La relación entre lo cuantitativo y lo cualitativo")

q1, q2 = st.columns(2)
with q1:
    st.markdown(
        """
<div class="context-box">
<h3>Lo que puede hacer el número</h3>
<p>El análisis no supervisado recorre a los estudiantes a la vez y muestra
parecidos que una lectura caso por caso no alcanza a ver. Entrega cuatro cosas
concretas:</p>
<ul>
<li><strong>Un mapa.</strong> Los componentes principales ordenan la variación:
un eje de desempeño general y otros de contraste, por ejemplo matemáticas frente a lectura, o inglés frente a sociales.</li>
<li><strong>Unos grupos.</strong> K-Means reúne estudiantes con una silueta parecida de puntajes.</li>
<li><strong>Un criterio de contraste.</strong> Los clusters sirven para comparar orígenes distintos, no para representar “el promedio”.</li>
<li><strong>Una descripción controlada.</strong> Las medias dicen en qué prueba un grupo está por encima o por debajo del conjunto.</li>
</ul>
</div>
""",
        unsafe_allow_html=True,
    )
with q2:
    st.markdown(
        """
<div class="reflection-box">
<h3>Lo que solo puede hacer la lectura cualitativa</h3>
<p>El grupo no explica su propia existencia. Para pasar del perfil al sentido
hace falta volver a materiales que el puntaje no contiene:</p>
<ul>
<li><strong>El colegio:</strong> jornada, naturaleza oficial o privada, zona urbana o rural, calendario.</li>
<li><strong>El hogar:</strong> estrato, NSE, educación de la madre, internet, horas de trabajo.</li>
<li><strong>El territorio:</strong> departamento y municipio donde está el colegio.</li>
<li><strong>La prueba misma:</strong> qué cuenta como matemáticas o como lectura crítica, y qué deja por fuera.</li>
</ul>
<p>La relación fértil es de ida y vuelta. El cluster sugiere a quién entrevistar,
qué documentos leer y qué contraste armar. El trabajo cualitativo devuelve nombres,
matices y límites que obligan a reescribir la etiqueta del grupo.</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="step-card">
    <h4>Cómo leer un cluster sin convertirlo en veredicto</h4>
    <p>Un grupo alto en matemáticas y bajo en lectura no “es de ciencias”
    hasta mirar el NSE, la naturaleza del colegio y el departamento.
    La página <strong>Perfiles</strong> hace ese cruce. El número abre la pregunta;
    el caso y las condiciones de quien estudia la responden.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown("## Recorrido de la aplicación")

st.markdown(
    """
| Página | Qué ocurre |
|--------|------------|
| **Inicio** | Este contexto: qué es la segmentación y cómo se articula con una lectura cualitativa. |
| **Datos** | La base se abre sola desde la carpeta `datos`. Ahí se revisa y se estandariza. |
| **ACP / PCA** | Se comprimen las competencias y se interpretan las cargas de cada componente. |
| **K-Means** | Se elige el número de grupos y se puede exportar la base con la etiqueta. |
| **Perfiles** | Cruza los clusters con NSE, estrato, colegio, zona y departamento. |
| **Reflexiones** y **Preguntas** | Cierre: alcances, límites y consignas para discutir los resultados. |
"""
)

st.info(
    "Siguiente paso: abre **Datos** en el menú lateral. "
    "La tabla de estudiantes ya está enlazada; no hace falta subir ningún archivo."
)

st.page_link("pages/2_Datos.py", label="Ir a los datos y al preprocesamiento", icon="📂")
