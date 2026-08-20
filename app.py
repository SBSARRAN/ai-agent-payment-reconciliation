
# IMPORTS


import streamlit as st
import requests
import pandas as pd



# SETTINGS


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Payment Reconciliation",
    page_icon="💳",
    layout="wide"
)



# TITLE


st.title("💳 AI Payment Reconciliation")

st.write(
    "Customer payment receipts are received through WhatsApp, "
    "processed by AI and matched with the uploaded statement."
)

st.divider()



# CHECK BACKEND


try:

    response = requests.get(
        f"{API_URL}/health",
        timeout=5
    )

    backend_connected = (
        response.status_code == 200
    )

except requests.RequestException:

    backend_connected = False


if backend_connected:

    st.success(
        "Backend Connected"
    )

else:

    st.error(
        "Backend Not Connected"
    )



# STATEMENT UPLOAD


st.subheader(
    "1. Upload Transaction Statement"
)


uploaded_file = st.file_uploader(
    "Choose CSV statement",
    type=["csv"]
)


if uploaded_file is not None:

    if st.button(
        "Upload Statement",
        type="primary"
    ):

        try:

            files = {

                "file": (

                    uploaded_file.name,

                    uploaded_file.getvalue(),

                    "text/csv"
                )
            }


            response = requests.post(
                f"{API_URL}/upload-statement",
                files=files,
                timeout=30
            )


            if response.status_code == 200:

                st.success(
                    "Statement uploaded successfully."
                )

            else:

                st.error(
                    "Statement upload failed."
                )


        except requests.RequestException as error:

            st.error(
                f"Connection error: {error}"
            )


st.divider()



# LIVE RECONCILIATION RESULTS


st.subheader(
    "2. Live Reconciliation Results"
)

st.caption(
    "This section refreshes automatically every 5 seconds."
)



# AUTO REFRESH SECTION


# Streamlit reruns only this section every 5 seconds.
#
# So when WhatsApp → LangGraph creates a new match,
# it automatically appears here without manually
# pressing Refresh.

@st.fragment(
    run_every="5s"
)
def show_live_matches():

    
    # CHECK BACKEND
    

    if not backend_connected:

        st.warning(
            "FastAPI backend is not connected."
        )

        return


    
    # GET MATCHED PAYMENTS
    

    try:

        response = requests.get(
            f"{API_URL}/matches",
            timeout=10
        )

    except requests.RequestException as error:

        st.error(
            f"Could not load matches: {error}"
        )

        return


    
    # CHECK RESPONSE
    

    if response.status_code != 200:

        st.error(
            "Failed to load reconciliation results."
        )

        return


    matches = response.json()


    
    # NO MATCHES
    

    if not matches:

        st.info(
            "Waiting for matched WhatsApp payments..."
        )

        return


    
    # SHOW SUMMARY
    

    approved_count = 0


    for payment in matches:

        approval = str(
            payment.get(
                "Accountant Approval",
                ""
            )
        ).strip().upper()


        if approval == "APPROVED":

            approved_count += 1


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Matched Payments",
            len(matches)
        )


    with col2:

        st.metric(
            "Approved Payments",
            approved_count
        )


    
    # CONVERT TO DATAFRAME
    

    dataframe = pd.DataFrame(
        matches
    )


    
    # COLUMNS WE WANT TO DISPLAY
    

    preferred_columns = [

        "Customer Name",

        "Phone Number",

        "Amount",

        "UTR",

        "Transaction ID",

        "Payment Date",

        "Payment Time",

        "Payment App",

        "Statement Payer",

        "Match Status",

        "Accountant Approval"
    ]


    available_columns = [

        column

        for column in preferred_columns

        if column in dataframe.columns
    ]


    
    # SHOW TABLE
    

    st.dataframe(
        dataframe[
            available_columns
        ],
        use_container_width=True,
        hide_index=True
    )


    st.divider()


    
    # ACCOUNTANT APPROVAL
    

    st.subheader(
        "3. Payment Approval"
    )


    payment_options = {}


    for payment in matches:

        transaction_id = str(
            payment.get(
                "Transaction ID",
                ""
            )
        )


        customer = str(
            payment.get(
                "Customer Name",
                "Unknown"
            )
        )


        amount = float(
            payment.get(
                "Amount",
                0
            )
        )


        approval = str(
            payment.get(
                "Accountant Approval",
                ""
            )
        ).strip()


        label = (
            f"{customer} | "
            f"₹{amount:,.2f} | "
            f"{transaction_id}"
        )


        if approval.upper() == "APPROVED":

            label += " | APPROVED"


        payment_options[
            label
        ] = payment


    
    # SELECT PAYMENT
    

    selected_label = st.selectbox(
        "Select Payment",
        list(
            payment_options.keys()
        ),
        key="payment_selector"
    )


    selected_payment = (
        payment_options[
            selected_label
        ]
    )


    
    # SHOW PAYMENT DETAILS
    

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Customer",
            selected_payment.get(
                "Customer Name",
                "-"
            )
        )


    with col2:

        amount = float(
            selected_payment.get(
                "Amount",
                0
            )
        )

        st.metric(
            "Amount",
            f"₹{amount:,.2f}"
        )


    with col3:

        st.metric(
            "Match Status",
            selected_payment.get(
                "Match Status",
                "-"
            )
        )


    st.write(
        "**Transaction ID:**",
        selected_payment.get(
            "Transaction ID",
            "-"
        )
    )


    st.write(
        "**UTR:**",
        selected_payment.get(
            "UTR",
            "-"
        )
    )


    st.write(
        "**Payment Date:**",
        selected_payment.get(
            "Payment Date",
            "-"
        )
    )


    st.write(
        "**Statement Payer:**",
        selected_payment.get(
            "Statement Payer",
            "-"
        )
    )


    
    # APPROVAL STATUS
    

    approval = str(
        selected_payment.get(
            "Accountant Approval",
            ""
        )
    ).strip()


    if approval.upper() == "APPROVED":

        st.success(
            "Payment Approved ✅"
        )


    else:

        st.warning(
            "Waiting for Accountant Approval"
        )


        # -------------------------------------------------
        # APPROVE BUTTON
        # -------------------------------------------------

        if st.button(
            "Approve Payment",
            type="primary",
            key="approve_payment"
        ):

            transaction_id = str(
                selected_payment.get(
                    "Transaction ID",
                    ""
                )
            )


            try:

                response = requests.post(
                    (
                        f"{API_URL}/payments/"
                        f"{transaction_id}/confirm"
                    ),
                    timeout=10
                )


                if response.status_code == 200:

                    st.success(
                        "Payment approved successfully."
                    )

                    st.rerun()


                else:

                    try:

                        error_data = response.json()

                        st.error(
                            str(
                                error_data.get(
                                    "detail",
                                    "Approval failed."
                                )
                            )
                        )

                    except Exception:

                        st.error(
                            "Approval failed."
                        )


            except requests.RequestException as error:

                st.error(
                    f"Connection error: {error}"
                )



# RUN LIVE SECTION


show_live_matches()