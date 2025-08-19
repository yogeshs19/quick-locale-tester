
import streamlit as st
from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_decimal, format_currency, format_percent
from datetime import datetime, date
import pandas as pd
import math
import re
import unicodedata

st.set_page_config(page_title="Quick Locale Tester (FR / DE / JA)", page_icon="🌍", layout="centered")
st.title("Quick Locale Tester (FR / DE / JA)")

# ---------- Helpers ----------
def _normalize_key(text: str) -> str:
    return re.sub(r"[^0-9a-zA-Z_-]+", "_", text)

def copy_field(label: str, value: str, locale_choice: str):
    key = f"copy_{_normalize_key(label)}_{locale_choice}"
    st.text_input(label, value, key=key, disabled=True)

def calc_bounds(n: int, pmin: int, pmax: int):
    if n == 0:
        return 0, 0
    low = math.ceil(n * (1 + pmin/100))
    high = math.ceil(n * (1 + pmax/100))
    return (low, high) if low <= high else (high, low)

# ---------- Inputs (shared) ----------
with st.container():
    st.subheader("Enter your values")
    col1, col2 = st.columns(2)
    with col1:
        number_input = st.number_input("Number", value=1234567.89, step=0.01, format="%.6f")
        percent_input = st.number_input("Percent value (0.1234 = 12.34%)", value=0.1234, step=0.0001, format="%.6f")
    with col2:
        date_input = st.date_input("Date", value=date.today())
        time_input = st.time_input("Time", value=datetime.now().time())

    currency_amount = st.number_input("Currency amount", value=246.88, step=0.01, format="%.2f")

    locale_choice = st.selectbox("Select Locale", ["fr_FR", "de_DE", "ja_JP"], index=0, key="locale_choice")
    locale_to_ccy = {"fr_FR": "EUR", "de_DE": "EUR", "ja_JP": "JPY"}

    if "currency_code" not in st.session_state:
        st.session_state.currency_code = locale_to_ccy.get(locale_choice, "EUR")

    auto_currency = st.checkbox(
        "Auto-set currency from locale (EUR for fr_FR/de_DE, JPY for ja_JP)",
        value=True,
        help="Uncheck to manually choose another currency code."
    )
    if auto_currency:
        st.session_state.currency_code = locale_to_ccy.get(locale_choice, "EUR")

    currency_code = st.text_input("Currency code (e.g., EUR, JPY, USD)", key="currency_code", disabled=auto_currency)

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["Format tester", "Text expansion (EN → FR/DE/JA)", "Pseudo translation"])

with tab1:
    st.subheader(f"Results for {locale_choice}")
    dt = datetime.combine(date_input, time_input)

    st.markdown("**Date & time formats**")
    copy_field("Short date", format_date(date_input, format="short", locale=locale_choice), locale_choice)
    copy_field("Long date",  format_date(date_input, format="long",  locale=locale_choice), locale_choice)
    copy_field("Short time", format_time(time_input, format="short", locale=locale_choice), locale_choice)
    copy_field("Medium datetime", format_datetime(dt, format="medium", locale=locale_choice), locale_choice)

    st.divider()
    st.markdown("**Number formats**")
    copy_field("Decimal", format_decimal(number_input, locale=locale_choice), locale_choice)
    copy_field("Percent", format_percent(percent_input, locale=locale_choice), locale_choice)

    st.divider()
    st.markdown("**Currency**")
    copy_field(f"{currency_code}", format_currency(currency_amount, currency_code, locale=locale_choice), locale_choice)

    if locale_choice == "fr_FR":
        st.info("**French (fr_FR)** — dd/MM/yyyy; 24h time; space as thousands; comma as decimal; € after amount with a space (e.g., 1 234,56 €).")
    elif locale_choice == "de_DE":
        st.info("**German (de_DE)** — d.M.yyyy; 24h time; period as thousands; comma as decimal; € after amount with a space (e.g., 1.234,56 €).")
    else:
        st.info("**Japanese (ja_JP)** — yyyy/MM/dd or yyyy年M月d日; 24h time or 午前/午後; thousands ',' and decimal '.'; Yen shown as ￥ or 円.")

with tab2:
    st.subheader("Text expansion estimator")
    st.caption(
        "Estimate length change for EN → FR/DE/JA. Defaults reflect common guidance: "
        "FR ≈ +15–25%, DE ≈ +10–35% expansion; JA typically contracts ≈ −10% to −50%."
    )

    src_text = st.text_area(
        "English source text",
        placeholder='Enter your UI string here (e.g., "Manage subscriptions")',
        height=100
    )
    src_len = len(src_text)
    st.write(f"**English length:** {src_len} characters")

    colA, colB, colC = st.columns(3)
    with colA:
        fr_min = st.slider("French min %", -50, 60, 15)
        fr_max = st.slider("French max %", -50, 80, 25)
    with colB:
        de_min = st.slider("German min %", -50, 60, 10)
        de_max = st.slider("German max %", -50, 100, 35)
    with colC:
        ja_min = st.slider("Japanese min %", -80, 60, -10)
        ja_max = st.slider("Japanese max %", -80, 60, -50)

    fr_low, fr_high = calc_bounds(src_len, fr_min, fr_max)
    de_low, de_high = calc_bounds(src_len, de_min, de_max)
    ja_low, ja_high = calc_bounds(src_len, ja_min, ja_max)

    data = [
        {"Target": "French (fr_FR)", "Min %": f"{fr_min}%", "Max %": f"{fr_max}%", "Est. min chars": fr_low, "Est. max chars": fr_high},
        {"Target": "German (de_DE)", "Min %": f"{de_min}%", "Max %": f"{de_max}%", "Est. min chars": de_low, "Est. max chars": de_high},
        {"Target": "Japanese (ja_JP)", "Min %": f"{ja_min}%", "Max %": f"{ja_max}%", "Est. min chars": ja_low, "Est. max chars": ja_high},
    ]
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    buffer_pct = st.slider("Recommended extra UI buffer %", 0, 30, 10, help="Add headroom over worst‑case estimate.")
    max_needed = max(fr_high, de_high, ja_high)
    with_buffer = math.ceil(max_needed * (1 + buffer_pct/100)) if src_len > 0 else 0
    if src_len > 0:
        st.success(f"Suggestion: size your control to at least **{with_buffer}** characters (includes +{buffer_pct}% buffer).")
    else:
        st.info("Enter source text above to get a recommendation.")

    st.caption("Short strings tend to expand more; results vary by domain and phrasing. Use this as planning guidance, not a guarantee.")

