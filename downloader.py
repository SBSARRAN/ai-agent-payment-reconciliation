
# IMPORTS


from pathlib import Path
from datetime import datetime
import re

# LangGraph workflow
from backend.graph.workflow import payment_graph

# Report exporter
from backend.services.report_exporter import (
    export_matched_payment
)



# RECEIPT SAVE FOLDER


RECEIPT_FOLDER = Path(
    "data/receipts"
)



# CLEAN FILE NAME


def clean_filename(value: str) -> str:

    # Remove characters that Windows does not allow
    # inside file names.
    value = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        str(value)
    )

    # Remove extra spaces.
    value = value.strip()

    # If name is empty, use Unknown.
    if not value:

        value = "Unknown"

    return value



# DOWNLOAD WHATSAPP IMAGE


def download_image(
    client,
    message_event
):

    try:

        
        # GET MESSAGE
        

        message = message_event.Message

        info = message_event.Info


        
        # GET IMAGE MESSAGE
        

        image_message = message.imageMessage
        print("\nIMAGE MESSAGE TYPE:")
        print(type(image_message))

        print("\nFULL MESSAGE TYPE:")
        print(type(message))


        
        # GET PHONE NUMBER
        

        phone_number = str(
            info.MessageSource.Sender.User
        )


        
        # GET CUSTOMER NAME
        

        customer_name = None


        # Neonize may provide push name
        # from the WhatsApp message information.
        try:

            customer_name = (
                info.PushName
            )

        except Exception:

            customer_name = None


        # If no contact name is available,
        # use the mobile number.
        if not customer_name:

            customer_name = phone_number


        
        # CLEAN CUSTOMER VALUES
        

        customer_name = clean_filename(
            customer_name
        )

        phone_number = clean_filename(
            phone_number
        )


        
        # DOWNLOAD IMAGE BYTES
        

        # Neonize client.download_any()
        # downloads the media attached to the message.
        image_bytes = client.download_any(
            message
        )


        
        # CHECK IMAGE DATA
        

        if not image_bytes:

            print(
                "IMAGE DOWNLOAD FAILED: "
                "No image bytes returned."
            )

            return None


        
        # CREATE RECEIPT FOLDER
        

        RECEIPT_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )


        
        # CREATE TIMESTAMP
        

        now = datetime.now()

        timestamp = now.strftime(
            "%Y-%m-%d_%H-%M-%S"
        )


        
        # CREATE FILE NAME
        

        file_name = (
            f"{timestamp}_"
            f"{customer_name}_"
            f"{phone_number}.jpg"
        )


        
        # FINAL IMAGE PATH
        

        image_path = (
            RECEIPT_FOLDER
            / file_name
        )


        
        # SAVE IMAGE
        

        with open(
            image_path,
            "wb"
        ) as image_file:

            image_file.write(
                image_bytes
            )


        
        # SHOW DOWNLOAD RESULT
        

        print(
            "\nIMAGE DOWNLOADED:"
        )

        print(
            image_path
        )

        print(
            "CUSTOMER:",
            customer_name
        )

        print(
            "PHONE:",
            phone_number
        )


        
        # SEND IMAGE INTO LANGGRAPH
        

        process_downloaded_image(

            image_path=image_path,

            customer_name=customer_name,

            phone_number=phone_number
        )


        return image_path


    except Exception as error:

        print(
            "\nWHATSAPP IMAGE DOWNLOAD FAILED"
        )

        print(
            f"ERROR: {error}"
        )

        return None



# PROCESS DOWNLOADED IMAGE WITH LANGGRAPH


def process_downloaded_image(
    image_path,
    customer_name,
    phone_number
):

    
    # CONVERT PATH
    

    image_path = Path(
        image_path
    )


    print(
        "\nPROCESSING WITH LANGGRAPH"
    )

    print(
        f"IMAGE: {image_path}"
    )


    
    # INITIAL LANGGRAPH STATE
    

    initial_state = {

        "image_path":
            str(image_path),

        "customer_name":
            str(customer_name),

        "phone_number":
            str(phone_number),

        "status":
            "STARTED",

        "error":
            None
    }


    
    # RUN GRAPH
    

    try:

        result = payment_graph.invoke(
            initial_state
        )

    except Exception as error:

        print(
            "\nLANGGRAPH WORKFLOW FAILED"
        )

        print(
            f"ERROR: {error}"
        )

        return None


    
    # READ FINAL STATE
    

    status = result.get(
        "status"
    )

    is_payment = result.get(
        "is_payment",
        False
    )

    receipt = result.get(
        "receipt"
    )

    matched_transaction = result.get(
        "matched_transaction"
    )

    workflow_error = result.get(
        "error"
    )


    
    # SHOW FINAL STATUS
    

    print(
        "\nLANGGRAPH FINAL STATUS:",
        status
    )


    
    # WORKFLOW ERROR
    

    if workflow_error:

        print(
            "WORKFLOW ERROR:",
            workflow_error
        )

        return result


    
    # NOT PAYMENT
    

    if not is_payment:

        print(
            "NOT A PAYMENT RECEIPT - IGNORED"
        )

        return result


    
    # PAYMENT RECEIPT
    

    print(
        "PAYMENT RECEIPT DETECTED"
    )


    if receipt:

        print(
            "\nFINAL PAYMENT DATA:"
        )

        print(
            receipt
        )


    
    # MATCH FOUND
    

    if (
        status == "MATCHED"
        and
        matched_transaction is not None
    ):

        print(
            "\nPAYMENT MATCHED ✅"
        )


        print(
            "TRANSACTION ID:",
            getattr(
                receipt,
                "transaction_id",
                None
            )
        )


        print(
            "AMOUNT:",
            getattr(
                receipt,
                "amount",
                None
            )
        )


        print(
            "PAYMENT DATE:",
            getattr(
                receipt,
                "payment_date",
                None
            )
        )


        
        # EXPORT MATCH
        

        try:

            export_matched_payment(
                receipt,
                matched_transaction
            )

            print(
                "REPORT UPDATED ✅"
            )

        except Exception as error:

            print(
                "REPORT EXPORT FAILED:"
            )

            print(
                error
            )


    
    # NO MATCH
    

    else:

        print(
            "PAYMENT RECEIPT FOUND "
            "BUT NO STATEMENT MATCH FOUND"
        )


    return result