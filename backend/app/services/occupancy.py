"""Indicative whole-building occupancy; not a legal capacity or bill forecast."""
import math

BASIX_SOURCE = "https://www.planningportal.nsw.gov.au/sites/default/files/documents/2022/BASIX%20standard%20occupancy%20-%20version%204%20-%2023.08.22%20LMv5.pdf"


def apartment_occupancy(area_m2, average_unit_m2=75, residential_share=.8):
    per_unit = min(6, max(1, 1.525 * math.log(average_unit_m2) - 4.533))
    dwellings = area_m2 * residential_share / average_unit_m2
    return dict(occupants=max(1, math.floor(dwellings * per_unit + .5)),
                estimated_dwellings=dwellings, occupants_per_dwelling=per_unit,
                residential_area_m2=area_m2 * residential_share,
                gross_m2_per_person=average_unit_m2 / (residential_share * per_unit))
