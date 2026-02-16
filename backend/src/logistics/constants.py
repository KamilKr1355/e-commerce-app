from enum import Enum


class Providers(Enum):
    stripe = "stripe"


class PaymentMethod(Enum):
    blik = "blik"
    card = "card"
    transfer = "transfer"


class Status(Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class Courier(Enum):
    dhl = "dhl"
    dhl_paczkomat = "dhl_paczkomat"
    inpost = "inpost"
    inpost_paczkomat = "inpost_paczkomat"
    dpd = "dpd"
    dpd_paczkomat = "dpd_paczkomat"
    orlen = "orlen"
    
class CourierPrice(Enum):
    dhl = 25
    dhl_paczkomat = 22.30
    inpost = 17.10
    inpost_paczkomat = 15.90
    dpd = 25
    dpd_paczkomat = 12.50
    orlen = 12.29
    
    


class DeliveryType(Enum):
    courier = "courier"
    paczkomat = "paczkomat"
    
