import streamlit as st
import pandas as pd

# --- 1. FULL RAJASTHAN ODOP DATA (41 Districts) ---
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

# --- 2. QUESTIONNAIRE (A-F) ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    
    # Core Compliance Inputs
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"], help="PMEGP is for New Units only.")
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual (SHG/Trust/Co-op)"], help="PMEGP focus: Individual Entrepreneurs.")
    has_other_subsidy = st.checkbox("Have you ever availed other Govt. Subsidies?")
    
    st.markdown("---")
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 Official ODOP: **{odop_item}**")
    
    sector = st.selectbox("C. Business Type", 
                         ["Manufacturing", "Service", "Food Processing", "Traditional Artisan"])
    
    st.subheader("D. Project Cost & Loan Requirements")
    capex = st.number_input("Total CAPEX (Machinery/Building)", value=2000000)
    wc_req = st.number_input("Total Working Capital (WC) Requirement", value=500000)
    total_cost = capex + wc_req
    land_building = st.number_input("Land & Building Portion (Included in CAPEX)", value=0)
    
    st.markdown("---")
    req_term_loan = st.number_input("Required Term Loan Amount", value=1500000)
    req_wc_loan = st.number_input("Required Working Capital (WC) Loan", value=300000)
    actual_total_loan = req_term_loan + req_wc_loan
    
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    age = st.number_input("Age of Entrepreneur", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])
    edu_8th = st.checkbox("Passed 8th Standard?")

# --- 3. THE EXPANDED SCHEME ENGINE ---
results = []

# --- PMEGP (Central) ---
# Strictly for NEW projects and INDIVIDUAL entrepreneurs
if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
    # Educational check
    edu_eligible = True
    if sector == "Manufacturing" and total_cost > 1000000 and not edu_8th: edu_eligible = False
    if sector == "Service" and total_cost > 500000 and not edu_8th: edu_eligible = False

    if edu_eligible:
        is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
        # Subsidy rates: General (15-25%), Special (25-35%)
        if loc == "Rural":
            p_rate_val = 35 if is_special else 25
        else:
            p_rate_val = 25 if is_special else 15
            
        max_cost = 5000000 if sector == "Manufacturing" else 2000000
        pmegp_sub = min(total_cost, max_cost) * (p_rate_val / 100)
        
        results.append({
            "Scheme": "PMEGP (Central)",
            "Capital %": f"{p_rate_val}%",
            "Capital Subsidy": pmegp_sub,
            "Interest %": "0%",
            "Interest Subsidy": 0,
            "Total Combined Benefit": pmegp_sub
        })

# --- VYUPY Logic (Rajasthan) ---
if state == "Rajasthan" and 18 <= age <= 45:
    v_int_rate = 8
    # 1% Addition for Special Category on loans > 1Cr
    if (gender == "Female" or social_cat in ["SC", "ST"]) and actual_total_loan > 10000000:
        v_int_rate = 9

    vyupy_int_benefit = actual_total_loan * (v_int_rate / 100) * 5
    vyupy_capex_sub = min(actual_total_loan * 0.25, 500000)
    
    if land_building <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY",
            "Capital %": "25% (Max 5L)",
            "Capital Subsidy": vyupy_capex_sub,
            "Interest %": f"{v_int_rate}%",
            "Interest Subsidy": vyupy_int_benefit,
            "Total Combined Benefit": vyupy_capex_sub + vyupy_int_benefit
        })

# --- RIPS 2024 / ODOP (Rajasthan) ---
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    # Base 6% + 2% Additional for ODOP/Special Category
    r_rate_val = 8 if (is_odop or gender == "Female" or social_cat != "General") else 6
    rips_int = actual_total_loan * (r_rate_val / 100) * tenure
    
    results.append({
        "Scheme": "RIPS 2024",
        "Capital %": "0%",
        "Capital Subsidy": 0,
        "Interest %": f"{r_rate_val}%",
        "Interest Subsidy": rips_int,
        "Total Combined Benefit": rips_int
    })

# --- 4. COMPARISON TABLE ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Combined Benefit", ascending=False)
    
    # Reorder for clarity
    df = df[["Scheme", "Capital %", "Capital Subsidy", "Interest %", "Interest Subsidy", "Total Combined Benefit"]]
    
    st.table(df.style.format({
        "Capital Subsidy": "₹{:,.0f}",
        "Interest Subsidy": "₹{:,.0f}",
        "Total Combined Benefit": "₹{:,.0f}"
    }))
    
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found for this profile. (PMEGP requires New Unit & Individual Applicant)")
