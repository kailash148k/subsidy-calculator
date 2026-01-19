import streamlit as st
import pandas as pd

# --- UPDATED DATA FROM PDF: RAJASTHAN ODOP (50 Districts) ---
rajasthan_odop = {
    "Ajmer": "Granite and Marble Products", "Alwar": "Automobiles Parts", "Balotra": "Textile Products",
    "Banswara": "Marble Products", "Baran": "Garlic Products", "Barmer": "Kasheedakari",
    "Beawar": "Quartz and Feldspar Powder", "Bharatpur": "Agro Based Product", "Bhilwara": "Textile Products",
    "Bikaner": "Bikaneri Namkeen", "Bundi": "Sand Stone", "Chittorgarh": "Granite and Marble Products",
    "Churu": "Wood Products", "Dausa": "Stone Products", "Deedwana-Kuchaman": "Marble and Granite Products",
    "Deeg": "Stone Based Products", "Dholpur": "Stone Based Products", "Dungarpur": "Marble Product",
    "Hanumangarh": "Agro Based Product", "Jaipur": "Gems & Jewellery", "Jaisalmer": "Yellow Stone Products",
    "Jalore": "Granite Products", "Jhalawar": "Kota Stone Products", "Jhunjhunu": "Wooden Handicraft Products",
    "Jodhpur": "Wooden Furniture Products", "Karauli": "Sandstone Products", "Khairthal-Tijara": "Automobiles Parts",
    "Kota": "Kota Doria", "Kotputli-Behror": "Automobiles Parts", "Nagaur": "Pan Methi and Spices Processing",
    "Pali": "Textile Products", "Phalodi": "Sonamukhi Products", "Pratapgarh": "Thewa Jewellery",
    "Rajsamand": "Granite and Marble Products", "Salumber": "Quartz", "Sawai Madhopur": "Marble Products",
    "Sikar": "Wooden Furniture Products", "Sirohi": "Marble Products", "Sri Ganganagar": "Mustard Oil",
    "Tonk": "Slate Stone Products", "Udaipur": "Marble and Granite Products"
}

st.set_page_config(page_title="Rajasthan MSME Subsidy Pro", layout="wide")
st.title("⚖️ Rajasthan MSME Subsidy Comparison Tool")

# --- 1. THE QUESTIONNAIRE (STRICT SEQUENCE) ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 Official ODOP for {district}: **{odop_item}**")
    
    sector = st.selectbox("C. Business Type", 
                         ["Manufacturing", "Service", "Food Processing", "Traditional Artisan (Vishwakarma)"])
    
    st.subheader("D. Financials")
    capex = st.number_input("CAPEX (Plant/Machinery)", value=2000000)
    wc_req = st.number_input("Working Capital", value=500000)
    total_cost = capex + wc_req
    loan_amt = total_cost * 0.75 
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    age = st.number_input("Age of Entrepreneur", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 2. THE EXPANDED SCHEME ENGINE ---
results = []

# 1. VYUPY (Vishwakarma Yuva Udyami Protsahan Yojana) 
# Max Loan Capping: 5 Lakh
if state == "Rajasthan" and 18 <= age <= 40:
    vyupy_eligible_cost = min(total_cost, 500000)
    vyupy_sub = vyupy_eligible_cost * 0.25 
    vyupy_int = (vyupy_eligible_cost * 0.75) * 0.08 * tenure 
    results.append({"Scheme": "VYUPY", "Benefit": "25% Sub (Max 5L Project) + 8% Int", "Value": vyupy_sub + vyupy_int})

# 2. Mukhyamantri Yuva Udyami Vikas Yojana (MYUVY)
# Max Loan Capping: 25 Lakh
if state == "Rajasthan" and 18 <= age <= 45:
    myuvy_eligible_loan = min(loan_amt, 2500000)
    myuvy_int = myuvy_eligible_loan * 0.09 * tenure 
    results.append({"Scheme": "MYUVY", "Benefit": "9% Interest Subvention (Max 25L Loan)", "Value": myuvy_int})

# 3. Dr. B.R. Ambedkar Scheme (SC/ST Rajasthan)
if state == "Rajasthan" and (social_cat == "SC" or social_cat == "ST"):
    amb_sub = min(total_cost * 0.25, 625000)
    amb_int = min(loan_amt, 2500000) * 0.09 * tenure
    results.append({"Scheme": "Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": amb_sub + amb_int})

# 4. PMEGP (Central)
pm_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
results.append({"Scheme": "PMEGP", "Benefit": f"{pm_rate*100}% Margin Money", "Value": total_cost * pm_rate})

# 5. RIPS 2024 / ODOP (Rajasthan)
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
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
