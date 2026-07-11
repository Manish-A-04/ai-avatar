# AI Avatar Assistant System

This project is an AI Avatar Assistant system comprising a React frontend and a FastAPI backend. The system transcribes user speech, generates text responses using Google Gemini, synthesizes text to speech, and generates lip-synced video animations of avatar images in response to user inputs.

---

## User Interface and Demonstration

The user interface of the frontend dashboard:

![Frontend User Interface](1.png)

A demonstration video showing the system's generated output can be played below:

![](7163e23b-237c-4eaf-9bb4-ee73f4fecc89.mp4)

---

## Architecture Overview

The application is split into two main sections: a frontend client interface and a backend API server.

### Backend Structure

The backend application is structured under the backend directory:

- app/main.py: The API gateway entry point. Configures lifespan triggers, middleware, and routers.
- app/config.py: The central configuration loader that coordinates database connections, JWT secrets, model directories, and other system defaults.
- app/database.py: Coordinates SQLAlchemy asynchronous database engines and sessions.
- app/cleanup.py: Houses the media file background expiration and cleanup loop.
- app/auth/: Manages user creation, authorization, JWT verification, and active sessions.
- app/avatars/: Manages avatar selections and mappings.
- app/conversations/: Houses conversation turn sequences and chat history logs.
- app/pipeline/: Coordinates the core multi-stage processing tasks:
  - stt/service.py: Transcribes user-submitted audio via faster-whisper.
  - llm/service.py: Connects to the Gemini SDK to process prompts.
  - tts/service.py: Generates voice audio from response texts using the Kokoro TTS model.
  - lipsync/service.py: Invokes the Wav2Lip inference module to generate lip-sync videos.
  - service.py: Orchestrates the pipeline stages in sequence.
  - router.py: Provides web endpoints for processing text and voice requests.

### Frontend Structure

The frontend client is structured under the frontend directory:

- src/App.jsx: Core entry wrapper that sets up routing and session guards.
- src/main.jsx: Mounts the main React application shell.
- src/api/client.js: Handles Axios setup, request interception, and JWT storage.
- src/api/services.js: Maps API routes to service requests.
- src/context/AuthContext.jsx: Manages global authentication states.
- src/layouts/MainLayout.jsx: Standard application wrapper.
- src/pages/Dashboard.jsx: Primary interactive workstation interface.
- src/components/ui/: Contains functional reusable interface blocks (Loader, Input, Button, AvatarVideo).

---

## Third-Party Repository Dependencies

The backend relies on Easy-Wav2Lip to execute lip-sync video generation:

- The backend/wav2lip directory contains a clone of the Easy-Wav2Lip repository.
- Due to its external nature, this repository is listed in the global .gitignore configuration to keep vendor code isolated from application repository changes.

---

## Installation and Configuration

Follow these instructions to configure and initialize the application.

### Prerequisites

Ensure the following tools are installed:
- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL database engine

### 1. Database Initialization

Configure a PostgreSQL database named aiavatar.

### 2. Backend Setup

Move to the backend folder:
```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv .venv
```

Activate the virtual environment:
- On Windows (PowerShell):
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- On Linux/macOS:
  ```bash
  source .venv/bin/activate
  ```

Install dependencies:
```bash
pip install -r requirements.txt
```

Initialize your .env configuration file under backend/.env based on backend/.env.example:
```ini
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aiavatar
SECRET_KEY=generate_your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
GEMINI_API_KEY=your_gemini_api_key
WAV2LIP_ENABLED=True
DEFAULT_SYSTEM_PROMPT="You are a helpful, friendly AI assistant."
```

Apply migrations using Alembic:
```bash
alembic upgrade head
```

### 3. Wav2Lip Vendor Configuration

Clone the Wav2Lip public repository into backend/wav2lip:
```bash
git clone https://github.com/another-public-repo/Easy-Wav2Lip backend/wav2lip
```

Ensure model weights are placed inside the vendor repository directories:
- Place the Wav2Lip model checkpoint (e.g. Wav2Lip_GAN.pt) in backend/wav2lip/checkpoints/Wav2Lip_GAN.pt.
- Place the face detection model checkpoint (e.g. s3fd.pth) in backend/wav2lip/face_detection/detection/SFD/s3fd.pth.

### 4. Frontend Setup

Move to the frontend folder:
```bash
cd ../frontend
```

Install packages:
```bash
npm install
```

Configure local environment variables if necessary in frontend/.env:
```ini
VITE_API_URL=http://localhost:8000
```

---

## Running the Application

Ensure database connections and configuration settings are in place.

### Start Backend

From the backend folder (with the virtual environment active):
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start Frontend

From the frontend folder:
```bash
npm run dev
```

Open http://localhost:5173 in your browser to run the interface.

---

## Coding Standards

Code files under backend/app and frontend/src adhere to the following formatting standards:
- All imports are declared at the top of files.
- No unused imports or unused functions remain in source files.
- No docstrings or comments are preserved within the main application source files.
