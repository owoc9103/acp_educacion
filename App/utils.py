# -*- coding: utf-8 -*-
"""Utilidades compartidas: datos, preprocesamiento y gráficos."""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler, normalize

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR.parent / "datos" / "saber_pro_2025_programas.csv"

# Paleta Facultad de Ciencias Sociales y Económicas, Universidad del Valle
COLOR_RED = "#a51e2c"
COLOR_TEAL = "#008687"
COLOR_GOLD = "#f3a731"
COLOR_BLUE = "#016cb6"
CLUSTER_COLORS = [
    "#a51e2c",
    "#008687",
    "#f3a731",
    "#016cb6",
    "#6d6e71",
    "#525471",
    "#e35a4d",
    "#1c6288",
]

# Columnas de contexto: se conservan en la base y no entran al ACP
CONTEXT_NUMERIC = ["evaluados", "puntaje_global"]

SESSION_KEYS = (
    "df_raw",
    "df_with_id",
    "cc_data",
    "missing",
    "norm_data",
    "feature_names",
    "id_col",
    "uploaded_name",
    "pca_full",
    "n_components",
    "pca_final",
    "pca_cc_data",
    "loadings",
    "k_selected",
    "kmeans_labels",
    "kmeans_model",
    "steps_done",
)


def init_session():
    if "steps_done" not in st.session_state:
        st.session_state.steps_done = {"prep": False, "pca": False, "kmeans": False}


def reset_analysis_state():
    for key in SESSION_KEYS:
        if key != "steps_done":
            st.session_state.pop(key, None)
    st.session_state.steps_done = {"prep": False, "pca": False, "kmeans": False}


def render_progress_sidebar():
    st.markdown("---")
    st.markdown("### 🧭 Progreso del análisis")
    steps = st.session_state.get("steps_done", {"prep": False, "pca": False, "kmeans": False})
    st.markdown(f"{'✅' if steps.get('prep') else '⬜'} Datos preparados")
    st.markdown(f"{'✅' if steps.get('pca') else '⬜'} ACP / PCA completado")
    st.markdown(f"{'✅' if steps.get('kmeans') else '⬜'} K-Means ejecutado")


def require_step(step: str, message: str) -> bool:
    if not st.session_state.get("steps_done", {}).get(step):
        st.warning(message)
        return False
    return True


@st.cache_data(show_spinner="Leyendo la base de Saber Pro…")
def load_database() -> pd.DataFrame:
    """Lee la tabla de programas ya conectada en la carpeta datos/."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"No está la base de análisis en {DATA_PATH}. "
            "Ejecuta datos/preparar_base.py a partir del Excel del ICFES."
        )
    return pd.read_csv(DATA_PATH, sep=";", encoding="utf-8-sig")


def detect_id_column(df: pd.DataFrame) -> Optional[str]:
    for col in ("programa_id", "empresa_id", "id", "ID", "Id"):
        if col in df.columns:
            return col
    for col in df.columns:
        if col.lower().endswith("_id") or col.lower() == "id":
            return col
    if df.columns[0] not in df.select_dtypes(include="number").columns:
        return df.columns[0]
    return None


def get_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=[np.number]).copy()
    for col in df.columns:
        if col not in numeric.columns:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() > 0.8 * len(df):
                numeric[col] = converted
    return numeric


def run_preprocessing(
    df_raw: pd.DataFrame,
    id_col: Optional[str],
    exclude_cols: Optional[list] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, np.ndarray]:
    df_with_id = df_raw.copy()
    drop_cols = [c for c in [id_col, *(exclude_cols or [])] if c]
    cc_data = df_raw.drop(columns=drop_cols, errors="ignore").copy()
    cc_data = get_numeric_features(cc_data)
    missing = cc_data.isna().sum()
    if missing.sum() > 0:
        cc_data = cc_data.fillna(0)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(cc_data)
    norm_data = normalize(scaled)
    return df_with_id, cc_data, missing, norm_data


# Criterios compartidos ACP ↔ K-Means (interpretación uniforme)
Z_THRESHOLD = 0.35
LOADING_MIN = 0.12
TOP_LOADINGS = 5


def _format_loading_list(series: pd.Series, limit: int = TOP_LOADINGS) -> str:
    if series is None or len(series) == 0:
        return f"<em>Sin variables con |carga| &gt; {LOADING_MIN}</em>"
    return ", ".join(f"<code>{v}</code> ({val:+.2f})" for v, val in series.head(limit).items())


def _pc_loadings_slices(loadings: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    top_abs = loadings.abs().sort_values(ascending=False).head(TOP_LOADINGS)
    pos_vars = loadings[loadings > LOADING_MIN].sort_values(ascending=False).head(TOP_LOADINGS)
    neg_vars = loadings[loadings < -LOADING_MIN].sort_values().head(TOP_LOADINGS)
    return top_abs, pos_vars, neg_vars


def build_extreme_loadings_subset(
    loadings: pd.DataFrame,
    top_n: int = 2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Por cada PC: top_n cargas positivas y top_n negativas más extremas.
    Devuelve submatriz para heatmap y tabla resumen por componente.
    """
    summary_rows = []
    row_order = []
    seen = set()

    for pc in loadings.columns:
        ld = loadings[pc]
        pos = ld[ld > 0].sort_values(ascending=False).head(top_n)
        neg = ld[ld < 0].sort_values().head(top_n)

        for var, val in pos.items():
            summary_rows.append({
                "Componente": pc,
                "Variable": var,
                "Carga": round(float(val), 3),
                "Polo": "Positiva (+)",
            })
            if var not in seen:
                row_order.append(var)
                seen.add(var)

        for var, val in neg.items():
            summary_rows.append({
                "Componente": pc,
                "Variable": var,
                "Carga": round(float(val), 3),
                "Polo": "Negativa (−)",
            })
            if var not in seen:
                row_order.append(var)
                seen.add(var)

    if not row_order:
        subset = loadings.iloc[0:0]
    else:
        subset = loadings.loc[row_order]

    summary = pd.DataFrame(summary_rows)
    if len(summary) > 0:
        summary = summary.sort_values(["Componente", "Polo", "Carga"], ascending=[True, True, False])

    return subset, summary


