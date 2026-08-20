# IMPORTS

from pathlib import Path

from backend.graph.state import PaymentState

from backend.services.receipt_classifier import (
    classify_receipt
)

from backend.services.receipt_extractor import (
    extract_receipt_details
)

from backend.services.bank_parser import (
    parse_bank_statement
)

from backend.services.matcher import (
    match_receipt
)


# STATEMENT PATH

STATEMENT_PATH = Path(
    "data/statements/current_statement.csv"
)


# CLASSIFY NODE

def classify_node(
    state: PaymentState
):

    # Get image path from LangGraph state.
    image_path = state[
        "image_path"
    ]

    # Run our existing payment classifier.
    is_payment = classify_receipt(
        image_path
    )

    # Return values back into LangGraph state.
    return {

        "is_payment":
            is_payment,

        "status":
            (
                "PAYMENT"
                if is_payment
                else "NOT_PAYMENT"
            )
    }


# EXTRACT NODE

def extract_node(
    state: PaymentState
):

    # Read required values from state.
    image_path = state[
        "image_path"
    ]

    customer_name = state[
        "customer_name"
    ]

    phone_number = state[
        "phone_number"
    ]


    # Run existing receipt extractor.
    receipt = extract_receipt_details(

        image_path=image_path,

        customer_name=customer_name,

        phone_number=phone_number
    )


    # Store extracted receipt in state.
    return {

        "receipt":
            receipt,

        "status":
            "EXTRACTED"
    }



# LOAD STATEMENT NODE

def load_statement_node(
    state: PaymentState
):

    # CHECK STATEMENT EXISTS

    if not STATEMENT_PATH.exists():

        return {

            "transactions":
                [],

            "status":
                "STATEMENT_NOT_FOUND",

            "error":
                "No uploaded statement found."
        }


    # PARSE STATEMENT

    transactions = parse_bank_statement(
        STATEMENT_PATH
    )


    # DEBUG OUTPUT

    print(
        f"\nSTATEMENT TRANSACTIONS LOADED: "
        f"{len(transactions)}"
    )


    for transaction in transactions:

        print(
            "STATEMENT:",
            transaction.transaction_id,
            transaction.amount,
            transaction.transaction_date
        )


    # RETURN TRANSACTIONS TO LANGGRAPH STATE

    return {

        "transactions":
            transactions,

        "status":
            "STATEMENT_LOADED",

        "error":
            None
    }


# MATCH NODE

def match_node(
    state: PaymentState
):

    # GET RECEIPT
    

    receipt = state[
        "receipt"
    ]


    # GET STATEMENT TRANSACTIONS

    transactions = state.get(
        "transactions",
        []
    )


    # NO TRANSACTIONS

    if not transactions:

        return {

            "matched_transaction":
                None,

            "status":
                "NOT_MATCHED"
        }


    # RUN MATCHER

    matched_transaction = match_receipt(
        receipt,
        transactions
    )


    # MATCH FOUND

    if matched_transaction:

        return {

            "matched_transaction":
                matched_transaction,

            "status":
                "MATCHED"
        }


    # NO MATCH

    return {

        "matched_transaction":
            None,

        "status":
            "NOT_MATCHED"
    }
