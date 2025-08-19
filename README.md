# Quick Locale Tester

A simple Streamlit app to test locale-based formatting for numbers, currencies, percentages, dates, and times.

## Features
- Default locales: **fr_FR**, **de_DE**, **ja_JP**
- Currency code input (try JPY for Yen)
- Quick reference notes for locale differences

## Usage
1. Install requirements:  
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:  
   ```bash
   streamlit run app.py
   ```

3. Select locales and enter test values.

## Notes for Japanese (ja_JP)
- Thousand separator: `,`
- Decimal separator: `.`
- Currency: `￥` or `円` before/after value
- Dates: `yyyy/MM/dd` or `yyyy年M月d日`
- Time: 24h format or with 午前/午後
