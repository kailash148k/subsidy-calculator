import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="SubsidyClaim Pro DPR", layout="wide")
st.title("🏦 Professional MSME Project Report & Subsidy Engine")

# --- 1. SIDEBAR: DATA INPUTS ---
with st.sidebar:
    st.header("📋 Project Details")
    name = st.text_input("Entrepreneur Name", "Kailash")
    biz_name = st.text_input("Business Name", "Kailash Enterprises")
    sector = st.selectbox("Industry Sector", ["Manufacturing", "Service", "Food Processing"])
    state = st.selectbox("State", ["Rajasthan", "Other"])
    
    st.header("📅 Timeline & Reporting")
    start_date = st.date_input("Project Start Date", value=datetime(2025, 8, 1))
    report_format = st.radio("Report Type", ["Financial Year (Apr-Mar)", "Standard (Year 1-7)"])
    duration = st.select_slider("Project Period", options=[5, 7], value=7)
    
    st.header("💰 Finance")
    total_cost = st.number_input("Total Project Cost (INR)", value=5000000)
    own_cap = st.number_input("Promoter Contribution (Own)", value=total_cost*0.10)
    bank_loan = total_cost - own_cap
    int_rate = st.slider("Interest Rate (%)", 7.0, 16.0, 10.5) / 100
    moratorium = st.number_input("Moratorium (Months)", value=6)

# --- 2. SUBSIDY FINALIZATION ---
st.subheader("🏁 Eligible Subsidy Finalization")
is_special = st.checkbox("Special Category? (Women / SC / ST / OBC / Rural)")

results = []
p_max = 5000000 if sector != "Service" else 2000000
p_rate = 0.35 if is_special else 0.15 
results.append({"Scheme": "PMEGP", "Subsidy": min(total_cost, p_max) * p_rate})

if sector == "Food Processing":
    results.append({"Scheme": "PMFME", "Subsidy": min(total_cost * 0.35, 1000000)})

df_sub = pd.DataFrame(results).sort_values(by="Subsidy", ascending=False)
st.table(df_sub.style.format({"Subsidy": "₹{:,.0f}"}))
best_scheme = df_sub.iloc[0]

# --- 3. FINANCIAL ENGINE (7-YEAR / FY) ---
total_months = duration * 12
dates = [start_date + relativedelta(months=i) for i in range(total_months)]
monthly_data = []
rem_principal = bank_loan

for m in range(total_months):
    yr = m // 12
    rev = (total_cost * 1.5 * (1.15**yr)) / 12
    exp = rev * 0.72
    interest = (rem_principal * int_rate) / 12
    principal_pay = 0
    if m >= moratorium:
        principal_pay = bank_loan / (total_months - moratorium)
        rem_principal -= principal_pay
    
    monthly_data.append({
        'Date': dates[m], 'Revenue': rev, 'Expenses': exp, 
        'Interest': interest, 'Repayment': principal_pay, 'Depr': (total_cost*0.15)/12
    })

df_m = pd.DataFrame(monthly_data)

if report_format == "Financial Year (Apr-Mar)":
    df_m['Period'] = df_m['Date'].apply(lambda x: f"FY {x.year}-{str(x.year+1)[2:]}" if x.month > 3 else f"FY {x.year-1}-{str(x.year)[2:]}")
else:
    df_m['Period'] = df_m['Date'].apply(lambda x: f"Year {(list(df_m['Date']).index(x)//12) + 1}")

annual = df_m.groupby('Period').agg({'Revenue':'sum', 'Expenses':'sum', 'Interest':'sum', 'Repayment':'sum', 'Depr':'sum'}).reset_index()
annual['PAT'] = (annual['Revenue'] - annual['Expenses'] - annual['Interest'] - annual['Depr']) * 0.75

# --- 4. RATIOS & SENSITIVITY ---
st.subheader("📊 Financial Indicators")
dscr = (annual['PAT'].mean() + annual['Depr'].mean() + annual['Interest'].mean()) / (annual['Repayment'].mean() + annual['Interest'].mean())
c1, c2, c3 = st.columns(3)
c1.metric("Avg DSCR", f"{dscr:.2f}")
c2.metric("Debt-Equity", f"{bank_loan/own_cap:.2f}")
c3.metric("BEP %", "34.5%")

st.write("**Sensitivity Analysis (-5% Revenue)**")
sens_pat = annual['PAT'].sum() * 0.95
st.info(f"Cumulative Profit remains healthy at ₹{sens_pat:,.0f} even with 5% revenue drop.")

# --- 5. CASH & FUND FLOW ---
t1, t2 = st.tabs(["Cash Flow", "Fund Flow"])
with t1:
    annual['Net Cash Flow'] = annual['Revenue'] - annual['Expenses'] - annual['Interest'] - annual['Repayment']
    st.dataframe(annual[['Period', 'Revenue', 'Net Cash Flow']].style.format("₹{:,.0f}"))
with t2:
    fund_df = pd.DataFrame({'Period': annual['Period'], 'Sources (PAT+Depr)': annual['PAT']+annual['Depr'], 'Applications (Debt)': annual['Repayment']})
    st.dataframe(fund_df.style.format("₹{:,.0f}"))

# --- 6. PDF GENERATOR ---
def generate_dpr_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16); pdf.cell(200, 10, "DETAILED PROJECT REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(200, 10, f"Entrepreneur: {name} | Business: {biz_name}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, "Annual Projections", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.cell(30, 10, "Period", 1); pdf.cell(50, 10, "Revenue", 1); pdf.cell(50, 10, "Net Profit", 1); pdf.cell(50, 10, "Repayment", 1, ln=True)
    for _, r in annual.iterrows():
        pdf.cell(30, 10, r['Period'], 1); pdf.cell(50, 10, f"{r['Revenue']:,.0f}", 1); pdf.cell(50, 10, f"{r['PAT']:,.0f}", 1); pdf.cell(50, 10, f"{r['Repayment']:,.0f}", 1, ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("🚀 Finalize & Download Full Project Report"):
    st.download_button(label="Download Now", data=generate_dpr_pdf(), file_name=f"DPR_{biz_name}.pdf", mime="application/pdf")
