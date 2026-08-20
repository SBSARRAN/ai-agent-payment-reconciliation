
# IMPORTS


# os lets us read environment variables such as OPENAI_API_KEY.
import os

# base64 converts the image into text format so it can be
# sent inside the API request.
import base64

# Path helps us work with image file paths.
from pathlib import Path

# load_dotenv loads values from our .env file.
from dotenv import load_dotenv

# OpenAI is the official OpenAI Python client.
from openai import OpenAI



# LOAD .ENV


# Read variables from:
#
# C:\ai-payment-reconciliation\.env
load_dotenv()



# CREATE OPENAI CLIENT


# OpenAI automatically uses the API key
# stored in the OPENAI_API_KEY environment variable.
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)



# CONVERT IMAGE TO BASE64


def encode_image(image_path):

    # Open the image in binary mode.
    #
    # "rb" means:
    # read binary.
    with open(image_path, "rb") as image_file:

        # Read the image bytes.
        image_bytes = image_file.read()

        # Convert bytes into base64 text.
        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        return encoded_image



# CLASSIFY IMAGE


def classify_receipt(image_path):

    # Convert the path into a Path object.
    image_path = Path(image_path)


    # Check whether the image actually exists.
    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    # Convert image into base64.
    base64_image = encode_image(image_path)


    
    # SEND IMAGE TO OPENAI
    

    response = client.responses.create(

        # Use a vision-capable OpenAI model.
        model="gpt-5.6",

        input=[
            {
                "role": "user",

                "content": [

                    
                    # INSTRUCTION FOR THE AI
                    

                    {
                        "type": "input_text",

                        "text": """
Look at this image and determine whether it is a payment receipt.

A payment receipt includes things such as:
- UPI payment confirmation
- Google Pay receipt
- PhonePe receipt
- Paytm receipt
- bank transfer confirmation
- transaction successful screen

Return ONLY one word:

PAYMENT

or

NOT_PAYMENT

Do not guess.
"""
                    },


                    # -------------------------------------------------
                    # IMAGE
                    # -------------------------------------------------

                    {
                        "type": "input_image",

                        # Send our image as a base64 data URL.
                        "image_url": (
                            f"data:image/jpeg;base64,"
                            f"{base64_image}"
                        )
                    }
                ]
            }
        ]
    )


    
    # GET AI RESPONSE
    

    # output_text contains the text returned by the model.
    result = response.output_text.strip()


    # Print result for testing.
    print(
        f"CLASSIFICATION RESULT: {result}"
    )


    
    # CONVERT RESULT INTO TRUE / FALSE
    

    if result == "PAYMENT":
        return True

    return False



# TEST CODE


# Python main guard.
#
# This lets us test this file directly.
if __name__ == "__main__":

    # Change this filename to one of the images
    # already downloaded from WhatsApp.
    image_path = (
        "data/receipts/"
        "2026-08-09_17-27-41_Magic_wallz_224588252373015.jpg"
    )


    # Run classifier.
    is_payment = classify_receipt(
        image_path
    )


    # Show final result.
    print(
        f"IS PAYMENT RECEIPT: {is_payment}"
    )