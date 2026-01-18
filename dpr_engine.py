import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Professional Manufacturing CMA Engine", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL UI ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏭 Manufacturing Project Report & CMA Engine")

# --- SECTION A: PROJECT COST & FUNDING (Module A) ---
with st.expander("🏢 Section A: Project Cost & Funding", expanded=True):
    col1, col2 = st.columns(2)
    
    # 1. CAPEX with IT Depreciation Search
    st.subheader("1. Capex Details")
    it_categories = {
        "Plant & Machinery (General)": 0.15,
        "Computers / Software": 0.40,
        "Building (Residential)": 0.05,
        "Building (Factory/Office)": 0.10,
        "Furniture & Fixtures": 0.10,
        "Motor Cars / Vehicles": 0.15,
        "Pollution Control Equip": 0.40
    }
    selected_cat = st.multiselect("Select Capex Categories", list(it_categories.keys()), default=["Plant & Machinery (General)"])
    
    capex_items = {}
    total_capex = 0
    for cat in selected_cat:
        val = st.number_input(f"Investment in {cat} (₹)", value=1000000, step=50000)
        capex_items[cat] = {"value": val, "rate": it_categories[cat]}
        total_capex += val

    # 2. Working Capital & Own Capital
    st.subheader("2. Working Capital & Margin")
    wc_margin_req = st.number_input("Working Capital Requirement (₹)", value=1000000)
    total_project_cost = total_capex + wc_margin_req
    
    own_cont_pct = st.number_input("Own Contribution (%)", value=25.0, step=0.1)
    own_capital_amt = total_project_cost * (own_cont_pct / 100)
    
    # 3. Bank Loans
    st.subheader("3. Bank Funding")
    c3, c4 = st.columns(2)
    term_loan_amt = c3.number_input("Term Loan Amount (₹)", value=3000000)
    tl_rate = c4.number_input("Term Loan Rate (%)", value=10.5) / 100
    tl_tenure = c3.number_input("Tenure (Months)", value=84)
    tl_moratorium = c4.number_input("Moratorium (Months)", value=6)
    
    cc_limit = c3.number_input("Bank CC Limit (₹)", value=500000)
    cc_rate = c4.number_input("CC Interest Rate (%)", value=11.5) / 100

    # 4. Existing Loan Pre-closure
    st.subheader("4. Existing Running Loan (Pre-closure Logic)")
    ex_bank = st.text_input("Existing Bank Name")
    ex_amt = st.number_input("Existing Loan Amount", value=0)
    ex_tenure = st.number_input("Remaining Tenure (Months)", value=0)
    pre_closure_month = st.number_input("Close this loan at month (1-84)", value=0)

    # --- FUNDING VALIDATION ---
    total_funding = own_capital_amt + term_loan_amt + cc_limit
    diff = total_project_cost - total_funding
    if abs(diff) > 10:
        st.error(f"❌ Funding Mismatch! Cost: ₹{total_project_cost:,.0f} | Funded: ₹{total_funding:,.0f} | Gap: ₹{diff:,.0f}")
        st.stop()
    else:
        st.success("✅ Funding Balanced")

# --- SECTION B: SALES ENGINE ---
with st.expander("📈 Section B: Sales & Production"):
    c1, c2, c3 = st.columns(3)
    uom = c1.selectbox("Unit of Measurement", ["Nos", "KG", "MT", "Units"])
    max_cap = c2.number_input(f"Max Annual Capacity ({uom})", value=50000)
    sale_price = c3.number_input(f"Selling Price per {uom} (₹)", value=500)
    growth_pct = c1.number_input("Annual Sales Growth (%)", value=10.0) / 100
    util_yr1 = c2.number_input("Year 1 Capacity Utilization (%)", value=60.0) / 100

# --- SECTION C & J: EXPENSES & MANPOWER ---
with st.expander("🏭 Section C & J: Expenses & Manpower"):
    st.subheader("Manpower (Staff x Salary)")
    levels = ["Management", "Skilled", "Unskilled", "Admin"]
    total_payroll = 0
    for level in levels:
        col_a, col_b = st.columns(2)
        count = col_a.number_input(f"No. of {level} Staff", value=2, step=1)
        sal = col_b.number_input(f"Monthly Salary for {level} (₹)", value=25000)
        total_payroll += (count * sal * 12)
    
    st.subheader("Direct & Indirect Expenses")
    rm_pct = st.number_input("Raw Material Cost (% of Sales)", value=55.0) / 100
    factory_power = st.number_input("Annual Factory Utilities/Power (₹)", value=200000)
    rent_annual = st.number_input("Annual Rent (Fixed)", value=480000)
    admin_hike = st.number_input("Annual Expense Hike (%)", value=7.0) / 100

