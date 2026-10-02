# -*- coding: utf-8 -*-
"""Página 2 — Base conectada y preprocesamiento."""
import streamlit as st

from styles import apply_styles, render_hero
from utils import (
    CONTEXT_NUMERIC,
    DATA_PATH,
    VARIABLE_GROUPS,
    detect_id_column,
    init_session,
    load_database,
    render_progress_sidebar,
    reset_analysis_state,
    run_preprocessing,
)

st.set_page_config(
    page_title="Datos | Saber 11",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
apply_styles()

with st.sidebar:
    render_progress_sidebar()

render_hero(
    "Datos y preprocesamiento",
    "Saber 11, periodo 2022-2: la base de estudiantes se lee desde la carpeta datos",
    kicker="Sin carga manual",
)

try:
    df_source = load_database()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

if st.session_state.get("uploaded_name") != DATA_PATH.name:
    reset_analysis_state()
    st.session_state.uploaded_name = DATA_PATH.name

st.session_state.df_raw = df_source
df_raw = df_source

st.markdown(
    """
<div class="context-box">
<h3>De dónde sale esta tabla</h3>
<p>La fuente es <code>SB11_20222.xlsx</code>, microdatos de <strong>Saber 11</strong>
del periodo <strong>2022-2</strong>. Cada fila es un estudiante. Al ACP entran solo
los cinco puntajes de área: lectura crítica, matemáticas, ciencias naturales,
sociales y ciudadanas, e inglés. El puntaje global, el INSE y las variables del
colegio y del hogar se conservan para leer los grupos después, en
<strong>Perfiles</strong>.</p>
<p>Ruta conectada: <code>datos/sb11_20222.csv.gz</code>.</p>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Estudiantes", f"{df_raw.shape[0]:,}")
c2.metric("Columnas", df_raw.shape[1])
depto_col = "depto_colegio" if "depto_colegio" in df_raw.columns else None
c3.metric(
    "Departamentos del colegio",
    f"{df_raw[depto_col].nunique():,}" if depto_col else "—",
)
c4.metric("Periodo", "2022-2")

with st.expander("Vista previa de la base", expanded=False):
    st.dataframe(df_raw.head(12), width="stretch")

st.markdown("---")
st.markdown("## Estructura de variables")

for group, vars_list in VARIABLE_GROUPS.items():
    with st.expander(f"{group} ({len(vars_list)} variables)", expanded=group.startswith("Puntajes")):
        st.write(", ".join(f"`{v}`" for v in vars_list))

st.markdown("---")
st.markdown("## Preprocesamiento")

detected_id = detect_id_column(df_raw)
id_options = ["— Sin columna ID —"] + list(df_raw.columns)
default_idx = id_options.index(detected_id) if detected_id in id_options else 0
id_col = st.selectbox(
    "Columna identificador (se excluirá del análisis)",
    id_options,
    index=default_idx,
)
id_col = None if id_col == "— Sin columna ID —" else id_col
df_model = df_raw

st.markdown(
    """
<div class="step-card">
    <h4>Qué se transforma</h4>
    <p>Se aparta el identificador. El puntaje global y el INSE no entran al modelo.
    Sobre los cinco puntajes de área se revisan faltantes, se rellenan con 0 si aparecen,
    y se aplica <code>StandardScaler</code> seguido de <code>normalize</code>.
    Así inglés y matemáticas pesan por su forma, no por estar en otra escala.</p>
</div>
""",
    unsafe_allow_html=True,
)

if st.button("Ejecutar preprocesamiento", type="primary"):
    df_with_id, cc_data, missing, norm_data = run_preprocessing(
        df_model, id_col, exclude_cols=CONTEXT_NUMERIC
    )
    st.session_state.df_with_id = df_with_id
    st.session_state.cc_data = cc_data
    st.session_state.missing = missing
    st.session_state.norm_data = norm_data
    st.session_state.feature_names = list(cc_data.columns)
    st.session_state.id_col = id_col
    st.session_state.steps_done = {"prep": True, "pca": False, "kmeans": False}
    st.session_state.pop("pca_full", None)
    st.success("Preprocesamiento completado. Continúa en **ACP / PCA**.")
    st.rerun()

if st.session_state.get("steps_done", {}).get("prep"):
    cc_data = st.session_state.cc_data
    missing = st.session_state.missing

    st.markdown("#### Resultados del preprocesamiento")
    if st.session_state.id_col:
        st.success(
            f"Columna **`{st.session_state.id_col}`** apartada. "
            f"El puntaje global y el INSE quedan fuera del modelo. "
            f"**{cc_data.shape[1]}** puntajes listos para el ACP."
        )

    missing_df = missing[missing > 0].reset_index()
    missing_df.columns = ["Variable", "Valores faltantes"]
    if len(missing_df) == 0:
        st.success("No se encontraron valores faltantes en las variables del modelo.")
    else:
        st.warning(f"Faltantes detectados en **{len(missing_df)}** variables y rellenados con **0**.")
        st.dataframe(missing_df, width="stretch", hide_index=True)

    st.code(
        "scaler = StandardScaler()\n"
        "scaled = scaler.fit_transform(cc_data)\n"
        "norm_data = normalize(scaled)",
        language="python",
    )
    st.info(
        f"Matriz transformada: **{st.session_state.norm_data.shape[0]:,}** estudiantes × "
        f"**{st.session_state.norm_data.shape[1]}** puntajes. "
        "Sigue en **ACP / PCA**."
    )
    with st.expander("Estadísticas descriptivas de las variables del modelo"):
        st.dataframe(cc_data.describe().T.round(3), width="stretch")
else:
    st.warning("Ejecuta el preprocesamiento para continuar con el ACP.")
