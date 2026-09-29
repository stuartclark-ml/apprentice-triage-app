from pydantic import BaseModel, Field


class PostcodeLookup(BaseModel):
    postcode: str
    latitude: float
    longitude: float
    lower_super_output_area: str = Field(alias="lsoa")

    model_config = {"populate_by_name": True}
