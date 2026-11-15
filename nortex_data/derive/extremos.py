import numpy as np
import pandas as pd


def extremos(precipitation, dry_threshold=1):
    """Resume lluvia diaria en el intervalo y acumula meses completos.

    Los umbrales p95 y p99 se calculan solo con días húmedos (lluvia >= ``dry_threshold``),
    como el índice R95p de ETCCDI. Con todos los días, en un clima seco como el de
    San Lorenzo el percentil queda cerca de 0 y el conteo equivale a «días con lluvia».
    """
    if precipitation.empty:
        return {}, pd.Series(dtype=float)
    daily = precipitation.sort_index().asfreq("D")
    valid = daily.dropna()
    wet = valid[valid.ge(dry_threshold)]
    dry = daily.lt(dry_threshold)
    runs = dry.groupby((~dry).cumsum()).sum()
    summary = {
        "rx1day": daily.max(),
        "rx5day": daily.rolling(5).sum().max(),
        "days_gt_p95": wet.gt(wet.quantile(0.95)).sum() if len(wet) else np.nan,
        "days_gt_p99": wet.gt(wet.quantile(0.99)).sum() if len(wet) else np.nan,
        "max_dry_days": runs.max() if len(valid) else np.nan,
    }
    monthly = daily.groupby(daily.index.to_period("M"))
    total = monthly.sum(min_count=1)
    total = total.where(monthly.count().eq(total.index.days_in_month))
    return summary, total.to_timestamp()
