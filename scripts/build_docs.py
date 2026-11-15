import argparse
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Genera la tabla del catálogo y sincroniza la configuración distribuida."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    config = ROOT / "config"
    mirror = ROOT / "nortex_data" / "_config"
    docs = ROOT / "docs" / "catalogo_variables.md"
    variables = yaml.safe_load((config / "variables.yaml").read_text(encoding="utf-8"))
    header = ["ID", "Fuente", "Producto", "Versión", "API", "Unidad", "Espacial", "Temporal",
              "Inicio", "Inicio aplicado", "Método", "Fórmula"]
    keys = ["source", "product", "version", "api", "unit", "spatial", "temporal",
            "first", "applied_start", "method", "formula"]
    lines = ["# Catálogo de variables", "", "Generado con `python scripts/build_docs.py`.", "",
             "| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for name, entry in variables.items():
        cells = [name, *(entry.get(key) for key in keys)]
        lines.append("| " + " | ".join(str(cell or "—").replace("|", "\\|") for cell in cells) + " |")
    rendered = "\n".join(lines) + "\n"
    if args.check:
        if not docs.exists() or docs.read_text(encoding="utf-8") != rendered:
            parser.exit(1, "Catálogo desactualizado. Ejecuta scripts/build_docs.py\n")
        for file in config.glob("*.yaml"):
            bundled = mirror / file.name
            if not bundled.exists() or file.read_bytes() != bundled.read_bytes():
                parser.exit(1, f"Configuración distribuida desactualizada: {file.name}\n")
        return
    mirror.mkdir(exist_ok=True)
    docs.parent.mkdir(exist_ok=True)
    docs.write_text(rendered, encoding="utf-8")
    for file in config.glob("*.yaml"):
        shutil.copyfile(file, mirror / file.name)


if __name__ == "__main__":
    main()
