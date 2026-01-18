import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="SubsidyClaim.com | Pro DPR", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""<style> .main { background-color: #f5f7f9; } .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); } </style>""", unsafe_allow_stats_be_allowed=True)

st.title("🏦 Professional MSME Project Report & Subsidy Engine")

# --- 1. SIDEBAR: DATA INPUTS ---
with st.sidebar:
    st.header("📋 Project Details")
    name = st.text_input("Entrepreneur Name", "Kailash")
    biz_name = st.text_input("Business Name", "Kailash Enterprises")
    sector = st.selectbox("Industry Sector", ["Manufacturing", "Service", "Food Processing", "Artisan/Handicraft"])
    state = st.selectbox("State", ["Rajasthan", "Other"])
    
    st.header("📅 Timeline & Reporting")
    start_date = st.date_input("Project Start Date", value=datetime(2025, 8, 1))
    report_format = st.radio("Report Type", ["Financial Year (Apr-Mar)", "Standard (Year 1-7)"])
    duration = st.select_slider("Project Period", options=[5, 7], value=7)
    
    st.header("💰 Means of Finance")
    total_cost = st.number_input("Total Project Cost (INR)", value=5000000)
    own_capital = st.number_input("Promoter Contribution (Own)", value=total_cost*0.10)
    bank_loan = total_cost - own_capital
    int_rate = st.slider("Interest Rate (%)", 7.0, 16.0, 10.5) / 100
    moratorium = st.number_input("Moratorium (Months)", value=6)

# --- 2. SUBSIDY FINALIZATION LOGIC ---
st.subheader("🏁 Eligible Subsidy Comparison")
is_special = st.checkbox("Special Category? (Women / SC / ST / OBC / Rural / Minority)")

results = []
# PMEGP Logic
p_max = 5000000 if sector in ["Manufacturing", "Food Processing"] else 2000000
p_rate = 0.35 if is_special else 0.15 # 15% Urban Gen, 35% Special
results.append({"Scheme": "PMEGP", "Subsidy": min(total_cost, p_max) * p_rate, "Type": "Capital Subsidy"})

# PMFME (Food Processing)
if sector == "Food Processing":
    results.append({"Scheme": "PMFME", "Subsidy": min(total_cost * 0.35, 1000000), "Type": "Food Sector Subsidy"})

# RIPS 2024 (Rajasthan)
if state == "Rajasthan":
    rips_val = bank_loan * (0.08 if is_special else 0.06) * duration
    results.append({"Scheme": "RIPS 2024", "Subsidy": rips_val, "Type": "Interest Subvention"})

df_sub = pd.DataFrame(results).sort_values(by="Subsidy", ascending=False)
st.table(df_sub.style.format({"Subsidy": "₹{:,.0f}"}))
best_scheme = df_sub.iloc[0]

# --- 3. FINANCIAL PROJECTION ENGINE ---
total_months = duration * 12
dates = [start_date + relativedelta(months=i) for i in range(total_months)]
monthly_data = []
rem_principal = bank_loan

for m in range(total_months):
    yr = m // 12
    rev = (total_cost * 1.5 * (1.15**yr)) / 12
    exp = rev * 0.72 # Operating Ratio
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

# Financial Year Grouping
if report_format == "Financial Year (Apr-Mar)":
    df_m['Period'] = df_m['Date'].apply(lambda x: f"FY {x.year}-{str(x.year+1)[2:]}" if x.month > 3 else f"FY {x.year-1}-{str(x.year)[2:]}")
else:
    df_m['Period'] = df_m['Date'].apply(lambda x: f"Year {(list(df_m['Date']).index(x)//12) + 1}")

annual = df_m.groupby('Period').agg({'Revenue':'sum', 'Expenses':'sum', 'Interest':'sum', 'Repayment':'sum', 'Depr':'sum'}).reset_index()
annual['PAT'] = (annual['Revenue'] - annual['Expenses'] - annual['Interest'] - annual['Depr']) * 0.75

# --- 4. RATIOS & SENSITIVITY ---
st.subheader("📊 Financial Health & Sensitivity")
dscr = (annual['PAT'].mean() + annual['Depr'].mean() + annual['Interest'].mean()) / (annual['Repayment'].mean() + annual['Interest'].mean())

c1, c2, c3 = st.columns(3)
c1.metric("Avg DSCR", f"{dscr:.2f}")
c2.metric("EBIT Margin", "28%")
c3.metric("Debt-Equity", f"{bank_loan/own_capital:.2f}")

# Sensitivity Analysis
st.write("**Sensitivity Analysis (Revenue -5%)**")
sens_profit = annual['PAT'].sum() - (annual['Revenue'].sum() * 0.05)
st.warning(f"If Revenue drops by 5%, total cumulative PAT reduces to ₹{sens_profit:,.0f}")

# --- 5. CASH & FUND FLOW TABS ---
t1, t2 = st.tabs(["Cash Flow Statement", "Fund Flow Statement"])
with t1:
    annual['Cash_Inflow'] = annual['Revenue']
    annual['Cash_Outflow'] = annual['Expenses'] + annual['Interest'] + annual['Repayment'] + (annual['PAT']*0.25)
    st.dataframe(annual[['Period', 'Cash_Inflow', 'Cash_Outflow']].style.format("₹{:,.0f}"))
with t2:
    fund_df = pd.DataFrame({'Period': annual['Period'], 'Sources (PAT+Depr)': annual['PAT']+annual['Depr'], 'Applications (Debt)': annual['Repayment']})
    st.dataframe(fund_df.style.format("₹{:,.0f}"))

# --- 6. PDF REPORT GENERATION ---
def generate_dpr_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20); pdf.cell(200, 15, "DETAILED PROJECT REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(200, 10, f"Generated for {biz_name} via SubsidyClaim.com", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, "1. Executive Summary", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, f"This report outlines the establishment of a {sector} unit by {name}. Total investment is ₹{total_cost:,.0f} with a proposed bank loan of ₹{bank_loan:,.0f}. The unit is eligible for {best_scheme['Scheme']} subsidy.")
    
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, "2. Financial Projections", ln=True)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(30, 10, "Period", 1); pdf.cell(40, 10, "Revenue", 1); pdf.cell(40, 10, "Net Profit", 1); pdf.cell(40, 10, "Repayment", 1, ln=True)
    pdf.set_font("Arial", size=9)
    for _, r in annual.iterrows():
        pdf.cell(30, 10, r['Period'], 1); pdf.cell(40, 10, f"{r['Revenue']:,.0f}", 1); pdf.cell(40, 10, f"{r['PAT']:,.0f}", 1); pdf.cell(40, 10, f"{r['Repayment']:,.0f}", 1, ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("🚀 Finalize & Download Full Project Report"):
    st.download_button("Download Now", generate_dpr_
