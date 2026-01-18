import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF

st.set_page_config(page_title="CMA Engine + Subsidy Search", layout="wide")

# --- DATA: RAJASTHAN ODOP MAPPING ---
rajasthan_odop = {
    "Ajmer": "Marble & Granite", "Alwar": "Automobile Parts", "Banswara": "Mango",
    "Baran": "Garlic", "Barmer": "Isabgol", "Bharatpur": "Mustard Oil",
    "Bhilwara": "Textiles", "Bikaner": "Moth Bhujia", "Chittorgarh": "Jaggery",
    "Churu": "Wood Products", "Dausa": "Stone Carpets", "Dholpur": "Milk Powder",
    "Dungarpur": "Black Stone", "Hanumangarh": "Guar Gum", "Jaipur": "Blue Pottery",
    "Jaisalmer": "Yellow Stone", "Jalore": "Granite", "Jhalawar": "Orange",
    "Jhunjhunu": "Stone Crafts", "Jodhpur": "Furniture", "Karauli": "Sandstone",
    "Kota": "Coriander", "Nagaur": "Fenugreek", "Pali": "Mehendi",
    "Pratapgarh": "Garlic", "Rajsamand": "Terracotta", "Sawai Madhopur": "Guava",
    "Sikar": "Furniture", "Sirohi": "Psyllium", "Sri Ganganagar": "Kinnow",
    "Tonk": "Namkeen", "Udaipur": "Ivory/Wood Crafts"
}

st.title("🏦 Manufacturing CMA & Subsidy Engine")

# --- SIDEBAR: ALL SECTIONS (A - K) ---
with st.sidebar:
    # --- DISTRICT SEARCH (SECTION K) ---
    st.header("🔍 District & ODOP Search")
    selected_district = st.selectbox("Type/Select Your District", list(rajasthan_odop.keys()))
    odop_product = rajasthan_odop[selected_district]
    st.info(f"📍 ODOP for {selected_district}: **{odop_product}**")
    is_odop_unit = st.checkbox("Is this an ODOP unit?")

    # --- PROJECT COST (SECTION A) ---
    st.header("🏢 Section A: Cost & Funding")
    capex = st.number_input("Total CAPEX (Machinery, etc.)", value=4000000)
    wc_req = st.number_input("Working Capital Requirement", value=1000000)
    total_cost = capex + wc_req
    
    own_pct = st.number_input("Own Contribution (%)", value=10.0)
    own_amt = total_cost * (own_pct / 100)

    # --- LOAN DETAILS ---
    st.header("💳 Section A: Loan Details")
    term_loan_amt = st.number_input("Term Loan Amount", value=3000000)
    tl_rate = st.number_input("Term Loan Rate (%)", value=10.5) / 100
    
    # --- SALES ENGINE (SECTION B) ---
    st.header("📈 Section B: Sales Engine")
    uom = st.selectbox("Unit of Measurement", ["Numbers (Nos)", "KG", "MT"])
    max_cap = st.number_input(f"Max Annual Capacity ({uom})", value=50000)
    price = st.number_input(f"Price per {uom} (₹)", value=200)

# --- SUBSIDY CALCULATION ENGINE ---
results = []

# 1. ODOP Logic
if is_odop_unit:
    # Rajasthan ODOP 2024: 25% subsidy capped at 15L
    odop_benefit = min(total_cost * 0.25, 1500000)
    results.append({"Scheme": "Rajasthan ODOP 2024", "Benefit": "Margin Money", "Value": odop_benefit})

# 2. RIPS 2024 (Rajasthan Interest Subvention)
rips_rate = 0.08 if is_odop_unit else 0.06
rips_saving = term_loan_amt * rips_rate * 7
results.append({"Scheme": "RIPS 2024", "Benefit": "7-Year Interest Saving", "Value": rips_saving})

# --- VALIDATION ---
total_funding = own_amt + term_loan_amt
if is_odop_unit:
    total_funding += results[0]['Value']

# Error Check
diff = total_cost - total_funding
if abs(diff) > 10:
    st.error(f"❌ Funding Mismatch! Cost: ₹{total_cost:,.0f} | Total Funding: ₹{total_funding:,.0f}. Difference: ₹{diff:,.0f}")
else:
    st.success("✅ Funding Balanced with Subsidy")

# --- TABBED RESULTS ---
tab1, tab2 = st.tabs(["💰 Subsidy Comparison", "📊 7-Year Projections"])

with tab1:
    st.subheader("Recommended Benefits")
    df_subsidy = pd.DataFrame(results)
    st.table(df_subsidy.style.format({"Value": "₹{:,.0f}"}))

with tab2:
    st.info("The 7-Year P&L and Balance Sheet (including Section I Loan split) will generate here.")
    # (P&L and BS Logic as defined in our locked blueprint)
