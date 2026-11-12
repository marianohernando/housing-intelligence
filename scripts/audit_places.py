"""T1 data audit (D-216): our facility counts against the official totals, and what we repaired.

Prints Markdown. Official totals are copied from the cited documents (12 Nov 2026); our counts
come from the local database. Usage:
    uv run python scripts/audit_places.py > evidence/gate-01/<date>/audit-places.md
"""

import sys
from dataclasses import dataclass

from sqlalchemy import Connection, bindparam, create_engine, text

from hi_db.settings import DatabaseSettings

PRIMARIA = (
    "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA",
    "COLEGIO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA",
    "COLEGIO DE EDUCACIÓN PRIMARIA",
    "CENTRO PRIVADO DE EDUCACIÓN INFANTIL Y PRIMARIA",
    "CENTRO PRIVADO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA",
    "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA",
    "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA Y SECUNDARIA",
)


@dataclass(frozen=True)
class Official:
    label: str
    where: str  # SQL filter on place_master p
    official: str
    reference_date: str
    source: str
    url: str
    note: str


SERMAS = "p.attributes->>'dependecia_funcional' = 'Servicios o Institutos de Salud de las CC.AA'"
NOTA_SERMAS = "https://www.comunidad.madrid/node/116506"
DYC = "https://gestiona3.madrid.org/bvirtual/BVCM051753.pdf"
IMSERSO = "https://imserso.es/documents/20123/10902543/inf_ssppmmesp2024.pdf/1432577e-5e36-5d7c-83d1-24864192dc99"
ROWS = [
    Official(
        "Centros de salud (SERMAS)",
        f"p.subcategory = 'Centro de salud' AND {SERMAS}",
        "265",
        "30 jun 2026",
        "CM, nota de prensa sobre la Atención Primaria",
        NOTA_SERMAS,
        "El registro de centros sanitarios autoriza edificios; el SERMAS cuenta equipos. D ve "
        "unos 10 consultorios inscritos como «centro de salud» (M2).",
    ),
    Official(
        "Consultorios locales (SERMAS)",
        f"p.subcategory = 'Consultorio de atención primaria' AND {SERMAS}",
        "163",
        "30 jun 2026",
        "CM, la misma nota",
        NOTA_SERMAS,
        "Centros de salud + consultorios: 417 SERMAS frente a 428 (−2,6 %).",
    ),
    Official(
        "Hospitales (todos)",
        "p.subcategory LIKE 'Hospital%'",
        "85 (CM, 2023) · 91 (CNH 2025)",
        "2023 · 31 dic 2024",
        "CM «Hospitales y datos asistenciales» · Ministerio de Sanidad, Catálogo Nacional de "
        "Hospitales 2025",
        "https://datos.comunidad.madrid/dataset/1912744",
        "El CNH cuenta uno a uno los hospitales de un complejo y los «otros centros con "
        "internamiento»; el registro CM coincide con la estadística CM.",
    ),
    Official(
        "Oficinas de farmacia",
        "p.category = 'pharmacy'",
        "2.950 (CM, 2025) · 2.948 (CGCOF)",
        "1 ene 2025 · 31 dic 2025",
        "CM `cm_farmacias_municipios` · Consejo General de Farmacéuticos",
        "https://www.farmaceuticos.com/wp-content/uploads/2026/05/2025-Estadisticas-Colegiados-Farmacias_version-corta-11062026.pdf",
        "El registro es de hoy y la estadística, anual (D7: ±1 en Alcobendas y Collado Villalba).",
    ),
    Official(
        "Colegios públicos con primaria",
        "p.subcategory IN :primaria AND p.attributes->>'titularidad' = 'PÚBLICO'",
        "769 (tipo «Infantil y Primaria»)",
        "curso 2024-25",
        "CM, «Datos y cifras de la educación 2025-2026», tabla 11",
        DYC,
        "Nuestro recuento suma CEIP (717), CEIPSO (93) y CEP (1); la tabla oficial cuenta los "
        "CEIPSO en otro tipo, así que la comparación buena es CEIP: 717 frente a 769, el "
        "registro va un curso por delante.",
    ),
    Official(
        "Colegios concertados con primaria",
        "p.subcategory IN :primaria AND p.attributes->>'titularidad' = 'PRIVADO CONCERTADO'",
        "429 (fila «Primaria y Secundaria»)",
        "curso 2024-25",
        "CM, «Datos y cifras de la educación 2025-2026», tabla 11",
        DYC,
        "Tipologías distintas: la tabla agrupa por enseñanzas impartidas.",
    ),
    Official(
        "Escuelas infantiles públicas (0–3)",
        "p.subcategory IN ('ESCUELA INFANTIL', 'ESCUELA  INFANTIL-CASA DE NIÑOS') "
        "AND p.attributes->>'titularidad' LIKE 'PÚBLICO%'",
        "486 (+85 CEIP con aula de 0–3)",
        "curso 2024-25",
        "CM, «Datos y cifras de la educación 2025-2026», figura 15",
        DYC,
        "Las privadas de 0–3 no se publican como tales.",
    ),
    Official(
        "Residencias de mayores",
        "p.subcategory LIKE 'RESIDENCIAS DE PERSONAS MAYORES%'",
        "478 centros · 55.457 plazas",
        "31 dic 2024",
        "IMSERSO, «Servicios sociales dirigidos a las personas mayores. Informe 2024»",
        IMSERSO,
        "Coincide.",
    ),
    Official(
        "Centros de día de mayores",
        "p.subcategory = 'CENTROS DE DÍA: OTROS'",
        "319 · 16.393 plazas",
        "31 dic 2024",
        "IMSERSO, informe 2024",
        IMSERSO,
        "",
    ),
    Official(
        "Hogares y clubes (centros de mayores)",
        "p.subcategory = 'HOGARES Y CLUBES'",
        "231",
        "31 dic 2024",
        "IMSERSO, informe 2024",
        IMSERSO,
        "El Ayuntamiento de Madrid tiene además 93 centros municipales de mayores (Carta de "
        "Servicios 2026) que no están en el registro de la CM.",
    ),
]
_COUNT = "SELECT count(*) FROM place_master p WHERE {where}"
_DUPLICATES = text(
    """
    SELECT a.official_dataset_id AS dataset, a.subcategory, a.official_entity_id AS a_id,
           b.official_entity_id AS b_id, a.canonical_name AS a_name, b.canonical_name AS b_name,
           round(ST_Distance(a.geom_25830, b.geom_25830)::numeric, 1) AS metres
      FROM place_master a
      JOIN place_master b
        ON a.official_dataset_id = b.official_dataset_id AND a.subcategory = b.subcategory
       AND a.canonical_place_id < b.canonical_place_id
       AND ST_DWithin(a.geom_25830, b.geom_25830, 10)
     WHERE a.category <> 'transport' AND a.subcategory IN :relevant
     ORDER BY 1, 2, 3
    """
)
RELEVANT = (
    *PRIMARIA,
    "ESCUELA INFANTIL",
    "ESCUELA  INFANTIL-CASA DE NIÑOS",
    "ESCUELA INFANTIL PRIVADA",
    "CENTRO PRIVADO DE EDUCACIÓN INFANTIL",
    "Centro de salud",
    "Consultorio de atención primaria",
    "Hospital general",
    "HOGARES Y CLUBES",
    "CENTROS DE DÍA: OTROS",
    "Farmacia",
)


