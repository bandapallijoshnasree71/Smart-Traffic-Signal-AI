import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO # type: ignore
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import random
from twilio.rest import Client
import folium
from streamlit_folium import st_folium

# ================= CONFIGURATION =================
SENDER_EMAIL = "bandapallijoshnasree130@gmail.com"  
SENDER_PASSWORD = "zhqyshlpdffpqxkn"  
RECIPIENT_EMAIL = "bandapallijoshnasree130@gmail.com"

TWILIO_ACCOUNT_SID = "AC0c52143566c67e6fac41e42b0aac7ea5"
TWILIO_AUTH_TOKEN = "0b0e163132b7904a2a94fcd84989ece7"
TWILIO_PHONE_NUMBER = "+12202720124"
YOUR_PHONE_NUMBER = "+917981897435"

ADMIN_PASSWORD = "admin123"

HYD_LOCATIONS = {
    "Accident": {"coords": [17.4483, 78.3915], "name": "Hitech City, Hyderabad", "file": "accident1.mp4"},
    "Fire1":    {"coords": [17.4400, 78.3489], "name": "Gachibowli, Hyderabad", "file": "fire1.mp4"}, 
    "Fire2":    {"coords": [17.4375, 78.4482], "name": "Ameerpet, Hyderabad", "file": "fire2.mp4"},
    "Flood":    {"coords": [17.4239, 78.4519], "name": "Panjagutta, Hyderabad", "file": "flood1.mp4"},
    "Traffic1": {"coords": [17.3850, 78.4867], "name": "Koti, Hyderabad", "file": "traffic1.mp4"},
    "Traffic2": {"coords": [17.4837, 78.3883], "name": "Miyapur, Hyderabad", "file": "traffic2.mp4"}
}

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Hyd Traffic AI Controller", layout="wide", page_icon="🚦")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'captcha_num1' not in st.session_state: st.session_state['captcha_num1'] = random.randint(10, 50)
if 'captcha_num2' not in st.session_state: st.session_state['captcha_num2'] = random.randint(10, 50)

if 'incident_timers' not in st.session_state:
    st.session_state['incident_timers'] = {key: None for key in HYD_LOCATIONS.keys()}
if 'sent_status' not in st.session_state:
    st.session_state['sent_status'] = {key: False for key in HYD_LOCATIONS.keys()}

# ================= BACKEND FUNCTIONS =================
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')

def send_alert(incident_type, image_frame, is_jam=False):
    filename = f"hyd_auto_{incident_type}.jpg"
    cv2.imwrite(filename, image_frame)
    location_name = HYD_LOCATIONS[incident_type]["name"]
    alert_subject = "TRAFFIC JAM ALERT" if is_jam else f"{incident_type.upper()} ALERT"

    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"🚨 HYD AI: {alert_subject} AT {location_name}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        body = f"HYDERABAD COMMAND CENTER: EMERGENCY RESPONSE\n\nIncident: {alert_subject}\nLocation: {location_name}\nTime: {datetime.now()}\n\nAI Captured Evidence Attached."
        msg.attach(MIMEText(body, 'plain'))
        with open(filename, 'rb') as f:
            msg.attach(MIMEImage(f.read(), name=filename))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    except Exception as e:
        print(f"Email Error: {e}")
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=f"🚨 HYD AI: {alert_subject} at {location_name}! Dispatched in 5s.", from_=TWILIO_PHONE_NUMBER, to=YOUR_PHONE_NUMBER)
    except Exception as e:
        print(f"SMS Error: {e}")
    
    if os.path.exists(filename): os.remove(filename)

