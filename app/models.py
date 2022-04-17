from pydantic import BaseModel
from typing import List


class Address(BaseModel):
	street1: str
	street2: str = None
	city: str
	state: str
	zip: str
	country: str
	name: str
	company: str =  None
	phone: str = None
	email: str = None
	verify: List[str] = ["delivery", "zip4"]


class Parcel(BaseModel):
	length: float
	width: float
	height: float
	weight: float
