# -*- coding: utf-8 -*-
"""
Página inicial — contexto de la segmentación de Saber Pro
y del diálogo entre lectura cuantitativa y cualitativa.
"""
import streamlit as st

from styles import apply_styles, render_hero
from utils import init_session, render_progress_sidebar

st.set_page_config(
    page_title="Inicio | Saber Pro",
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
    "Segmentación de programas en Saber Pro",
    "Análisis de componentes principales y K-Means sobre las competencias genéricas",
    kicker="Laboratorio de Analítica · Sociología",
)

st.markdown(
    """
<div class="context-box">
<h3>De un puntaje a una pregunta sociológica</h3>
<p>Saber Pro es el examen de Estado que presenta quien está por terminar un programa de
educación superior en Colombia. El ICFES resume ese desempeño en cinco
<strong>competencias genéricas</strong>: lectura crítica, razonamiento cuantitativo,
competencias ciudadanas, comunicación escrita e inglés. Esta aplicación no clasifica
“buenos” y “malos” programas. Busca <strong>perfiles</strong>: grupos de programas que
se parecen entre sí en la forma del resultado, no solo en el promedio global.</p>
<p>La base ya está conectada. No hay que cargarla. Corresponde a los
<strong>resultados agregados de Saber Pro 2025</strong>, la publicación más reciente
del ICFES (mayo de 2026), en el nivel de <strong>programa académico</strong>.</p>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### Qué se observa")
    st.markdown(
        """
Cada fila es un **programa**, no un estudiante. De cada uno se usan:

- el promedio en las cinco competencias genéricas;
- la **desviación** interna, es decir qué tan desigual es el resultado dentro del programa;
- el contexto: institución, sede, núcleo de conocimiento, municipio y número de evaluados.

El puntaje global se conserva para leer los grupos, y no entra al modelo: es un resumen de las mismas pruebas.
"""
    )
with c2:
    st.markdown("### Para qué segmentar")
    st.markdown(
        """
Con cinco competencias correlacionadas, el promedio esconde la forma del perfil.
Dos programas pueden tener un global parecido y, aun así, uno apoyarse en lectura
y escritura y el otro en razonamiento cuantitativo.

El ACP comprime esa estructura. K-Means propone grupos. La segmentación sirve para
**comparar perfiles de formación**, no para producir un ranking.
"""
    )
with c3:
    st.markdown("### Qué no dice el examen")
    st.markdown(
        """
Un cluster no mide la calidad de una universidad ni el mérito de sus estudiantes.
El puntaje mezcla aprendizaje, selectividad, condiciones de origen y la propia
forma de la prueba.

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
<p>El análisis no supervisado recorre miles de programas a la vez y muestra
parecidos que una lectura caso por caso no alcanza a ver. Entrega cuatro cosas
concretas:</p>
<ul>
<li><strong>Un mapa.</strong> Los componentes principales ordenan la variación:
un eje de desempeño general y otros de contraste, por ejemplo cuantitativo frente a escrito, o inglés frente a competencias ciudadanas.</li>
<li><strong>Unos grupos.</strong> K-Means reúne programas con una silueta parecida de puntajes y de dispersión interna.</li>
<li><strong>Un criterio de muestreo.</strong> Los clusters sirven para elegir casos distintos, no para “representar el promedio”.</li>
<li><strong>Una descripción controlada.</strong> Las medias estandarizadas dicen en qué competencia un grupo está por encima o por debajo del conjunto.</li>
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
<li><strong>El currículo y la pedagogía:</strong> qué se enseña, cómo se evalúa y qué cuenta como logro en ese programa.</li>
<li><strong>Las trayectorias:</strong> quién llega, con qué capital escolar, cuánto trabaja, en qué municipio estudia.</li>
<li><strong>La institución:</strong> carácter académico, selectividad, recursos y la promesa formativa que hace en público.</li>
<li><strong>La prueba misma:</strong> qué entiende el ICFES por “competencia ciudadana” o por “lectura crítica”, y qué deja por fuera.</li>
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
    <p>Un grupo con lectura crítica alta y razonamiento cuantitativo bajo no “es de humanidades”
    hasta que se mire el núcleo de conocimiento, la dispersión interna y algunos programas
    concretos. La desviación importa: un promedio alto con mucha dispersión habla de una
    experiencia desigual dentro del mismo programa. El número abre la pregunta;
    el caso, el currículo y las voces de quienes estudian y enseñan la responden.</p>
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
| **K-Means** | Se elige el número de grupos, se perfilan y se puede exportar la base con la etiqueta. |
| **Reflexiones** y **Preguntas** | Cierre: alcances, límites y consignas para discutir los resultados. |
"""
)

st.info(
    "Siguiente paso: abre **Datos** en el menú lateral. "
    "La tabla de programas ya está enlazada; no hace falta subir ningún archivo."
)

st.page_link("pages/2_Datos.py", label="Ir a los datos y al preprocesamiento", icon="📂")
