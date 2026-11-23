"""D-253: services and supplies of a parcel, pure and without I/O.

No open data says whether a parcel has its services (the legal «solar»: Ley 9/2001 del Suelo de
la Comunidad de Madrid, art. 14.1.a) nor how much power the network can give it. What we can
say is how much power a residential building of that size has to plan for, with the official
rule, as an assumption:

    homes   n ≈ buildable m² / 80 (the home of the calculator, D-248)
    power   P = 5,75 kW × coefficient of simultaneity of n homes

The coefficient is table 1 of ITC-BT-10 of the low-voltage regulation (RD 842/2002), as printed
in the BOE supplement 224 of 18/09/2002, p. 68; past 21 homes, 15,3 + (n − 21) · 0,5. 5,75 kW is
the minimum of the basic electrification (apdo. 2.2). Common services and garages are added
apart with simultaneity 1 (apdo. 3): not counted here, so the figure is a floor.

Past 100 kW the building has to keep a room for the distributor's transformer (RD 1048/2013,
art. 26.1), and the network extension is paid by whoever asks for the supply (art. 25).
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from hi_domain.viability import HOME_M2

BASIC_KW = 5.75
TRANSFORMER_KW = 100.0
SIMULTANEITY: dict[int, float] = {
    1: 1.0,
    2: 2.0,
    3: 3.0,
    4: 3.8,
    5: 4.6,
    6: 5.4,
    7: 6.2,
    8: 7.0,
    9: 7.8,
    10: 8.5,
    11: 9.2,
    12: 9.9,
    13: 10.6,
    14: 11.3,
    15: 11.9,
    16: 12.5,
    17: 13.1,
    18: 13.7,
    19: 14.3,
    20: 14.8,
    21: 15.3,
}


STEP = 0.5  # past the table, each home adds 0,5


def simultaneity(homes: int) -> float:
    """Table 1 of ITC-BT-10; past 21 homes, 15,3 + (n − 21) · 0,5."""
    if homes < 1:
        raise ValueError("at least one home")
    last = max(SIMULTANEITY)
    return SIMULTANEITY[homes] if homes <= last else SIMULTANEITY[last] + (homes - last) * STEP


@dataclass(frozen=True)
class PowerEstimate:
    homes: int
    simultaneity: float
    kw_per_home: float
    kw: float

    @property
    def over_transformer_threshold(self) -> bool:
        return self.kw > TRANSFORMER_KW


def power_estimate(buildable_m2: float | None) -> PowerEstimate | None:
    """The least power the homes of a building of that size need; None without m²."""
    if buildable_m2 is None or buildable_m2 <= 0:
        return None
    exact_homes = Decimal(str(buildable_m2)) / Decimal(str(HOME_M2))
    homes = max(1, int(exact_homes.quantize(Decimal(1), rounding=ROUND_HALF_UP)))
    coefficient = simultaneity(homes)
    exact = Decimal(str(BASIC_KW)) * Decimal(str(coefficient))  # 5,75 × 3,8 = 21,85 → 21,9
    kw = float(exact.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
    return PowerEstimate(homes, coefficient, BASIC_KW, kw)
