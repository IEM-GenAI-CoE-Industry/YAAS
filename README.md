# YAAS Platform

A modern, AI-powered skill development application that allows users to ask questions and receive intelligent, context-aware responses. Built with FastAPI backend and React frontend.

![YAAS](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Features

- **AI-Powered Content Generation**: Leverages multiple AI models (OpenAI, MistralAI, Ollama, Google GenAI, Groq)
- **Modern UI**: Beautiful, responsive interface with gradient design and smooth animations
- **Real-time Processing**: Fast content generation with loading states and error handling
- **RESTful API**: Well-documented FastAPI backend with OpenAPI/Swagger support
- **Cross-Origin Support**: Configured CORS for seamless frontend-backend communication

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Tech Stack](#tech-stack)


## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11.94** - [Download Python](https://www.python.org/downloads/)
- **Node.js 22.20.0** and **npm** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/downloads)

## Project Structure

```
YAAS/
├── backend/
│   ├── app.py                 # FastAPI application entry point
│   ├── api_services.py        # API route handlers
│   ├── base_requests.py       # Pydantic request/response models
│   ├── config.py              # Configuration settings
│   ├── test_run.py            # Content generation logic
│   ├── requirements.txt       # Python dependencies
│   ├── util/
│   │   ├── constants.py       # Application constants
│   │   ├── llm_factory.py     # Factory for LLM integrations
│   │   ├── utility.py         # Utility functions
│   │   └── system_prompt.py   # System prompts for AI models
│   └── venv/                  # Virtual environment (not in git)
├── frontend/
│   └── test/
│       ├── src/
│       │   ├── App.jsx        # Main React component
│       │   ├── App.css        # Application styles
│       │   ├── index.css      # Global styles
│       │   └── main.jsx       # React entry point
│       ├── package.json       # Node.js dependencies
│       └── vite.config.js     # Vite configuration
├── .gitignore                 # Git ignore file
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Installation

### Backend Setup

1. **Clone the repository**

```bash
git clone https://github.com/Sujaanb/YAAS.git
cd YAAS
```

2. **Navigate to the backend directory**

```bash
cd backend
```

3. **Create a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

4. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

5. **Set up environment variables**

Create a `.env` file in the `backend` directory:

```bash
# Copy from example
cp ../.env.example .env

# Edit .env and add your API keys
```

Required environment variables:
```env
llm_provider = "groq"  # Could be "mistral", "gemini", "openai" or "groq"

# Add your API keys here
openai_api_key=your_openai_key
mistral_api_key=your_mistral_key
groq_api_key=your_groq_key
gemini_api_key=your_gemini_key
# Or configure Ollama for local models
```

### Local LLM Setup with Ollama (Optional)

If you want to use local LLMs instead of cloud providers:

1. **Install Ollama**
   - Visit [Ollama's official website](https://ollama.com/download) and download the installer for your OS
   - Run the installer and follow the setup instructions

2. **Run your preferred model**
   ```bash
   # Run a specific model (example: gemma)
   ollama run gemma3

   # Or run a smaller model for testing
   ollama run tinyllama
   # In this case, change the local_model value to tinyllama in the constants.py file.
   ```

3. **Configure the environment**
   In your `.env` file:
   ```env
   local_model_url = "http://localhost:11434"  # Default Ollama API endpoint
   ```

4. **Test the local setup**
   ```bash
   # Verify Ollama is running
   curl http://localhost:11434/api/tags
   ```

### Frontend Setup

1. **Navigate to the frontend directory**

```bash
cd ../frontend/test
```

2. **Install Node.js dependencies**

```bash
npm install
```

3. **Configure API endpoint (optional)**

The frontend is preconfigured to connect to `http://localhost:8001`. If you need to change this, edit the API URL in `src/App.jsx`.

## Configuration

### Backend Configuration

The backend configuration is managed in `backend/config.py`:

- **API Version**: `/YAAS/content/v1`
- **Server Port**: `8001`
- **CORS Origins**: Configured for `localhost:3000`, `localhost:5173`, `localhost:8000`

### Frontend Configuration

The frontend is built with Vite and runs on port `5173` by default. The Vite configuration is in `frontend/test/vite.config.js`.

## Running the Application

### Start the Backend Server

1. **Activate the virtual environment** (if not already active)

```bash
# Windows
cd backend
venv\Scripts\activate

# macOS/Linux
cd backend
source venv/bin/activate
```

2. **Run the FastAPI server**

```bash
python app.py
```

The backend will start at `http://localhost:8001`

**Verify the backend is running:**
- Visit `http://localhost:8001/docs` for API documentation
- Visit `http://localhost:8001` for the welcome page

### Start the Frontend Development Server

1. **Open a new terminal** and navigate to the frontend directory

```bash
cd frontend/test
```

2. **Start the Vite development server**

```bash
npm run dev
```

The frontend will start at `http://localhost:5173`

3. **Open your browser** and visit `http://localhost:5173`

## API Documentation

### Endpoints

#### `POST /YAAS/content/v1/generate`

Generate content based on a user question.

**Request Body:**
```json
{
  "question": "What is artificial intelligence?",
  "local_llm": false
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Content generated successfully",
  "data": "Generated content response..."
}
```

**Error Responses:**
- `400 Bad Request`: Invalid question
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Interactive API Documentation

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server implementation
- **LangChain** - Framework for developing LLM applications
- **Multiple AI Integrations**:
  - OpenAI
  - MistralAI
  - Ollama
  - Google GenAI
  - Groq
- **ChromaDB** - Vector database for embeddings
- **Python-dotenv** - Environment variable management

### Frontend
- **React 19** - UI library
- **Vite** - Fast build tool and dev server
- **CSS3** - Modern styling with gradients and animations
- **Fetch API** - HTTP client for API calls

## Development

### Backend Development

```bash
# Install development dependencies
pip install black ruff

# Format code
black .

# Lint code
ruff check .
```

### Frontend Development

```bash
# Run linter
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## Building for Production

### Backend

```bash
# The backend can be deployed using any ASGI server
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Frontend

```bash
cd frontend/test
npm run build
# Build output will be in the 'dist' directory
```

## Troubleshooting

### CORS Issues
If you encounter CORS errors:
1. Ensure the backend is running before starting the frontend
2. Verify that `http://localhost:5173` is in the CORS origins list in `backend/config.py`
3. Restart the backend server after configuration changes

### Backend Connection Issues
If the frontend can't connect to the backend:
1. Verify the backend is running on port `8001`
2. Check that there are no firewall rules blocking the connection
3. Ensure the API URL in the frontend matches the backend URL

### Python Dependencies Issues
If you encounter dependency conflicts:
```bash
# Clear existing installations
pip uninstall -r requirements.txt -y

# Reinstall fresh
pip install -r requirements.txt
```