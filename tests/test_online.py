import os

import pytest
from dotenv import load_dotenv

from nortex_data import get_dataset
from nortex_data.sources.gaez import _sample
from nortex_data.utils.core import COLUMNS


@pytest.mark.online
@pytest.mark.parametrize(
    ("source", "aoi_id", "variables"),
    [
        ("smap", "parcela_01", ["sm_surface", "sm_rootzone"]),
        ("imerg", "parcela_01", ["precipitation", "monthly_precip"]),
        ("ecostress", "parcela_01", ["lst"]),
        ("s2", "parcela_poligono", ["ndre", "ndre_count"]),
        ("faostat", "parcela_01", ["production"]),
    ],
)
def test_point_source(source, aoi_id, variables):
    load_dotenv()
    if source == "ecostress" and not (
        os.getenv("APPEEARS_TOKEN")
        or (os.getenv("EARTHDATA_USERNAME") and os.getenv("EARTHDATA_PASSWORD"))
    ):
        pytest.skip("Configura las credenciales de AppEEARS")
    if source == "faostat" and not (
        os.getenv("FAOSTAT_TOKEN")
        or (os.getenv("FAOSTAT_USERNAME") and os.getenv("FAOSTAT_PASSWORD"))
    ):
        pytest.skip("Configura las credenciales de FAOSTAT")
    start, end = ("2024-01-01", "2024-01-31") if source == "faostat" else ("2025-01-01", "2025-01-31")
    result = get_dataset(source, aoi_id, start, end, variables=variables)
    assert list(result.columns) == COLUMNS
    assert set(result.variable) == set(variables)
    assert result.groupby("variable").value.count().gt(0).all()
    if source == "imerg" and os.getenv("EARTHDATA_TOKEN"):
        assert not result.qc_flag.str.contains("auth_error").any(), (
            "Earthdata rechazó EARTHDATA_TOKEN (401/403): el token venció, se copió con «Bearer» o "
            "espacios, o falta autorizar «NASA GESDISC DATA ARCHIVE» en el perfil de Earthdata. Los datos "
            "salieron de la copia pública de NASA POWER.")
    if source == "smap":
        assert result.value.dropna().between(0, 1).all()
    if source == "s2":
        assert result.loc[result.variable == "ndre", "value"].dropna().between(-1, 1).all()


@pytest.mark.online
def test_gaez_pixel():
    aoi = {"lat": -5.093608, "lon": -80.340280}
    endpoint = "https://gaez-services.fao.org/server/rest/services/res05/ImageServer"
    assert float(_sample(endpoint, aoi, 288)) >= 0


@pytest.mark.online
@pytest.mark.parametrize(
    ("source", "variables", "start", "end"),
    [
        ("enso", ["icen", "oni"], "2023-01-01", "2023-12-31"),
        ("srtm", ["elevation", "slope"], None, None),
        ("soilgrids", ["soil_theta_fc", "soil_theta_wp"], None, None),
        ("estacion", ["station_tmax", "station_tmin"], "2024-01-01", "2024-01-31"),
        ("power_horario", ["hours_rh90"], "2024-01-01", "2024-01-31"),
    ],
)
def test_decision_sources(source, variables, start, end):
    result = get_dataset(source, "parcela_01", start, end, variables=variables)
    assert list(result.columns) == COLUMNS
    assert set(result.variable) == set(variables)
    assert result.value.notna().any()
