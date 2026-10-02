# -*- coding: utf-8 -*-
"""Página 5 — Los clusters cruzados con variables que no entraron al modelo."""
import streamlit as st

from styles import apply_styles, render_hero
from utils import (
    init_session,
    plot_cluster_composition,
    plot_numeric_by_cluster,
    plot_score_profile,
    render_progress_sidebar,
    require_step,
)

st.set_page_config(
    page_title="Perfiles | Saber 11",
    page_icon="🧩",
    layout="wide",
)

init_session()
apply_styles()
with st.sidebar:
    render_progress_sidebar()

render_hero(
    "Perfiles de los clusters",
    "Los grupos salen solo de los puntajes. Aquí se leen con el colegio, el hogar y el territorio",
    kicker="Lo que el ACP no usó",
)

if not require_step("kmeans", "Primero ejecuta **K-Means** para tener los grupos."):
    st.stop()

df = st.session_state.df_with_id.copy()
labels = st.session_state.kmeans_labels
cc_data = st.session_state.cc_data
df["cluster"] = labels

st.markdown(
    """
<div class="step-card">
    <h4>Cómo leer esta página</h4>
    <p>El modelo no vio el estrato, el NSE, si el colegio es oficial o si está en zona rural.
    Si un cluster de puntajes altos concentra colegios privados, urbanos y de NSE alto,
    el perfil académico y el origen social van juntos. Esa coincidencia es una pista,
    no una explicación.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("## 1. La forma del puntaje")
st.plotly_chart(plot_score_profile(cc_data, labels), width="stretch")
st.caption("Promedio original de cada prueba dentro del cluster. No está estandarizado: se lee en la escala del ICFES.")

st.markdown("## 2. Puntaje global e índice socioeconómico")
st.caption("Estas dos variables no entraron al ACP. Sirven para ver si el grupo de puntajes también ordena el resultado global y el origen.")

left, right = st.columns(2)
with left:
    if "puntaje_global" in df.columns:
        st.plotly_chart(
            plot_numeric_by_cluster(df["puntaje_global"], labels, "Puntaje global", "Puntaje global por cluster"),
            width="stretch",
        )
with right:
    if "inse" in df.columns and df["inse"].notna().any():
        st.plotly_chart(
            plot_numeric_by_cluster(df["inse"], labels, "INSE", "INSE individual por cluster"),
            width="stretch",
        )
    else:
        st.info("Esta base no trae INSE con valores suficientes para la caja.")

st.markdown("## 3. Composición social e institucional")

CONTEXT_PLOTS = [
    ("nse", "Nivel socioeconómico del estudiante (NSE)"),
    ("estrato", "Estrato de la vivienda"),
    ("naturaleza_colegio", "Naturaleza del colegio"),
    ("area", "Zona del colegio"),
    ("genero", "Género"),
    ("bilingue", "Colegio bilingüe"),
    ("internet", "Internet en el hogar"),
    ("educacion_madre", "Educación de la madre"),
    ("depto_colegio", "Departamento del colegio"),
    ("jornada", "Jornada"),
    ("horas_trabajo", "Horas de trabajo a la semana"),
    ("tiene_etnia", "Pertenencia étnica declarada"),
]

shown = 0
for column, title in CONTEXT_PLOTS:
    if column not in df.columns:
        continue
    valid = df[column].notna() & ~df[column].astype(str).str.lower().isin(["nan", "none", ""])
    if valid.mean() < 0.25:
        continue
    top_share = df.loc[valid, column].astype(str).value_counts(normalize=True).iloc[0]
    if top_share > 0.95:
        continue
    st.plotly_chart(
        plot_cluster_composition(df.loc[valid], column, title),
        width="stretch",
    )
    shown += 1

if shown == 0:
    st.warning("No hay variables de contexto con suficiente información para cruzar.")

st.markdown("## 4. Dónde se concentran los grupos")
if "depto_colegio" in df.columns:
    top = (
        df.groupby(["cluster", "depto_colegio"])
        .size()
        .rename("Estudiantes")
        .reset_index()
    )
    top["Cluster"] = top["cluster"].map(lambda c: f"Cluster {int(c)}")
    top = top.sort_values(["cluster", "Estudiantes"], ascending=[True, False])
    resumen = top.groupby("Cluster", as_index=False).head(5)
    resumen = resumen.rename(columns={"depto_colegio": "Departamento"})
    st.dataframe(
        resumen[["Cluster", "Departamento", "Estudiantes"]],
        width="stretch",
        hide_index=True,
    )
    st.caption("Los cinco departamentos con más estudiantes dentro de cada cluster.")

st.info("Estos cruces no cambian la segmentación. Muestran con quién coincide cada perfil de puntaje.")
