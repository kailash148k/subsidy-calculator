import streamlit as st
import pandas as pd
import numpy as np
import io
from fpdf import FPDF
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="CMA & DPR Generator", layout="wide")

st.title("📊 Professional CMA Data & DPR Generator")

# --- SIDEBAR: ALL BANKING PARAMETERS ---
with st.sidebar:
    st.header("1. Project & Loan Setup")
    total_cost = st.number_input("Total Project Cost (INR)", value=5000000)
    own_capital = st.number_input("Own Capital (Margin)", value=total_cost * 0.20)
    
    st.header("2. Term Loan Details")
    loan_amount = total_cost - own_capital
    st.write(f"**Calculated Loan Amount:** ₹{loan_amount:,.0f}")
    
    interest_rate = st.slider("Interest Rate (%)", 7.0, 16.0, 10.5)
    tenure_months = st.number_input("Tenure (Months)", value=84)
    moratorium = st.number_input("Moratorium Period (Months)", value=6)
    
    st.header("3. Working Capital")
    wc_limit = st.number_input("Bank CC / OD Limit", value=500000)
    
    st.header("4. Timeline")
    start_date = st.date_input("Start Month", value=datetime(2025, 4, 1))

# --- FINANCIAL ENGINE ---
years = [f"FY {start_date.year + i}-{str(start_date.year + i + 1)[2:]}" for i in range(7)]

# Projections based on inputs
revenue = [total_cost * 1.5 * (1.12**i) for i in range(7)]
ebitda = [r * 0.20 for r in revenue] # 20% EBITDA margin
interest_cost = [loan_amount * (interest_rate/100)] * 7
depreciation = [total_cost * 0.15 * (0.85**i) for i in range(7)]
pbt = [e - i - d for e, i, d in zip(ebitda, interest_cost, depreciation)]
pat = [p * 0.75 if p > 0 else 0 for p in pbt] # 25% Tax

# Create DataFrame for Display
df_cma = pd.DataFrame({
    "Particulars": ["Revenue", "EBITDA", "Interest", "Depreciation", "PAT"],
    years[0]: [revenue[0], ebitda[0], interest_cost[0], depreciation[0], pat[0]],
    years[1]: [revenue[1], ebitda[1], interest_cost[1], depreciation[1], pat[1]],
    years[2]: [revenue[2], ebitda[2], interest_cost[2], depreciation[2], pat[2]],
    years[3]: [revenue[3], ebitda[3], interest_cost[3], depreciation[3], pat[3]],
    years[4]: [revenue[4], ebitda[4], interest_cost[4], depreciation[4], pat[4]],
    years[5]: [revenue[5], ebitda[5], interest_cost[5], depreciation[5], pat[5]],
    years[6]: [revenue[6], ebitda[6], interest_cost[6], depreciation[6], pat[6]],
})

st.subheader("📈 7-Year CMA Projection Summary")
st.dataframe(df_cma.style.format(precision=0, thousands=","), use_container_width=True)

# --- RATIO ANALYSIS ---
st.subheader("📊 Key Financial Ratios")
dscr = (sum(pat) + sum(depreciation) + sum(interest_cost)) / (loan_amount + sum(interest_cost))
c1, c2, c3 = st.columns(3)
c1.metric("Average DSCR", f"{dscr:.2f}")
c2.metric("Debt-Equity Ratio", f"{loan_amount/own_capital:.2f}")
c3.metric("Interest Coverage", f"{sum(ebitda)/sum(interest_cost):.2f}")

# --- DOWNLOADS ---
def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='CMA_Data')
    return output.getvalue()

st.markdown("---")
col_pdf, col_xls = st.columns(2)

with col_xls:
    st.download_button("📗 Download CMA Data (Excel)", create_excel(df_cma), "CMA_Data.xlsx")

with col_pdf:
    # Basic PDF generation
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "DETAILED PROJECT REPORT", ln=True, align='C')
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    st.download_button("📥 Download Summary Report (PDF)", pdf_bytes, "DPR_Report.pdf")