def _pc_position(z: float) -> tuple[str, str, bool]:
    """Etiqueta uniforme, sentido del score y si es diferenciador."""
    if z > Z_THRESHOLD:
        return "Por encima del promedio global", "alto", True
    if z < -Z_THRESHOLD:
        return "Por debajo del promedio global", "bajo", True
    return "En la media global", "neutro", False


def _pc_symbol(z: float) -> str:
    if z > Z_THRESHOLD:
        return "↑"
    if z < -Z_THRESHOLD:
        return "↓"
    return "≈"


def _explained_var_label(pc: str, explained_var: Optional[np.ndarray]) -> str:
    if explained_var is None:
        return "—"
    idx = int(pc.replace("PC", "")) - 1
    if 0 <= idx < len(explained_var):
        return f"{explained_var[idx] * 100:.1f}%"
    return "—"


def _axis_reading_text(
    pc: str,
    pos_vars: pd.Series,
    neg_vars: pd.Series,
    sense: Optional[str] = None,
    z: Optional[float] = None,
) -> str:
    """Lectura del eje: bidireccional (ACP) o según posición del cluster (K-Means)."""
    if sense == "neutro":
        return (
            f"Score <strong>neutro</strong> en {pc} (|z| = {abs(z or 0):.2f} ≤ {Z_THRESHOLD}): "
            f"el cluster no se separa del centro de la nube en este eje."
        )
    if sense == "alto":
        return (
            f"Score <strong>alto</strong> en {pc}: perfil coherente con puntajes relativamente "
            f"<strong>elevados</strong> en {_format_loading_list(pos_vars, 3)} y/o "
            f"<strong>reducidos</strong> en {_format_loading_list(neg_vars, 3)}."
        )
    if sense == "bajo":
        return (
            f"Score <strong>bajo</strong> en {pc}: perfil coherente con puntajes relativamente "
            f"<strong>elevados</strong> en {_format_loading_list(neg_vars, 3)} y/o "
            f"<strong>reducidos</strong> en {_format_loading_list(pos_vars, 3)}."
        )
    return (
        f"Un score <strong>alto</strong> en {pc} se asocia con puntajes relativamente "
        f"<strong>elevados</strong> en {_format_loading_list(pos_vars, 3)} y/o "
        f"<strong>reducidos</strong> en {_format_loading_list(neg_vars, 3)}; "
        f"un score <strong>bajo</strong> implica el patrón opuesto."
    )


def describe_pc_loadings(
    pc_name: str,
    loadings: pd.Series,
    explained_var: Optional[np.ndarray] = None,
) -> str:
    """Interpretación uniforme de un componente según cargas del ACP."""
    top_abs, pos_vars, neg_vars = _pc_loadings_slices(loadings)
    ve = _explained_var_label(pc_name, explained_var)
    return "\n".join([
        f"<p><strong>{pc_name}</strong> · Varianza explicada: {ve}</p>",
        "<ol>",
        (
            f"<li><strong>Variables definitorias del eje (|carga|):</strong> "
            f"{_format_loading_list(top_abs)}.</li>"
        ),
        (
            f"<li><strong>Cargas positivas en {pc_name}:</strong> "
            f"{_format_loading_list(pos_vars)}.</li>"
        ),
        (
            f"<li><strong>Cargas negativas en {pc_name}:</strong> "
            f"{_format_loading_list(neg_vars)}.</li>"
        ),
        (
            f"<li><strong>Lectura del eje:</strong> "
            f"{_axis_reading_text(pc_name, pos_vars, neg_vars)}</li>"
        ),
        "</ol>",
    ])


