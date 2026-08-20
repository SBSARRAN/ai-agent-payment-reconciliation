
# IMPORTS


from backend.schemas.receipt import Receipt
from backend.schemas.bank_transaction import BankTransaction



# NORMALIZE TEXT


def normalize_text(value):
    """
    Convert a value to clean text.

    This prevents matching problems caused by:
    - spaces
    - different Python types
    - uppercase/lowercase differences
    """

    if value is None:
        return ""

    return str(value).strip().lower()



# NORMALIZE DATE


def normalize_date(value):
    """
    Convert the date to YYYY-MM-DD text.

    Example:

    "2026-08-06"
            ↓
    "2026-08-06"

    Python date(2026, 8, 6)
            ↓
    "2026-08-06"
    """

    if value is None:
        return ""

    # If this is a Python date/datetime object,
    # isoformat() converts it to YYYY-MM-DD.
    if hasattr(value, "isoformat"):

        return value.isoformat()[:10]

    # Otherwise convert it to text.
    return str(value).strip()[:10]



# MATCH RECEIPT AGAINST STATEMENT


def match_receipt(
    receipt: Receipt,
    bank_transactions: list[BankTransaction]
):

    print("\n")
    print("STARTING PAYMENT MATCH")
    print("")


    
    # NORMALIZE RECEIPT VALUES
    

    receipt_transaction_id = normalize_text(
        receipt.transaction_id
    )

    receipt_amount = round(
        float(receipt.amount),
        2
    )

    receipt_date = normalize_date(
        receipt.payment_date
    )


    print(
        "RECEIPT TRANSACTION ID:",
        receipt_transaction_id
    )

    print(
        "RECEIPT AMOUNT:",
        receipt_amount
    )

    print(
        "RECEIPT DATE:",
        receipt_date
    )


    
    # LOOP THROUGH STATEMENT
    

    for transaction in bank_transactions:

        
        # NORMALIZE STATEMENT VALUES
        

        statement_transaction_id = normalize_text(
            transaction.transaction_id
        )

        statement_amount = round(
            float(transaction.amount),
            2
        )

        statement_date = normalize_date(
            transaction.transaction_date
        )


        print("\nCHECKING STATEMENT TRANSACTION")

        print(
            "ID:",
            statement_transaction_id
        )

        print(
            "AMOUNT:",
            statement_amount
        )

        print(
            "DATE:",
            statement_date
        )


        
        # TRANSACTION ID MATCH
        

        id_match = (
            receipt_transaction_id
            != ""
            and
            statement_transaction_id
            != ""
            and
            receipt_transaction_id
            == statement_transaction_id
        )


        
        # AMOUNT MATCH
        

        amount_match = (
            receipt_amount
            ==
            statement_amount
        )


        
        # DATE MATCH
        

        date_match = (
            receipt_date
            != ""
            and
            statement_date
            != ""
            and
            receipt_date
            ==
            statement_date
        )


        
        # DEBUG MATCH RESULT
        

        print(
            "ID MATCH:",
            id_match
        )

        print(
            "AMOUNT MATCH:",
            amount_match
        )

        print(
            "DATE MATCH:",
            date_match
        )


        
        # FINAL MATCH
        

        if (
            id_match
            and
            amount_match
            and
            date_match
        ):

            print(
                "\n================================"
            )

            print(
                "PAYMENT MATCHED ✅"
            )

            print(
                "================================"
            )

            print(
                "TRANSACTION ID:",
                receipt.transaction_id
            )

            print(
                "AMOUNT:",
                receipt.amount
            )

            print(
                "DATE:",
                receipt.payment_date
            )

            print(
                "STATEMENT PAYER:",
                getattr(
                    transaction,
                    "payer_name",
                    None
                )
            )

            return transaction


    
    # NO MATCH
    

    print(
        "\n================================"
    )

    print(
        "NO MATCH FOUND ❌"
    )

    print(
        "================================"
    )

    return None