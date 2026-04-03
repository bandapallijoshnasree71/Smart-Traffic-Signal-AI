# Smart & Secure Real-time Traffic Signal Controller using AI

This project is an AI-powered traffic management system designed to optimize signal timings based on real-time vehicle density. It uses Computer Vision to detect traffic levels and adjust signals to reduce congestion and improve urban security.

## 🚀 Key Features
* **Real-time Vehicle Detection:** Uses YOLOv8 for high-accuracy vehicle counting.
* **Dynamic Signal Control:** Automatically adjusts green light duration based on traffic density.
* **Smart Dashboard:** A Python-based interface to monitor traffic flow and system status.
* **Security Integration:** Capable of identifying emergency vehicles or unusual traffic patterns.

## 🛠️ Tech Stack
* **Language:** Python
* **AI Model:** YOLOv8 (Ultralytics)
* **Libraries:** OpenCV, Pandas, NumPy
* **Frontend:** Streamlit/Tkinter (Dashboard)

## 📁 Project Structure
* `dashboard.py`: The main application interface.
* `traffic_videos/`: Sample footage used for testing and validation.
* `yolov8n.pt`: The pre-trained weights for the detection model.
* `requirements.txt`: List of dependencies required to run the project.

## 🚦 How to Run
1. Clone the repository:
   ```bash
   git clone [https://github.com/bandapallijoshnasree71/Smart-Traffic-Signal-AI.git](https://github.com/bandapallijoshnasree71/Smart-Traffic-Signal-AI.git)
   Install dependencies:

Bash
pip install -r requirements.txt
Run the dashboard:

Bash
python dashboard.py

