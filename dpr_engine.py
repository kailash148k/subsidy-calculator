import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PMEGP Official DPR Generator", layout="wide")

# --- 2. DATA INPUT (Matches your DataSheet.csv) ---
with st.sidebar:
    st.header("📋 Applicant Profile")
    beneficiary_name = st.text_input("Name of Beneficiary", "SMITA SINGH")
    father_husband = st.text_input("Father's/Spouse's Name", "SUNIL BORANA")
    agency = st.selectbox("Sponsoring Agency", ["DIC", "KVIC", "KVIB"], index=0)
    
    st.markdown("---")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST", "Minority"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    location = st.radio("Unit Location", ["Rural", "Urban"])
    
    # Qualification check for PMEGP eligibility
    qualification = st.selectbox("Qualification", ["Under 8th", "8th Pass", "10th Pass", "Graduate"])
    
    st.markdown("---")
    industry_type = st.radio("Sector", ["Manufacturing", "Service"])
    project_name = st.text_input("Project Name", "TENT HOUSE SERVICES")

# --- 3. FINANCIAL INPUTS (Matches Project_Report.csv) ---
st.header(f"📊 Project Report for {project_name}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("I. Project Cost")
    lb_cost = st.number_input("Land & Building / Shed", value=300000)
    pm_cost = st.number_input("Plant & Machinery / Equipment", value=1500000)
    furn_cost = st.number_input("Furniture & Fixtures", value=20000)
    wc_req = st.number_input("Working Capital (1 Cycle)", value=180000)
    total_cost = lb_cost + pm_cost + furn_cost + wc_req

with col2:
    st.subheader("II. Means of Finance")
    # Official Contribution Logic
    is_special = (gender == "Female" or social_cat != "General" or location == "Rural")
    own_cont_pct = 0.05 if is_special else 0.10
    own_cont_amt = total_cost * own_cont_pct
    
    bank_loan = total_cost - own_cont_amt
    st.metric("Total Project Cost", f"₹{total_cost:,.0f}")
    st.metric(f"Own Contribution ({int(own_cont_pct*100)}%)", f"₹{own_cont_amt:,.0f}")
    st.metric("Bank Loan (Term + WC)", f"₹{bank_loan:,.0f}")

# --- 4. REPORT CONTENT (Matches smita.xls Text Sections) ---
st.markdown("---")
st.subheader("📝 Descriptive Sections for DPR")

col_a, col_b = st.columns(2)
with col_a:
    about_me = st.text_area("About the Beneficiary", 
        f"The Proprietor {beneficiary_name} is a {gender} candidate belonging to {social_cat} category...")
with col_b:
    market_potential = st.text_area("Market Potential", 
        "Keeping in view the present demand in the local area, the project has good potential...")

# --- 5. THE REPORT GENERATOR (THE "PRINT" BUTTON) ---
if st.button("🖨️ Preview Official Project Report (Top Sheet)"):
    st.markdown(f"""
    <div style="border:2px solid black; padding:40px; background-color:white; color:black;">
        <h2 style="text-align:center;">PROJECT AT A GLANCE - TOP SHEET</h2>
        <hr>
        <table style="width:100%; border-collapse: collapse;">
            <tr><td><b>1.0 Name of Beneficiary</b></td><td>{beneficiary_name}</td></tr>
            <tr><td><b>2.0 Constitution</b></td><td>Individual</td></tr>
            <tr><td><b>3.0 Sponsoring Agency</b></td><td>{agency}</td></tr>
            <tr><td><b>4.0 Social Category</b></td><td>{social_cat} ({gender})</td></tr>
            <tr><td><b>5.0 Location</b></td><td>{location}</td></tr>
            <tr><td><br><b>6.0 COST OF PROJECT</b></td><td><b>(Amount in Rs.)</b></td></tr>
            <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;Fixed Capital (Machinery/Shed)</td><td>₹{pm_cost+lb_cost+furn_cost:,.0f}</td></tr>
            <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;Working Capital</td><td>₹{wc_req:,.0f}</td></tr>
            <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;<b>Total Project Cost</b></td><td><b>₹{total_cost:,.0f}</b></td></tr>
            <tr><td><br><b>7.0 MEANS OF FINANCE</b></td><td></td></tr>
            <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;Own Contribution</td><td>₹{own_cont_amt:,.0f}</td></tr>
            <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;Bank Loan Required</td><td>₹{bank_loan:,.0f}</td></tr>
        </table>
        <br>
        <h4>8.0 Market Potential</h4>
        <p>{market_potential}</p>
        <br><br><br>
        <p style="text-align:right;"><b>Signature of the Beneficiary</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Official Subsidy Calculation Box
    if location == "Rural":
        p_rate = 35 if is_special else 25
    else:
        p_rate = 25 if is_special else 15
    
    subsidy = (total_cost - lb_cost) * (p_rate / 100) # Land excluded from subsidy
    st.success(f"Expected Margin Money (Subsidy): ₹{subsidy:,.0f}")
