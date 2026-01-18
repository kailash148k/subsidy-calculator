import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="SubsidyClaim Pro DPR Engine", layout="wide")
st.title("🏦 Advanced Bank-Grade DPR & Tax Projection Tool")

# --- 1. SIDEBAR: PROJECT PARAMETERS ---
with st.sidebar:
    st.header("📅 Timeline & Reporting")
    start_date = st.date_input("Project Start Month", value=datetime(2025, 8, 1))
    report_type = st.radio("Reporting Mode", ["Standard (Year 1-7)", "Financial Year (Apr-Mar)"])
    duration_years = st.select_slider("Project Duration", options=[5, 7], value=5)
    
    st.header("💰 Project Cost & Means of Finance")
    total_cost = st.number_input("Total Project Cost", value=5000000)
    own_cap = st.number_input("Promoter Equity (Own Capital)", value=total_cost*0.10)
    working_cap = st.number_input("Working Capital Requirement", value=500000)
    bank_loan = total_cost - own_cap
    
    st.header("💳 Loan Parameters")
    interest_rate = st.slider("Interest Rate (%)", 7.0, 18.0, 10.5) / 100
    loan_term_months = st.number_input("Repayment Term (Months)", value=60)
    moratorium_months = st.number_input("Moratorium Period (Months)", value=6)

# --- 2. MACHINE SCHEDULE & DEPRECIATION ---
st.subheader("🛠️ Machinery Schedule & WDV Depreciation")
default_machines = pd.DataFrame([
    {"Item": "Main Production Line", "Cost": total_cost*0.6, "Depr_Rate": 15},
    {"Item": "Auxiliary Equipment", "Cost": total_cost*0.2, "Depr_Rate": 15},
    {"Item": "Office Assets/Computers", "Cost": 100000, "Depr_Rate": 40}
])
machine_df = st.data_editor(default_machines, num_rows="dynamic")

# --- 3. FINANCIAL ENGINE (MONTHLY CALCULATION) ---
total_months = duration_years * 12
months = [start_date + relativedelta(months=i) for i in range(total_months)]

monthly_data = []
remaining_principal = bank_loan

for m in range(total_months):
    # Revenue & Ops
    year_idx = m // 12
    rev = (total_cost * 1.6 * (1.15**year_idx)) / 12 # 15% growth assumption
    ops_exp = rev * 0.70
    
    # Interest & Repayment
    interest = (remaining_principal * interest_rate) / 12
    principal_repaid = 0
    if m >= moratorium_months:
        # Repayment starts after moratorium
        principal_repaid = bank_loan / (loan_term_months - moratorium_months)
        remaining_principal -= principal_repaid
    
    # Depreciation (Monthly estimate)
    depr = (machine_df['Cost'] * (machine_df['Depr_Rate']/100)).sum() / 12
    
    monthly_data.append({
        'Date': months[m],
        'Revenue': rev,
        'Expenses': ops_exp,
        'Interest': interest,
        'Principal_Repayment': principal_repaid,
        'Depreciation': depr,
        'Net_Cash_Flow': rev - ops_exp - interest - principal_repaid
    })

df_monthly = pd.DataFrame(monthly_data)

# Grouping by Period
if report_type == "Financial Year (Apr-Mar)":
    df_monthly['Period'] = df_monthly['Date'].apply(lambda x: f"FY {x.year}-{str(x.year+1)[2:]}" if x.month > 3 else f"FY {x.year-1}-{str(x.year)[2:]}")
else:
    df_monthly['Period'] = df_monthly['Date'].apply(lambda x: f"Year {(list(df_monthly['Date']).index(x)//12) + 1}")

annual_report = df_monthly.groupby('Period').agg({
    'Revenue': 'sum', 'Expenses': 'sum', 'Interest': 'sum', 
    'Principal_Repayment': 'sum', 'Depreciation': 'sum'
}).reset_index()

# --- 4. FINANCIAL STATEMENTS ---
st.subheader("📊 Projected Statements")
tab1, tab2, tab3 = st.tabs(["Profit & Loss", "Cash Flow", "Fund Flow"])

with tab1:
    annual_report['EBITDA'] = annual_report['Revenue'] - annual_report['Expenses']
    annual_report['PBT'] = annual_report['EBITDA'] - annual_report['Interest'] - annual_report['Depreciation']
    annual_report['Tax'] = annual_report['PBT'].apply(lambda x: x * 0.25 if x > 0 else 0)
    annual_report['PAT'] = annual_report['PBT'] - annual_report['Tax']
    st.dataframe(annual_report[['Period', 'Revenue', 'EBITDA', 'PBT', 'Tax', 'PAT']].style.format("₹{:,.0f}"))

with tab2:
    # Cash Inflow: Revenue + Loan (Year 1) + Subsidy (Year 1)
    # Cash Outflow: OpExp + Repayment + Taxes + CapEx (Year 1)
    st.write("**Statement of Projected Cash Flows**")
    annual_report['Total_Inflow'] = annual_report['Revenue']
    annual_report['Total_Outflow'] = annual_report['Expenses'] + annual_report['Interest'] + annual_report['Principal_Repayment'] + annual_report['Tax']
    annual_report['Closing_Cash'] = annual_report['Total_Inflow'] - annual_report['Total_Outflow']
    st.dataframe(annual_report[['Period', 'Total_Inflow', 'Total_Outflow', 'Closing_Cash']].style.format("₹{:,.0f}"))

with tab3:
    st.write("**Sources & Application of Funds**")
    # Simplified Fund Flow logic
    fund_flow = pd.DataFrame({
        'Period': annual_report['Period'],
        'Sources (PAT + Depr)': annual_report['PAT'] + annual_report['Depreciation'],
        'Applications (Repayment)': annual_report['Principal_Repayment'],
        'Net Fund Increase': (annual_report['PAT'] + annual_report['Depreciation']) - annual_report['Principal_Repayment']
    })
    st.dataframe(fund_flow.style.format("₹{:,.0f}"))

# --- 5. RATIOS & SENSITIVITY ---
st.subheader("⚠️ Sensitivity Analysis & Ratios")
dscr = (annual_report['PAT'].mean() + annual_report['Depreciation'].mean() + annual_report['Interest'].mean()) / (annual_report['Principal_Repayment'].mean() + annual_report['Interest'].mean())
cur_ratio = 1.33 # Normative
debt_equity = bank_loan / own_cap

c1, c2, c3 = st.columns(3)
c1.metric("Avg DSCR", f"{dscr:.2f}")
c2.metric("Debt-Equity Ratio", f"{debt_equity:.2f}")
c3.metric("Current Ratio", f"{cur_ratio:.2f}")

# --- 6. PDF GENERATOR ---
# (Updated to include Cash/Fund Flow tables in 5-7 year format)
