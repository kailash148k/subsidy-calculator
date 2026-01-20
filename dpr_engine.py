import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PMEGP Official DPR Generator", layout="wide")

# --- 2. SIDEBAR: APPLICANT DATA (Based on k1.pdf & k2.pdf) ---
with st.sidebar:
    st.header("📋 Applicant Profile")
    beneficiary_name = st.text_input("1.0 Name of Beneficiary", "SMITA SINGH")
    father_husband = st.text_input("3.0 Father's/Spouse's Name", "SOURAV SINGH")
    address = st.text_area("4.0 Unit Address", "F-1 GOKUL BLISS BHUWANA, UDAIPUR")
    district = st.text_input("District", "UDAIPUR")
    
    st.markdown("---")
    industry_type = st.radio("Sector", ["Manufacturing", "Service"])
    activity = st.text_input("5.0 Proposed Activity", "ORTHODONTIC AND IMPLANT CENTRE")
    
    st.markdown("---")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST", "Minority"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    location = st.radio("Unit Location", ["Rural", "Urban"])

# --- 3. FINANCIAL INPUTS (Based on k2.pdf) ---
st.header(f"🏭 Detailed Project Report: {activity}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("3.0 Cost of Project")
    lb_cost = st.number_input("a. Workshed / Building", value=0)
    pm_cost = st.number_input("b. Plant & Machinery (CBCT System etc.)", value=3200000)
    furn_cost = st.number_input("c. Furniture & Fixtures", value=200000)
    pre_op = st.number_input("d. Preliminary & Pre-operative", value=0)
    wc_loan = st.number_input("Working Capital Loan", value=190000)
    total_project_cost = lb_cost + pm_cost + furn_cost + pre_op + wc_loan

with col2:
    st.subheader("7.0 Means of Finance")
    # PMEGP Contribution Logic [cite: 81, 82]
    is_special = (gender == "Female" or social_cat != "General" or location == "Rural")
    own_cont_pct = 0.05 if is_special else 0.10
    own_cont_amt = total_project_cost * own_cont_pct
    
    # KVIC Margin Money (Subsidy) Logic [cite: 88, 89]
    if location == "Rural":
        sub_rate = 35 if is_special else 25
    else:
        sub_rate = 25 if is_special else 15
    
    margin_money = (total_project_cost - lb_cost) * (sub_rate / 100)
    term_loan = total_project_cost - own_cont_amt - wc_loan

    st.info(f"Own Contribution: ₹{own_cont_amt:,.0f}")
    st.info(f"Term Loan: ₹{term_loan:,.0f}")
    st.success(f"Expected Subsidy (Margin Money): ₹{margin_money:,.0f}")

# --- 4. 7-YEAR PROJECTED SUMMARY (Based on k3.pdf, k5.pdf & k6.pdf) ---
st.markdown("---")
st.subheader("📈 Financial Projections (7-Year Summary)")

# Mock Data Generation based on k5.pdf & k6.pdf ratios
years = [f"Year {i}" for i in range(1, 8)]
data = {
    "Sales / Receipts": [6300000, 6825000, 7350000, 7875000, 8400000, 8925000, 9450000],
    "Net Profit": [1168650, 1435548, 1692321, 1940407, 2181024, 2415203, 2643815],
    "Depreciation": [480000, 408000, 346800, 294780, 250563, 212979, 181032],
    "Term Loan Installment": [434286] * 7
}
df_projections = pd.DataFrame(data, index=years).T
st.table(df_projections.style.format("₹{:,.0f}"))

# --- 5. RATIO ANALYSIS (Based on k6.pdf) ---
st.subheader("⚖️ Key Financial Ratios")
r_col1, r_col2, r_col3 = st.columns(3)
r_col1.metric("Average DSCR", "3.93") # Based on k5.pdf [cite: 161]
r_col2.metric("Break Even Point (%)", "72.49%") # Based on k1.pdf [cite: 40]
r_col3.metric("Current Ratio (Year 1)", "7.44") # Based on k6.pdf [cite: 174]

# --- 6. GENERATE TOP SHEET (Based on k1.pdf) ---
if st.button("📄 View PMEGP Top Sheet"):
    st.markdown(f"""
    <div style="border:1px solid #ccc; padding:20px; background-color:#f9f9f9; color:black;">
        <h3 style="text-align:center;">PROJECT AT A GLANCE - TOP SHEET</h3>
        <p><b>Beneficiary:</b> {beneficiary_name}</p>
        <p><b>Activity:</b> {activity}</p>
        <p><b>Location:</b> {location} ({district})</p>
        <hr>
        <table style="width:100%">
            <tr><td><b>Total Cost of Project</b></td><td style="text-align:right;">₹{total_project_cost:,.0f}</td></tr>
            <tr><td><b>Own Capital ({int(own_cont_pct*100)}%)</b></td><td style="text-align:right;">₹{own_cont_amt:,.0f}</td></tr>
            <tr><td><b>Term Loan</b></td><td style="text-align:right;">₹{term_loan:,.0f}</td></tr>
            <tr><td><b>KVIC Margin Money</b></td><td style="text-align:right;">₹{margin_money:,.0f}</td></tr>
        </table>
        <br>
        <p style="text-align:right;"><i>Digitally Generated on {beneficiary_name}'s Application</i></p>
    </div>
    """, unsafe_allow_html=True)
