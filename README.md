# 🎟️ Tickefy — Intelligent Facial Recognition Ticketing System

## 🧠 Overview
**Tickefy** is an end-to-end intelligent ticketing system built for large-scale events such as the **Africa Cup of Nations (CAN) 2025**.  
It uses **facial recognition** to eliminate physical tickets, reduce fraud, and streamline stadium access — providing a secure, seamless, and modern spectator experience.

Developed as a final-year engineering project, Tickefy combines **AI, microservices, IoT, and cloud-ready architecture** to demonstrate a next-generation ticketing platform.

---

## 🚀 Features

### 🎫 Ticket Management
- Secure account creation and JWT authentication  
- Purchase, transfer, and manage tickets online  
- Real-time seat availability and QR code generation  

### 👤 Facial Recognition
- Registration of a facial image linked to each ticket  
- Quality verification of the uploaded photo  
- Real-time identification during stadium entry via FastAPI AI module  

### ⚙️ Microservice Architecture
- **Spring Boot** for core business logic (users, matches, tickets)  
- **FastAPI (Python)** for AI-powered facial recognition  
- **React.js** web interface for users  
- **MySQL** for persistence  
- **Android app** for on-site access control (camera + Raspberry Pi + Arduino)  

### 🧩 Containerization
All services are fully containerized with **Docker Compose**, making deployment simple and portable across systems.

---

## 🧱 Architecture
<img width="1190" height="520" alt="architecture" src="https://github.com/user-attachments/assets/3df8a134-156c-4a24-afa0-298366d2ef8e" />


- **Frontend (React):** Provides user interaction (browsing matches, purchasing, and uploading face images).  
- **Backend (Spring Boot):** Manages users, tickets, matches, and communication between services.  
- **AI Microservice (FastAPI):** Performs face detection, embedding, and verification.  
- **IoT Layer:** Raspberry Pi and Arduino handle real-time gate automation.  
- **Android App:** Used by stadium staff for biometric verification at entry points.

---

## 📱 Android App — *Tickefy Entry Capture Interface*

The **Android application** is the **user-facing interface deployed at event entry points**.  
It allows spectators to **capture their facial images** upon arrival, which are then sent to the backend for identity verification.

