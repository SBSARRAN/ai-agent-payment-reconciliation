# IMPORTS

# BaseModel is used to create a validated data model.
from pydantic import BaseModel

# Optional means a field can contain a value or None.
from typing import Optional


# RECEIPT MODEL

# This class defines the final structure
# of one customer payment receipt.
class Receipt(BaseModel):

    # Customer name from WhatsApp.
    customer_name: str

    # Customer phone number from WhatsApp.
    phone_number: str

    # Payment amount extracted from receipt.
    amount: float

    # UTR may sometimes be missing.
    utr: Optional[str] = None

    # Transaction ID may sometimes be missing.
    transaction_id: Optional[str] = None

    # Payment date.
    payment_date: Optional[str] = None

    # Payment time.
    payment_time: Optional[str] = None

    # SUCCESS / FAILED / PENDING / UNKNOWN
    payment_status: str

    # Payer name may not be visible.
    payer_name: Optional[str] = None

    # Payee/company name may not be visible.
    payee_name: Optional[str] = None

    # Example:
    # PhonePe / Google Pay / Paytm
    payment_app: Optional[str] = None