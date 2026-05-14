# Kubrick AI: Advanced Video-RAG Analysis Platform

Kubrick AI is a sophisticated, real-time Video Retrieval-Augmented Generation (RAG) platform. It allows users to "chat" with video content, perform multimodal searches (text/image to video), and extract precise clips based on semantic understanding of speech and visual context.

---

## 🚀 Tech Stack & Rationale

### **Frontend: Next.js 14 & Tailwind CSS**
- **Why?** Chosen for its robust Server-Side Rendering (SSR) capabilities and React-based component architecture, enabling a highly responsive and premium user experience. Tailwind CSS was utilized for rapid, consistent UI development with modern aesthetics.

### **Backend: FastAPI (Python)**
- **Why?** FastAPI provides high-performance asynchronous execution, which is critical for handling long-running video processing tasks and real-time agentic interactions.

### **Data Orchestration: Pixeltable**
- **Why?** **Pixeltable** is the core of our RAG pipeline. It unifies traditional data storage with AI processing. Instead of managing separate databases, vector stores, and model pipelines, Pixeltable allows us to treat videos as "smart tables" where frames, audio, and transcriptions are automatically processed and indexed via computed columns.

### **Inference Engine: Groq**
- **Why?** We utilize Groq for our LLM agent to achieve ultra-fast inference speeds. This ensures that the conversational experience feels instantaneous, even when the agent is orchestrating complex tool calls.

### **Standardized Tooling: Model Context Protocol (MCP)**
- **Why?** By implementing the **Model Context Protocol**, we decoupled our video processing logic from the chat agent. This standardized interface allows the Groq-powered agent to interact with our video tools (search, clip extraction, Q&A) in a secure and scalable way.

---

## 🛠️ System Architecture

The platform is built on a microservices architecture, containerized with Docker:

1.  **`kubrick-ui`**: The React-based frontend providing a seamless chat and video management interface.
2.  **`kubrick-api`**: The central orchestrator that manages authentication, chat history, and agentic reasoning.
3.  **`kubrick-mcp`**: A dedicated Model Context Protocol server that handles heavy-duty video processing and vector searches.
4.  **`nginx-gateway`**: A unified entry point for the entire application, handling reverse-proxying and routing.

---

## 🧠 Video Processing Pipeline (Video RAG)

Our RAG implementation goes beyond simple text. We process video in multiple dimensions to ensure accurate retrieval:

1.  **Audio Ingestion**:
    - **Extraction**: Extracting audio from uploaded MP4s using FFmpeg.
    - **Transcription**: Utilizing **OpenAI Whisper** via Pixeltable to generate high-fidelity transcripts.
    - **Vector Indexing**: Segmenting text into chunks and generating semantic embeddings for speech-based search.

2.  **Visual Ingestion**:
    - **Frame Sampling**: Extracting strategic frames from the video at specific intervals.
    - **Intelligent Captioning**: Using **OpenAI GPT-4o-Vision** to generate descriptive captions for every sampled frame.
    - **Vision Indexing**: Generating embeddings for frame captions to enable search based on visual content (e.g., "Find the part where the player scores").

3.  **Multimodal Retrieval**:
    - When a user asks a question, the agent searches both the **Speech Index** and the **Vision Index** to find the most relevant timestamps.
    - **Dynamic Clip Extraction**: The system uses FFmpeg to cut and serve the exact video segment identified by the RAG search.

---

## ✨ Key Features

- **Semantic Video Search**: Find moments in videos by describing them in plain English.
- **Image-to-Video Retrieval**: Upload an image to find similar visual moments in a video.
- **Contextual Q&A**: Ask complex questions about video content and receive answers backed by extracted video evidence.
- **Real-time Processing**: Background task orchestration allows for seamless ingestion of large video files.

---

## 🛠️ Installation & Setup

### Prerequisites
- Docker & Docker Compose
- API Keys for Groq and OpenAI

### Running the App
1. Clone the repository.
2. Create a `.env` file in `kubrick-api` and `kubrick-mcp` with your API keys.
3. Run the orchestration:
   ```bash
   docker-compose up --build
   ```
4. Access the platform at `http://localhost`.

---

## 📈 Future Roadmap
- [ ] Multi-video cross-referencing for global RAG.
- [ ] Integration with open-source Vision LLMs for local processing.
- [ ] WebSocket streaming for real-time processing feedback.
