from pydantic import BaseModel
  
class Tracking(BaseModel):
  number: str
  courierService: str
  
class TrackingInfo(BaseModel):
    state: str
    description: str
    datetime: str
    branch: str

class FurgonetkaWebhookPayload(BaseModel):
    package_id: int
    package_no: str
    partner_order_id: str
    tracking: TrackingInfo
    control: str