"""Build the DATAMAD 2026 slides (pitch/deck/) into a PDF and check they read well projected.

Slide 2 (datasets) is filled from the same catalog and portal snapshot as pitch/datasets_cm.md.
Before printing, colour pairs are checked for WCAG contrast (glass blended over the darkest
background) and every font size against the projector minimum. After printing, the PDF is
checked for 4 pages of 1920 x 1080 px and embedded Inter + Plus Jakarta Sans.

Usage (from the repo root; needs Chrome and network for the Google fonts):
    uv run --with segno==1.6.6 python pitch/deck/build.py           # draft: pending marks allowed
    uv run --with segno==1.6.6 python pitch/deck/build.py --final   # 24 Nov: nothing pending

Environment:
    DECK_INTEGRANTES  name(s) for slide 1; kept out of the public repo
    CHROME            Chrome or Chromium binary (default: macOS Google Chrome, then PATH)
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import segno

DECK = Path(__file__).resolve().parent
PITCH = DECK.parent
ROOT = PITCH.parent
BUILD = DECK / "build"
CAPTURES = PITCH / "capturas"
PDF_NAME = "VidaFacil_DATAMAD2026.pdf"

sys.path.insert(0, str(PITCH))
from build_datasets_cm import SNAPSHOT, group_datasets  # noqa: E402

from hi_ingestion.catalog.loader import load_catalog  # noqa: E402
from hi_ingestion.catalog.provenance import portal_url  # noqa: E402

DEMO_URL = "https://vidafacil-madrid.vercel.app"
REPO_URL = "https://github.com/marianohernando/housing-intelligence"
DEFAULT_TEAM = "Mariano"
MIN_FONT_PX = 22  # ~11 pt on a standard 13.33 in slide: only for sources and footers
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

THEMES = [
    ("Geografía", {"geography"}),
    ("Población y hogares", {"population"}),
    ("Vivienda", {"housing"}),
    ("Renta", {"income"}),
    ("Servicios", {"education", "health", "social"}),
    ("Transporte (CRTM)", {"transport"}),
]
SHORT_NAMES = {
    "cm_secciones_censales": "Secciones censales",
    "cm_poblacion_edad_nacionalidad_sexo": "Población por edad",
    "cm_hogares_tamano_censo_2021": "Hogares por tamaño",
    "cm_nacidos_vivos_municipios": "Nacidos vivos",
    "cm_viviendas_superficie": "Viviendas por superficie",
    "cm_viviendas_tenencia_censo_2021": "Viviendas por tenencia",
    "cm_alquiler_m2_municipios": "Alquiler €/m² por municipio",
    "cm_alquiler_m2_codigo_postal_madrid": "Alquiler €/m² por código postal",
    "cm_renta_disponible_municipal": "Renta disponible",
    "cm_centros_educativos": "Centros educativos",
    "cm_unidades_escolares": "Unidades escolares",
    "cm_centros_sanitarios": "Centros sanitarios",
    "cm_centros_atencion_social": "Centros de atención social",
    "cm_oficinas_farmacia": "Oficinas de farmacia",
    "cm_farmacias_municipios": "Farmacias por municipio",
    "crtm_gtfs_metro": "Metro",
    "crtm_gtfs_metro_ligero": "Metro Ligero",
    "crtm_gtfs_cercanias": "Cercanías",
    "crtm_gtfs_emt": "EMT",
    "crtm_gtfs_autobuses_urbanos": "Autobuses urbanos",
    "crtm_gtfs_interurbanos": "Interurbanos",
}
# (text token, background, minimum ratio, where it is used). "glass@X" = glass blended over X.
CONTRAST_CHECKS = [
    ("ink", "glass@bg-deep", 4.5, "texto sobre cristal"),
    ("ink-soft", "glass@bg-deep", 4.5, "texto secundario sobre cristal"),
    ("violet-strong", "glass@bg-deep", 4.5, "enlaces y rótulos violetas sobre cristal"),
    ("violet", "glass@bg-deep", 3.0, "cifra grande (texto grande) sobre cristal"),
    ("ink", "bg-deep", 4.5, "texto sobre el fondo más oscuro"),
    ("ink-soft", "bg-deep", 4.5, "pies y fuentes sobre el fondo"),
    ("violet-strong", "bg-deep", 4.5, "lema y rótulos sobre el fondo"),
    ("on-violet", "violet", 3.0, "número en círculo (texto grande en negrita)"),
    ("falta-ink", "falta-bg", 4.5, "estado FALTA"),
    ("justo-ink", "justo-bg", 4.5, "estado JUSTO"),
    ("cubierto-ink", "cubierto-bg", 4.5, "estado CUBIERTO"),
    ("sin-datos-ink", "sin-datos-bg", 4.5, "estado SIN DATOS"),
]
Rgba = tuple[float, float, float, float]


def css_tokens(css: str) -> dict[str, Rgba]:
    tokens: dict[str, Rgba] = {}
    for name, value in re.findall(r"--([\w-]+):\s*([^;]+);", css):
        hex_match = re.fullmatch(r"#([0-9a-fA-F]{6})", value.strip())
        rgba_match = re.fullmatch(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", value.strip())
        if hex_match:
            h = hex_match.group(1)
            tokens[name] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
        elif rgba_match:
            r, g, b, a = rgba_match.groups()
            tokens[name] = (int(r), int(g), int(b), float(a))
    return tokens


def blend(top: Rgba, under: Rgba) -> Rgba:
    a = top[3]
    mixed = [top[i] * a + under[i] * (1 - a) for i in range(3)]
    return (mixed[0], mixed[1], mixed[2], 1.0)


def luminance(color: Rgba) -> float:
    def channel(c: float) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(color[0]) + 0.7152 * channel(color[1]) + 0.0722 * channel(color[2])


def contrast(a: Rgba, b: Rgba) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def resolve(tokens: dict[str, Rgba], name: str) -> Rgba:
    if name.startswith("glass@"):
        return blend(tokens["glass-bg"], tokens[name.removeprefix("glass@")])
    return tokens[name]


def check_design(css: str) -> list[str]:
    tokens = css_tokens(css)
    problems: list[str] = []
    print("Contraste (WCAG 2.2):")
    for fg, bg, minimum, where in CONTRAST_CHECKS:
        ratio = contrast(resolve(tokens, fg), resolve(tokens, bg))
        ok = ratio >= minimum
        print(
            f"  {'OK ' if ok else 'MAL'} {ratio:5.2f}:1 (mín. {minimum}) {fg} sobre {bg}: {where}"
        )
        if not ok:
            problems.append(f"contraste {fg} sobre {bg}: {ratio:.2f} < {minimum}")
    sizes = [int(px) for px in re.findall(r"font-size:\s*(\d+)px", css)]
    print(f"Letra: mínimo {min(sizes)} px (umbral {MIN_FONT_PX} px), máximo {max(sizes)} px")
    problems += [f"letra de {px} px < {MIN_FONT_PX} px" for px in sizes if px < MIN_FONT_PX]
    return problems


def dataset_rows() -> tuple[int, str]:
    catalog = load_catalog(include_drafts=False)
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8")) if SNAPSHOT.exists() else {}
    groups = group_datasets(catalog, snapshot.get("datasets", {}))
    cm = [dataset for dataset, gate, _ in groups.cm_own + groups.cm_partner if gate.passed]
    order = list(SHORT_NAMES)
    rows: list[str] = []
    placed: set[str] = set()
    for label, domains in [*THEMES, ("Otros", None)]:
        members = [d for d in cm if (domains is None or str(d.domain) in domains)]
        members = [d for d in members if d.dataset_id not in placed]
        if not members:
            continue
        members.sort(key=lambda d: order.index(d.dataset_id) if d.dataset_id in order else 99)
        placed.update(d.dataset_id for d in members)
        links = " · ".join(
            f'<a href="{html.escape(str(portal_url(d)))}">'
            f"{html.escape(SHORT_NAMES.get(d.dataset_id, d.name))}</a>"
            for d in members
        )
        rows.append(f"<tr><th>{html.escape(label)} ({len(members)})</th><td>{links}</td></tr>")
    return len(cm), "\n        ".join(rows)


def qr_svg(url: str) -> str:
    return segno.make(url, error="m").svg_inline(omitsize=True, border=0, dark="#141b3d")


def place_captures(page: str) -> tuple[str, list[str]]:
    missing: list[str] = []

    def fill(match: re.Match[str]) -> str:
        shot, img = match.group(1), match.group(2)
        if (CAPTURES / f"{shot}.png").exists():
            return f'<figure class="shot has-img" data-shot="{shot}">{img}'
        missing.append(shot)
        return f'<figure class="shot" data-shot="{shot}">'

    filled = re.sub(r'<figure class="shot" data-shot="(C\d)">\s*(<img [^>]*>)', fill, page)
    return filled, missing


def render() -> tuple[str, list[str]]:
    team = os.environ.get("DECK_INTEGRANTES", "").strip()
    count, rows = dataset_rows()
    replacements = {
        "{{INTEGRANTES}}": html.escape(team or DEFAULT_TEAM),
        "{{INTEGRANTES_PENDING}}": (
            "" if team else ' class="pending" data-pending="nombre completo (DECK_INTEGRANTES)"'
        ),
        "{{CM_COUNT}}": str(count),
        "{{DATASET_ROWS}}": rows,
        "{{QR_DEMO}}": qr_svg(DEMO_URL),
        "{{QR_REPO}}": qr_svg(REPO_URL),
        "{{DEMO_URL}}": DEMO_URL,
        "{{DEMO_HOST}}": DEMO_URL.removeprefix("https://"),
        "{{REPO_URL}}": REPO_URL,
    }
    page = (DECK / "deck.html").read_text(encoding="utf-8")
    for token, value in replacements.items():
        page = page.replace(token, value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", page)
    if leftover:
        raise SystemExit(f"Huecos sin rellenar en la plantilla: {leftover}")
    return place_captures(page)


def chrome_binary() -> str:
    candidates = [os.environ.get("CHROME"), MAC_CHROME]
    candidates += [shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser")]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("No encuentro Chrome: define CHROME con la ruta del ejecutable.")


def print_pdf(page_html: Path, pdf: Path) -> None:
    command = [
        chrome_binary(),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=20000",
        f"--print-to-pdf={pdf}",
        page_html.as_uri(),
    ]
    # Fixed local binary and arguments built here; no external input reaches the command.
    subprocess.run(command, check=True, capture_output=True, timeout=180)  # noqa: S603


def tool_output(tool: str, *args: str) -> str | None:
    binary = shutil.which(tool)
    if binary is None:
        print(f"  (sin {tool}: instala poppler para esta comprobación)")
        return None
    result = subprocess.run([binary, *args], check=True, capture_output=True, text=True)  # noqa: S603
    return result.stdout


def check_pdf(pdf: Path) -> list[str]:
    problems: list[str] = []
    info = tool_output("pdfinfo", str(pdf)) or ""
    pages = re.search(r"Pages:\s+(\d+)", info)
    size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", info)
    if pages and pages.group(1) != "4":
        problems.append(f"el PDF tiene {pages.group(1)} páginas, no 4")
    if size and (round(float(size.group(1))), round(float(size.group(2)))) != (1440, 810):
        problems.append(f"tamaño de página {size.group(1)} x {size.group(2)} pt, no 1440 x 810")
    fonts = tool_output("pdffonts", str(pdf)) or ""
    for family in ("Inter", "PlusJakartaSans"):
        embedded = [line for line in fonts.splitlines() if family in line and " yes " in line]
        if fonts and not embedded:
            problems.append(f"la fuente {family} no está incrustada (¿no cargó Google Fonts?)")
    print(f"PDF: {pages.group(1) if pages else '?'} páginas, fuentes: {'OK' if fonts else '?'}")
    tool_output("pdftoppm", "-png", "-r", "40", str(pdf), str(BUILD / "preview"))
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Build pitch/deck into a PDF")
    parser.add_argument("--final", action="store_true", help="fail on pending marks or captures")
    args = parser.parse_args()

    problems = check_design((DECK / "deck.css").read_text(encoding="utf-8"))
    page, missing = render()
    BUILD.mkdir(exist_ok=True)
    page_html = BUILD / "index.html"
    page_html.write_text(page, encoding="utf-8")
    pdf = BUILD / PDF_NAME
    print_pdf(page_html, pdf)
    problems += check_pdf(pdf)

    pending = re.findall(r'data-pending="([^"]+)"', page)
    print(f"Capturas que faltan: {', '.join(missing) or 'ninguna'}")
    print(f"Marcas pendientes: {'; '.join(pending) or 'ninguna'}")
    if args.final:
        problems += [f"falta la captura {shot}" for shot in missing]
        problems += [f"pendiente: {item}" for item in pending]
    print(f"Escrito {pdf.relative_to(ROOT)} y vistas previas en {BUILD.relative_to(ROOT)}/")
    if problems:
        print("\nPROBLEMAS:\n- " + "\n- ".join(problems))
        raise SystemExit(1)
    print("Comprobaciones superadas.")


if __name__ == "__main__":
    main()
