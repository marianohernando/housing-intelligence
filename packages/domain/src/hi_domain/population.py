"""Age bands shared by every population source, so ratios over them compare like with like.

The keys are the CM census ones (`poblacion_censada`): 5-year bands up to 99 and an open band
from 100, plus `total`.
"""

BAND_WIDTH = 5
OPEN_BAND_FROM = 100
OPEN_BAND = f"de_{OPEN_BAND_FROM}_y_mas_anos"
TOTAL_AGE = "total"


def five_year_age_band(age: int) -> str:
    if age < 0:
        msg = f"negative age {age}"
        raise ValueError(msg)
    if age >= OPEN_BAND_FROM:
        return OPEN_BAND
    start = age - age % BAND_WIDTH
    return f"de_{start}_{start + BAND_WIDTH - 1}_anos"


def five_year_age_bands() -> list[str]:
    return [five_year_age_band(age) for age in range(0, OPEN_BAND_FROM + 1, BAND_WIDTH)]
