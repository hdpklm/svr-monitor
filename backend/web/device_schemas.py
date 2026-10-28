from pydantic import BaseModel, ConfigDict, Field


class DeviceInput(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True)

	name: str = Field(min_length=1, max_length=100)
	description: str = Field(default="", max_length=255)
