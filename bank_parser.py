
# IMPORTS


# Path helps us work with file paths.
from pathlib import Path

# Pandas is used to read the CSV transaction statement.
import pandas as pd

# Import our Pydantic BankTransaction model.
from backend.schemas.bank_transaction import BankTransaction



# BANK STATEMENT PARSER


def parse_bank_statement(file_path):

    # Convert the incoming path into a Path object.
    file_path = Path(file_path)


    
    # CHECK FILE EXISTS
    

    if not file_path.exists():

        raise FileNotFoundError(
            f"Bank statement not found: {file_path}"
        )


    
    # CHECK FILE TYPE
    

    # Your Google Pay Business export is a CSV file.
    if file_path.suffix.lower() != ".csv":

        raise ValueError(
            "Only .csv transaction statements are supported for now."
        )


    
    # READ CSV FILE
    

    # Pandas reads the CSV and creates a DataFrame.
    dataframe = pd.read_csv(
        file_path
    )


    
    # CLEAN COLUMN NAMES
    

    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]


    
    # REQUIRED COLUMNS
    

    required_columns = [
        "Payer/Receiver",
        "Paid via",
        "Type",
        "Creation time",
        "Transaction ID",
        "Amount",
        "Status"
    ]


    for column in required_columns:

        if column not in dataframe.columns:

            raise ValueError(
                f"Missing required column: {column}"
            )


    
    # FINAL TRANSACTION LIST
    

    transactions = []


    
    # PROCESS EACH ROW
    

    for _, row in dataframe.iterrows():

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        status = str(
            row["Status"]
        ).strip()


        # Only settled transactions should be considered
        # for reconciliation.
        if status.lower() != "settled":

            continue


        # -------------------------------------------------
        # CREATION DATE + TIME
        # -------------------------------------------------

        creation_time = pd.to_datetime(
            row["Creation time"],
            errors="coerce"
        )


        # Skip invalid dates.
        if pd.isna(creation_time):

            continue


        transaction_date = creation_time.strftime(
            "%Y-%m-%d"
        )


        transaction_time = creation_time.strftime(
            "%H:%M"
        )


        # -------------------------------------------------
        # PAYMENT APP
        # -------------------------------------------------

        payment_app = str(
            row["Paid via"]
        ).strip()


        # Fix encoding issue such as:
        #
        # GoogleÂ Pay
        #
        # becomes:
        #
        # Google Pay
        # Remove encoding problems.
        payment_app = payment_app.replace(
            "Â",
            ""
        )

        # Replace non-breaking spaces with normal spaces.
        #
        # Example:
        # Google\xa0Pay
        # becomes:
        # Google Pay
        payment_app = payment_app.replace(
            "\xa0",
            " "
        )

        # Remove any extra spaces.
        payment_app = " ".join(
            payment_app.split()
        )


        
        # TRANSACTION TYPE
       

        transaction_type = str(
            row["Type"]
        ).strip()


        
        # TRANSACTION ID
        

        # IMPORTANT:
        #
        # Keep the transaction ID exactly as it appears.
        #
        # Example:
        #
        # CICAgJjZ-aKHag
        transaction_id = str(
            row["Transaction ID"]
        ).strip()


       
        # AMOUNT
       

        amount = float(
            row["Amount"]
        )


        
        # PAYER NAME
        

        payer_name = str(
            row["Payer/Receiver"]
        ).strip()


       
        # NOTES
        

        notes = None


        if "Notes" in dataframe.columns:

            notes_value = row["Notes"]


            if not pd.isna(notes_value):

                notes = str(
                    notes_value
                ).strip()


        
        # CREATE PYDANTIC BANK TRANSACTION
       

        transaction = BankTransaction(

            payer_name=payer_name,

            payment_app=payment_app,

            transaction_type=transaction_type,

            transaction_date=transaction_date,

            transaction_time=transaction_time,

            transaction_id=transaction_id,

            amount=amount,

            status=status,

            notes=notes
        )


        transactions.append(
            transaction
        )


    
    # RETURN TRANSACTIONS
    

    return transactions



# TEST CODE


if __name__ == "__main__":

    # Put the CSV statement inside:
    #
    # data/statements/
    #
    # Use your real Google Pay Business CSV filename here.
    statement_path = (
        "data/statements/"
        "GPay_Business_Transactions_20260806-20260806_1786088081508.csv"
    )


    # Parse the CSV statement.
    transactions = parse_bank_statement(
        statement_path
    )


    print(
        f"\nTOTAL SETTLED TRANSACTIONS: {len(transactions)}"
    )


    # Print each normalized transaction.
    for transaction in transactions:

        print(transaction)