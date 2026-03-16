# Aegis: The Self-Healing Multimodal Cyber Engine 🛡️🛡️🛡️

Aegis is an enterprise-grade cyber-defense engine built for the **Gemini Live Agent Challenge (2026)**. Unlike traditional reactive security bots, Aegis utilizes a persistent, bidirectional neural link to provide real-time threat detection and autonomous system recovery.

## 🚀 The "Grand Prize" Innovation
Most AI agents operate on a "turn-based" request-response loop. Aegis breaks this paradigm with two core architectural advancements:

1. **Persistent Neural Link (Gemini Live API):** Using `client.aio.live.connect`, Aegis maintains a low-latency (<150ms) asynchronous stream. This allows the engine to "see" network telemetry and "hear" system alerts simultaneously with native **Barge-in** support for human-in-the-loop intervention.

2. **Reflexive Self-Healing (ADK Plugin):**
   Aegis is built with a custom **Self-Healing Wrapper**. If the connection jitters or an API fails, a **Reflexive Diagnostic Loop** automatically triggers. It analyzes the error and restores the agent's **Tactical State** from **Google Firestore** (prefixed with `diag_`), ensuring the sentinel never stays down.

## 🛠️ Technical Stack
* **Framework:** Google Agent Development Kit (ADK)
* **Intelligence:** Gemini 1.5 Pro (Vertex AI)
* **Infrastructure:** Google Cloud Run (Containerized)
* **Database:** Google Firestore (State Persistence)
* **Automation:** Terraform (Infrastructure-as-Code)

## 🏗️ Architecture
The system consists of a high-performance asynchronous bridge between the client-side WebSocket and the Vertex AI Live API. 
* **State Management:** All critical session data is synced to Firestore, allowing for seamless recovery after a dashboard refresh or server restart.
* **Non-Blocking I/O:** Utilizes `asyncio.create_task` for parallel processing of multimodal media chunks.

## 🏃‍♂️ Spin-up Instructions
1. **Prerequisites:** * Google Cloud Project with Vertex AI and Firestore enabled.
   * `GOOGLE_APPLICATION_CREDENTIALS` set in your environment.
2. **Installation:**
   ```bash
   pip install -r requirements.txt