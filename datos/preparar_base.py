# -*- coding: utf-8 -*-
"""Arma la tabla de estudiantes que consume la app, desde SB11_20222.xlsx.

Saber 11, periodo 2022-2 (calendario B). El ACP usa solo los cinco puntajes
de área. El puntaje global y el contexto socioeconómico se conservan para
leer los clusters, y no entran al modelo.
"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "SB11_20222.xlsx"
OUT = HERE / "sb11_20222.csv"
OUT_GZ = HERE / "sb11_20222.csv.gz"

RENAME = {
    "ESTU_CONSECUTIVO": "estudiante_id",
    "ESTU_GENERO": "genero",
    "ESTU_TIENEETNIA": "tiene_etnia",
    "ESTU_DEPTO_RESIDE": "depto_reside",
    "FAMI_ESTRATOVIVIENDA": "estrato",
    "FAMI_EDUCACIONMADRE": "educacion_madre",
    "FAMI_TIENEINTERNET": "internet",
    "FAMI_TIENECOMPUTADOR": "computador",
    "ESTU_HORASSEMANATRABAJA": "horas_trabajo",
    "COLE_NATURALEZA": "naturaleza_colegio",
    "COLE_AREA_UBICACION": "area",
    "COLE_JORNADA": "jornada",
    "COLE_BILINGUE": "bilingue",
    "COLE_CALENDARIO": "calendario",
    "COLE_DEPTO_UBICACION": "depto_colegio",
    "COLE_MCPIO_UBICACION": "municipio_colegio",
    "ESTU_NSE_INDIVIDUAL": "nse",
    "ESTU_NSE_ESTABLECIMIENTO": "nse_colegio",
    "ESTU_INSE_INDIVIDUAL": "inse",
    "PUNT_LECTURA_CRITICA": "lectura_critica",
    "PUNT_MATEMATICAS": "matematicas",
    "PUNT_C_NATURALES": "ciencias_naturales",
    "PUNT_SOCIALES_CIUDADANAS": "sociales_ciudadanas",
    "PUNT_INGLES": "ingles",
    "PUNT_GLOBAL": "puntaje_global",
    "ESTU_ESTADOINVESTIGACION": "estado",
}

SCORE_COLS = [
    "lectura_critica",
    "matematicas",
    "ciencias_naturales",
    "sociales_ciudadanas",
    "ingles",
]


def build() -> pd.DataFrame:
    raw = pd.read_excel(SOURCE, usecols=list(RENAME))
    print("filas leidas", len(raw))
    if "ESTU_ESTADOINVESTIGACION" in raw.columns:
        print(raw["ESTU_ESTADOINVESTIGACION"].value_counts(dropna=False).head(8).to_string())
    raw = raw.rename(columns=RENAME)
    for col in SCORE_COLS + ["puntaje_global", "inse"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")

    if "estado" in raw.columns:
        estado = raw["estado"].astype(str).str.upper()
        publicar = estado.str.contains("PUBLIC", na=False)
        if publicar.any() and publicar.mean() >= 0.4:
            raw = raw.loc[publicar].copy()
            print("filas con estado publicable", len(raw))

    antes = len(raw)
    raw = raw.dropna(subset=SCORE_COLS).copy()
    raw = raw[(raw[SCORE_COLS] > 0).all(axis=1)].copy()
    print(f"filas con los 5 puntajes: {len(raw):,} (de {antes:,})")

    raw["estudiante_id"] = raw["estudiante_id"].astype(str)
    for col in ("nse", "nse_colegio"):
        if col in raw.columns:
            num = pd.to_numeric(raw[col], errors="coerce")
            raw[col] = num.map(lambda v: f"NSE {int(v)}" if pd.notna(v) else pd.NA)
    for col in raw.select_dtypes(include="object").columns:
        raw[col] = raw[col].astype(str).replace({"nan": pd.NA, "None": pd.NA})

    ordered = [c for c in [
        "estudiante_id", "genero", "tiene_etnia", "depto_reside", "estrato",
        "educacion_madre", "internet", "computador", "horas_trabajo",
        "naturaleza_colegio", "area", "jornada", "bilingue", "calendario",
        "depto_colegio", "municipio_colegio", "nse", "nse_colegio", "inse",
        *SCORE_COLS, "puntaje_global",
    ] if c in raw.columns]
    raw = raw[ordered].reset_index(drop=True)
    raw.to_csv(OUT, index=False, sep=";", encoding="utf-8-sig")
    raw.to_csv(OUT_GZ, index=False, sep=";", encoding="utf-8-sig", compression="gzip")
    print("escrito", OUT, "mb", round(OUT.stat().st_size / 1e6, 2))
    print("escrito", OUT_GZ, "mb", round(OUT_GZ.stat().st_size / 1e6, 2))
    print(raw[SCORE_COLS].describe().round(1).to_string())
    return raw


if __name__ == "__main__":
    build()
