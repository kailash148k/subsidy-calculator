import streamlit as st
import pandas as pd

# --- 1. ODOP DATA (41 Districts from PDF) ---
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
} [cite: 13, 18]

st.set_page_config(page_title="Rajasthan MSME Subsidy Pro", layout="wide")
st.title("⚖️ Rajasthan MSME Subsidy Comparison Tool")

# --- 2. THE QUESTIONNAIRE (A-F) ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 Official ODOP: **{odop_item}**") [cite: 13, 18]
    
    sector = st.selectbox("C. Business Type", 
                         ["Manufacturing", "Service", "Food Processing", "Traditional Artisan"])
    
    st.subheader("D. Project Cost & Loan Requirements")
    capex = st.number_input("Total CAPEX (Machinery/Building)", value=2000000)
    wc_req = st.number_input("Total Working Capital Requirement", value=500000)
    total_cost = capex + wc_req
    land_building = st.number_input("Land & Building Portion (Included in CAPEX)", value=0)
    
    st.markdown("---")
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

# --- VYUPY Logic ---
if state == "Rajasthan" and 18 <= age <= 45:
    eligible_wc_loan = min(req_wc_loan, total_cost * 0.30)
    vyupy_eligible_loan = min(req_term_loan + eligible_wc_loan, 20000000)
    
    v_rate = 0.08 if vyupy_eligible_loan <= 10000000 else 0.07
    if gender == "Female" or social_cat in ["SC", "ST"]:
        v_rate += 0.01

    vyupy_int_benefit = vyupy_eligible_loan * v_rate * 5
    vyupy_capex_sub = min(total_cost * 0.25, 500000)
    
    if land_building <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY", 
            "Capital Subsidy": vyupy_capex_sub,
            "Interest Subsidy": vyupy_int_benefit,
            "Total Combined Benefit": vyupy_capex_sub + vyupy_int_benefit
        })
    else:
        st.sidebar.error("❌ VYUPY Ineligible: Land/Building > 25%")

# --- Ambedkar Scheme ---
if state == "Rajasthan" and social_cat in ["SC", "ST"]:
    amb_sub = min(total_cost * 0.25, 625000)
    amb_int = min(actual_total_loan, 2500000) * 0.09 * tenure
    results.append({
        "Scheme": "Ambedkar Scheme", 
        "Capital Subsidy": amb_sub,
        "Interest Subsidy": amb_int,
        "Total Combined Benefit": amb_sub + amb_int
    })

# --- PMEGP ---
p_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
pmegp_sub = total_cost * p_rate
results.append({
    "Scheme": "PMEGP", 
    "Capital Subsidy": pmegp_sub,
    "Interest Subsidy": 0,
    "Total Combined Benefit": pmegp_sub
})

# --- RIPS 2024 ---
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    r_rate = 0.08 if (is_odop or gender == "Female" or social_cat != "General") else 0.06
    rips_int = actual_total_loan * r_rate * tenure
    results.append({
        "Scheme": "RIPS 2024", 
        "Capital Subsidy": 0,
        "Interest Subsidy": rips_int,
        "Total Combined Benefit": rips_int
    })

# --- 4. COMPARISON TABLE ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Combined Benefit", ascending=False)
    
    # Currency formatting for all numeric columns
    st.table(df.style.format({
        "Capital Subsidy": "₹{:,.0f}",
        "Interest Subsidy": "₹{:,.0f}",
        "Total Combined Benefit": "₹{:,.0f}"
    }))
    
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found for this profile.")
