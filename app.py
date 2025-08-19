import streamlit as st
import pandas as pd
from babel.numbers import format_currency, format_decimal, format_percent
from babel.dates import format_date, format_time
from datetime import datetime

st.title("Quick Locale Tester")
st.write("Test number, currency, percent, date, and time formats across locales.")

# Default locales
default_locales = ["fr_FR", "de_DE", "ja_JP"]
locales = st.multiselect("Select Locales", default_locales, default=default_locales)

# Inputs
number = st.number_input("Number", value=1234567.89)
currency_code = st.text_input("Currency Code", value="JPY")
percent_value = st.slider("Percent", 0.0, 1.0, 0.42)
date_value = datetime.now()

results = []
for loc in locales:
    try:
        formatted_number = format_decimal(number, locale=loc)
        formatted_currency = format_currency(number, currency_code, locale=loc)
        formatted_percent = format_percent(percent_value, locale=loc)
        formatted_date = format_date(date_value, locale=loc)
        formatted_time = format_time(date_value, locale=loc)
        results.append({
            "Locale": loc,
            "Number": formatted_number,
            "Currency": formatted_currency,
            "Percent": formatted_percent,
            "Date": formatted_date,
            "Time": formatted_time
        })
    except Exception as e:
        results.append({
            "Locale": loc,
            "Number": str(e),
            "Currency": str(e),
            "Percent": str(e),
            "Date": str(e),
            "Time": str(e)
        })

df = pd.DataFrame(results)
st.dataframe(df)

st.markdown("### Notes")
st.markdown("""
- **fr_FR**: Uses space as thousands separator, comma as decimal, € after amount.
- **de_DE**: Uses period as thousands separator, comma as decimal, € before amount.
- **ja_JP**: Uses comma as thousands separator, period as decimal, yen (￥) before amount. 
  Dates can be `yyyy/MM/dd` or `yyyy年M月d日`. Time often uses 24h or 午前/午後.
""")
