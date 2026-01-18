import streamlit as st
import pandas as pd

# --- DISTRICT DATA ---
rajasthan_odop = {
    "Udaipur": "Ivory/Wood Crafts", "Jaipur": "Blue Pottery", "Jodhpur": "Furniture",
    "Kota": "Coriander", "Ajmer": "Granite", "Bhilwara": "Textiles"
}

st.set_page_config(page_title="MSME Subsidy Search", layout="wide")
st.title("⚖️ MSME Subsidy & Project Engine")

# --- 1. HIGHLIGHTED QUESTIONNAIRE (STRICT SEQUENCE) ---
with st.sidebar:
    st.header("🔍 Eligibility Search")
    
    # A & B: State & District
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 ODOP for {district}: {odop_item}")
    
    # C: Nature of Business
    sector = st.radio("C. Business Type", ["Manufacturing", "Service"])
    
    # D: Project Cost & Loan
    st.subheader("D. Financials")
    capex = st.number_input("Total CAPEX (Machinery/Land)", value=4000000)
    wc_req = st.number_input("Working Capital", value=1000000)
    total_cost = capex + wc_req
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    
    # E: Location
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    # F: Category
    st.subheader("F. Social Profile")
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 2. MULTI-SCHEME ENGINE (INCLUDING AMBEDKAR SCHEME) ---
results = []

# Logic for Ambedkar Scheme (Rajasthan SC/ST Focus)
if state == "Rajasthan" and (social_cat == "SC" or social_cat == "ST"):
    # Ambedkar Scheme offers 25% subsidy on first 25L
    ambedkar_sub = min(total_cost * 0.25, 625000) 
    # 9% Interest subvention for 7 years
    ambedkar_int_save = min(total_cost * 0.75, 2500000) * 0.09 * tenure
    results.append({
        "Scheme": "Dr. B.R. Ambedkar Scheme",
        "Benefit": "25% Subsidy + 9% Interest Save",
        "Value": ambedkar_sub + ambedkar_int_save
    })

# PMEGP Logic (Central)
pm_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
pm_benefit = total_cost * pm_rate
results.append({"Scheme": "PMEGP", "Benefit": f"{pm_rate*100}% Margin Money", "Value": pm_benefit})

# ODOP/RIPS Logic
is_odop = st.checkbox(f"Is your project specifically for {odop_item}?")
if is_odop:
    rips_save = total_cost * 0.75 * 0.08 * tenure # 8% Subvention
    results.append({"Scheme": "RIPS 2024 (ODOP)", "Benefit": "8% Interest Subvention", "Value": rips_save})

# --- 3. DISPLAY RESULTS ---
st.subheader("🏁 Eligible Subsidies for your Profile")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    st.table(df.style.format({"Value": "₹{:,.0f}"}))
    
    # Highlight Best
    st.success(f"🏆 **Best Scheme for you:** {df.iloc[0]['Scheme']}")
else:
    st.warning("No specific subsidies found for this profile. Checking General Schemes...")
