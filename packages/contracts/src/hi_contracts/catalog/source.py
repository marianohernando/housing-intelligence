"""Source Registry contract (docs/02_data/11_source_registry_contract.md)."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from hi_contracts.catalog.enums import ApiType, LicenseStatus, TrustTier

SOURCE_ID_PATTERN = r"^[a-z][a-z0-9_]{2,63}$"


class SourceSpec(BaseModel):
    """One provider/endpoint we may pull data from."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str = Field(pattern=SOURCE_ID_PATTERN)
    name: str
    provider: str
    source_type: str = Field(description="open_data_portal | official_service | open_dataset | ...")
    api_type: ApiType
    base_url: HttpUrl | None = None
    catalog_url: HttpUrl | None = None
    license_name: str | None = None
    license_url: HttpUrl | None = None
    license_status: LicenseStatus
    attribution_text: str | None = None
    commercial_use: bool | None = None
    redistribution_allowed: bool | None = None
    trust_tier: TrustTier
    default_confidence: float | None = Field(default=None, ge=0, le=1)
    update_frequency: str | None = None
    geographic_scope: str | None = None
    terms_reviewed_at: datetime | None = None
    robots_status: str | None = None
    active: bool = True
    notes: str | None = None

    @model_validator(mode="after")
    def _active_sources_are_reviewed(self) -> Self:
        if self.license_status is LicenseStatus.REJECTED and self.active:
            msg = f"{self.source_id}: a REJECTED source cannot be active"
            raise ValueError(msg)
        if self.active:
            required = {
                "license_name": self.license_name,
                "update_frequency": self.update_frequency,
                "geographic_scope": self.geographic_scope,
                "terms_reviewed_at": self.terms_reviewed_at,
                "attribution_text": self.attribution_text,
            }
            missing = sorted(k for k, v in required.items() if v is None)
            if missing:
                msg = f"{self.source_id}: active source missing {missing}"
                raise ValueError(msg)
        return self