def _counts(conn: Connection) -> list[str]:
    lines = [
        "| Tipo | Nuestro recuento | Oficial | Fecha | Fuente | Nota |",
        "|---|---|---|---|---|---|",
    ]
    for row in ROWS:
        sql = text(_COUNT.format(where=row.where))
        params: dict[str, object] = {}
        if ":primaria" in row.where:
            sql = sql.bindparams(bindparam("primaria", expanding=True))
            params = {"primaria": list(PRIMARIA)}
        ours = conn.execute(sql, params).scalar_one()
        lines.append(
            f"| {row.label} | {ours} | {row.official} | {row.reference_date} | "
            f"[{row.source}]({row.url}) | {row.note} |"
        )
    return lines


def main() -> int:
    engine = create_engine(DatabaseSettings().database_url)
    out: list[str] = ["## 1. Recuentos frente a los totales oficiales", ""]
    with engine.connect() as conn:
        out += _counts(conn)
        sql = _DUPLICATES.bindparams(bindparam("relevant", expanding=True))
        dups = conn.execute(sql, {"relevant": list(RELEVANT)}).mappings()
        out += ["", "## 2. Mismo tipo a menos de 10 m (posibles duplicados)", ""]
        out += [
            "| Registro | Tipo | Id A | Id B | Nombre A | Nombre B | m |",
            "|---|---|---|---|---|---|---|",
        ]
        out += [
            f"| {d['dataset']} | {d['subcategory']} | {d['a_id']} | {d['b_id']} | {d['a_name']} "
            f"| {d['b_name']} | {d['metres']} |"
            for d in dups
        ]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