def interpret_criteria_caption(include_z: bool = False, for_variables: bool = False) -> str:
    """Texto de criterios uniformes para pies de sección."""
    if for_variables:
        parts = ["medias estandarizadas (z) respecto a la muestra global"]
        if include_z:
            parts.append(
                f"|z| &gt; {Z_THRESHOLD} → diferenciador (↑/↓); |z| ≤ {Z_THRESHOLD} → en la media (≈)"
            )
        return "; ".join(parts) + "."
    parts = [f"|carga| &gt; {LOADING_MIN} → variables del eje"]
    if include_z:
        parts.append(f"|z| &gt; {Z_THRESHOLD} → diferenciador (↑/↓); |z| ≤ {Z_THRESHOLD} → en la media (≈)")
    return "; ".join(parts) + "; misma estructura de lectura por PC."


def interpret_component(loadings: pd.Series, top_n: int = TOP_LOADINGS) -> dict:
    """Compatibilidad: desglose de cargas con umbrales unificados."""
    top_abs, pos_vars, neg_vars = _pc_loadings_slices(loadings)
    return {
        "top_relevant": top_abs.head(top_n),
        "positive": pos_vars.head(top_n),
        "negative": neg_vars.head(top_n),
    }


def characterize_component(
    pc_name: str,
    loadings: pd.Series,
    explained_var: Optional[np.ndarray] = None,
) -> str:
    """Alias de describe_pc_loadings (misma salida HTML)."""
    return describe_pc_loadings(pc_name, loadings, explained_var)


def plot_variance_explained(ratio: np.ndarray):
    """Scree plot interactivo: varianza individual (barras) y acumulada (línea)."""
    import plotly.graph_objects as go

    ind = list(range(1, len(ratio) + 1))
    individual = ratio * 100
    cum = np.cumsum(ratio) * 100

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=ind,
            y=individual,
            name="Varianza individual",
            marker_color=COLOR_RED,
            opacity=0.75,
            hovertemplate="PC%{x}<br>Varianza individual: %{y:.2f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ind,
            y=cum,
            name="Varianza acumulada",
            mode="lines+markers",
            line=dict(color=COLOR_TEAL, width=2),
            marker=dict(size=6, color=COLOR_TEAL),
            hovertemplate="PC%{x}<br>Varianza acumulada: %{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="Varianza explicada por componente principal",
        xaxis_title="Componente principal",
        yaxis_title="Varianza explicada (%)",
        template="plotly_white",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.85)"),
        hovermode="x unified",
        height=520,
        bargap=0.05,
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray", dtick=10 if len(ind) > 15 else 1)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgray", range=[0, 100])
    return fig


def get_company_ids(df_with_id: pd.DataFrame, id_col: Optional[str]) -> list:
    """Etiqueta de programa para el hover de los gráficos."""
    if {"institucion", "programa"}.issubset(df_with_id.columns):
        labels = (
            df_with_id["institucion"].fillna("").astype(str)
            + " · "
            + df_with_id["programa"].fillna("").astype(str)
        )
        if id_col and id_col in df_with_id.columns:
            labels = df_with_id[id_col].astype(str) + " · " + labels
        return labels.tolist()
    if id_col and id_col in df_with_id.columns:
        return df_with_id[id_col].astype(str).tolist()
    return [f"Observación {i + 1}" for i in range(len(df_with_id))]


def build_clustered_export_df(
    df_with_id: pd.DataFrame,
    pca_cc_data: np.ndarray,
    labels: np.ndarray,
    n_components: int,
) -> pd.DataFrame:
    """Base original + scores PCA + cluster."""
    df = df_with_id.copy()
    for i in range(n_components):
        df[f"PC{i + 1}"] = pca_cc_data[:, i].round(6)
    df["cluster"] = labels
    return df


def get_top_variables_from_loadings(loadings: pd.DataFrame, top_n: int = 8) -> list:
    """Variables originales con mayor |carga| en el ACP (promedio entre PCs)."""
    ranking = loadings.abs().mean(axis=1).sort_values(ascending=False)
    return ranking.head(top_n).index.tolist()