# --- SECTION D & G: CYCLE & PRELIMINARY ---
with st.expander("🔄 Section D & G: WC Cycle & Preliminary"):
    c1, c2, c3 = st.columns(3)
    debt_days = c1.number_input("Debtor Days", value=45)
    cred_days = c2.number_input("Creditor Days", value=30)
    stock_days = c3.number_input("Stock Days", value=30)
    
    prelim_exp = st.number_input("Preliminary Expenses (₹)", value=100000)
    st.info("Treatment: Amortized over 5 years as per Sec 35D (Income Tax Act).")

# --- FINAL CALCULATION ENGINE ---
if st.button("🚀 Generate Full 7-Year CMA Report"):
    years = [f"Year {i}" for i in range(1, 8)]
    pl_rows = []
    bs_rows = []

    curr_tl_bal = term_loan_amt
    curr_ex_bal = ex_amt
    total_prelim_amortized = 0

    for i in range(7):
        # 1. Revenue
        util = min(0.95, util_yr1 + (i * 0.05))
        units = max_cap * util
        price = sale_price * (1 + growth_pct)**i
        sales = units * price
        
        # 2. Expenses
        rm_cost = sales * rm_pct
        mfg_exp = (factory_power + (total_payroll * 0.7)) * (1 + admin_hike)**i
        ebitda = sales - rm_cost - mfg_exp - (rent_annual * (1 + admin_hike)**i)
        
        # 3. Depreciation (IT Searchable Logic)
        annual_depr = sum([v['value'] * v['rate'] for v in capex_items.values()])
        
        # 4. Interest & Loan Split (Module I)
        int_tl = curr_tl_bal * tl_rate
        int_cc = cc_limit * 0.75 * cc_rate # Assuming 75% util
        
        # Pre-closure Logic (Module H)
        int_ex = 0
        if ex_amt > 0 and (i*12) < pre_closure_month:
            int_ex = curr_ex_bal * 0.11 # Assumed 11%
        
        pbt = ebitda - annual_depr - (int_tl + int_cc + int_ex) - (prelim_exp/5 if i < 5 else 0)
        tax = max(0, pbt * 0.25)
        pat = pbt - tax
        
        # 5. Loan Repayment
        repay_tl = term_loan_amt / (tl_tenure/12) if i >= (tl_moratorium/12) else 0
        curr_tl_bal -= repay_tl
        
        pl_rows.append({
            "Particulars": years[i], "Gross Sales": sales, "RM Cost": rm_cost, "EBITDA": ebitda,
            "Depreciation": annual_depr, "Interest": int_tl + int_cc, "PBT": pbt, "PAT": pat
        })

        # 6. Balance Sheet Bifurcation (Module I)
        inventory = (rm_cost / 365) * stock_days
        debtors = (sales / 365) * debt_days
        creditors = (rm_cost / 365) * cred_days
        
        cpltd = term_loan_amt / (tl_tenure/12) # Principal due next year
        
        bs_rows.append({
            "Year": years[i],
            "Net Fixed Assets": max(0, total_capex - (annual_depr * (i+1))),
            "Current Assets": inventory + debtors + (pat * 0.1),
            "Net Worth": own_capital_amt + (pat * (i+1)),
            "Long Term Loan (>1yr)": max(0, curr_tl_bal - cpltd),
            "Current Liabilities (incl TL <1yr)": creditors + cpltd + cc_limit
        })

    # --- LOCKED FORMAT DISPLAY ---
    df_pl = pd.DataFrame(pl_rows).set_index("Particulars").T
    df_bs = pd.DataFrame(bs_rows).set_index("Year").T

    t1, t2, t3 = st.tabs(["📊 Profit & Loss Account", "⚖️ Balance Sheet", "📈 Ratio Analysis"])
    with t1: st.dataframe(df_pl.style.format("₹{:,.0f}"))
    with t2: st.dataframe(df_bs.style.format("₹{:,.0f}"))
    with t3:
        ratios = pd.DataFrame({
            "Year": years,
            "Current Ratio": [df_bs.loc["Current Assets", y] / df_bs.loc["Current Liabilities (incl TL <1yr)", y] for y in years],
            "DSCR": [(df_pl.loc["PAT", y] + annual_depr + df_pl.loc["Interest", y]) / (repay_tl + df_pl.loc["Interest", y]) for y in years]
        }).set_index("Year").T
        st.dataframe(ratios.style.format("{:.2f}"))

    # Excel Download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_pl.to_excel(writer, sheet_name='P_and_L')
        df_bs.to_excel(writer, sheet_name='Balance_Sheet')
    st.download_button("📗 Download CMA Excel", output.getvalue(), "Manufacturing_CMA.xlsx")
