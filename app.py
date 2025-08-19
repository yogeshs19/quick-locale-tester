
import streamlit as st
from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_decimal, format_currency, format_percent
from datetime import datetime, date
import pandas as pd
import math

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
    st.info("**French (fr_FR)**: dd/MM/yyyy; 24h time; space as thousands; comma as decimal; € after amount with a space (e.g., 1 234,56 €).")
elif locale_choice == "de_DE":
    st.info("**German (de_DE)**: d.M.yyyy; 24h time; period as thousands; comma as decimal; € after amount with a space (e.g., 1.234,56 €).")
else:
    st.info("**Japanese (ja_JP)**: yyyy/MM/dd or yyyy年M月d日; 24h time or 午前/午後; thousands ',' and decimal '.'; Yen shown as ￥ or 円 (auto‑set JPY here).")

# ---------------- Text Expansion Estimator ----------------
st.markdown('---')
st.header("🪄 Text Expansion Estimator (EN → FR / DE / JA)")

st.caption(
    "Paste English UI text and estimate length change after translation. "
    "Defaults use commonly cited ranges: FR +15–25%, DE +10–35%, JA −60–−30% (Japanese usually contracts). "
    "Adjust the sliders for your content type."
)

src_text = st.text_area("English source text", placeholder='Enter your UI string here (e.g., "Manage subscriptions")', height=100)
src_len = len(src_text)
st.write(f"**English length:** {src_len} characters")

# Default ranges (min%, max%). Support negative % for contraction.
colA, colB, colC = st.columns(3)
with colA:
    fr_min = st.slider("French min %", -60, 80, 15)
    fr_max = st.slider("French max %", -60, 80, 25)
with colB:
    de_min = st.slider("German min %", -60, 100, 10)
    de_max = st.slider("German max %", -60, 100, 35)
with colC:
    ja_min = st.slider("Japanese min %", -80, 80, -60)
    ja_max = st.slider("Japanese max %", -80, 80, -30)

# Ensure min <= max for each pair
def ordered(a, b):
    return (a, b) if a <= b else (b, a)

fr_min, fr_max = ordered(fr_min, fr_max)
de_min, de_max = ordered(de_min, de_max)
ja_min, ja_max = ordered(ja_min, ja_max)

def apply_change(n: int, pct: float) -> int:
    # Return the rounded character length after applying +/- pct change.
    return int(math.ceil(n * (1 + pct/100.0))) if n > 0 else 0

def bounds(n: int, pmin: int, pmax: int):
    return apply_change(n, pmin), apply_change(n, pmax)

fr_low, fr_high = bounds(src_len, fr_min, fr_max)
de_low, de_high = bounds(src_len, de_min, de_max)
ja_low, ja_high = bounds(src_len, ja_min, ja_max)

data = [
    {"Target": "French (fr_FR)", "Min %": f"{fr_min}%", "Max %": f"{fr_max}%", "Est. min chars": fr_low, "Est. max chars": fr_high},
    {"Target": "German (de_DE)", "Min %": f"{de_min}%", "Max %": f"{de_max}%", "Est. min chars": de_low, "Est. max chars": de_high},
    {"Target": "Japanese (ja_JP)", "Min %": f"{ja_min}%", "Max %": f"{ja_max}%", "Est. min chars": ja_low, "Est. max chars": ja_high},
]
st.subheader("Estimated lengths")
st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# Recommended buffer: pick largest estimated length (even if some languages contract)
buffer_pct = st.slider("Recommended extra UI buffer %", 0, 40, 10)
max_needed = max(fr_high, de_high, ja_high)
with_buffer = apply_change(max_needed, buffer_pct) if src_len > 0 else 0
st.write(f"**Suggestion:** size your control to at least **{with_buffer}** characters "
         f"(includes +{buffer_pct}% buffer over the highest estimate).")

st.caption("Notes: Short strings tend to expand more; results vary by domain and phrasing. Use this as a planning aid, not a guarantee.")
