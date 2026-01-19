import streamlit as st
import pandas as pd

# --- RAJASTHAN ODOP DATA (50 Districts) ---
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

# --- 1. THE QUESTIONNAIRE (REFINED D SECTION) ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    
    sector = st.selectbox("C. Business Type", ["Manufacturing", "Service", "Food Processing", "Traditional Artisan"])
    
    st.subheader("D. Project Cost & Loan Requirements")
    capex = st.number_input("Total CAPEX (Machinery/Building)", value=2000000)
    wc_req = st.number_input("Total Working Capital Requirement", value=500000)
    total_cost = capex + wc_req
    land_building = st.number_input("Land & Building Portion (Included in CAPEX)", value=0)
    
    st.markdown("---")
    # NEW: Specific Loan Inputs
    req_term_loan = st.number_input("Required Term Loan Amount", value=1500000)
    req_wc_loan = st.number_input("Required Working Capital Loan", value=300000)
    actual_total_loan = req_term_loan + req_wc_loan
    
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    age = st.number_input("Age of Entrepreneur", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 2. SCHEME ENGINE (VYUPY UPDATED) ---
results = []

if state == "Rajasthan" and 18 <= age <= 45:
    # Point F: WC Loan cap 30% of Project Cost
    eligible_wc_loan = min(req_wc_loan, total_cost * 0.30)
    
    # Point A & B: Capping total loan for subsidy at 2 Crores (20,000,000)
    # The subsidy is calculated on (Term Loan + Eligible WC Loan) capped at 2 Cr
    vyupy_eligible_loan = min(req_term_loan + eligible_wc_loan, 20000000)
    
    # Tiered Interest Subvention
    if vyupy_eligible_loan <= 10000000:
        v_rate = 0.08  # 8% up to 1Cr
    else:
        v_rate = 0.07  # 7% for 1Cr to 2Cr
        
    # Point C: 1% Addition for Female/SC/ST/PH
    if gender == "Female" or social_cat in ["SC", "ST"]:
        v_rate += 0.01

    # Point D: 5 Year Limit for Interest Subvention
    vyupy_int_benefit = vyupy_eligible_loan * v_rate * 5
    
    # Point H: 25% Capex Subsidy capped at 5L
    vyupy_capex_sub = min(total_cost * 0.25, 500000)
    
    # Point I Check (Land/Building <= 25%)
    if land_building <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY", 
            "Benefit": f"Capex Sub + {v_rate*100:.0f}% Int (Capped at 2Cr, 5 Yrs)",
            "Value": vyupy_int_benefit + vyupy_capex_sub
        })
    else:
        st.sidebar.error("❌ VYUPY Ineligible: Land/Building > 25%")

# --- OTHER SCHEMES ---
# Ambedkar (Uses Requested Loan Amount)
if state == "Rajasthan" and social_cat in ["SC", "ST"]:
    amb_val = min(total_cost * 0.25, 625000) + (min(actual_total_loan, 2500000) * 0.09 * tenure)
    results.append({"Scheme": "Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": amb_val})

# PMEGP
p_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
results.append({"Scheme": "PMEGP", "Benefit": f"{p_rate*100:.0f}% Margin Money", "Value": total_cost * p_rate})

# --- DISPLAY ---
st.subheader("🏁 Comparative Analysis")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    st.table(df.style.format({"Value": "₹{:,.0f}"}))
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found for this profile.")
