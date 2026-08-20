
# IMPORTS


# os is used to read environment variables.
import os

# json converts the AI JSON text into a Python dictionary.
import json

# base64 converts the receipt image into text form
# so it can be sent to the OpenAI API.
import base64

# Path helps us work safely with file paths.
from pathlib import Path

# load_dotenv loads values from our .env file.
from dotenv import load_dotenv

# Official OpenAI Python client.
from openai import OpenAI

# Import our Pydantic Receipt model.
from backend.schemas.receipt import Receipt



# LOAD ENVIRONMENT VARIABLES


# Loads values such as:
#
# OPENAI_API_KEY=...
#
# from:
#
# C:\ai-payment-reconciliation\.env
load_dotenv()



# CREATE OPENAI CLIENT


# Read the API key from the environment.
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)



# IMAGE ENCODER


def encode_image(image_path):

    # Open the image in binary mode.
    with open(image_path, "rb") as image_file:

        # Read all bytes from the image.
        image_bytes = image_file.read()

        # Convert image bytes into base64 text.
        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        # Return the encoded image.
        return encoded_image



# RECEIPT EXTRACTION FUNCTION


def extract_receipt_details(
    image_path,
    customer_name,
    phone_number
):

    
    # CONVERT IMAGE PATH
    

    # Convert incoming path into a Path object.
    image_path = Path(image_path)


    
    # CHECK IMAGE EXISTS
    

    # Stop if the image cannot be found.
    if not image_path.exists():

        raise FileNotFoundError(
            f"Receipt image not found: {image_path}"
        )


    
    # ENCODE IMAGE
    

    base64_image = encode_image(
        image_path
    )


    
    # SEND IMAGE TO OPENAI
    

    response = client.responses.create(

        # Vision-capable model.
        model="gpt-5.6",

        input=[
            {
                "role": "user",

                "content": [

                    
                    # EXTRACTION INSTRUCTIONS
                    

                    {
                        "type": "input_text",

                        "text": """
You are extracting payment information from a payment receipt image.

Return ONLY valid JSON.

Extract exactly these fields:

amount
utr
transaction_id
payment_date
payment_time
payment_status
payer_name
payee_name
payment_app


IMPORTANT ID RULES:

1. "utr" means:

   - UTR
   - UPI transaction ID
   - UPI reference number
   - bank reference number

   Examples:

   UPI transaction ID:
   127473011105

   UTR:
   156985157872

   Store this value in:

   "utr"


2. "transaction_id" means the payment application's
   own transaction ID.

   This is very important for reconciliation.

   Examples:

   Google transaction ID:
   CICAgJjZ-aKHag

   PhonePe Transaction ID:
   OLEX2608091457431473534882

   Paytm Transaction ID:
   202608091234567890

   Store this value in:

   "transaction_id"


3. If BOTH a UPI/UTR reference and an app transaction ID
   are visible, keep them separate.

   Example:

   UPI transaction ID:
   127473011105

   Google transaction ID:
   CICAgJjZ-aKHag

   Correct output:

   "utr": "127473011105"

   "transaction_id": "CICAgJjZ-aKHag"


4. NEVER place the UTR / UPI transaction ID inside
   "transaction_id" when a separate app transaction ID
   is visible.


OTHER EXTRACTION RULES:

5. Do not guess missing values.

6. If a value is not visible or cannot be determined,
   return null.

7. amount must contain only the numeric payment amount.

   Example:

   ₹52,360

   should become:

   52360


8. payment_status must be one of:

   SUCCESS
   FAILED
   PENDING
   UNKNOWN


9. Treat words such as these as SUCCESS:

   Successful
   Completed
   Paid
   Payment successful


10. payment_date should be returned in:

    YYYY-MM-DD


11. payment_time should be returned in:

    HH:MM

    using 24-hour format.

    Example:

    4:59 PM

    becomes:

    16:59


12. payer_name means the person/business who sent the money.

13. payee_name means the person/business who received the money.

14. payment_app should identify the payment application
    when visible.

    Examples:

    Google Pay
    PhonePe
    Paytm


Example Google Pay receipt:

{
  "amount": 52360,
  "utr": "127473011105",
  "transaction_id": "CICAgJjZ-aKHag",
  "payment_date": "2026-08-06",
  "payment_time": "16:59",
  "payment_status": "SUCCESS",
  "payer_name": "SUSHMANITI CONSTRUCTIONS",
  "payee_name": "SHIVA KARTHIKEYAA STEELS",
  "payment_app": "Google Pay"
}
"""
                    },


                    
                    # RECEIPT IMAGE
                    

                    {
                        "type": "input_image",

                        "image_url": (
                            "data:image/jpeg;base64,"
                            f"{base64_image}"
                        )
                    }
                ]
            }
        ]
    )


    
    # GET RAW AI RESULT
    

    raw_result = response.output_text.strip()


    print("\nRAW AI RESULT:")

    print(raw_result)


    
    # CONVERT JSON STRING TO PYTHON DICTIONARY
    

    receipt_data = json.loads(
        raw_result
    )


    
    # ADD WHATSAPP CUSTOMER DATA
    

    # These fields come from Neonize,
    # not from the receipt image.
    receipt_data["customer_name"] = customer_name

    receipt_data["phone_number"] = phone_number


    
    # PYDANTIC VALIDATION
    

    # Validate the final combined data.
    receipt = Receipt(
        **receipt_data
    )


    
    # PRINT VALIDATED DATA
    

    print("\nVALIDATED RECEIPT:")

    print(receipt)


    
    # RETURN FINAL RECEIPT OBJECT
    

    return receipt



# TEST CODE


if __name__ == "__main__":

    # Use one payment receipt already downloaded.
    image_path = (
        "data/receipts/"
        "2026-08-09_18-36-45_Sarran_919360968857.jpg"
    )


    # In the live application these two values
    # come automatically from Neonize.
    receipt = extract_receipt_details(

        image_path=image_path,

        customer_name="Sarran",

        phone_number="919360968857"
    )


    print("\nFINAL RECEIPT OBJECT:")

    print(receipt)