def interpret_cluster_from_pcs(
    cluster_id: int,
    n_obs: int,
    pct_total: float,
    pc_means: pd.Series,
    global_pc_mean: pd.Series,
    global_pc_std: pd.Series,
    loadings: pd.DataFrame,
    explained_var: Optional[np.ndarray] = None,
    top_loadings: int = TOP_LOADINGS,
) -> str:
    """Interpretación uniforme del cluster basada estrictamente en PCs y cargas."""
    pc_cols = list(loadings.columns)
    pc_stats = []

    for pc in pc_cols:
        mu_c = float(pc_means[pc])
        mu_g = float(global_pc_mean[pc])
        sd_g = float(global_pc_std[pc]) if global_pc_std[pc] > 0 else 1.0
        z = (mu_c - mu_g) / sd_g
        position, sense, is_diff = _pc_position(z)
        pc_stats.append({
            "pc": pc, "mu_c": mu_c, "mu_g": mu_g, "z": z,
            "position": position, "sense": sense, "is_diff": is_diff,
            "ve": _explained_var_label(pc, explained_var),
        })

    profile_code = " · ".join(f"{s['pc']}{_pc_symbol(s['z'])}" for s in pc_stats)
    diff_pcs = [s["pc"] for s in pc_stats if s["is_diff"]]

    lines = [
        f"<p><strong>Cluster {cluster_id}</strong> · "
        f"N = {n_obs:,} programas · {pct_total:.1f}% del total · "
        f"Perfil PCA: <code>{profile_code}</code></p>",
        "<p><strong>Resumen de posición en componentes principales</strong></p>",
        "<ul>",
    ]
    for s in pc_stats:
        lines.append(
            f"<li><strong>{s['pc']}</strong> (VE {s['ve']}): "
            f"media = <code>{s['mu_c']:.4f}</code>, "
            f"z = <code>{s['z']:+.2f}</code> → <em>{s['position']}</em></li>"
        )
    lines.append("</ul>")

    lines.append("<p><strong>Detalle por componente principal</strong> "
                 f"(criterio uniforme: |z| &gt; {Z_THRESHOLD} para diferenciación; "
                 f"|carga| &gt; {LOADING_MIN} para variables del eje):</p>")

    for s in pc_stats:
        pc = s["pc"]
        ld = loadings[pc]
        top_abs, pos_vars, neg_vars = _pc_loadings_slices(ld)

        lines.append(f"<p><strong>{pc}</strong> — {s['position']}</p>")
        lines.append("<ol>")
        lines.append(
            f"<li><strong>Posición:</strong> media cluster <code>{s['mu_c']:.4f}</code> vs. "
            f"global <code>{s['mu_g']:.4f}</code> (z = <code>{s['z']:+.2f}</code>).</li>"
        )
        lines.append(
            f"<li><strong>Variables definitorias del eje (|carga|):</strong> "
            f"{_format_loading_list(top_abs, top_loadings)}.</li>"
        )
        lines.append(
            f"<li><strong>Cargas positivas en {pc}:</strong> "
            f"{_format_loading_list(pos_vars, top_loadings)}.</li>"
        )
        lines.append(
            f"<li><strong>Cargas negativas en {pc}:</strong> "
            f"{_format_loading_list(neg_vars, top_loadings)}.</li>"
        )
        lines.append(
            f"<li><strong>Lectura PCA:</strong> "
            f"{_axis_reading_text(pc, pos_vars, neg_vars, sense=s['sense'], z=s['z'])}</li>"
        )
        lines.append("</ol>")

    lines.append("<p><strong>Síntesis del perfil PCA</strong></p>")
    if diff_pcs:
        diff_detail = "; ".join(
            f"{s['pc']} {_pc_symbol(s['z'])} (z = {s['z']:+.2f})"
            for s in pc_stats if s["is_diff"]
        )
        lines.append(
            f"<p>El Cluster {cluster_id} se diferencia en: <strong>{', '.join(diff_pcs)}</strong> "
            f"({diff_detail}). La caracterización del perfil de competencias debe inferirse exclusivamente "
            f"desde las cargas de esos componentes.</p>"
        )
    else:
        lines.append(
            f"<p>El Cluster {cluster_id} presenta posición <strong>central</strong> en todos los "
            f"componentes analizados (ningún |z| &gt; {Z_THRESHOLD}).</p>"
        )

    return "\n".join(lines)


def build_cluster_profile_summary(
    df_result: pd.DataFrame,
    cc_data: pd.DataFrame,
    labels: np.ndarray,
    loadings: pd.DataFrame,
    n_components: int,
    top_n_vars: int = 8,
    explained_var: Optional[np.ndarray] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, dict, list]:
    """
    Resumen descriptivo por cluster: medias de PCs, variables de apoyo e interpretación PCA.
    """
    pc_cols = [f"PC{i + 1}" for i in range(n_components)]
    top_vars = get_top_variables_from_loadings(loadings, top_n_vars)
    n_total = len(labels)

    profile = cc_data[top_vars].copy()
    for pc in pc_cols:
        profile[pc] = df_result[pc].values
    profile["cluster"] = labels

    global_pc_mean = profile[pc_cols].mean()
    global_pc_std = profile[pc_cols].std().replace(0, np.nan).fillna(1.0)

    pc_rows, var_rows, notes = [], [], {}
    for cl in sorted(profile["cluster"].unique()):
        sub = profile[profile["cluster"] == cl]
        means = sub[pc_cols + top_vars].mean()
        n_obs = len(sub)
        pct = 100 * n_obs / n_total

        z_scores = (means[pc_cols] - global_pc_mean) / global_pc_std
        profile_code = " · ".join(
            f"{pc}{_pc_symbol(float(z_scores[pc]))}" for pc in pc_cols
        )

        pc_row = {
            "Cluster": int(cl),
            "N": n_obs,
            "% del total": round(pct, 1),
            "Perfil PCA": profile_code,
        }
        for pc in pc_cols:
            z = float(z_scores[pc])
            position, _, _ = _pc_position(z)
            pc_row[f"{pc} (media)"] = round(means[pc], 4)
            pc_row[f"{pc} (z)"] = round(z, 3)
            pc_row[f"{pc} (posición)"] = position
        pc_rows.append(pc_row)

        var_row = {"Cluster": int(cl), "N": n_obs}
        for var in top_vars:
            var_row[var] = round(means[var], 4)
        var_rows.append(var_row)

        notes[int(cl)] = interpret_cluster_from_pcs(
            cluster_id=int(cl),
            n_obs=n_obs,
            pct_total=pct,
            pc_means=means[pc_cols],
            global_pc_mean=global_pc_mean,
            global_pc_std=global_pc_std,
            loadings=loadings,
            explained_var=explained_var,
        )

    return (
        pd.DataFrame(pc_rows),
        pd.DataFrame(var_rows),
        notes,
        top_vars,
    )


