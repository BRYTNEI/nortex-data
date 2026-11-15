import os

import pytest
from dotenv import load_dotenv

from nortex_data import get_dataset
from nortex_data.sources.gaez import _sample
from nortex_data.utils.core import COLUMNS


@pytest.mark.online
@pytest.mark.parametrize(
    ("source", "variables", "credentials"),
    [
        ("smap", ["sm_surface", "sm_rootzone"], ("EARTHDATA_TOKEN",)),
        ("imerg", ["precipitation"], ("EARTHDATA_TOKEN",)),
        ("ecostress", ["lst"], ("EARTHDATA_TOKEN",)),
        ("s2", ["ndre", "ndre_count"], ("CDSE_CLIENT_ID", "CDSE_CLIENT_SECRET")),
        ("faostat", ["production"], ("FAOSTAT_TOKEN",)),
    ],
)
def test_point_source(source, variables, credentials):
    load_dotenv()
    password_auth = source in {"smap", "ecostress"} and all(
        os.getenv(name) for name in ("EARTHDATA_USERNAME", "EARTHDATA_PASSWORD")
    )
    if not password_auth and not all(os.getenv(name) for name in credentials):
        pytest.skip("Credenciales del proveedor sin configurar")
    start, end = ("2024-01-01", "2024-01-31") if source == "faostat" else ("2025-01-01", "2025-01-31")
    result = get_dataset(source, "parcela_01", start, end, variables=variables)
    assert list(result.columns) == COLUMNS
    assert not result.empty
    assert result.value.notna().any()
    assert set(result.variable) <= set(variables)


@pytest.mark.online
def test_gaez_pixel():
    aoi = {"lat": -5.093608, "lon": -80.340280}
    endpoint = "https://gaez-services.fao.org/server/rest/services/res05/ImageServer"
    assert float(_sample(endpoint, aoi, 288)) >= 0