# ---------------- Pseudo translation tab ----------------
def latin_diacritics(s: str) -> str:
    repl = {
        "A":"Å","B":"Ɓ","C":"Č","D":"Ď","E":"Ē","F":"Ƒ","G":"Ğ","H":"Ħ","I":"Í","J":"Ĵ","K":"Ķ","L":"Ļ","M":"Ḿ","N":"Ń","O":"Ø","P":"Ṕ","Q":"Ǫ","R":"Ŕ","S":"Š","T":"Ť","U":"Ů","V":"Ṽ","W":"Ŵ","X":"Ẍ","Y":"Ý","Z":"Ž",
        "a":"å","b":"ƀ","c":"č","d":"ď","e":"ē","f":"ƒ","g":"ğ","h":"ħ","i":"í","j":"ĵ","k":"ķ","l":"ļ","m":"ḿ","n":"ń","o":"ø","p":"ṕ","q":"ǫ","r":"ŕ","s":"š","t":"ť","u":"ů","v":"ṽ","w":"ŵ","x":"ẍ","y":"ý","z":"ž"
    }
    return "".join(repl.get(ch, ch) for ch in s)

def to_fullwidth(s: str) -> str:
    out = []
    for ch in s:
        code = ord(ch)
        if ch == " ":
            out.append("\u3000")  # ideographic space
        elif 0x21 <= code <= 0x7E:
            out.append(chr(code + 0xFEE0))
        else:
            out.append(ch)
    return "".join(out)

# protect placeholders and HTML-like tags
PLACEHOLDER_RE = re.compile(r"(\{[^}]+\}|%\w|%\([^)]+\)s|<[^>]+>|&[a-zA-Z]+;|\$\{[^}]+\})")

def pseudo_localize(text: str, target: str, pct: int, wrap: bool, use_fullwidth_ja: bool):
    parts = []
    last = 0
    for m in PLACEHOLDER_RE.finditer(text):
        chunk = text[last:m.start()]
        parts.append(("t", chunk))
        parts.append(("k", m.group(0)))  # keep
        last = m.end()
    parts.append(("t", text[last:]))

    transformed = []
    for kind, chunk in parts:
        if kind == "k":
            transformed.append(chunk)
        else:
            if target in ("fr_FR", "de_DE"):
                transformed.append(latin_diacritics(chunk))
            elif target == "ja_JP":
                transformed.append(to_fullwidth(chunk) if use_fullwidth_ja else chunk)
            else:
                transformed.append(chunk)
    out = "".join(transformed)

    # length padding to simulate expansion (or leave as-is if negative)
    if pct > 0:
        pad_len = math.ceil(len(text) * pct/100)
        pad_char = "・" if target == "ja_JP" else "ˑ"
        out = out + pad_char * pad_len

    if wrap:
        prefix = "⟦"
        suffix = "⟧"
        out = f"{prefix}{out}{suffix}"
    return out

with tab3:
    st.subheader("Pseudo translation")
    st.caption("Generate pseudo-localized strings that preserve placeholders and optionally simulate length changes.")

    pseudo_src = st.text_area(
        "English source text",
        placeholder='Enter your UI string here (e.g., "Manage subscriptions")',
        height=100,
        key="pseudo_src"
    )
    colL, colR = st.columns([2,1])
    with colL:
        pseudo_lang = st.selectbox("Target (simulate)", ["fr_FR", "de_DE", "ja_JP"], index=0, key="pseudo_lang")
        simulate_pct = st.slider("Simulate expansion/contraction % (JA usually 0 to +10 here)", -50, 60, 20 if pseudo_lang!='ja_JP' else 0)
    with colR:
        wrap_markers = st.checkbox("Wrap with ⟦ ⟧ markers", value=True)
        fullwidth_ja = st.checkbox("JA: Use fullwidth characters", value=True, disabled=(pseudo_lang!="ja_JP"))

    if pseudo_src.strip():
        pseudo_out = pseudo_localize(pseudo_src, pseudo_lang, simulate_pct, wrap_markers, fullwidth_ja)
        st.markdown("**Pseudo output**")
        st.text_area("Result", pseudo_out, height=120, key="pseudo_out", disabled=True)
    else:
        st.info("Enter a source string to see the pseudo translation.")
