import streamlit as st
import pandas as pd

# --- DISTRICT DATA ---
rajasthan_odop = {
    "Udaipur": "Ivory/Wood Crafts", "Jaipur": "Blue Pottery", "Jodhpur": "Furniture",
    "Kota": "Coriander", "Ajmer": "Granite", "Bhilwara": "Textiles"
}

st.set_page_config(page_title="Rajasthan MSME Subsidy Pro", layout="wide")
st.title("⚖️ Rajasthan MSME Subsidy Comparison Tool")

# --- 1. THE QUESTIONNAIRE (STRICT SEQUENCE) ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    
    # A & B: Geography
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 ODOP for {district}: {odop_item}")
    
    # C: Nature of Business
    sector = st.selectbox("C. Business Type", 
                         ["Manufacturing", "Service", "Food Processing", "Traditional Artisan (Vishwakarma)"])
    
    # D: Financials
    st.subheader("D. Financials")
    capex = st.number_input("CAPEX", value=2000000)
    wc_req = st.number_input("Working Capital", value=500000)
    total_cost = capex + wc_req
    loan_amt = total_cost * 0.75 
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    
    # E: Location
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    # F: Social Profile
    st.subheader("F. Social Profile")
    age = st.number_input("Age of Entrepreneur", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 2. THE EXPANDED SCHEME ENGINE ---
results = []

# 1. Vishwakarma Yuva Udyami Protsahan Yojana (VYUPY) - Rajasthan
# Target: 18-40 years, Focus on youth and traditional trades
if state == "Rajasthan" and 18 <= age <= 40:
    vyupy_sub = min(total_cost * 0.25, 500000) # Estimated 25% subsidy
    vyupy_int = loan_amt * 0.08 * tenure # 8% Interest Subvention
    results.append({"Scheme": "VYUPY (Vishwakarma Youth)", "Benefit": "25% Sub + 8% Int Save", "Value": vyupy_sub + vyupy_int})

# 2. Mukhyamantri Yuva Udyami Vikas Yojana (MYUVY) - Rajasthan
# Focus: Composite loans with high interest subvention for educated youth
if state == "Rajasthan" and 18 <= age <= 45:
    myuvy_int = loan_amt * 0.09 * tenure # Up to 9% Subvention for certain categories
    results.append({"Scheme": "Mukhyamantri Yuva Udyami", "Benefit": "9% Interest Subvention", "Value": myuvy_int})

# 3. Dr. B.R. Ambedkar Scheme (SC/ST Rajasthan)
if state == "Rajasthan" and (social_cat == "SC" or social_cat == "ST"):
    amb_sub = min(total_cost * 0.25, 625000)
    amb_int = min(loan_amt, 2500000) * 0.09 * tenure
    results.append({"Scheme": "Dr. B.R. Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": amb_sub + amb_int})

# 4. PMEGP (Central)
pm_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
results.append({"Scheme": "PMEGP", "Benefit": f"{pm_rate*100}% Margin Money", "Value": total_cost * pm_rate})

# 5. RIPS 2024 / ODOP (Rajasthan)
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this unit for {odop_item}?")
    rips_rate = 0.08 if (is_odop or gender == "Female" or social_cat != "General") else 0.06
    results.append({"Scheme": "RIPS 2024 / ODOP", "Benefit": f"{rips_rate*100}% Int. Save", "Value": loan_amt * rips_rate * tenure})

# 6. PMFME (Food Processing)
if sector == "Food Processing":
    pmfme_val = min(total_cost * 0.35, 1000000)
    results.append({"Scheme": "PMFME", "Benefit": "35% Credit Linked Sub", "Value": pmfme_val})

# --- 3. COMPARISON TABLE ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    st.table(df.style.format({"Value": "₹{:,.0f}"}))
    
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found for this profile.")
