import numpy as np


def saturation_vapor_pressure(temperature):
    """Calcula la presión de vapor de saturación en kPa."""
    return 0.6108 * np.exp(17.27 * temperature / (temperature + 237.3))


def et0(tmax, tmin, rs, wind, ea, latitude, elevation, day_of_year, pressure=None):
    """Calcula ET0 diaria FAO-56 en mm/día con radiación solar en MJ/m²/día."""
    temperature = (tmax + tmin) / 2
    es = (saturation_vapor_pressure(tmax) + saturation_vapor_pressure(tmin)) / 2
    delta = 4098 * saturation_vapor_pressure(temperature) / (temperature + 237.3)**2
    if pressure is None:
        pressure = 101.3 * ((293 - 0.0065 * elevation) / 293)**5.26
    gamma = 0.000665 * pressure
    phi, angle, declination, sunset = _solar_geometry(latitude, day_of_year)
    ra = (24 * 60 / np.pi) * 0.0820 * (1 + 0.033 * np.cos(angle)) * (
        sunset * np.sin(phi) * np.sin(declination)
        + np.cos(phi) * np.cos(declination) * np.sin(sunset)
    )
    rso = (0.75 + 0.00002 * elevation) * ra
    ratio = np.clip(rs / np.maximum(rso, 1e-12), 0.3, 1.0)
    rnl = 4.903e-9 * ((tmax + 273.16)**4 + (tmin + 273.16)**4) / 2 * (
        0.34 - 0.14 * np.sqrt(ea)
    ) * (1.35 * ratio - 0.35)
    rn = 0.77 * rs - rnl
    return np.maximum(0, (
        0.408 * delta * rn + gamma * 900 / (temperature + 273) * wind * np.maximum(es - ea, 0)
    ) / (delta + gamma * (1 + 0.34 * wind)))


def _solar_geometry(latitude, day_of_year):
    phi = np.deg2rad(latitude)
    angle = 2 * np.pi * day_of_year / 365
    declination = 0.409 * np.sin(angle - 1.39)
    sunset = np.arccos(np.clip(-np.tan(phi) * np.tan(declination), -1, 1))
    return phi, angle, declination, sunset


def daylight_seconds(latitude, day_of_year):
    """Calcula la duración astronómica del día en segundos según FAO-56."""
    return 86400 * _solar_geometry(latitude, day_of_year)[3] / np.pi
