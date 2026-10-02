from datetime import date
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Money = Annotated[float, Field(ge=0, le=1e12)]
Fraction = Annotated[float, Field(ge=0, le=1)]
Growth = Annotated[float, Field(ge=-0.2, le=0.3)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Material(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: Money = 0
    unit: str = Field(default="m²", max_length=20)
    unit_cost: Money = 0
    service_life: int | None = Field(default=None, ge=1, le=100)
    replacement_interval: int | None = Field(default=None, ge=1, le=100)
    maintenance: Money = 0


class Replacement(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    scenario: Literal["both", "conventional", "sustainable"] = "both"
    interval: int = Field(ge=1, le=100)
    cost: Money
    escalation: Growth = 0.025


class Project(StrictModel):
    name: str = Field(default="Sydney project", min_length=1, max_length=120)
    postcode: str = Field(pattern=r"^2\d{3}$")
    zone: Literal["Ausgrid", "Endeavour Energy", "Essential Energy"]
    building_type: Literal["Residential House", "Apartment", "Commercial / Other"] = "Residential House"
    area: float = Field(gt=0, le=1e7)
    area_unit: Literal["m²", "ft²"] = "m²"
    floors: int = Field(ge=1, le=100)
    rooms: int = Field(ge=0, le=10000)
    bathrooms: int = Field(ge=0, le=10000)
    occupants: int = Field(ge=1, le=100000)
    quality: Literal["Standard", "Mid-range", "Premium"] = "Standard"
    cost_mode: Literal["quick", "detailed"] = "quick"
    conventional_cost: Money | None = None
    cost_per_m2: Money | None = None
    historical_index: float | None = Field(default=None, gt=0)
    materials: list[Material] = Field(default_factory=list, max_length=100)
    other_construction: Money = 0
    detailed_complete: bool = False
    sustainable_cost: Money | None = None
    premium: Fraction = 0.1
    energy_kwh: Money
    water_kl: Money
    energy_reduction: Fraction = 0.3
    water_reduction: Fraction = 0.4
    maintenance_reduction: Fraction = 0.15
    performance_source: Literal["research", "user"] = "research"
    input_quality: Literal["demo", "estimate", "actual"] = "estimate"
    features: list[str] = Field(default_factory=list, max_length=30)
    hvac: str = Field(default="User specified", max_length=100)
    hot_water: str = Field(default="User specified", max_length=100)
    lighting: str = Field(default="User specified", max_length=100)
    maintenance_annual: Money | None = None
    maintenance_fraction: Fraction = 0.01
    replacements: list[Replacement] = Field(default_factory=list, max_length=100)
    water_connected: bool = True
    wastewater_connected: bool = True
    stormwater: bool = False
    drought_tariff: bool = False
    tariff_mode: Literal["official", "user"] = "official"
    electricity_rate: Money | None = None
    electricity_daily: Money | None = None
    water_rate: Money | None = None
    water_fixed_annual: Money | None = None
    tariff_note: str = Field(default="", max_length=300)
    web_research: bool = True
    price_date: date = Field(default_factory=date.today)
    years: Literal[30, 40, 50] = 40
    discount: Fraction = 0.05
    energy_escalation: Growth = 0.03
    water_escalation: Growth = 0.025
    maintenance_escalation: Growth = 0.025
    other_escalation: Growth = 0.025
    terminal_escalation: Growth = 0.025
    other_annual: Money = 0
    disposal_conventional: Money = 0
    disposal_sustainable: Money = 0
    residual_conventional: Money = 0
    residual_sustainable: Money = 0

    @model_validator(mode="after")
    def coherent(self):
        if self.conventional_cost == 0:
            raise ValueError("Construction total must be positive; leave it blank to use AUD/m².")
        if self.cost_mode == "quick" and not (self.conventional_cost or self.cost_per_m2):
            raise ValueError("Enter conventional construction cost or AUD/m²; no benchmark is assumed.")
        if self.cost_mode == "detailed":
            if not self.materials or not self.detailed_complete:
                raise ValueError(
                    "Add materials and confirm labour, fees and remaining construction scope are included."
                )
            if sum(m.quantity * m.unit_cost for m in self.materials) + self.other_construction <= 0:
                raise ValueError("Detailed construction total must be positive.")
            if self.historical_index:
                raise ValueError("Historical indexation is supported for quick-cost inputs only.")
        if self.building_type == "Commercial / Other" and self.tariff_mode != "user":
            raise ValueError("Commercial projects require user-supplied applicable utility prices.")
        if self.tariff_mode == "user":
            if (
                any(
                    x is None
                    for x in (self.electricity_rate, self.electricity_daily, self.water_rate, self.water_fixed_annual)
                )
                or not self.tariff_note.strip()
            ):
                raise ValueError("Supply all four utility rates and a source note for custom tariffs.")
        if self.performance_source == "research":
            if self.energy_reduction and not any(
                x in self.features for x in ("solar", "insulation", "glazing", "hvac", "hot_water", "lighting")
            ):
                raise ValueError("Select an energy feature or set energy reduction to zero.")
            if self.water_reduction and not any(x in self.features for x in ("rainwater", "fixtures")):
                raise ValueError("Select a water feature or set water reduction to zero.")
            if self.maintenance_reduction and "durable" not in self.features:
                raise ValueError("Select durable materials or set maintenance reduction to zero.")
        return self


class ChatRequest(StrictModel):
    question: str = Field(min_length=1, max_length=500)
    years: Literal[30, 40, 50] | None = None


class Source(StrictModel):
    id: str
    title: str
    organisation: str
    url: str
    publication_date: date | None
    effective_from: date
    effective_to: date | None
    retrieved_at: date
    jurisdiction: str
    source_category: Literal["CURRENT_OFFICIAL_PRICING", "OFFICIAL_INDEX", "REGULATORY_CONTEXT"]
    confidence: Literal["high", "medium", "low"]
    customer_type: str
    values: dict
    evidence: list[str]
    notes: str
    verification: Literal["verified"] = "verified"
