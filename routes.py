

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from pathlib import Path

import shutil

import pandas as pd



router = APIRouter()

STATEMENT_FOLDER = Path(
    "data/statements"
)

CURRENT_STATEMENT_PATH = (
    STATEMENT_FOLDER
    / "current_statement.csv"
)

REPORT_PATH = Path(
    "data/reports/reconciliation_report.xlsx"
)


# HEALTH CHECK


@router.get("/health")
def health_check():

    return {
        "status": "ok"
    }



# UPLOAD STATEMENT


@router.post("/upload-statement")
async def upload_statement(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Only CSV statement files are supported."
        )


    STATEMENT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )


    try:

        with open(
            CURRENT_STATEMENT_PATH,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save statement: "
                f"{error}"
            )
        )


    return {

        "message":
            "Statement uploaded successfully",

        "filename":
            file.filename,

        "saved_as":
            str(CURRENT_STATEMENT_PATH)
    }


# GET MATCHED PAYMENTS

@router.get("/matches")
def get_matches():

    if not REPORT_PATH.exists():

        return []


    try:

        dataframe = pd.read_excel(
            REPORT_PATH,
            engine="openpyxl"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to read reconciliation report: "
                f"{error}"
            )
        )


    if dataframe.empty:

        return []


    # Keep identifiers as text.
    if "Phone Number" in dataframe.columns:

        dataframe["Phone Number"] = (
            dataframe["Phone Number"]
            .astype(str)
        )


    if "UTR" in dataframe.columns:

        dataframe["UTR"] = (
            dataframe["UTR"]
            .astype(str)
        )


    if "Transaction ID" in dataframe.columns:

        dataframe["Transaction ID"] = (
            dataframe["Transaction ID"]
            .astype(str)
        )


    # Convert NaN into None for JSON.
    dataframe = dataframe.astype(
        object
    ).where(
        pd.notnull(dataframe),
        None
    )


    return dataframe.to_dict(
        orient="records"
    )


# ACCOUNTANT CONFIRM PAYMENT


@router.post(
    "/payments/{transaction_id}/confirm"
)
def confirm_payment(
    transaction_id: str
):

    
    # CHECK REPORT EXISTS
   

    if not REPORT_PATH.exists():

        raise HTTPException(
            status_code=404,
            detail="Reconciliation report not found."
        )

    # READ REPORT

    try:

        dataframe = pd.read_excel(
            REPORT_PATH,
            engine="openpyxl"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to read reconciliation report: "
                f"{error}"
            )
        )


    # CHECK TRANSACTION COLUMN
    

    if "Transaction ID" not in dataframe.columns:

        raise HTTPException(
            status_code=500,
            detail="Transaction ID column missing in report."
        )


    # NORMALIZE TRANSACTION IDS

    dataframe["Transaction ID"] = (
        dataframe["Transaction ID"]
        .astype(str)
        .str.strip()
    )


    transaction_id = str(
        transaction_id
    ).strip()


    # FIND SELECTED PAYMENT

    selected_rows = dataframe[
        dataframe["Transaction ID"]
        == transaction_id
    ]


    if selected_rows.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Transaction not found: "
                f"{transaction_id}"
            )
        )


    row_index = selected_rows.index[0]

    row = selected_rows.iloc[0]


    # CHECK MATCH STATUS

    match_status = str(
        row.get(
            "Match Status",
            ""
        )
    ).strip()


    if match_status.upper() != "MATCHED":

        raise HTTPException(
            status_code=400,
            detail="Payment is not in MATCHED status."
        )


    # CREATE APPROVAL COLUMN IF NEEDED

    if "Accountant Approval" not in dataframe.columns:

        dataframe[
            "Accountant Approval"
        ] = ""


    # PREVENT DUPLICATE APPROVAL

    existing_approval = str(
        dataframe.loc[
            row_index,
            "Accountant Approval"
        ]
    ).strip()


    if existing_approval.upper() == "APPROVED":

        return {

            "status":
                "already_approved",

            "message":
                "Payment was already approved by accountant",

            "transaction_id":
                transaction_id
        }


    # APPROVE PAYMENT

    dataframe.loc[
        row_index,
        "Accountant Approval"
    ] = "APPROVED"


    # SAVE UPDATED REPORT

    try:

        dataframe.to_excel(
            REPORT_PATH,
            index=False,
            engine="openpyxl"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to update reconciliation report: "
                f"{error}"
            )
        )


    # RETURN APPROVAL RESULT

    return {

        "status":
            "approved",

        "message":
            "Payment approved by accountant",

        "transaction_id":
            transaction_id,

        "customer_name":
            str(
                row.get(
                    "Customer Name",
                    ""
                )
            ),

        "phone_number":
            str(
                row.get(
                    "Phone Number",
                    ""
                )
            ),

        "amount":
            float(
                row.get(
                    "Amount",
                    0
                )
            ),

        "utr":
            str(
                row.get(
                    "UTR",
                    ""
                )
            ),

        "payment_date":
            str(
                row.get(
                    "Payment Date",
                    ""
                )
            ),

        "accountant_approval":
            "APPROVED"
    }