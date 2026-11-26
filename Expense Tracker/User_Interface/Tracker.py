import streamlit as st
import gspread
from pathlib import Path
import re
from sheet import user_sheet 

BASE_DIR = Path(__file__).resolve().parent
credentials_file = BASE_DIR / "EXP_TRK.json"

gc = gspread.service_account(filename=credentials_file)

spreadsheet = gc.open_by_key(
    "1aXn65_c11extJTEuG2PwApy42pJNJh9AMGuGwQYKoxw"
)

worksheet = spreadsheet.sheet1


st.set_page_config(
    page_icon="💶",
    page_title="Expense Tracker",
    layout="centered"
)

st.title("Expense Tracker")
page = st.sidebar.selectbox(
    "Menu",
    ["Add Expense", "Dashboard","Report System"]
)

if page == "Add Expense":

 st.subheader("Add New Expense")

 with st.form("expense form"):
    
    date = st.date_input("Date")
    date = date.strftime("%Y-%m-%d")

    category = st.selectbox(
        "Category",
        ["Food", "Shopping", "Education", "Transportation", "Others"],
    )

    item = st.text_input("Item")

    price = st.number_input("Price")

    submitted = st.form_submit_button("Add expense")
    
 if submitted:
    if item == "":
        st.error("Please enter the item")
    elif price <= 0:
        st.error("Please enter a price greater than 0")
    else:
        ids = worksheet.col_values(1)

        if len(ids) <= 1:
            new_id = 1
        else:
            try:
                latest_id = max(
                    int(value) for value in ids[1:] if value.strip()
                )
                new_id = latest_id + 1
            except ValueError:
                new_id = 1

        expense_row = [
            new_id,
            date,
            category,
            item,
            price,
        ]

        worksheet.append_row(expense_row)

        st.success("Expense Added Successfully")
        
elif page == "Dashboard":
    st.iframe(
    "https://script.google.com/macros/s/AKfycbysaMNeZ6y6BbV_sqM6LnKmQeJIn6twWOX9uRve_XwtIyTBtYzfgRWCMNP6kUBZK8_Rig/exec",
    height=900,
    width="stretch"
)
    
elif page == "Report System":

    st.subheader("Monthly Financial Report")

    with st.form("report_form"):

        name = st.text_input("Enter your name")

        email = st.text_input("Enter your email")

        submitted = st.form_submit_button("Activate Monthly Reports")

    if submitted:

        if name.strip() == "":
            st.error("Please enter your name.")

        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            st.error("Please enter a valid email address.")

        else:
            user_sheet.append_row([
                name.strip(),
                email.strip(),
                True
            ])

            st.success("Monthly report system activated successfully!")    
