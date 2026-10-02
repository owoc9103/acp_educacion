# -*- coding: utf-8 -*-
"""Página 3 — K-Means, visualización y exportación de la base clusterizada."""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans

from styles import apply_styles, render_hero, render_interpret_box
from utils import (
    build_cluster_standardized_means,
    build_cluster_variable_interpretation,
    build_clustered_export_df,
    get_company_ids,
    get_top_variables_from_loadings,
    init_session,
    interpret_criteria_caption,
    plot_cluster_means_heatmap,
    plot_cluster_sizes,
    plot_clusters,
    plot_kmeans_diagnostics,
    render_progress_sidebar,
    require_step,
)

st.set_page_config(
    page_title="K-Means | Saber 11",
    page_icon="🎯",
    layout="wide",
)

init_session()
apply_styles()
with st.sidebar:
    render_progress_sidebar()

render_hero(
    "Clustering con K-Means",
    "Elección de k, segmentación en el espacio PCA y exportación",
    kicker="Grupos de estudiantes",
)

with st.expander("📐 Detalle matemático de K-Means", expanded=True):
    st.markdown(
        """
<div class="math-box">
<h3>Fundamento matemático del algoritmo K-Means</h3>
<p>K-Means particiona el espacio de observaciones en <strong>k grupos</strong> minimizando la suma
de distancias cuadradas intra-cluster. En esta aplicación, los puntos a agrupar son los estudiantes
proyectadas en el espacio PCA (<code>pca_ccData</code>).</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### 1. Notación en el espacio PCA")
    st.markdown(
        r"""
Tras el ACP, cada estudiante $i$ queda representado por un vector de scores en $\mathbb{R}^{k_{\mathrm{PCA}}}$:

$$
\mathbf{z}_i \in \mathbb{R}^{d}, \quad d = k_{\mathrm{PCA}}
$$

La matriz completa de datos transformados es $\mathbf{Z} \in \mathbb{R}^{n \times d}$, donde $n$ es
el número de estudiantes. K-Means opera sobre $\mathbf{Z}$, no sobre las $p$ variables originales.
"""
    )

    st.markdown("#### 2. Función objetivo (inercia o SSE)")
    st.markdown(
        r"""
Dado un número de clusters $K$, buscamos una partición $\mathcal{C} = \{C_1, C_2, \ldots, C_K\}$
y centroides $\boldsymbol{\mu}_1, \ldots, \boldsymbol{\mu}_K \in \mathbb{R}^{d}$ que minimicen la
**suma de cuadrados intra-cluster** (Within-Cluster Sum of Squares, WCSS), también llamada **inercia**:

$$
J = \sum_{j=1}^{K} \sum_{\mathbf{z}_i \in C_j} \|\mathbf{z}_i - \boldsymbol{\mu}_j\|_2^2
$$

En esta app, el gráfico del **método del codo** muestra $J$ (o `inertia_` de sklearn) para distintos
valores de $K$. A mayor $K$, $J$ siempre disminuye; buscamos el punto donde la mejora marginal se reduce.
"""
    )

    st.markdown("#### 3. Centroides óptimos (paso de actualización)")
    st.markdown(
        r"""
Para una partición fija, el centroide que minimiza la distancia cuadrática dentro del cluster $C_j$ es
la **media aritmética** de los puntos asignados:

$$
\boldsymbol{\mu}_j = \frac{1}{|C_j|} \sum_{\mathbf{z}_i \in C_j} \mathbf{z}_i
$$

Este es el paso **Update** (actualización) del algoritmo: recalcular cada $\boldsymbol{\mu}_j$ dada
la asignación actual.
"""
    )

    st.markdown("#### 4. Asignación de observaciones (paso de asignación)")
    st.markdown(
        r"""
Para centroides fijos, cada observación se asigna al cluster cuyo centroide esté más cercano
(en distancia euclídea):

$$
C_j = \left\{ \mathbf{z}_i : \|\mathbf{z}_i - \boldsymbol{\mu}_j\|_2 \leq \|\mathbf{z}_i - \boldsymbol{\mu}_\ell\|_2,\;
\forall \ell \neq j \right\}
$$

Equivalentemente, la etiqueta del cluster para la observación $i$ es:

$$
y_i = \arg\min_{j \in \{1,\ldots,K\}} \|\mathbf{z}_i - \boldsymbol{\mu}_j\|_2
$$

Este es el paso **Assign** (asignación) del algoritmo.
"""
    )

    st.markdown("#### 5. Algoritmo de Lloyd (iterativo)")
    st.markdown(
        r"""
K-Means alterna los dos pasos anteriores hasta convergencia:

1. **Inicializar** $K$ centroides $\boldsymbol{\mu}_1^{(0)}, \ldots, \boldsymbol{\mu}_K^{(0)}$
   (p. ej. $K$-means++ en sklearn).
2. **Repetir** hasta que las asignaciones no cambien (o se alcance `max_iter`):
   - **Assign:** asignar cada $\mathbf{z}_i$ al cluster más cercano → etiquetas $y_i$.
   - **Update:** recalcular $\boldsymbol{\mu}_j$ como media de los puntos en $C_j$.
3. **Salida:** partición final $\{C_j\}$, centroides $\{\boldsymbol{\mu}_j\}$ e inercia $J$.

En Python: `KMeans(n_clusters=K, random_state=42, n_init=10).fit_predict(pca_ccData)`.
El parámetro `n_init` ejecuta el algoritmo varias veces con distintas inicializaciones y conserva
la solución con menor inercia.
"""
    )

    st.markdown("#### 6. Método del codo e interpretación de la inercia")
    st.markdown(
        r"""
Para cada $K = 2, 3, \ldots, K_{\max}$, se calcula la inercia óptima $J(K)$. La curva $J(K)$ es
decreciente; el **codo** es el valor de $K$ donde agregar un cluster adicional ya no reduce $J$ de
forma sustancial:

$$
\Delta J(K) = J(K) - J(K+1)
$$

Si $\Delta J(K)$ es pequeño, un cluster extra aporta poca mejora y $K$ puede ser suficiente.
Este criterio es **heurístico** y debe complementarse con la pregunta de investigación.
"""
    )

    st.markdown("#### 7. Silhouette Score (calidad de la partición)")
    st.markdown(
        r"""
El **coeficiente de silueta** mide qué tan bien separada está cada observación de clusters vecinos.
Para un punto $\mathbf{z}_i$ con etiqueta $y_i = j$:

$$
a(i) = \frac{1}{|C_j|-1} \sum_{\mathbf{z}_\ell \in C_j,\, \ell \neq i} \|\mathbf{z}_i - \mathbf{z}_\ell\|_2
\quad \text{(cohesión intra-cluster)}
$$

$$
b(i) = \min_{m \neq j} \frac{1}{|C_m|} \sum_{\mathbf{z}_\ell \in C_m} \|\mathbf{z}_i - \mathbf{z}_\ell\|_2
\quad \text{(separación al cluster más cercano)}
$$

$$
s(i) = \frac{b(i) - a(i)}{\max\{a(i),\, b(i)\}} \in [-1, 1]
$$

El **Silhouette Score promedio** es $\bar{s} = \frac{1}{n}\sum_{i=1}^{n} s(i)$. Valores cercanos a 1
indican clusters compactos y bien separados; valores cercanos a 0 o negativos sugieren solapamiento.
"""
    )

    st.markdown("#### 8. Propiedades, limitaciones y conexión con esta aplicación")
    st.markdown(
        r"""
**Propiedades:**
- Complejidad aproximada $O(n \cdot K \cdot d \cdot \text{iteraciones})$.
- Converge a un **mínimo local** de $J$ (no necesariamente global).
- Asume clusters **esféricos** y de varianza similar (distancia euclídea).

**Limitaciones:**
- Sensible a **outliers** e **inicialización** (mitigado con `n_init` y `random_state`).
- Requiere fijar $K$ **a priori**.
- En alta dimensionalidad el clustering es inestable; por eso aplicamos K-Means sobre $\mathbf{Z}$
  (espacio PCA) y no sobre los cinco puntajes originales.

**En esta aplicación:**
1. Entrada: $\mathbf{Z}$ = `pca_ccData` con $d$ componentes elegidas en el ACP.
2. Diagnóstico: gráficos de $J(K)$ (codo) y $\bar{s}(K)$ (Silhouette).
3. Decisión: el usuario elige $K$ con el slider.
4. Salida: vector de etiquetas `cluster` añadido a la base original para exportación.
"""
    )

st.markdown("---")

if not require_step("pca", "⚠️ Completa primero el **ACP / PCA** antes de ejecutar K-Means."):
    st.stop()

st.markdown(
    """
<div class="step-card">
    <h4>Segmentación no supervisada</h4>
    <p>K-Means agrupa estudiantes con perfiles de puntaje similares en el espacio reducido por PCA.
    Usa los gráficos de diagnóstico para elegir <em>k</em> y luego abre <strong>Perfiles</strong>
    para cruzar los grupos con el colegio y el hogar.</p>
</div>
""",
    unsafe_allow_html=True,
)

pca_cc_data = st.session_state.pca_cc_data
n_comp = st.session_state.n_components

st.markdown("## 1. Diagnóstico de k — Codo y Silhouette")

max_k = min(10, len(pca_cc_data) - 1)
n_clust = np.arange(2, max_k + 1)

@st.cache_data(show_spinner="Calculando el codo y la silueta…")
def _k_diagnostics(data: np.ndarray, k_max: int):
    from sklearn.metrics import silhouette_score

    scores_sse, scores_sil = {}, {}
    sample = min(len(data), 8000)
    for k in range(2, k_max + 1):
        km = KMeans(n_clusters=k, random_state=0, n_init=10)
        pred = km.fit_predict(data)
        scores_sse[k] = float(km.inertia_)
        scores_sil[k] = float(
            silhouette_score(data, pred, sample_size=sample, random_state=0)
        )
    return scores_sse, scores_sil


sse, silhouette_scores = _k_diagnostics(pca_cc_data, int(max_k))

fig_diag = plot_kmeans_diagnostics(sse, silhouette_scores)
st.plotly_chart(fig_diag, width="stretch")

diag_df = pd.DataFrame({
    "k": list(sse.keys()),
    "SSE (Inercia)": [round(v, 2) for v in sse.values()],
    "Silhouette Score": [round(v, 4) for v in silhouette_scores.values()],
})
st.dataframe(diag_df, width="stretch", hide_index=True)

best_k = max(silhouette_scores, key=silhouette_scores.get)
st.info(
    f"💡 Mayor Silhouette en **k = {best_k}** ({silhouette_scores[best_k]:.4f}). "
    "Combina este criterio con el método del codo y con la pregunta de investigación."
)
if len(pca_cc_data) > 8000:
    st.caption(
        "La silueta usa una muestra de 8.000 estudiantes para poder calcularse. "
        "La inercia y los grupos finales usan la base completa."
    )

st.markdown("## 2. Selección de k y ajuste final")

k_selected = st.slider(
    "Número de clusters (k)",
    min_value=2,
    max_value=max_k,
    value=min(st.session_state.get("k_selected", 3), max_k),
)

st.code(
    f"kmeans = KMeans(n_clusters={k_selected}, random_state=42)\n"
    "labels = kmeans.fit_predict(pca_ccData)",
    language="python",
)

if st.button("▶️ Ejecutar K-Means final", type="primary"):
    kmeans = KMeans(n_clusters=k_selected, random_state=42, n_init=10)
    labels = kmeans.fit_predict(pca_cc_data)
    st.session_state.k_selected = k_selected
    st.session_state.kmeans_labels = labels
    st.session_state.kmeans_model = kmeans
    st.session_state.steps_done["kmeans"] = True
    st.success(f"K-Means completado con **k = {k_selected}**.")
    st.rerun()

if not st.session_state.get("steps_done", {}).get("kmeans"):
    st.warning("Ejecuta K-Means para ver la visualización y exportar la base.")
    st.stop()

labels = st.session_state.kmeans_labels
k_sel = st.session_state.k_selected
loadings = st.session_state.loadings
cc_data = st.session_state.cc_data
company_ids = get_company_ids(
    st.session_state.df_with_id,
    st.session_state.get("id_col"),
)

df_result = build_clustered_export_df(
    st.session_state.df_with_id,
    pca_cc_data,
    labels,
    n_comp,
)

st.markdown("---")
st.markdown("## 3. Visualización de clústeres")
st.caption(
    "Tres vistas del resultado: scatter en espacio PCA, heatmap e interpretación por variables, "
    "y tamaño de cada grupo."
)

# --- A. Scatter ACP + clusters ---
st.markdown("### A. Scatter ACP + clusters")
if n_comp >= 2:
    pc_options = list(range(1, n_comp + 1))
    c1, c2 = st.columns(2)
    with c1:
        cl_x = st.selectbox("Eje X", pc_options, index=0, key="km_pc_x")
    with c2:
        cl_y = st.selectbox("Eje Y", pc_options, index=min(1, n_comp - 1), key="km_pc_y")
    if cl_x != cl_y:
        fig_cl = plot_clusters(pca_cc_data, labels, cl_x, cl_y, company_ids=company_ids)
        st.plotly_chart(fig_cl, width="stretch")
        st.caption("Pasa el cursor sobre un punto para ver el **estudiante**. Si hay muchos, el gráfico muestra una muestra; los tamaños y el heatmap usan la base completa.")
    else:
        st.info("Selecciona dos componentes distintos para el scatter.")
else:
    st.info("Se requieren al menos 2 componentes PCA para el scatter.")

st.markdown("---")

# --- B. Heatmap medias estandarizadas (variables) ---
st.markdown("### B. Heatmap de medias estandarizadas por cluster — variables originales")
n_feat = max(2, cc_data.shape[1])
hm_n_vars = st.slider(
    "Variables en el heatmap (según |carga| en el ACP)",
    min_value=min(3, n_feat),
    max_value=n_feat,
    value=n_feat,
    key="hm_cluster_vars",
)
hm_vars = get_top_variables_from_loadings(loadings, hm_n_vars)
z_means = build_cluster_standardized_means(cc_data, labels, hm_vars)
fig_hm = plot_cluster_means_heatmap(
    z_means,
    title="Medias estandarizadas por cluster — variables originales",
    row_label="Competencia (puntaje estandarizado)",
)
st.plotly_chart(fig_hm, width="stretch")
st.caption(
    "Cada celda es la **media del cluster** en escala z respecto a la muestra global "
    "(rojo = por encima; azul = por debajo)."
)

z_profile, raw_profile, cluster_notes = build_cluster_variable_interpretation(
    cc_data, labels, hm_vars
)

st.markdown("#### Interpretación por cluster (basada en el heatmap)")
st.markdown(
    f"La lectura siguiente usa **las mismas variables y z-scores** del heatmap: "
    f"{interpret_criteria_caption(include_z=True, for_variables=True)}"
)
for cl in sorted(cluster_notes.keys()):
    render_interpret_box(cluster_notes[cl])

with st.expander("📋 Tabla de z-scores por cluster (datos del heatmap)"):
    st.dataframe(z_profile, width="stretch", hide_index=True)

with st.expander("📋 Medias originales por cluster (referencia numérica)"):
    st.dataframe(raw_profile, width="stretch", hide_index=True)

st.markdown("---")

# --- C. Tamaño de los clusters ---
st.markdown("### C. Tamaño de los clusters")
fig_sizes = plot_cluster_sizes(labels)
st.plotly_chart(fig_sizes, width="stretch")

st.markdown("---")
st.markdown("## 4. Exportar base clusterizada")

pc_cols = [f"PC{i + 1}" for i in range(n_comp)]
original_cols = list(st.session_state.df_with_id.columns)
id_col = st.session_state.get("id_col")

st.markdown(
    f"El archivo exportado reúne **{len(original_cols)} columnas originales**, "
    f"**{len(pc_cols)} componentes principales** (`{'`, `'.join(pc_cols)}`) "
    f"y la columna **`cluster`**."
)

r1, r2, r3, r4 = st.columns(4)
r1.metric("Observaciones", f"{len(df_result):,}")
r2.metric("Columnas originales", len(original_cols))
r3.metric("Componentes PCA", n_comp)
r4.metric("Clusters (k)", k_sel)

st.markdown("#### Vista previa por bloques")

tab_orig, tab_pca, tab_clust, tab_full = st.tabs([
    f"📋 Originales ({len(original_cols)})",
    f"🔬 PCA ({len(pc_cols)})",
    "🎯 Cluster",
    "📄 Base completa",
])

with tab_orig:
    st.caption("Variables de la base conectada (`sb11_20222.csv.gz`).")
    st.dataframe(df_result[original_cols].head(12), width="stretch")

with tab_pca:
    st.caption("Scores de los componentes principales seleccionados en el ACP.")
    pca_preview = ([id_col] if id_col and id_col in df_result.columns else []) + pc_cols
    st.dataframe(df_result[pca_preview].head(12), width="stretch")

with tab_clust:
    st.caption("Etiqueta de cluster asignada por K-Means.")
    cluster_preview = []
    if id_col and id_col in df_result.columns:
        cluster_preview.append(id_col)
    elif original_cols:
        cluster_preview.append(original_cols[0])
    cluster_preview.append("cluster")
    st.dataframe(df_result[cluster_preview].head(12), width="stretch")

with tab_full:
    st.caption("Base original + PCA + cluster (contenido exacto del CSV descargable).")
    st.dataframe(df_result.head(12), width="stretch")

dist = df_result["cluster"].value_counts().sort_index().reset_index()
dist.columns = ["Cluster", "Cantidad"]
dist["Porcentaje (%)"] = (dist["Cantidad"] / len(df_result) * 100).round(1)
st.dataframe(dist, width="stretch", hide_index=True)

csv_bytes = df_result.to_csv(index=False, sep=";").encode("utf-8-sig")
st.download_button(
    label="Descargar sb11_con_clusters.csv",
    data=csv_bytes,
    file_name="sb11_con_clusters.csv",
    mime="text/csv",
    type="primary",
)

st.success(
    f"El CSV incluye **{len(original_cols)} columnas originales** + **{len(pc_cols)} PCs** + **`cluster`**. "
    "Revisa **Perfiles**, **Reflexiones** y **Preguntas** en el menú lateral."
)
