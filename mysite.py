import streamlit as st
import pandas as pd

# --- 1. ENTIRE ODOP DATA (41 Districts from Uploaded PDF) ---
# Source: odop product list of rajasthan 03-07-2025.pdf 
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
                         ["Manufacturing", "Service", "Food Processing", "Traditional Artisan"])
    
    st.subheader("D. Project Cost & Loan Requirements")
    capex = st.number_input("Total CAPEX (Machinery/Building)", value=2000000)
    wc_req = st.number_input("Total Working Capital (WC) Requirement", value=500000)
    total_cost = capex + wc_req
    # Point I: Land/Building must be <= 25% of project cost
    land_building = st.number_input("Land & Building Portion (Included in CAPEX)", value=0)
    
    # Required Loan Inputs
    req_term_loan = st.number_input("Required Term Loan Amount", value=1500000)
    req_wc_loan = st.number_input("Required Working Capital Loan", value=300000)
    actual_total_loan = req_term_loan + req_wc_loan
    
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    age = st.number_input("Age of Entrepreneur", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 3. THE EXPANDED SCHEME ENGINE ---
results = []

# 1. VYUPY (Vishwakarma Yuva Udyami Protsahan Yojana) - Points A to I
if state == "Rajasthan" and 18 <= age <= 45:
    # Point F: WC Loan capped at 30% of total project cost
    eligible_wc_loan = min(req_wc_loan, total_cost * 0.30)
    
    # Point A, B & Max Cap: Subsidy calculated on loan capped at 2 Crores
    vyupy_eligible_loan = min(req_term_loan + eligible_wc_loan, 20000000)
    
    if vyupy_eligible_loan <= 10000000:
        v_rate = 0.08  # 8% up to 1Cr
    else:
        v_rate = 0.07  # 7% for 1Cr to 2Cr
        
    # Point C: 1% Addition for Female/SC/ST
    if gender == "Female" or social_cat in ["SC", "ST"]:
        v_rate += 0.01

    # Point D: Interest subvention for 1st FIVE YEARS only
    vyupy_int_benefit = vyupy_eligible_loan * v_rate * 5
    
    # Point H: Additional Capex Subsidy (25% capped at 5 Lakh)
    vyupy_capex_sub = min(total_cost * 0.25, 500000)
    
    # Point I Check: Land/Building <= 25%
    if land_building <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY", 
            "Benefit": f"Capex Sub + {v_rate*100:.0f}% Int (5 Yrs, 2Cr Cap)", 
            "Value": vyupy_int_benefit + vyupy_capex_sub
        })
    else:
        st.sidebar.error("❌ VYUPY Ineligible: Land/Building > 25%")

# 2. Dr. B.R. Ambedkar Scheme (SC/ST Rajasthan)
if state == "Rajasthan" and (social_cat == "SC" or social_cat == "ST"):
    amb_sub = min(total_cost * 0.25, 625000)
    amb_int = min(actual_total_loan, 2500000) * 0.09 * tenure
    results.append({"Scheme": "Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": amb_sub + amb_int})

# 3. PMEGP (Central)
pm_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
results.append({"Scheme": "PMEGP", "Benefit": f"{pm_rate*100:.0f}% Margin Money", "Value": total_cost * pm_rate})

# 4. RIPS 2024 / ODOP (Rajasthan)
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    r_rate = 0.08 if (is_odop or gender == "Female" or social_cat != "General") else 0.06
    results.append({
        "Scheme": "RIPS 2024", 
        "Benefit": f"{r_rate*100:.0f}% Interest Saving", 
        "Value": actual_total_loan * r_rate * tenure
    })

# 5. PMFME (Food Processing)
if sector == "Food Processing":
    results.append({"Scheme": "PMFME", "Benefit": "35% Credit Linked Sub", "Value": min(total_cost * 0.35, 1000000)})

# --- 4. COMPARISON TABLE ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    # Clean display with no decimals for percentages and currency
    st.table(df.style.format({"Value": "₹{:,.0f}"}))
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found for this profile.")
