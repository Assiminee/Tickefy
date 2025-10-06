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

### ⚙️ 1. Run the Platform (Dockerized Stack)

#### Clone the main repository
```bash
git clone https://github.com/<yourusername>/Tickefy-Docker.git
cd Tickefy-Docker
```

#### Build and start the system
Given the fact that the AI microservice container is considerably large, this might take a considerable amount of time.
Keep in mind that this system uses CUDA, which means that a NVIDIA GPU is required.
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
