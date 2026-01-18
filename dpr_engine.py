import streamlit as st
import pandas as pd
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Professional CMA, Cash & Fund Flow", layout="wide")
st.title("📊 Professional CMA Data & Flow Statements")

# --- 1. SIDEBAR & INPUTS ---
with st.sidebar:
    st.header("🏢 Capital Structure")
    total_project_cost = st.number_input("Total Project Cost", value=5000000)
    promoter_margin = st.number_input("Promoter's Contribution (Equity)", value=1000000)
    term_loan_amt = total_project_cost - promoter_margin
    
    st.header("💳 Working Capital (WC) Gap")
    cc_limit = st.number_input("Proposed Bank CC Limit", value=500000)
    unsecured_loans = st.number_input("Unsecured Loans (Friends/Family)", value=0)

# --- 2. INPUT TABS ---
t1, t2, t3 = st.tabs(["Sales & Production", "Cash Flow Settings", "Fund Flow Details"])

with t2:
    st.subheader("Cash Flow Questions")
    opening_cash = st.number_input("Initial Cash Balance (INR)", value=100000)
    dividend_drawings = st.number_input("Annual Proprietor Drawings (INR)", value=240000)

with t3:
    st.subheader("Fund Flow Variables")
    st.write("Does the business plan to buy more assets in Year 3 or 5?")
    future_capex = st.number_input("Additional Asset Purchase Estimate", value=0)

# --- 3. THE FINANCIAL ENGINE ---
years = [f"Year {i}" for i in range(1, 8)]
revenue = [total_project_cost * 1.5 * (1.10**i) for i in range(7)]
pat = [r * 0.12 for r in revenue] 
depreciation = [total_project_cost * 0.08] * 7 
repayment = [term_loan_amt / 7] * 7 

# --- 4. CASH FLOW LOGIC ---
cash_flow_data = []
current_cash = opening_cash

for i in range(7):
    inflow = pat[i] + depreciation[i]
    outflow = repayment[i] + (dividend_drawings if i > 0 else 0)
    closing_cash = current_cash + inflow - outflow
    cash_flow_data.append({
        "Period": years[i],
        "Opening Cash": current_cash,
        "Cash Inflow (PAT+Depr)": inflow,
        "Cash Outflow (EMI+Drawings)": outflow,
        "Closing Cash": closing_cash
    })
    current_cash = closing_cash

df_cash = pd.DataFrame(cash_flow_data)

# --- 5. FUND FLOW STATEMENT ---
fund_flow = pd.DataFrame({
    "Particulars": years,
    "Sources (PAT + Depreciation)": [pat[i] + depreciation[i] for i in range(7)],
    "Applications (Term Loan Repayment)": repayment,
    "Net Fund Change": [(pat[i] + depreciation[i]) - repayment[i] for i in range(7)]
})

# --- 6. DISPLAY ---
st.subheader("🌊 Cash Flow Statement")
st.dataframe(df_cash.style.format("₹{:,.0f}"), use_container_width=True)

st.subheader("⚖️ Fund Flow Statement (Sources & Applications)")
st.dataframe(fund_flow.style.format("₹{:,.0f}"), use_container_width=True)

# --- 7. EXCEL EXPORT ---
def to_excel(df1, df2):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, index=False, sheet_name='Cash_Flow')
        df2.to_excel(writer, index=False, sheet_name='Fund_Flow')
    return output.getvalue()

st.download_button(
    label="📗 Download Multi-Sheet CMA Excel",
    data=to_excel(df_cash, fund_flow),
    file_name="CMA_Full_Financials.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
