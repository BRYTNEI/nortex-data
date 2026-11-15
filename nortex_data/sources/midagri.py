from nortex_data.utils.http import request


def search_datasets(query="costos de producción", limit=10):
    """Busca metadatos de datasets de MIDAGRI/SIEA en CKAN."""
    url = "https://www.datosabiertos.gob.pe/api/3/action/package_search"
    response = request("GET", url, params={"q": f"{query} MIDAGRI", "rows": limit}).json()
    if not response.get("success"):
        raise RuntimeError("El portal de datos abiertos no respondió con metadatos CKAN")
    return [
        {"id": item["id"], "title": item["title"], "name": item["name"]}
        for item in response["result"]["results"]
    ]
