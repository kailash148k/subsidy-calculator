import streamlit as st
import pandas as pd

# --- 1. UPDATED RAJASTHAN ODOP DATA (50 Districts from PDF) ---
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

# --- 2. THE QUESTIONNAIRE (STRICT SEQUENCE A-F) ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 Official ODOP for {district}: **{odop_item}**")
    
    sector = st.selectbox("C. Business Type", 
                         ["Manufacturing", "Service", "Food Processing", "Traditional Artisan (Vishwakarma)"])
    
    st.subheader("D. Financials")
    capex = st.number_input("CAPEX (Plant/Machinery/Building)", value=2000000)
    wc_req = st.number_input("Working Capital", value=500000)
    total_cost = capex + wc_req
    # Point I Validation: Land & Building cap
    land_building = st.number_input("Land & Building Portion (Included in CAPEX)", value=0)
    
    loan_amt = total_cost * 0.75 
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    age = st.number_input("Age of Entrepreneur", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 3. THE EXPANDED SCHEME ENGINE ---
results = []

# --- 1. VYUPY Logic (Points A-I) ---
if state == "Rajasthan" and 18 <= age <= 45:
    # Point F: WC cap 30% of project cost
    eligible_wc = min(wc_req, total_cost * 0.30)
    # Point G: 10% Own Contribution
    vyupy_loan = (capex + eligible_wc) * 0.90 
    
    # Point A & B: Tiered Interest Subvention
    if vyupy_loan <= 10000000:
        v_rate = 0.08
    elif vyupy_loan <= 20000000:
        v_rate = 0.07
    else: v_rate = 0.0
    
    # Point C: 1% Addition for Female/SC/ST
    if gender == "Female" or social_cat in ["SC", "ST"]:
        v_rate += 0.01

    # Point D: 5 Year Limit for Interest Subvention
    vyupy_int_benefit = vyupy_loan * v_rate * 5
    # Point H: 25% Capex Subsidy capped at 5L
    vyupy_capex_sub = min(total_cost * 0.25, 500000)
    
    # Point I Check
    if land_building <= (total_cost * 0.25):
        results.append({"Scheme": "VYUPY", "Benefit": f"Capex Sub + {v_rate*100}% Int (5 Yrs)", "Value": vyupy_int_benefit + vyupy_capex_sub})
    else:
        st.sidebar.error("❌ VYUPY Ineligible: Land/Building > 25%")

# --- 2. MYUVY Logic (Tiered Subvention) ---
if state == "Rajasthan" and 18 <= age <= 45:
    if gender == "Male" and social_cat in ["General", "OBC"]:
        m_rate = 0.08 if loan_amt <= 500000 else 0.07
    else:
        m_rate = 0.09 if social_cat in ["SC", "ST"] else 0.08
    
    results.append({"Scheme": "MYUVY", "Benefit": f"{m_rate*100}% Interest Subvention", "Value": min(loan_amt, 2500000) * m_rate * tenure})

# --- 3. Ambedkar Scheme (SC/ST Only) ---
if state == "Rajasthan" and social_cat in ["SC", "ST"]:
    amb_sub = min(total_cost * 0.25, 625000)
    amb_int = min(loan_amt, 2500000) * 0.09 * tenure
    results.append({"Scheme": "Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": amb_sub + amb_int})

# --- 4. PMEGP (Central) ---
pm_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
results.append({"Scheme": "PMEGP", "Benefit": f"{pm_rate*100}% Margin Money", "Value": total_cost * pm_rate})

# --- 5. RIPS 2024 / ODOP ---
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    r_rate = 0.08 if (is_odop or gender == "Female" or social_cat != "General") else 0.06
    results.append({"Scheme": "RIPS 2024", "Benefit": f"{r_rate*100}% Interest Saving", "Value": loan_amt * r_rate * tenure})

# --- 4. COMPARISON TABLE ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    st.table(df.style.format({"Value": "₹{:,.0f}"}))
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found for this profile.")
