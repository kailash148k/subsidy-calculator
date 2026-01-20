import streamlit as st
import pandas as pd

st.set_page_config(page_title="PMEGP Official DPR Engine", layout="wide")
st.title("📄 Official PMEGP DPR & Subsidy Engine")

# --- SIDEBAR: OFFICIAL FILTERS ---
with st.sidebar:
    st.header("📋 Application Details")
    agency = st.selectbox("Sponsoring Agency", ["DIC", "KVIC", "KVIB"])
    location = st.radio("Unit Location", ["Rural", "Urban"])
    industry_type = st.radio("Industry Type", ["Manufacturing Unit", "Service Unit"])
    
    st.markdown("---")
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST", "Minority", "Ex-Serviceman"])
    qualification = st.selectbox("Academic Qualification", ["Below 8th Pass", "8th Pass", "10th Pass", "Graduate", "Post Graduate"])

    # Official Minimum Contribution Logic
    is_special = (gender == "Female" or social_cat != "General" or location == "Rural")
    min_cont_pct = 0.05 if is_special else 0.10

# --- MAIN SECTION: PROJECT COST (Official Format) ---
st.subheader("🏗️ Step 1: Project Cost (Assets)")
col1, col2 = st.columns(2)

with col1:
    lb_cost = st.number_input("Workshed / Building (Shed)", value=0)
    pm_cost = st.number_input("Plant & Machinery / Equipment", value=1500000)
    furn_cost = st.number_input("Furniture & Fixtures", value=20000)
    pre_op_cost = st.number_input("Pre-operative Expenses", value=0)
    wc_margin = st.number_input("Working Capital (1 Cycle)", value=100000)
    
    total_project_cost = lb_cost + pm_cost + furn_cost + pre_op_cost + wc_margin
    st.info(f"**Total Project Cost: ₹{total_project_cost:,.0f}**")

# --- MEANS OF FINANCE ---
with col2:
    st.write(f"**Step 2: Means of Finance (Funding)**")
    min_amt = total_project_cost * min_cont_pct
    own_cont = st.number_input(f"Own Contribution (Min {int(min_cont_pct*100)}%)", value=float(min_amt))
    
    if own_cont < min_amt:
        st.error(f"⚠️ Policy requires minimum ₹{min_amt:,.0f} contribution.")
    
    bank_loan = total_project_cost - own_cont
    st.success(f"Bank Loan Amount: ₹{bank_loan:,.0f}")
    
    # Official KVIC Repayment Slab
    tenure = st.slider("Repayment Period (Years)", 3, 7, 7)

# --- OFFICIAL SUBSIDY CALCULATION ---
st.markdown("---")
st.subheader("🏁 Official PMEGP Subsidy Analysis")

# PMEGP Rates
if location == "Rural":
    p_rate = 35 if is_special else 25
else:
    p_rate = 25 if is_special else 15

# Land is excluded from PMEGP cost
pmegp_eligible = total_project_cost - lb_cost
max_limit = 5000000 if industry_type == "Manufacturing Unit" else 2000000
pmegp_subsidy = min(pmegp_eligible, max_limit) * (p_rate / 100)

c1, c2, c3 = st.columns(3)
c1.metric("Subsidy Percentage", f"{p_rate}%")
c2.metric("Margin Money (Subsidy)", f"₹{pmegp_subsidy:,.0f}")
c3.metric("Lock-in Period", "3 Years")

st.info("💡 Note: This Margin Money will be kept in a 3-year TDR (Term Deposit Receipt) in your name at the financing bank branch.")

# --- MANPOWER (Required for DPR) ---
with st.expander("👥 Manpower & Employment Details"):
    skilled = st.number_input("No. of Skilled Workers", value=5)
    unskilled = st.number_input("No. of Unskilled Workers", value=5)
    total_emp = skilled + unskilled
    st.write(f"Total Employment Generated: {total_emp} Persons")
