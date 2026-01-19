import streamlit as st
import pandas as pd

# --- 1. RAJASTHAN ODOP DATA (50 Districts) ---
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
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 Official ODOP: **{odop_item}**")
    
    sector = st.selectbox("C. Business Type", ["Manufacturing", "Service", "Food Processing", "Traditional Artisan"])
    
    st.subheader("D. Financials")
    capex = st.number_input("CAPEX (Plant/Machinery/Building)", value=2000000)
    wc_req = st.number_input("Working Capital", value=500000)
    total_cost = capex + wc_req
    land_building = st.number_input("Land & Building Portion (Included in CAPEX)", value=0)
    
    loan_amt = total_cost * 0.75 
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    age = st.number_input("Age of Entrepreneur", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 3. SCHEME ENGINE ---
results = []

# --- VYUPY Logic (Points A-I) ---
if state == "Rajasthan" and 18 <= age <= 45:
    eligible_wc = min(wc_req, total_cost * 0.30) # Point F
    vyupy_loan = (capex + eligible_wc) * 0.90 # Point G
    
    if vyupy_loan <= 10000000:
        v_rate = 0.08 # Point A
    elif vyupy_loan <= 20000000:
        v_rate = 0.07 # Point B
    else: v_rate = 0.0
    
    if gender == "Female" or social_cat in ["SC", "ST"]:
        v_rate += 0.01 # Point C

    vyupy_int_benefit = vyupy_loan * v_rate * 5 # Point D (5 Yrs)
    vyupy_capex_sub = min(total_cost * 0.25, 500000) # Point H
    
    if land_building <= (total_cost * 0.25): # Point I
        results.append({
            "Scheme": "VYUPY", 
            "Benefit": f"Capex Sub + {v_rate*100:.0f}% Int (5 Yrs)", # Fixed Precision Error
            "Value": vyupy_int_benefit + vyupy_capex_sub
        })
    else:
        st.sidebar.error("❌ VYUPY Ineligible: Land/Building > 25%")

# --- Ambedkar Scheme ---
if state == "Rajasthan" and social_cat in ["SC", "ST"]:
    amb_sub = min(total_cost * 0.25, 625000)
    amb_int = min(loan_amt, 2500000) * 0.09 * tenure
    results.append({"Scheme": "Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": amb_sub + amb_int})

# --- PMEGP ---
p_rate = 0.35 if (loc == "Rural" or gender == "Female" or social_cat != "General") else 0.15
results.append({"Scheme": "PMEGP", "Benefit": f"{p_rate*100:.0f}% Margin Money", "Value": total_cost * p_rate})

# --- RIPS 2024 ---
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    r_rate = 0.08 if (is_odop or gender == "Female" or social_cat != "General") else 0.06
    results.append({"Scheme": "RIPS 2024", "Benefit": f"{r_rate*100:.0f}% Interest Saving", "Value": loan_amt * r_rate * tenure})

# --- DISPLAY ---
st.subheader("🏁 Comparative Analysis")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    st.table(df.style.format({"Value": "₹{:,.0f}"})) # Formats value with comma and no decimals
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found for this profile.")
