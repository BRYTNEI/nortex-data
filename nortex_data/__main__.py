import argparse
import logging
from pathlib import Path

from nortex_data import get_dataset
from nortex_data.utils.core import SOURCES, load_aois


def main():
    """Ejecuta consultas y escribe un Parquet por AOI."""
    parser = argparse.ArgumentParser(prog="python -m nortex_data")
    fetch = parser.add_subparsers(dest="command", required=True).add_parser("fetch")
    fetch.add_argument("--source", choices=[*SOURCES, "all"])
    fetch.add_argument("--variables", nargs="+")
    fetch.add_argument("--aoi", dest="aoi_path")
    fetch.add_argument("--aoi-id")
    fetch.add_argument("--start")
    fetch.add_argument("--end")
    fetch.add_argument("--out", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    if args.source is None and args.variables is None:
        parser.error("Indica --source o --variables")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    errors = False
    for index, aoi_id in enumerate([args.aoi_id] if args.aoi_id else load_aois(args.aoi_path), 1):
        try:
            result = get_dataset(
                args.source, aoi_id, args.start, args.end,
                variables=args.variables, aoi_path=args.aoi_path,
            )
            args.out.mkdir(parents=True, exist_ok=True)
            # El identificador se conserva dentro del archivo.
            path = args.out / f"{args.source or 'variables'}-{index}.parquet"
            errors |= bool(result.attrs.get("errors"))
            result.to_parquet(path, index=False)
            logging.info("%s: %s filas en %s", aoi_id, len(result), path)
        except Exception as error:
            logging.error("%s: %s", aoi_id, error)
            errors = True
    return int(errors)


if __name__ == "__main__":
    raise SystemExit(main())
