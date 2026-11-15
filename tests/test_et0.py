import pytest

from nortex_data.derive.et0 import et0


def test_fao_56_example_18():
    assert et0(21.5, 12.3, 22.07, 2.078, 1.409, 50.8, 100, 187) == pytest.approx(3.88, abs=0.02)