def build_cluster_standardized_means(
    cc_data: pd.DataFrame,
    labels: np.ndarray,
    variables: Optional[list] = None,
) -> pd.DataFrame:
    """Medias por cluster expresadas como z-score respecto a la muestra global."""
    vars_use = variables if variables else list(cc_data.columns)
    global_mean = cc_data[vars_use].mean()
    global_std = cc_data[vars_use].std().replace(0, np.nan).fillna(1.0)

    rows = []
    for cl in sorted(np.unique(labels)):
        sub = cc_data.loc[labels == cl, vars_use]
        z_means = (sub.mean() - global_mean) / global_std
        row = {"Cluster": int(cl)}
        for var in vars_use:
            row[var] = round(float(z_means[var]), 3)
        rows.append(row)
    return pd.DataFrame(rows).set_index("Cluster")


def interpret_cluster_from_variables(
    cluster_id: int,
    n_obs: int,
    pct_total: float,
    z_scores: pd.Series,
    raw_means: pd.Series,
    global_means: pd.Series,
    top_n: int = TOP_LOADINGS,
) -> str:
    """Interpretación del cluster a partir de medias estandarizadas (heatmap de variables)."""
    var_stats = []
    for var in z_scores.index:
        z = float(z_scores[var])
        position, sense, is_diff = _pc_position(z)
        var_stats.append({
            "var": var,
            "z": z,
            "position": position,
            "sense": sense,
            "is_diff": is_diff,
            "mu_c": float(raw_means[var]),
            "mu_g": float(global_means[var]),
        })

    ranked = sorted(var_stats, key=lambda s: -abs(s["z"]))
    profile_code = " · ".join(
        f"<code>{s['var']}</code>{_pc_symbol(s['z'])}" for s in ranked[:5]
    )
    diff_high = [s for s in var_stats if s["is_diff"] and s["sense"] == "alto"]
    diff_low = [s for s in var_stats if s["is_diff"] and s["sense"] == "bajo"]
    diff_high.sort(key=lambda s: -s["z"])
    diff_low.sort(key=lambda s: s["z"])

    lines = [
        f"<p><strong>Cluster {cluster_id}</strong> · "
        f"N = {n_obs:,} programas · {pct_total:.1f}% del total · "
        f"Competencias destacadas: {profile_code}</p>",
        "<p><strong>Resumen de medias estandarizadas</strong> "
        f"(mismo criterio del heatmap; |z| &gt; {Z_THRESHOLD} → diferenciador):</p>",
        "<ul>",
    ]
    for s in ranked:
        lines.append(
            f"<li><strong><code>{s['var']}</code></strong>: "
            f"z = <code>{s['z']:+.2f}</code>, "
            f"media cluster = <code>{s['mu_c']:.4f}</code> vs. "
            f"global <code>{s['mu_g']:.4f}</code> → <em>{s['position']}</em></li>"
        )
    lines.append("</ul>")

    lines.append("<p><strong>Variables diferenciadoras del cluster</strong></p>")
    lines.append("<ol>")
    if diff_high:
        high_txt = ", ".join(
            f"<code>{s['var']}</code> (z = {s['z']:+.2f})" for s in diff_high[:top_n]
        )
        lines.append(
            f"<li><strong>Por encima del promedio global:</strong> {high_txt}.</li>"
        )
    else:
        lines.append(
            "<li><strong>Por encima del promedio global:</strong> "
            "<em>ninguna variable supera el umbral en este grupo.</em></li>"
        )
    if diff_low:
        low_txt = ", ".join(
            f"<code>{s['var']}</code> (z = {s['z']:+.2f})" for s in diff_low[:top_n]
        )
        lines.append(
            f"<li><strong>Por debajo del promedio global:</strong> {low_txt}.</li>"
        )
    else:
        lines.append(
            "<li><strong>Por debajo del promedio global:</strong> "
            "<em>ninguna variable supera el umbral en este grupo.</em></li>"
        )
    lines.append("</ol>")

    lines.append("<p><strong>Síntesis del perfil</strong></p>")
    if diff_high or diff_low:
        parts = []
        if diff_high:
            parts.append(
                "puntajes relativamente <strong>elevados</strong> en "
                + ", ".join(f"<code>{s['var']}</code>" for s in diff_high[:3])
            )
        if diff_low:
            parts.append(
                "puntajes relativamente <strong>reducidos</strong> en "
                + ", ".join(f"<code>{s['var']}</code>" for s in diff_low[:3])
            )
        lines.append(
            f"<p>El Cluster {cluster_id} se caracteriza por {'; '.join(parts)} "
            f"respecto al promedio de la muestra (variables del heatmap).</p>"
        )
    else:
        lines.append(
            f"<p>El Cluster {cluster_id} no presenta competencias claramente diferenciadas "
            f"(ningún |z| &gt; {Z_THRESHOLD}) entre las variables analizadas.</p>"
        )

    return "\n".join(lines)


