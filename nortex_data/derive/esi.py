import numpy as np


def esi(actual, potential):
    """Calcula ET real / ET potencial con coincidencia por fecha."""
    return actual.where(actual >= 0).div(potential.where(potential > 0)).replace(
        [np.inf, -np.inf], np.nan
    )


def anomaly(index):
    """Estandariza el ESI respecto al intervalo de referencia suministrado."""
    deviation = index.std(ddof=0)
    if not np.isfinite(deviation) or deviation == 0:
        return index * np.nan
    return (index - index.mean()) / deviation
