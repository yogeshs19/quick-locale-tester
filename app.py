import streamlit as st
from babel.dates import format_date, format_time
from babel.numbers import format_decimal, format_currency
from datetime import datetime

# Title
st.title("Quick Locale Tester (FR / DE)")

# Inputs
st.subheader("Enter your values")
number_input = st.number_input("Enter a number:", value=1234567.89)
date_input = st.date_input("Pick a date:", value=datetime.today())
currency_input = st.number_input("Enter a currency amount:", value=246.88)
locale_choice = st.selectbox("Select Locale", ["fr_FR", "de_DE"])

# Output section
st.subheader(f"Results for {locale_choice}")

# Date formatting
st.write("**Date formats:**")
st.write("Short:", format_date(date_input, format="short", locale=locale_choice))
st.write("Long:", format_date(date_input, format="long", locale=locale_choice))
st.write("Time:", format_time(datetime.now(), format="short", locale=locale_choice))

# Number formatting
st.write("**Number formats:**")
st.write("Standard:", format_decimal(number_input, locale=locale_choice))

# Currency formatting
st.write("**Currency formats:**")
st.write("EUR:", format_currency(currency_input, "EUR", locale=locale_choice))

# Style guide notes
if locale_choice == "fr_FR":
    st.info("French (FR): dd/MM/yyyy dates, 24h time, comma as decimal, space as thousands separator, € follows number with space.")
else:
    st.info("German (DE): d.M.yyyy dates, 24h time, comma as decimal, period as thousands separator, € follows number with space.")
