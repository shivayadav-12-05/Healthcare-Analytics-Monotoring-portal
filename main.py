import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import random
import time
import os

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Healthcare Analytics Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# PATH SETUP
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "patients_data.csv")

# ==========================================
# ADMIN CREDENTIALS
# ==========================================
ADMIN_EMAIL = "sindesriya@gmail.com"
ADMIN_PHONE = "8919575730"
OTP_EXPIRY_SECONDS = 30

# ==========================================
# GLOBAL CSS (BLUE THEME + LOGIN UI)
# ==========================================
st.markdown("""
<style>

/* Animated blue background */
@keyframes blueFlow {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.stApp {
    background: linear-gradient(
        270deg,
        #1e3a8a,
        #2563eb,
        #38bdf8
    );
    background-size: 500% 500%;
    animation: blueFlow 20s ease infinite;
}

/* Glass login card */
.login-card {
    background: rgba(255, 255, 255, 0.20);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 30px;
    max-width: 380px;
    margin: 90px auto;
    box-shadow: 0 10px 35px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.35);
}

/* Login title */
.login-title {
    text-align: center;
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
}

/* Subtitle */
.login-subtitle {
    text-align: center;
    font-size: 13px;
    color: #e0f2fe;
    margin-bottom: 20px;
}

/* OTP countdown */
.countdown {
    text-align: center;
    font-size: 13px;
    color: #fee2e2;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INIT
# ==========================================
defaults = {
    "logged_in": False,
    "otp": None,
    "otp_sent": False,
    "otp_time": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.logged_in:

    st.markdown("""
    <div class="login-card">
        <div class="login-title">🏥 Healthcare Admin Login</div>
        <div class="login-subtitle">Secure administrator access</div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Admin Email")
        phone = st.text_input("Admin Phone")
        send_otp = st.form_submit_button("Send OTP")

    if send_otp:
        if email.strip().lower() == ADMIN_EMAIL and phone.strip() == ADMIN_PHONE:
            st.session_state.otp = str(random.randint(100000, 999999))
            st.session_state.otp_time = time.time()
            st.session_state.otp_sent = True
            st.success(f"OTP (Demo): {st.session_state.otp}")
        else:
            st.error("Unauthorized Admin ❌")

    if st.session_state.otp_sent:
        remaining = OTP_EXPIRY_SECONDS - int(time.time() - st.session_state.otp_time)

        if remaining > 0:
            st.markdown(
                f"<div class='countdown'>OTP expires in {remaining} seconds</div>",
                unsafe_allow_html=True
            )

            with st.form("otp_form"):
                otp_input = st.text_input("Enter OTP")
                verify = st.form_submit_button("Verify & Login")

            if verify:
                if otp_input == st.session_state.otp:
                    st.session_state.logged_in = True
                    st.success("Login Successful 🎉")
                    st.rerun()
                else:
                    st.error("Invalid OTP")
        else:
            st.error("OTP expired. Please resend OTP.")
            st.session_state.otp_sent = False

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
# ==========================================
# LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv("patients_data.csv")
    df["AdmissionDate"] = pd.to_datetime(df["AdmissionDate"], errors="coerce")
    df["Month"] = df["AdmissionDate"].dt.strftime("%Y-%m")
    return df

df = load_data()

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("📌 Navigation")
option = st.sidebar.selectbox(
    "Go to",
    [
        "Dashboard",
        "Patient Profile",
        "Add Patient",
        "Department Analysis",
        "Risk Alerts",
        "Monthly Disease Report",
        "Gender Based Disease Analysis",
    ],
)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    for k in defaults:
        st.session_state[k] = defaults[k]
    st.rerun()


# ==========================================
# MAIN TITLE
# ==========================================
st.title("🏥 Healthcare Analytics & Monitoring Portal")
st.caption("Interactive system for hospital data analysis and early risk detection")

# ==========================================
# DASHBOARD
# ==========================================
if option == "Dashboard":
    st.subheader("📊 Hospital Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"👥 Total Patients\n\n{len(df)}"):
            st.dataframe(df, use_container_width=True)

    with col2:
        if st.button(f"🏬 Departments\n\n{df['Department'].nunique()}"):
            st.dataframe(
                df[["Department"]].drop_duplicates().reset_index(drop=True),
                use_container_width=True,
            )

    with col3:
        if st.button(f"🦠 Diseases\n\n{df['Disease'].nunique()}"):
            st.dataframe(
                df[["Disease"]].drop_duplicates().reset_index(drop=True),
                use_container_width=True,
            )

    st.markdown("### 📊 Disease Overview")

    disease_counts = df["Disease"].value_counts()
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(4.5, 3))
        ax.bar(disease_counts.index, disease_counts.values)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        ax.set_title("Disease-wise Patient Count")
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        fig2, ax2 = plt.subplots(figsize=(4, 3))
        ax2.pie(
            disease_counts.values,
            labels=disease_counts.index,
            autopct="%1.0f%%",
            startangle=90,
            textprops={"fontsize": 8},
        )
        ax2.set_title("Disease Distribution")
        st.pyplot(fig2)
        plt.close(fig2)

# ==========================================
# PATIENT PROFILE
# ==========================================
elif option == "Patient Profile":
    pid = st.selectbox("Select Patient ID", df["PatientID"])
    st.dataframe(df[df["PatientID"] == pid], use_container_width=True)

# ==========================================
# ADD PATIENT
# ==========================================
elif option == "Add Patient":
    with st.form("add_patient"):
        pid = st.text_input("Patient ID")
        name = st.text_input("Name")
        age = st.number_input("Age", 0, 120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        department = st.text_input("Department")
        disease = st.text_input("Disease")
        hr = st.number_input("Heart Rate", 0)
        bp_sys = st.number_input("BP Systolic", 0)
        bp_dia = st.number_input("BP Diastolic", 0)
        glucose = st.number_input("Glucose", 0)
        ad_date = st.date_input("Admission Date", date.today())
        submit = st.form_submit_button("Save Patient")

    if submit:
        new_row = pd.DataFrame([{
            "PatientID": pid,
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Department": department,
            "Disease": disease,
            "HeartRate": hr,
            "BP_Systolic": bp_sys,
            "BP_Diastolic": bp_dia,
            "Glucose": glucose,
            "AdmissionDate": ad_date,
            "Month": ad_date.strftime("%Y-%m"),
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv("patients_data.csv", index=False)
        st.cache_data.clear()
        st.success("Patient added successfully")
        st.rerun()

# ==========================================
# DEPARTMENT ANALYSIS
# ==========================================
elif option == "Department Analysis":
    for dept, count in df["Department"].value_counts().items():
        if st.button(f"{dept} → {count}"):
            st.dataframe(df[df["Department"] == dept], use_container_width=True)

# ==========================================
# RISK ALERTS
# ==========================================
elif option == "Risk Alerts":
    st.subheader("🚨 High-Risk Patient Alerts")

    risk_df = df[
        (df["BP_Systolic"] >= 160) |
        (df["Glucose"] >= 200) |
        (df["HeartRate"] >= 120)
    ]

    st.metric("⚠️ Total High-Risk Patients", len(risk_df))

    st.markdown("### 🦠 Disease-wise High-Risk Count")

    risk_counts = risk_df["Disease"].value_counts()

    if risk_counts.empty:
        st.success("No high-risk patients detected")
    else:
        for disease, count in risk_counts.items():
            c1, c2 = st.columns([4, 1])
            c1.write(f"{disease}")
            if c2.button(str(count), key=f"risk_{disease}"):
                st.dataframe(
                    risk_df[risk_df["Disease"] == disease],
                    use_container_width=True
                )

# ==========================================
# MONTHLY DISEASE REPORT
# ==========================================
elif option == "Monthly Disease Report":
    st.subheader("📅 Monthly Disease Report")

    df["Month"] = df["AdmissionDate"].dt.strftime("%Y-%m")
    month = st.selectbox("Select Month", sorted(df["Month"].dropna().unique()))

    month_df = df[df["Month"] == month]
    disease_counts = month_df["Disease"].value_counts()

    for disease, count in disease_counts.items():
        if st.button(f"{disease} → {count} cases"):
            st.dataframe(
                month_df[month_df["Disease"] == disease],
                use_container_width=True
            )

# ==========================================
# GENDER BASED DISEASE ANALYSIS
# ==========================================
elif option == "Gender Based Disease Analysis":
    st.subheader("🚻 Gender Based Disease Analysis")

    gender = st.selectbox("Select Gender", df["Gender"].unique())
    gdf = df[df["Gender"] == gender]

    disease_counts = gdf["Disease"].value_counts()

    for disease, count in disease_counts.items():
        if st.button(f"{disease} → {count} patients"):
            st.dataframe(
                gdf[gdf["Disease"] == disease],
                use_container_width=True
            )