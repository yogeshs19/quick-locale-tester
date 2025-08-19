
import streamlit as st
from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_decimal, format_currency, format_percent
from datetime import datetime, date

st.set_page_config(page_title="Quick Locale Tester (FR / DE / JA)", page_icon="🌍", layout="centered")
st.title("Quick Locale Tester (FR / DE / JA)")

# ---------------- Inputs ----------------
st.subheader("Enter your values")

col1, col2 = st.columns(2)
with col1:
    number_input = st.number_input("Number", value=1234567.89, step=0.01, format="%.6f")
    percent_input = st.number_input("Percent value (0.1234 = 12.34%)", value=0.1234, step=0.0001, format="%.6f")
with col2:
    date_input = st.date_input("Date", value=date.today())
    time_input = st.time_input("Time", value=datetime.now().time())

currency_amount = st.number_input("Currency amount", value=246.88, step=0.01, format="%.2f")

locale_choice = st.selectbox("Select Locale", ["fr_FR", "de_DE", "ja_JP"], index=0)

# ---- Auto currency mapping & override control ----
locale_to_ccy = {"fr_FR": "EUR", "de_DE": "EUR", "ja_JP": "JPY"}

if "currency_code" not in st.session_state:
    st.session_state.currency_code = locale_to_ccy.get(locale_choice, "EUR")

auto_currency = st.checkbox(
    "Auto‑set currency from locale (EUR for fr_FR/de_DE, JPY for ja_JP)",
    value=True,
    help="Uncheck to manually choose another currency code."
)

if auto_currency:
    # Always align currency to the current locale
    st.session_state.currency_code = locale_to_ccy.get(locale_choice, "EUR")

currency_code = st.text_input(
    "Currency code (e.g., EUR, JPY, USD)",
    key="currency_code",
    disabled=auto_currency
)

# ---------------- Output ----------------
st.subheader(f"Results for {locale_choice}")

dt = datetime.combine(date_input, time_input)

st.write("**Date & time formats:**")
st.write("Short date:", format_date(date_input, format="short", locale=locale_choice))
st.write("Long date:", format_date(date_input, format="long", locale=locale_choice))
st.write("Short time:", format_time(time_input, format="short", locale=locale_choice))
st.write("Medium datetime:", format_datetime(dt, format="medium", locale=locale_choice))

st.write("**Number formats:**")
st.write("Decimal:", format_decimal(number_input, locale=locale_choice))
st.write("Percent:", format_percent(percent_input, locale=locale_choice))

st.write("**Currency formats:**")
st.write(f"{currency_code}:", format_currency(currency_amount, currency_code, locale=locale_choice))

# ---- Style guide notes ----
if locale_choice == "fr_FR":
    st.info("**French (fr_FR)**: dd/MM/yyyy; 24h time; space as thousands; comma as decimal; € after amount with a space (e.g., 1 234,56 €).")
elif locale_choice == "de_DE":
    st.info("**German (de_DE)**: d.M.yyyy; 24h time; period as thousands; comma as decimal; € after amount with a space (e.g., 1.234,56 €).")
else:
    st.info("**Japanese (ja_JP)**: yyyy/MM/dd or yyyy年M月d日; 24h time or 午前/午後; thousands ',' and decimal '.'; Yen shown as ￥ or 円 (try currency JPY).")