def build_cluster_variable_interpretation(
    cc_data: pd.DataFrame,
    labels: np.ndarray,
    variables: list,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Perfil por cluster a partir del heatmap de variables:
    z-scores, medias crudas e interpretación HTML.
    """
    z_means = build_cluster_standardized_means(cc_data, labels, variables)
    global_means = cc_data[variables].mean()

    z_rows, raw_rows, notes = [], [], {}
    n_total = len(labels)

    for cl in sorted(np.unique(labels)):
        sub = cc_data.loc[labels == cl, variables]
        raw = sub.mean()
        z = z_means.loc[cl]
        n_obs = len(sub)
        pct = 100 * n_obs / n_total

        z_row = {"Cluster": int(cl), "N": n_obs, "% del total": round(pct, 1)}
        raw_row = {"Cluster": int(cl), "N": n_obs}
        for var in variables:
            z_row[var] = z[var]
            raw_row[var] = round(float(raw[var]), 4)
        z_rows.append(z_row)
        raw_rows.append(raw_row)

        notes[int(cl)] = interpret_cluster_from_variables(
            cluster_id=int(cl),
            n_obs=n_obs,
            pct_total=pct,
            z_scores=z,
            raw_means=raw,
            global_means=global_means,
        )

    return pd.DataFrame(z_rows), pd.DataFrame(raw_rows), notes


def compute_cluster_quality_metrics(
    pca_data: np.ndarray,
    labels: np.ndarray,
    kmeans_model=None,
) -> dict:
    """Métricas de calidad del clustering final."""
    from sklearn.metrics import (
        calinski_harabasz_score,
        davies_bouldin_score,
        silhouette_samples,
        silhouette_score,
    )

    avg_sil = float(silhouette_score(pca_data, labels))
    sample_sil = silhouette_samples(pca_data, labels)

    per_cluster = {}
    for cl in sorted(np.unique(labels)):
        mask = labels == cl
        per_cluster[int(cl)] = round(float(sample_sil[mask].mean()), 4)

    metrics = {
        "silhouette_promedio": round(avg_sil, 4),
        "silhouette_por_cluster": per_cluster,
        "calinski_harabasz": round(float(calinski_harabasz_score(pca_data, labels)), 2),
        "davies_bouldin": round(float(davies_bouldin_score(pca_data, labels)), 4),
    }
    if kmeans_model is not None:
        metrics["inercia"] = round(float(kmeans_model.inertia_), 2)
    return metrics


def plot_cluster_quality(pca_data: np.ndarray, labels: np.ndarray, metrics: dict):
    """Silhouette plot del modelo final + línea del promedio."""
    from sklearn.metrics import silhouette_samples
    import plotly.graph_objects as go

    sample_sil = silhouette_samples(pca_data, labels)
    avg_sil = metrics["silhouette_promedio"]
    unique_labels = sorted(np.unique(labels))
    colors = CLUSTER_COLORS

    fig = go.Figure()
    y_lower = 10

    for i, cl in enumerate(unique_labels):
        cl_sil = np.sort(sample_sil[labels == cl])
        size = len(cl_sil)
        y_upper = y_lower + size
        color = colors[i % len(colors)]

        fig.add_trace(
            go.Bar(
                x=cl_sil,
                y=np.arange(y_lower, y_upper),
                orientation="h",
                marker=dict(color=color, line=dict(width=0.5, color="white")),
                name=f"Cluster {cl}",
                hovertemplate="Silhouette: %{x:.3f}<extra>Cluster %{fullData.name}</extra>",
                showlegend=True,
            )
        )
        fig.add_annotation(
            x=-0.08,
            y=(y_lower + y_upper) / 2,
            xref="paper",
            yref="y",
            text=f"C{cl}",
            showarrow=False,
            font=dict(size=11),
        )
        y_lower = y_upper + 12

    fig.add_vline(
        x=avg_sil,
        line_dash="dash",
        line_color="#111827",
        annotation_text=f"Promedio = {avg_sil:.3f}",
        annotation_position="top right",
    )
    fig.update_layout(
        title="Silhouette por observación (modelo final)",
        xaxis_title="Coeficiente de silueta s(i)",
        yaxis_title="Observaciones (agrupadas por cluster)",
        template="plotly_white",
        height=max(420, 80 + len(labels) * 0.35),
        bargap=0,
        legend=dict(title="Cluster"),
    )
    fig.update_yaxes(showticklabels=False)
    return fig


def plot_cluster_means_heatmap(
    z_means: pd.DataFrame,
    title: str = "Medias estandarizadas por cluster",
    row_label: str = "Variable",
):
    """Heatmap de z-scores de medias cluster vs. media global."""
    import plotly.graph_objects as go

    z = z_means.values.T
    clusters = [f"Cluster {c}" for c in z_means.index]
    variables = list(z_means.columns)

    height = max(480, len(variables) * 22 + 120)
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=clusters,
            y=variables,
            colorscale="RdBu_r",
            zmid=0,
            zmin=-2.5,
            zmax=2.5,
            hovertemplate=f"Cluster: %{{x}}<br>{row_label}: %{{y}}<br>z: %{{z:.2f}}<extra></extra>",
            colorbar=dict(title="z (media)"),
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        template="plotly_white",
        height=height,
        xaxis_title="Cluster",
        yaxis_title=row_label,
        margin=dict(l=max(120, max(len(v) for v in variables) * 6), r=40, t=60, b=60),
    )
    fig.update_yaxes(autorange="reversed")
    return fig


def plot_cluster_sizes(labels: np.ndarray):
    """Barplot del número de observaciones por cluster."""
    import plotly.express as px

    counts = pd.Series(labels).value_counts().sort_index()
    df_plot = pd.DataFrame({
        "Cluster": [f"Cluster {c}" for c in counts.index],
        "Observaciones": counts.values,
        "Porcentaje (%)": (counts.values / len(labels) * 100).round(1),
    })

    fig = px.bar(
        df_plot,
        x="Cluster",
        y="Observaciones",
        text="Observaciones",
        title="Tamaño de los clusters",
        color="Cluster",
        color_discrete_sequence=CLUSTER_COLORS,
    )
    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        hovertemplate="Cluster: %{x}<br>Observaciones: %{y:,}<br>%{customdata:.1f}% del total<extra></extra>",
        customdata=df_plot["Porcentaje (%)"],
    )
    fig.update_layout(
        template="plotly_white",
        height=460,
        showlegend=False,
        yaxis_title="Número de programas",
    )
    return fig


def plot_pc_scatter(
    pca_data: np.ndarray,
    pc_x: int,
    pc_y: int,
    company_ids: Optional[list] = None,
):
    """Dispersión interactiva entre dos componentes principales."""
    import plotly.express as px

    n = len(pca_data)
    ids = company_ids if company_ids and len(company_ids) == n else [f"Programa {i + 1}" for i in range(n)]

    df_plot = pd.DataFrame({
        f"PC{pc_x}": pca_data[:, pc_x - 1],
        f"PC{pc_y}": pca_data[:, pc_y - 1],
        "programa_id": ids,
    })

    fig = px.scatter(
        df_plot,
        x=f"PC{pc_x}",
        y=f"PC{pc_y}",
        hover_name="programa_id",
        title=f"Dispersión: PC{pc_x} vs PC{pc_y}",
    )
    fig.update_traces(
        marker=dict(size=9, color=COLOR_RED, opacity=0.65, line=dict(width=1, color="white")),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            f"PC{pc_x}: %{{x:.3f}}<br>"
            f"PC{pc_y}: %{{y:.3f}}<extra></extra>"
        ),
    )
    fig.update_layout(template="plotly_white", height=560, hovermode="closest")
    fig.update_xaxes(title_text=f"PC{pc_x}", showgrid=True, gridwidth=1, gridcolor="lightgray")
    fig.update_yaxes(title_text=f"PC{pc_y}", showgrid=True, gridwidth=1, gridcolor="lightgray")
    return fig


def plot_loadings_heatmap(
    loadings: pd.DataFrame,
    scale: float = 1.4,
    show_annot: bool = True,
    title: str = "Heatmap de cargas en componentes principales",
):
    """Heatmap interactivo de cargas PCA (Plotly)."""
    import plotly.graph_objects as go

    n_vars = len(loadings)
    n_pcs = len(loadings.columns)
    max_label_len = max((len(str(v)) for v in loadings.index), default=20)

    z = loadings.values
    text = np.round(z, 2).astype(str) if show_annot else None
    annot_size = max(8, min(12, int(9 * scale)))

    height = max(520, int(n_vars * 24 * scale))
    width = max(760, int(220 + n_pcs * 90 + max_label_len * 5))

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=list(loadings.columns),
            y=list(loadings.index),
            colorscale="RdBu_r",
            zmid=0,
            zmin=-1,
            zmax=1,
            text=text,
            texttemplate="%{text}" if show_annot else None,
            textfont={"size": annot_size},
            hovertemplate="Variable: %{y}<br>%{x}: %{z:.3f}<extra></extra>",
            colorbar=dict(title="Carga"),
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        xaxis_title="Componentes principales",
        yaxis_title="Variables originales",
        template="plotly_white",
        height=height,
        width=width,
        margin=dict(l=max(180, max_label_len * 7), r=60, t=60, b=60),
    )
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=max(9, int(10 * scale))))
    fig.update_xaxes(tickfont=dict(size=11))
    return fig


def plot_kmeans_diagnostics(sse: dict, silhouette_scores: dict):
    """Gráficos interactivos: método del codo e índice Silhouette."""
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    k_values = list(sse.keys())

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Método del codo", "Evaluación Silhouette"),
        horizontal_spacing=0.12,
    )

    fig.add_trace(
        go.Scatter(
            x=k_values,
            y=list(sse.values()),
            mode="lines+markers",
            name="SSE (Inercia)",
            line=dict(color=COLOR_RED, width=2),
            marker=dict(size=8, color=COLOR_RED),
            hovertemplate="k = %{x}<br>SSE: %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=k_values,
            y=list(silhouette_scores.values()),
            mode="lines+markers",
            name="Silhouette Score",
            line=dict(color=COLOR_TEAL, width=2),
            marker=dict(size=8, color=COLOR_TEAL),
            hovertemplate="k = %{x}<br>Silhouette: %{y:.4f}<extra></extra>",
        ),
        row=1,
        col=2,
    )

    fig.update_xaxes(title_text="Número de clusters", dtick=1, row=1, col=1, showgrid=True, gridcolor="lightgray")
    fig.update_xaxes(title_text="Número de clusters", dtick=1, row=1, col=2, showgrid=True, gridcolor="lightgray")
    fig.update_yaxes(title_text="SSE (Inercia)", row=1, col=1, showgrid=True, gridcolor="lightgray")
    fig.update_yaxes(title_text="Silhouette Score promedio", row=1, col=2, showgrid=True, gridcolor="lightgray")

    fig.update_layout(
        height=480,
        template="plotly_white",
        showlegend=False,
        hovermode="x unified",
    )
    return fig


def plot_clusters(
    pca_data: np.ndarray,
    labels: np.ndarray,
    pc_x: int,
    pc_y: int,
    company_ids: Optional[list] = None,
):
    """Scatter interactivo de clústeres en espacio PCA (Plotly, leyenda categórica)."""
    import plotly.express as px

    n = len(pca_data)
    ids = company_ids if company_ids and len(company_ids) == n else [f"Programa {i + 1}" for i in range(n)]

    df_plot = pd.DataFrame({
        f"PC{pc_x}": pca_data[:, pc_x - 1],
        f"PC{pc_y}": pca_data[:, pc_y - 1],
        "cluster": [f"Cluster {c}" for c in labels],
        "programa_id": ids,
    })

    fig = px.scatter(
        df_plot,
        x=f"PC{pc_x}",
        y=f"PC{pc_y}",
        color="cluster",
        hover_name="programa_id",
        color_discrete_sequence=CLUSTER_COLORS,
        title="Visualización de clústeres con K-Means en espacio PCA",
        labels={
            f"PC{pc_x}": f"Componente Principal {pc_x} (PC{pc_x})",
            f"PC{pc_y}": f"Componente Principal {pc_y} (PC{pc_y})",
            "cluster": "Cluster",
        },
        category_orders={"cluster": [f"Cluster {c}" for c in sorted(np.unique(labels))]},
    )

    fig.update_traces(
        marker=dict(size=10, opacity=0.75, line=dict(width=1, color="black")),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Cluster: %{fullData.name}<br>"
            f"PC{pc_x}: %{{x:.3f}}<br>"
            f"PC{pc_y}: %{{y:.3f}}<extra></extra>"
        ),
    )
    fig.update_layout(
        legend_title_text="Cluster",
        width=950,
        height=620,
        template="plotly_white",
        hovermode="closest",
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")
    return fig


# Grupos de variables (saber_pro_2025_programas.csv)
VARIABLE_GROUPS = {
    "Contexto del programa": [
        "programa_id", "institucion", "sede", "programa", "nbc",
        "departamento", "municipio", "evaluados", "puntaje_global",
    ],
    "Competencias genéricas (promedio del programa)": [
        "lectura_critica", "razonamiento_cuantitativo", "competencias_ciudadanas",
        "comunicacion_escrita", "ingles",
    ],
    "Dispersión interna (desviación del programa)": [
        "desv_lectura_critica", "desv_razonamiento_cuantitativo",
        "desv_competencias_ciudadanas", "desv_comunicacion_escrita", "desv_ingles",
    ],
}
