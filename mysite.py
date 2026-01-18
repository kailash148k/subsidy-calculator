import streamlit as st
import pandas as pd

# --- DISTRICT DATA ---
rajasthan_odop = {
    "Udaipur": "Ivory/Wood Crafts", "Jaipur": "Blue Pottery", "Jodhpur": "Furniture",
    "Kota": "Coriander", "Ajmer": "Granite", "Bhilwara": "Textiles"
}

st.set_page_config(page_title="MSME Subsidy Comparison", layout="wide")
st.title("⚖️ MSME Subsidy & Project Engine")

# --- 1. HIGHLIGHTED QUESTIONNAIRE (STRICT SEQUENCE) ---
with st.sidebar:
    st.header("🔍 Eligibility Search")
    
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 ODOP for {district}: {odop_item}")
    
    sector = st.radio("C. Business Type", ["Manufacturing", "Service", "Traditional Artisan"])
    
    st.subheader("D. Financials")
    capex = st.number_input("Total CAPEX", value=4000000)
    wc_req = st.number_input("Working Capital", value=1000000)
    total_cost = capex + wc_req
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 2. MULTI-SCHEME ENGINE ---
results = []

# Scheme 1: PMEGP (Universal)
pm_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
results.append({"Scheme": "PMEGP", "Benefit": f"{pm_rate*100}% Margin Money", "Value": total_cost * pm_rate})

# Scheme 2: Dr. B.R. Ambedkar Scheme (SC/ST in Rajasthan)
if state == "Rajasthan" and (social_cat == "SC" or social_cat == "ST"):
    ambedkar_sub = min(total_cost * 0.25, 625000) # 25% capped at 6.25L
    ambedkar_int = min(total_cost * 0.75, 2500000) * 0.09 * tenure # 9% Int. Subvention
    results.append({"Scheme": "Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": ambedkar_sub + ambedkar_int})

# Scheme 3: PM Vishwakarma (Artisans)
if sector == "Traditional Artisan":
    vishwa_toolkit = 15000
    vishwa_int = min(total_cost, 300000) * 0.07 * 5 # 7% saving over 5% fixed rate
    results.append({"Scheme": "PM Vishwakarma", "Benefit": "Toolkit + 5% Fixed Int.", "Value": vishwa_toolkit + vishwa_int})

# Scheme 4: RIPS 2024 (Rajasthan Business)
if state == "Rajasthan":
    rips_rate = 0.08 if (gender == "Female" or social_cat != "General") else 0.06
    results.append({"Scheme": "RIPS 2024", "Benefit": f"{rips_rate*100}% Int. Subvention", "Value": (total_cost * 0.75) * rips_rate * tenure})

# --- 3. DISPLAY COMPARISON ---
st.subheader("🏁 Eligible Subsidies for your Profile")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    st.table(df.style.format({"Value": "₹{:,.0f}"}))
    st.success(f"🏆 Best Choice: {df.iloc[0]['Scheme']}")
