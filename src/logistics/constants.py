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
    inpost = "inpost"
    dhl = "dhl"


class DeliveryType(Enum):
    courier = "courier"
    paczkomat = "paczkomat"
