import streamlit as st
import pandas as pd

# --- 1. FULL RAJASTHAN ODOP DATA ---
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

# --- 2. ELIGIBILITY FILTERS ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"])
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual"])
    has_other_subsidy = st.checkbox("Already availed other Govt. Subsidies?")
    
    st.markdown("---")
    state = st.selectbox("State", ["Rajasthan", "Other"])
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 Official ODOP: **{odop_item}**")
    
    sector = st.selectbox("Sector", ["Manufacturing", "Service", "Food Processing"])
    
    st.subheader("D. Financials")
    capex = st.number_input("Total CAPEX", value=2000000)
    wc_req = st.number_input("Total WC Requirement", value=500000)
    total_cost = capex + wc_req
    land_building = st.number_input("Land & Building Portion", value=0)
    
    req_term_loan = st.number_input("Required Term Loan", value=15000000) # 1.5 Cr
    req_wc_loan = st.number_input("Required WC Loan", value=3000000)
    
    tenure = st.slider("Tenure (Years)", 1, 7, 7)
    loc = st.radio("Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])
    edu_8th = st.checkbox("Passed 8th Standard?")

# --- 3. SCHEME ENGINE ---
results = []

# --- VYUPY Compliance Logic (Corrected Rates) ---
if state == "Rajasthan":
    # WC capping at 30% of project cost
    eligible_wc_loan = min(req_wc_loan, total_cost * 0.30)
    # Total loan capped at 2 Cr
    vyupy_loan_capped = min(req_term_loan + eligible_wc_loan, 20000000)
    
    # --- CORRECTED INTEREST RATE LOGIC ---
    if vyupy_loan_capped <= 10000000:
        v_int_rate = 8  # 8% for loans up to 1 Cr
    else:
        v_int_rate = 7  # Base rate drops to 7% for 1Cr - 2Cr
        
    # Additional 1% for Special Categories (including Rural Male)
    is_vyupy_special = (gender == "Female" or social_cat in ["SC", "ST"] or loc == "Rural")
    if is_vyupy_special and vyupy_loan_capped > 10000000:
        v_int_rate += 1  # Becomes 8% (Not 9%)

    vyupy_int_benefit = vyupy_loan_capped * (v_int_rate / 100) * 5 # First 5 years
    vyupy_grant = min(vyupy_loan_capped * 0.25, 500000) # 25% capped at 5L
    
    if land_building <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY",
            "Capital %": "25% (Grant)",
            "Capital Subsidy": vyupy_grant,
            "Interest %": f"{v_int_rate}%",
            "Interest Subsidy": vyupy_int_benefit,
            "Total Benefit": vyupy_grant + vyupy_int_benefit
        })

# --- PMEGP Logic ---
if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
    is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
    p_rate = (35 if loc == "Rural" else 25) if is_special else (25 if loc == "Rural" else 15)
    
    max_limit = 5000000 if sector == "Manufacturing" else 2000000
    pmegp_sub = min(total_cost, max_limit) * (p_rate / 100)
    
    results.append({
        "Scheme": "PMEGP",
        "Capital %": f"{p_rate}%",
        "Capital Subsidy": pmegp_sub,
        "Interest %": "0%",
        "Interest Subsidy": 0,
        "Total Benefit": pmegp_sub
    })

# --- RIPS 2024 / ODOP ---
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    r_rate = 8 if (is_odop or gender == "Female" or social_cat != "General") else 6
    rips_int = (req_term_loan + req_wc_loan) * (r_rate / 100) * tenure
    
    results.append({
        "Scheme": "RIPS 2024",
        "Capital %": "0%",
        "Capital Subsidy": 0,
        "Interest %": f"{r_rate}%",
        "Interest Subsidy": rips_int,
        "Total Benefit": rips_int
    })

# --- 4. DISPLAY ---
st.subheader("🏁 Comparative Analysis")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    st.table(df.style.format({
        "Capital Subsidy": "₹{:,.0f}",
        "Interest Subsidy": "₹{:,.0f}",
        "Total Benefit": "₹{:,.0f}"
    }))
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found.")
