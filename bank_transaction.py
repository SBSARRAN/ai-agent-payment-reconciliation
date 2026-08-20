# IMPORTS


from pydantic import BaseModel
from typing import Optional


# BANK TRANSACTION MODEL

class BankTransaction(BaseModel):

    # Name shown in Excel.
    payer_name: str

    # Google Pay / PhonePe / Unknown app
    payment_app: Optional[str] = None

    # UPI / NEFT / IMPS etc.
    transaction_type: Optional[str] = None

    # Example:
    # 2026-08-06
    transaction_date: str

    # Example:
    # 16:59
    transaction_time: Optional[str] = None

    # Important matching field.
    #
    # Example:
    # CICAgJjZ-aKHag
    transaction_id: Optional[str] = None

    # Payment amount.
    amount: float

    # Settled / Pending / Failed
    status: str

    # Optional notes.
    notes: Optional[str] = None