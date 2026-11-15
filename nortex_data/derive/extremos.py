import numpy as np
import pandas as pd


def extremos(precipitation, dry_threshold=1):
    """Resume lluvia diaria en el intervalo y acumula meses completos."""
    if precipitation.empty:
        return {}, pd.Series(dtype=float)
    daily = precipitation.sort_index().asfreq("D")
    valid = daily.dropna()
    dry = daily.lt(dry_threshold)
    runs = dry.groupby((~dry).cumsum()).sum()
    summary = {
        "rx1day": daily.max(),
        "rx5day": daily.rolling(5).sum().max(),
        "days_gt_p95": valid.gt(valid.quantile(0.95)).sum() if len(valid) else np.nan,
        "days_gt_p99": valid.gt(valid.quantile(0.99)).sum() if len(valid) else np.nan,
        "max_dry_days": runs.max() if len(valid) else np.nan,
    }
    monthly = daily.groupby(daily.index.to_period("M"))
    total = monthly.sum(min_count=1)
    total = total.where(monthly.count().eq(total.index.days_in_month))
    return summary, total.to_timestamp()
