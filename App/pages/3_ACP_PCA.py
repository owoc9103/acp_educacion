# -*- coding: utf-8 -*-
"""Página 2 — Análisis de Componentes Principales (ACP / PCA)."""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.decomposition import PCA

from styles import apply_styles, render_hero, render_interpret_box
from utils import (
    build_extreme_loadings_subset,
    describe_pc_loadings,
    get_company_ids,
    init_session,
    interpret_criteria_caption,
    plot_loadings_heatmap,
    plot_pc_scatter,
    plot_variance_explained,
    render_progress_sidebar,
    require_step,
)

st.set_page_config(
    page_title="ACP / PCA | Saber 11",
    page_icon="🔬",
    layout="wide",
)

init_session()
apply_styles()
with st.sidebar:
    render_progress_sidebar()

render_hero(
    "Análisis de Componentes Principales",
    "Varianza explicada, cargas y lectura de las competencias genéricas",
    kicker="ACP",
)

with st.expander("📐 Detalle matemático del ACP", expanded=True):
    st.markdown(
        """
<div class="math-box">
<h3>Fundamento matemático del Análisis de Componentes Principales</h3>
<p>El ACP busca nuevas variables (componentes principales) que sean combinaciones lineales de las
variables originales y que capturen la mayor variabilidad posible del conjunto de datos, en orden decreciente.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### 1. Notación y matriz de datos")
    st.markdown(
        r"""
Tras el preprocesamiento, trabajamos con una matriz de datos estandarizados y normalizados:

$$
\mathbf{X} \in \mathbb{R}^{n \times p}
$$

donde $n$ es el número de estudiantes (observaciones) y $p$ el número de puntajes de área (variables).
Cada fila es un vector $\mathbf{x}_i^\top \in \mathbb{R}^{p}$.
"""
    )

    st.markdown("#### 2. Matriz de covarianzas (muestral)")
    st.markdown(
        r"""
La estructura de dependencia lineal entre variables se resume en la matriz de covarianzas muestral:

$$
\mathbf{S} = \frac{1}{n-1}\,\mathbf{X}^\top \mathbf{X}
$$

(para datos ya centrados en cero; con `StandardScaler`, cada columna tiene media 0 y varianza 1).
El elemento $s_{jk}$ mide cómo covarian las variables $j$ y $k$.
"""
    )

    st.markdown("#### 3. Descomposición en valores y vectores propios")
    st.markdown(
        r"""
El núcleo del ACP es la **descomposición espectral** de $\mathbf{S}$:

$$
\mathbf{S} = \mathbf{V}\,\mathbf{\Lambda}\,\mathbf{V}^\top
$$

donde:

- $\mathbf{\Lambda} = \mathrm{diag}(\lambda_1, \lambda_2, \ldots, \lambda_p)$ con
  $\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_p \geq 0$ (valores propios),
- $\mathbf{V} = [\mathbf{v}_1 \mid \mathbf{v}_2 \mid \cdots \mid \mathbf{v}_p]$ es ortogonal
  ($\mathbf{V}^\top\mathbf{V} = \mathbf{I}$) y sus columnas son los **vectores propios** (direcciones principales).
"""
    )

    st.markdown("#### 4. Componentes principales y scores")
    st.markdown(
        r"""
La **$j$-ésima componente principal** es la proyección de los datos sobre el vector propio $\mathbf{v}_j$:

$$
Z_j = \mathbf{X}\,\mathbf{v}_j
$$

En forma matricial, conservando las primeras $k$ componentes ($\mathbf{V}_k = [\mathbf{v}_1 \mid \cdots \mid \mathbf{v}_k]$):

$$
\mathbf{Z} = \mathbf{X}\,\mathbf{V}_k \in \mathbb{R}^{n \times k}
$$

Cada columna $Z_j$ es el **score** de la componente $j$ para todos los estudiantes.
En esta app, `pca_ccData` corresponde a $\mathbf{Z}$.
"""
    )

    st.markdown("#### 5. Varianza explicada")
    st.markdown(
        r"""
La varianza (inercia) capturada por la componente $j$ es $\lambda_j$. La **varianza explicada proporcional** es:

$$
\text{VE}_j = \frac{\lambda_j}{\displaystyle\sum_{i=1}^{p}\lambda_i}
$$

La **varianza acumulada** hasta la componente $k$:

$$
\text{VE}_{\mathrm{acum}}(k) = \frac{\displaystyle\sum_{i=1}^{k}\lambda_i}{\displaystyle\sum_{i=1}^{p}\lambda_i}
$$

Este es el criterio del gráfico de varianza explicada: elegir $k$ tal que $\text{VE}_{\mathrm{acum}}(k)$ sea
suficientemente alto (p. ej. 80–90 %).
"""
    )

    st.markdown("#### 6. Cargas (loadings)")
    st.markdown(
        r"""
Las **cargas** relacionan cada variable original con cada componente. En `sklearn`, la matriz
`components_` contiene los vectores propios (filas) $\mathbf{w}_j^\top$, de modo que:

$$
\mathbf{Z} = \mathbf{X}\,\mathbf{W}^\top, \quad \mathbf{W} = \begin{bmatrix} \mathbf{w}_1^\top \\ \vdots \\ \mathbf{w}_k^\top \end{bmatrix}
$$

El heatmap de cargas muestra $\mathbf{W}^\top$: cada columna indica qué variables pesan en cada PC.
Valores grandes en magnitud (positivos o negativos) señalan mayor contribución a esa dimensión.
"""
    )

    st.markdown("#### 7. Propiedades clave y optimización")
    st.markdown(
        r"""
- **PC1** maximiza $\mathrm{Var}(\mathbf{X}\mathbf{v})$ sujeto a $\|\mathbf{v}\|=1$.
- **PC2** maximiza la varianza restante siendo **ortogonal** a PC1: $\mathbf{v}_2^\top \mathbf{v}_1 = 0$.
- En general, las componentes son **ortogonales** e **incorrelacionadas**:
  $\mathrm{Cov}(Z_i, Z_j) = 0$ para $i \neq j$.
- El ACP es equivalente a una **descomposición en valores singulares (SVD)** de $\mathbf{X}$:
  $\mathbf{X} = \mathbf{U}\mathbf{\Sigma}\mathbf{V}^\top$, donde los valores singulares al cuadrado
  (normalizados) coinciden con los autovalores de $\mathbf{S}$.
"""
    )

    st.markdown("#### 8. Conexión con esta aplicación")
    st.markdown(
        r"""
En el flujo de la aplicación:

1. $\mathbf{X}$ = `norm_ccData` (datos estandarizados y normalizados).
2. `PCA.fit_transform` calcula $\mathbf{Z}$ con las $k$ componentes seleccionadas.
3. El gráfico de varianza usa $\text{VE}_j$ y $\text{VE}_{\mathrm{acum}}(k)$.
4. El heatmap muestra las cargas para interpretar qué puntajes definen cada eje.
5. K-Means se aplica sobre $\mathbf{Z}$, no sobre las $p$ variables originales.
"""
    )

st.markdown("---")

if not require_step("prep", "⚠️ Primero ejecuta el preprocesamiento en la página **Datos**."):
    st.stop()

st.markdown(
    """
<div class="step-card">
    <h4>¿Qué hace el ACP con Saber 11?</h4>
    <p>El ACP rota los cinco puntajes de área para separar un eje de desempeño general
    de los contrastes entre pruebas, antes de aplicar K-Means.</p>
</div>
""",
    unsafe_allow_html=True,
)

norm_data = st.session_state.norm_data
feature_names = st.session_state.feature_names
n_features = norm_data.shape[1]
max_components = min(n_features, norm_data.shape[0])

if "pca_full" not in st.session_state:
    pca_full = PCA(n_components=max_components)
    pca_full.fit(norm_data)
    st.session_state.pca_full = pca_full

pca_full = st.session_state.pca_full
ratio = pca_full.explained_variance_ratio_
cum_ratio = np.cumsum(ratio)

st.markdown("## 1. Varianza explicada")
fig_var = plot_variance_explained(ratio)
st.plotly_chart(fig_var, width="stretch")

variance_df = pd.DataFrame({
    "Componente": [f"PC{i}" for i in range(1, len(ratio) + 1)],
    "N° componente": range(1, len(ratio) + 1),
    "Varianza explicada (%)": (ratio * 100).round(2),
    "Varianza acumulada (%)": (cum_ratio * 100).round(2),
})
st.dataframe(variance_df, width="stretch", hide_index=True)

st.markdown("## 2. Selección interactiva de componentes")
st.markdown(
    "Revisa la tabla y el gráfico. Un criterio habitual es conservar componentes hasta alcanzar "
    "**≥ 80–90 %** de varianza acumulada o hasta donde la curva se aplana."
)

n_components = st.slider(
    "Número de componentes principales",
    min_value=2,
    max_value=max_components,
    value=min(st.session_state.get("n_components", 2), max_components),
)

m1, m2, m3 = st.columns(3)
m1.metric("Componentes", n_components)
m2.metric("Varianza acumulada", f"{cum_ratio[n_components - 1] * 100:.1f} %")
m3.metric("Variables originales", n_features)

if st.button("▶️ Aplicar PCA con esta selección", type="primary"):
    pca_final = PCA(n_components=n_components)
    pca_cc_data = pca_final.fit_transform(norm_data)
    loadings = pd.DataFrame(
        pca_final.components_.T,
        columns=[f"PC{i+1}" for i in range(pca_final.n_components_)],
        index=feature_names,
    )
    st.session_state.n_components = n_components
    st.session_state.pca_final = pca_final
    st.session_state.pca_cc_data = pca_cc_data
    st.session_state.loadings = loadings
    st.session_state.steps_done["pca"] = True
    st.session_state.steps_done["kmeans"] = False
    st.success(f"PCA aplicado con **{n_components}** componentes. Continúa en **K-Means**.")
    st.rerun()

if not st.session_state.get("steps_done", {}).get("pca"):
    st.warning("Confirma la selección de componentes con el botón anterior.")
    st.stop()

pca_cc_data = st.session_state.pca_cc_data
loadings = st.session_state.loadings
n_comp = st.session_state.n_components

st.markdown("---")
st.markdown("## 3. Proyección en el espacio PCA")
st.code(
    f"n_components = {n_comp}\n"
    "pca_final = PCA(n_components=n_components)\n"
    "pca_final.fit(norm_ccData)\n"
    "pca_ccData = pca_final.fit_transform(norm_ccData)",
    language="python",
)

if n_comp >= 2:
    pc_options = list(range(1, n_comp + 1))
    c1, c2 = st.columns(2)
    with c1:
        pc_x = st.selectbox("Eje X — componente", pc_options, index=0)
    with c2:
        pc_y = st.selectbox("Eje Y — componente", pc_options, index=min(1, n_comp - 1))
    if pc_x != pc_y:
        company_ids = get_company_ids(
            st.session_state.df_with_id,
            st.session_state.get("id_col"),
        )
        fig_sc = plot_pc_scatter(pca_cc_data, pc_x, pc_y, company_ids=company_ids)
        st.plotly_chart(fig_sc, width="stretch")
        st.caption("Pasa el cursor sobre un punto para ver el **estudiante**. Si hay muchos, el gráfico muestra una muestra.")
    else:
        st.info("Selecciona dos componentes distintos.")

st.markdown("---")
st.markdown("## 4. Heatmap de cargas e interpretación")

st.markdown(
    "Las **cargas** indican qué variables pesan en cada componente. "
    "Valores altos (positivos o negativos) señalan mayor contribución."
)

hm_c1, hm_c2 = st.columns([2, 1])
with hm_c1:
    hm_scale = st.slider(
        "Escala del heatmap (tamaño / legibilidad)",
        min_value=1.0,
        max_value=2.5,
        value=1.6,
        step=0.1,
        help="Aumenta el valor si los nombres de las variables se ven pequeños o cortados.",
    )
with hm_c2:
    show_annot = st.checkbox("Mostrar valores en celdas", value=True)

st.caption(
    f"**{len(loadings)}** variables × **{len(loadings.columns)}** componentes — "
    "usa el scroll o el zoom de Plotly para explorar el gráfico."
)

fig_hm = plot_loadings_heatmap(loadings, scale=hm_scale, show_annot=show_annot)
st.plotly_chart(fig_hm, width="stretch")

st.markdown("---")
st.markdown("### 4.1 Cargas extremas por componente (complemento)")
st.markdown(
    "Vista resumida del apartado anterior: para cada PC se muestran las "
    "**2 variables con mayor carga positiva** y las **2 con carga negativa más extrema**. "
    "Facilita identificar los polos opuestos de cada eje sin recorrer el heatmap completo."
)

ext_loadings, ext_summary = build_extreme_loadings_subset(loadings, top_n=2)

if len(ext_loadings) == 0:
    st.warning("No se encontraron cargas positivas o negativas para construir el heatmap resumido.")
else:
    st.caption(
        f"**{len(ext_loadings)}** variables seleccionadas × **{len(ext_loadings.columns)}** componentes."
    )
    fig_ext = plot_loadings_heatmap(
        ext_loadings,
        scale=max(1.0, hm_scale * 0.95),
        show_annot=show_annot,
        title="Top 2 cargas positivas y top 2 negativas por componente",
    )
    st.plotly_chart(fig_ext, width="stretch")

    st.markdown("#### Variables seleccionadas por componente")
    st.dataframe(ext_summary, width="stretch", hide_index=True)

st.markdown("---")
st.markdown("### Interpretación por componente")
st.markdown(
    f"Cada eje se lee con los **mismos criterios** que en K-Means: {interpret_criteria_caption()} "
    "Aquí la lectura es **bidireccional** (alto/bajo); en clusters se aplica según la posición z del grupo."
)

explained_var = None
if st.session_state.get("pca_final") is not None:
    explained_var = st.session_state.pca_final.explained_variance_ratio_

for i in range(n_comp):
    pc_name = f"PC{i+1}"
    render_interpret_box(describe_pc_loadings(pc_name, loadings[pc_name], explained_var))

with st.expander("📋 Tabla completa de cargas"):
    st.dataframe(loadings.round(3), width="stretch")

st.info("Cuando hayas revisado el ACP, continúa en **K-Means** para segmentar a los estudiantes.")