# ================= LOGIN PAGE =================
def login_page():
    st.markdown("""
        <style>
            .stApp {
                background: radial-gradient(circle at center, #0a192f 0%, #020c1b 100%);
                overflow: hidden;
            }

            /* Radar Sweep Layer */
            .stApp::before {
                content: '';
                position: absolute;
                top: 50%; left: 70%;
                width: 150vmax; height: 150vmax;
                background: conic-gradient(from 0deg, transparent 0%, rgba(0, 255, 170, 0.1) 50%, transparent 100%);
                animation: radar-sweep 10s linear infinite;
                z-index: 0;
                transform: translate(-50%, -50%);
                pointer-events: none; /* Fixed: Allows clicks to pass through */
            }

            /* Grid Layer */
            .stApp::after {
                content: '';
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background-image: 
                    linear-gradient(rgba(0, 255, 170, 0.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 255, 170, 0.05) 1px, transparent 1px);
                background-size: 50px 50px;
                z-index: 0;
                pointer-events: none; /* Fixed: Allows clicks to pass through */
            }

            @keyframes radar-sweep {
                from { transform: translate(-50%, -50%) rotate(0deg); }
                to { transform: translate(-50%, -50%) rotate(360deg); }
            }

            .login-card {
                background: rgba(10, 25, 47, 0.9);
                backdrop-filter: blur(15px);
                border: 2px solid #00ffaa;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                box-shadow: 0 0 30px rgba(0, 255, 170, 0.3);
                position: relative;
                z-index: 10; /* Fixed: Bring to front */
            }

            h1 { color: #00ffaa !important; font-family: 'Courier New', monospace; }
            .captcha-box {
                background: rgba(0, 255, 170, 0.1);
                border-left: 5px solid #00ffaa;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                color: #00ffaa;
                font-family: 'Courier New', monospace;
                text-align: left;
            }
        </style>
    """, unsafe_allow_html=True)

    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        # Changed text from "HYD TRAFFIC AI" to "HYDERABAD TRAFFIC AI CONTROLLER"
        st.markdown('<div class="login-card"><h1>HYDERABAD TRAFFIC AI CONTROLLER</h1><p style="color:#8892b0;">COMMAND CENTER ACCESS</p>', unsafe_allow_html=True)
        password = st.text_input("ACCESS KEY", type="password")
        
        n1, n2 = st.session_state['captcha_num1'], st.session_state['captcha_num2']
        st.markdown(f'<div class="captcha-box">> SCANNING...<br>> INTEGRITY CHECK: {n1} + {n2} = ?</div>', unsafe_allow_html=True)
        
        captcha_ans = st.text_input("VERIFICATION CODE")
        
        if st.button("🚀 INITIALIZE SYSTEM", use_container_width=True):
            if password == ADMIN_PASSWORD and captcha_ans == str(n1 + n2):
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("🚨 ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= DASHBOARD PAGE =================
def dashboard_page():
    st.markdown("<style>.stApp { background-color: #0E1117; color: white; }</style>", unsafe_allow_html=True)
    with st.sidebar:
        if st.button("🚪 LOGOUT SECURELY", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()
        st.markdown("---")
        st.title("📍 HYD SURVEILLANCE")
        m = folium.Map(location=[17.4200, 78.4500], zoom_start=11, tiles="CartoDB dark_matter")
        for loc, data in HYD_LOCATIONS.items():
            folium.Marker(data["coords"], popup=data['name'], icon=folium.Icon(color="red")).add_to(m)
        st_folium(m, height=250, width=250)

    st.title("🚀 Live Hyderabad Traffic Command Center")
    
    r1_cols = st.columns(3)
    r2_cols = st.columns(3)
    all_cols = r1_cols + r2_cols
    
    base_path = "traffic_videos"
    feeds = {}
    
    for i, (key, info) in enumerate(HYD_LOCATIONS.items()):
        path = os.path.join(base_path, info['file'])
        if os.path.exists(path):
            with all_cols[i]:
                st.caption(f"Feed: {info['file']}")
                feeds[key] = {"cap": cv2.VideoCapture(path), "ph": st.empty(), "mt": st.empty()}

    model = load_model()
    while True:
        for name, data in feeds.items():
            ret, frame = data["cap"].read()
            if not ret: 
                data["cap"].set(cv2.CAP_PROP_POS_FRAMES, 0)
                _, frame = data["cap"].read()
            
            frame = cv2.resize(frame, (640, 360))
            res = model(frame, verbose=False, classes=[2,3,5,7])
            data["ph"].image(res[0].plot(), channels="BGR", use_container_width=True)
            cnt = len(res[0].boxes)
            
            is_jam = "Traffic" in name and cnt > 15
            is_incident = any(x in name for x in ["Accident", "Fire", "Flood"]) and cnt > 0
            
            if (is_incident or is_jam) and not st.session_state['sent_status'][name]:
                if st.session_state['incident_timers'][name] is None:
                    st.session_state['incident_timers'][name] = time.time()
                
                elapsed = time.time() - st.session_state['incident_timers'][name]
                if elapsed >= 5:
                    send_alert(name, frame, is_jam=is_jam)
                    st.session_state['sent_status'][name] = True
                else:
                    label = "JAM" if is_jam else name.upper()
                    data["mt"].warning(f"🚨 {label} DETECTED! Alert in {5-int(elapsed)}s...")
            else:
                data["mt"].info(f"{HYD_LOCATIONS[name]['name']}: {cnt} Vehicles")
        time.sleep(0.01)

if st.session_state['logged_in']: dashboard_page()
else: login_page()