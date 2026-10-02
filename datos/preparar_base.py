# -*- coding: utf-8 -*-
"""Arma la tabla de programas que consume la app, a partir del Excel oficial del ICFES.

Fuente:
https://www.icfes.gov.co/wp-content/uploads/2026/05/2026-05-11-base-de-datos-de-resultados-agregados-de-saber-pro-2025.xlsx
Resultados agregados Saber Pro 2025 (competencias genéricas), nivel programa académico.
"""
import unicodedata
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "saber_pro_2025_agregados.xlsx"
OUT = HERE / "saber_pro_2025_programas.csv"

GENERIC = {
    "LECTURA CRITICA": "lectura_critica",
    "RAZONAMIENTO CUANTITATIVO": "razonamiento_cuantitativo",
    "COMPETENCIAS CIUDADANAS": "competencias_ciudadanas",
    "COMUNICACION ESCRITA": "comunicacion_escrita",
    "INGLES": "ingles",
}


def _norm(value) -> str:
    text = unicodedata.normalize("NFKD", "" if pd.isna(value) else str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.upper().split())


def build() -> pd.DataFrame:
    usecols = [
        "AGREGACION",
        "MEDIDA_AGREGACION",
        "CANTIDADEVALUADOS",
        "NOMBRE_DEPARTAMENTO",
        "NOMBRE_MUNICIPIO",
        "NOMBRE_INSTITUCION",
        "NOMBRE_SEDE",
        "NBC",
        "ID_PROGRAMA_ACAD",
        "NOMBRE_PROGRAMA_ACAD",
        "NOMBRE_PRUEBA",
        "CATEGORIAPRUEBA",
        "PROMEDIO_GLOBAL",
        "PROMEDIO_PRUEBA",
        "DESVIACION",
    ]
    raw = pd.read_excel(SOURCE, usecols=usecols)
    raw["_agregacion"] = raw["AGREGACION"].map(_norm)
    raw["_medida"] = raw["MEDIDA_AGREGACION"].map(_norm)
    raw["_prueba"] = raw["NOMBRE_PRUEBA"].map(_norm)

    programa = raw["_agregacion"].str.startswith("PROGRAMA")
    generica = raw["CATEGORIAPRUEBA"].eq(1)
    puntaje = raw["_medida"].eq("PUNTAJE_PRUEBA") & raw["_prueba"].isin(GENERIC)
    modulos = raw.loc[programa & generica & puntaje].copy()
    modulos["variable"] = modulos["_prueba"].map(GENERIC)

    contexto = (
        modulos.groupby("ID_PROGRAMA_ACAD", as_index=False)
        .agg(
            institucion=("NOMBRE_INSTITUCION", "first"),
            sede=("NOMBRE_SEDE", "first"),
            programa=("NOMBRE_PROGRAMA_ACAD", "first"),
            nbc=("NBC", "first"),
            departamento=("NOMBRE_DEPARTAMENTO", "first"),
            municipio=("NOMBRE_MUNICIPIO", "first"),
            evaluados=("CANTIDADEVALUADOS", "max"),
        )
    )

    promedios = modulos.pivot_table(
        index="ID_PROGRAMA_ACAD",
        columns="variable",
        values="PROMEDIO_PRUEBA",
        aggfunc="mean",
    )
    desviaciones = modulos.pivot_table(
        index="ID_PROGRAMA_ACAD",
        columns="variable",
        values="DESVIACION",
        aggfunc="mean",
    )
    desviaciones = desviaciones.rename(columns=lambda col: f"desv_{col}")

    global_mask = programa & raw["_medida"].eq("PUNTAJE_GLOBAL")
    puntaje_global = (
        raw.loc[global_mask]
        .groupby("ID_PROGRAMA_ACAD")["PROMEDIO_GLOBAL"]
        .mean()
        .rename("puntaje_global")
    )

    tabla = (
        contexto.merge(promedios.reset_index(), on="ID_PROGRAMA_ACAD", how="left")
        .merge(desviaciones.reset_index(), on="ID_PROGRAMA_ACAD", how="left")
        .merge(puntaje_global.reset_index(), on="ID_PROGRAMA_ACAD", how="left")
    )
    tabla = tabla.rename(columns={"ID_PROGRAMA_ACAD": "programa_id"})

    score_cols = list(GENERIC.values())
    antes = len(tabla)
    tabla = tabla.dropna(subset=score_cols).copy()
    tabla["programa_id"] = tabla["programa_id"].astype("int64").astype(str)
    for col in score_cols + [f"desv_{c}" for c in score_cols] + ["puntaje_global", "evaluados"]:
        tabla[col] = pd.to_numeric(tabla[col], errors="coerce")

    ordered = [
        "programa_id",
        "institucion",
        "sede",
        "programa",
        "nbc",
        "departamento",
        "municipio",
        "evaluados",
        "puntaje_global",
        *score_cols,
        *[f"desv_{c}" for c in score_cols],
    ]
    tabla = tabla[ordered].sort_values(["institucion", "programa"]).reset_index(drop=True)
    print(f"programas con las 5 competencias: {len(tabla):,} (de {antes:,})")
    print(tabla["evaluados"].describe().round(1).to_string())
    tabla.to_csv(OUT, index=False, sep=";", encoding="utf-8-sig")
    print("escrito", OUT, "filas", len(tabla))
    return tabla


if __name__ == "__main__":
    build()
