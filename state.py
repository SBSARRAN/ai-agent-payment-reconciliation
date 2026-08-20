from typing import TypedDict
from typing import Any
from typing import Optional

class PaymentState(TypedDict,total=False):
    image_path : str
    customer_name : str
    phone_number : str
    is_payment : bool
    receipt : Any
    transactions : list
    matched_transaction : Optional[Any]
    status : str
    error : Optional[str]
