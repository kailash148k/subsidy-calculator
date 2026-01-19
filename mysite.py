import streamlit as st
import pandas as pd

# --- 1. DATA INITIALIZATION ---
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

st.set_page_config(page_title="PMEGP & Rajasthan MSME Tool", layout="wide")
st.title("⚖️ Rajasthan MSME Subsidy Comparison Tool")

# --- 2. SIDEBAR INPUTS ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    
    # User-requested PMEGP constraints
    is_new_project = st.radio("Project Status", ["New Project", "Existing Unit"], 
                              help="PMEGP is strictly for New Projects.")
    applicant_entity = st.selectbox("Applicant Type", ["Individual Entrepreneur", "SHG", "Trust", "Co-operative"],
                                   help="PMEGP prefers Individual Entrepreneurs for most categories.")
    has_other_subsidy = st.checkbox("Already have another Govt. Subsidy?")
    is_negative_list = st.checkbox("Business in Meat/Liquor/Tobacco?")

    st.markdown("---")
    state = st.selectbox("State", ["Rajasthan", "Other"])
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    sector = st.selectbox("Sector", ["Manufacturing", "Service", "Food Processing"])
    
    st.subheader("Financials")
    capex = st.number_input("CAPEX (Machinery/Building)", value=2000000)
    wc_req = st.number_input("Working Capital", value=500000)
    total_cost = capex + wc_req
    
    st.subheader("Social Profile")
    age = st.number_input("Age", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])
    edu_8th = st.checkbox("Passed 8th Standard?")
    loc = st.radio("Location", ["Urban", "Rural"])

# --- 3. SUBSIDY CALCULATION ENGINE ---
results = []

# --- PMEGP Logic (Strictly Updated) ---
pmegp_eligible = True
pmegp_reason = ""

if is_new_project != "New Project":
    pmegp_eligible = False
    pmegp_reason = "PMEGP is for New Projects only."
elif applicant_entity != "Individual Entrepreneur":
    pmegp_eligible = False
    pmegp_reason = "Individual Entrepreneurs only (per your settings)."
elif has_other_subsidy:
    pmegp_eligible = False
    pmegp_reason = "Cannot combine with other subsidies."
elif is_negative_list:
    pmegp_eligible = False
    pmegp_reason = "Activity is on the Negative List."

if pmegp_eligible:
    # Education Check
    if (sector == "Manufacturing" and total_cost > 1000000 and not edu_8th) or \
       (sector == "Service" and total_cost > 500000 and not edu_8th):
        st.sidebar.warning("⚠️ PMEGP requires 8th Pass for this project size.")
    else:
        # Rate calculation
        is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
        if loc == "Rural":
            p_rate = 0.35 if is_special else 0.25
        else:
            p_rate = 0.25 if is_special else 0.15
            
        max_cap = 5000000 if sector == "Manufacturing" else 2000000
        pmegp_sub = min(total_cost, max_cap) * p_rate
        results.append({
            "Scheme": "PMEGP (Central Govt)",
            "Capital Subsidy": pmegp_sub,
            "Interest Subsidy": 0,
            "Total Benefit": pmegp_sub
        })

# --- VYUPY Logic (State) ---
if state == "Rajasthan" and 18 <= age <= 45:
    v_sub = min(total_cost * 0.25, 500000)
    # Simplified interest subvention for display
    v_int = (total_cost * 0.08 * 5) 
    results.append({
        "Scheme": "VYUPY (Rajasthan)",
        "Capital Subsidy": v_sub,
        "Interest Subsidy": v_int,
        "Total Benefit": v_sub + v_int
    })

# --- 4. DISPLAY RESULTS ---
st.subheader("📊 Subsidy Comparison")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    st.table(df.style.format({"Capital Subsidy": "₹{:,.0f}", "Interest Subsidy": "₹{:,.0f}", "Total Benefit": "₹{:,.0f}"}))
else:
    st.error(f"No schemes eligible. {pmegp_reason}")

with st.expander("See PMEGP Compliance Rules Applied"):
    st.write(f"- **Project Status:** {is_new_project} (Requirement: New Project)")
    st.write(f"- **Applicant:** {applicant_entity} (Requirement: Individual)")
    st.write(f"- **Other Subsidies:** {'Yes' if has_other_subsidy else 'No'} (Requirement: No)")
