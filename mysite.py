import streamlit as st
import pandas as pd

# --- DISTRICT DATA ---
rajasthan_odop = {
    "Udaipur": "Ivory/Wood Crafts", "Jaipur": "Blue Pottery", "Jodhpur": "Furniture",
    "Kota": "Coriander", "Ajmer": "Granite", "Bhilwara": "Textiles"
}

st.set_page_config(page_title="MSME Subsidy Comparison", layout="wide")
st.title("⚖️ MSME Subsidy Comparison Engine")

# --- 1. HIGHLIGHTED QUESTIONNAIRE (REFINED) ---
with st.sidebar:
    st.header("🔍 Eligibility Search")
    
    # A & B: Location
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 ODOP for {district}: {odop_item}")
    
    # C: Nature of Business (Critical for PMFME & Vishwakarma)
    sector = st.selectbox("C. Business Type", 
                         ["Manufacturing (General)", "Food Processing", "Traditional Artisan (Vishwakarma)", "Service"])
    
    # D: Financials
    st.subheader("D. Financials")
    capex = st.number_input("Total CAPEX", value=4000000)
    wc_req = st.number_input("Working Capital", value=1000000)
    total_cost = capex + wc_req
    loan_amt = total_cost * 0.75 # Standard 75% loan for subvention calculation
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    
    # E: Location
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    # F: Category
    st.subheader("F. Social Profile")
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 2. MULTI-SCHEME ENGINE (THE COMPARATOR) ---
results = []

# 1. PMEGP (Universal)
pm_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
results.append({"Scheme": "PMEGP", "Benefit": f"{pm_rate*100}% Margin Money", "Value": total_cost * pm_rate})

# 2. PMFME (Food Processing Only)
if sector == "Food Processing":
    pmfme_sub = min(total_cost * 0.35, 1000000) # 35% capped at 10L
    results.append({"Scheme": "PMFME", "Benefit": "35% Credit Linked Subsidy", "Value": pmfme_sub})

# 3. PM Vishwakarma (Artisans Only)
if sector == "Traditional Artisan (Vishwakarma)":
    vishwa_toolkit = 15000
    vishwa_int = min(total_cost, 300000) * 0.07 * 5 # 7% interest benefit over 5 years
    results.append({"Scheme": "PM Vishwakarma", "Benefit": "Toolkit + 5% Fixed Int.", "Value": vishwa_toolkit + vishwa_int})

# 4. Dr. B.R. Ambedkar Scheme (SC/ST Rajasthan Only)
if state == "Rajasthan" and (social_cat == "SC" or social_cat == "ST"):
    amb_sub = min(total_cost * 0.25, 625000)
    amb_int = min(loan_amt, 2500000) * 0.09 * tenure # 9% Int Subvention
    results.append({"Scheme": "Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": amb_sub + amb_int})

# 5. RIPS 2024 / ODOP (Rajasthan Interest Subvention)
if state == "Rajasthan":
    # Is it an ODOP unit?
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    rips_rate = 0.08 if (is_odop or gender == "Female" or social_cat != "General") else 0.06
    results.append({"Scheme": "RIPS 2024 / ODOP", "Benefit": f"{rips_rate*100}% Int. Subvention", "Value": loan_amt * rips_rate * tenure})

# --- 3. DISPLAY COMPARISON ---
st.subheader("🏁 Subsidy Comparison Table")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    st.table(df.style.format({"Value": "₹{:,.0f}"}))
    
    best = df.iloc[0]
    st.success(f"🏆 Best Financial Benefit: **{best['Scheme']}** (Estimated ₹{best['Value']:,.0f})")
else:
    st.error("No eligible schemes found for this profile.")
