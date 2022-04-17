from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import Address, Parcel
from dotenv import load_dotenv
import easypost
import os

load_dotenv()

test_api_key = os.getenv('EASYPOST_TEST_KEY')
prod_api_key = os.getenv('EASYPOST_PRODUCTION_KEY')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
	return {"status": "running"}


@app.post("/shipments")
async def create_shipment(to_address_id: str, from_adddress_id: str, parcel_id: str):
	easypost.api_key = test_api_key
	try:
		return easypost.Shipment.create(
			to_address=easypost.Address.retrieve(to_address_id),
			from_address=easypost.Address.retrieve(from_adddress_id),
			parcel=easypost.Parcel.retrieve(parcel_id),
		).to_dict()
	except easypost.error.Error as e:
		# could not create shipment or addresses/parcel not found
		raise HTTPException(status_code=e.http_status, detail=e.message)


@app.post("/shipments/{shipment_id}/buy")
async def buy_shipment(shipment_id: str, rate_id: str = None):
	easypost.api_key = test_api_key
	try:
		shipment = easypost.Shipment.retrieve(shipment_id)
		rate = shipment.lowest_rate() if rate_id is None else {"id": rate_id}  # use lowest rate if rate_id not supplied
		return shipment.buy(rate=rate).to_dict()
	except easypost.error.Error as e:
		# shipment not found, rate not found, or shipment already purchased
		raise HTTPException(status_code=e.http_status, detail=e.message)


@app.post("/addresses")
async def create_address(address: Address):
	easypost.api_key = test_api_key
	try:
		return easypost.Address.create(
			street1=address.street1,
		    street2=address.street2,
		    city=address.city,
		    state=address.state,
		    zip=address.zip,
		    country=address.country,
			name=address.name,
		    company=address.company,
		    phone=address.phone,
			email=address.email,
			verify=address.verify
		).to_dict()
	except easypost.error.Error as e:
		# params were invalid
		raise HTTPException(status_code=e.http_status, detail=e.message)


@app.get("/addresses")
async def get_addresses(page_size: int = 20):
	easypost.api_key = test_api_key
	response = easypost.Address.all(page_size=page_size)
	return {"addresses": [obj.to_dict() for obj in response.addresses], "has_more": response.has_more}  # sterilize API key from response


@app.post("/parcels")
async def create_parcel(parcel: Parcel):
	easypost.api_key = test_api_key
	try:
		return easypost.Parcel.create(
			length=parcel.length,
			width=parcel.width,
			height=parcel.height,
			weight=parcel.weight
		).to_dict()
	except easypost.error.Error as e:
		# params were invalid
		raise HTTPException(status_code=e.http_status, detail=e.message)


@app.get("/carrier_accounts")
async def get_carrier_accounts():
	easypost.api_key = prod_api_key  # this API call requires the production key
	exclusions = ["DHL Express Account", "LSO Account"]  # exclude returning these accounts
	accounts = filter(lambda acct: acct.description not in exclusions, easypost.CarrierAccount.all())
	return [obj.to_dict() for obj in accounts]  # convert EasyPost objects to JSON