### 🔗 Repository
➡️ [Tickefy Android (Assiminee/TickefyAndroid)](https://github.com/Assiminee/TickefyAndroid)

### 📘 Description
The application was developed by **customizing an open-source Android camera UI project** (**[placeholder for original repository link]**) to fit Tickefy’s workflow.  
The base project originally handled only image capture, with no recognition or backend integration.  

Within **Tickefy**, the app’s purpose was extended to:
- Serve as the **official entry-point terminal UI** (used by staff or kiosks at stadium gates)  
- Capture high-quality images of spectators for **authentication through the FastAPI microservice**  
- Send these images to the backend over HTTP for **real-time identity validation**  
- Contribute additional samples (under user consent) to the **biometric dataset**, improving the model’s robustness across:
  - different lighting conditions  
  - camera angles  
  - facial expressions  

### 🧠 AI Integration
Captured images are sent to the FastAPI endpoint:

# POST /api/v1/face/validate
This endpoint handles:
- Preprocessing (face alignment, quality verification)
- Embedding extraction and comparison
- Return of an *accept/reject* signal (and optional contribution to the dataset)

The Android device thus remains lightweight and fast, while the heavy facial recognition computations are offloaded to GPU-backed containers.

---

## 🧰 Tech Stack Summary

| Layer | Technology |
|-------|-------------|
| **Frontend** | React.js, Node.js |
| **Backend** | Spring Boot (Java 21), Eureka, MySQL |
| **AI Module** | FastAPI, TensorFlow, PyTorch, FAISS, OpenCV |
| **Mobile App** | Android (Java, CameraX, Retrofit) |
| **Orchestration** | Docker & Docker Compose |
| **Hardware Prototype** | Raspberry Pi 4, Arduino, Servo Motors |

---

## 🐳 Dockerized Setup

### Included Services
- `spring-app` — Core backend (Java)
- `python-app` — AI and facial recognition (Python + CUDA)
- `frontend` — Web client (React)
- `mysql` — Database
- `phpmyadmin` — Optional DB management UI

## 🧪 Full System Test — End-to-End Demonstration

This section explains how anyone can **run the complete Tickefy ecosystem** — including the web platform, AI microservice, and Android application — to experience the full ticketing and access-control workflow.

---

### 1. Run the Platform (Dockerized Stack)

#### Clone the main repository
```bash
git clone https://github.com/<yourusername>/Tickefy-Docker.git
cd Tickefy-Docker
```

#### Build and start the system
> ⚠️ **Note:**  
> The AI microservice container (FastAPI with CUDA support) is quite large and may take some time to build, especially on first run.  
> This system relies on **CUDA**, so an **NVIDIA GPU** and the **NVIDIA Container Toolkit** are required to enable hardware acceleration.
```bash
docker compose up --build
```

Once the containers are up, the services will be available at:

|Service|URL|
|-------|---|
|🖥️ Frontend (React)|http://localhost:5173|
|⚙️ Spring Boot Backend|http://localhost:5001|
|🤖 FastAPI (AI Module)|http://localhost:8000/docs|
|🗄️ PhpMyAdmin (optional)|http://localhost:8080|

### 2. Run the Android App (Entry Capture Interface)
The Android app is used at stadium entry points to capture and validate spectators’ faces.
Clone the Android repository
```bash
git clone https://github.com/Assiminee/TickefyAndroid.git
```
Run it on your Android device or tablet:

1. Open the project in Android Studio.

2. Enable Developer Options and USB Debugging on your Android device:

3. Settings → About phone → Tap Build number 7 times.

4. Developer Options → Enable USB debugging.

5. Connect your device via USB.

6. Click Run ▶ in Android Studio.

7. When prompted, allow the app to install and run.

**📱 Recommendation: For best performance and visibility, use a tablet.**

Once the app is running, make sure it’s configured to connect to your backend:
```
http://<your-computer-IP>:8000
```

### 3. Follow the Full User Flow

Once both systems (web & Android) are running, you can test the complete Tickefy experience as a spectator:

#### Step 1 — Sign up

1. Go to http://localhost:5173

2. Create a new user account with your name, email, and password.

#### Step 2 — Upload or Skip Facial Image

During registration or profile setup, you’ll be asked to upload a photo of yourself.

You may upload one for biometric registration or opt out and continue without it.

#### Step 3 — Purchase a Ticket

1. Browse available matches on the home page.

2. Choose your seat and complete your purchase.

Your ticket will include a QR code for digital validation.

#### Step 4 — Post-Purchase Photo (Optional)

After purchase, you’ll again be prompted to add an additional photo or skip.

This allows users to update their biometric data under different lighting or angles to improve recognition robustness.

#### Step 5 — Non-Biometric Entry (Optional)

If you opted out of facial recognition:

1. You can print your ticket or

2. Present the QR code directly at the entry point (scannable via a physical or digital device).

#### Step 6 — Biometric Entry (Facial Recognition)

If you chose to enable facial authentication:

1. Open the Tickefy Android App on your device or at an entry kiosk.

2. Position your face within the on-screen frame — the app will capture and send your image to the FastAPI backend.

3. The backend verifies your identity in real time and grants or denies access.

4. Respect the access window indicated on your ticket:

- ⏱️ 3 hours before match time

- ⏱️ 1 hour after the scheduled start

If access is valid and recognition succeeds, the system will mark you as checked-in, and the Raspberry/Arduino module (in a full deployment) triggers gate opening.

## 🎥 Demo video

https://github.com/user-attachments/assets/2c79efd6-a09d-4400-98e2-b783128953a1

## 👩🏼‍💻 Contributors

This project was made possible thanks to the efforts of our talented team:

- **Backend Developer:** Saad Boukili ([GitHub](https://github.com/dermokill)) 
- **Frontend Developers:**  
  - Mohammed Amin Esfouna ([GitHub](https://github.com/ESFOUNA))  
  - Mohammed Lahkim ([GitHub](https://github.com/mohammedlahkim))
- **AI, Android & Docker Developer, Project Manager:** Myself, Yasmine Znatni ([GitHub](https://github.com/Assiminee))
- **Embedded Systems Developer:**
  - Oussama El Idrissi
