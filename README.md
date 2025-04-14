# Bank RAG Application

A comprehensive document analysis system for banking documents using RAG (Retrieval-Augmented Generation) with AWS Bedrock and PostgreSQL.

## Features

- Document ingestion and processing
- Intelligent document chunking and embedding
- Vector storage using PostgreSQL with pgvector
- Document summarization and analysis
- Query-based recommendations
- Conversation history tracking
- Modern React frontend with Material-UI

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL 13+ with pgvector extension
- AWS Account with Bedrock access
- AWS CLI configured with appropriate credentials

## Setup Instructions

### 1. Database Setup

```bash
# Install PostgreSQL and pgvector
# Create database and enable extension
createdb bank_rag_db
psql bank_rag_db
CREATE EXTENSION vector;
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

## Usage

1. Access the application at `http://localhost:3000`
2. Upload documents using the drag-and-drop interface
3. Enter queries in the text field
4. View summaries, recommendations, and source documents

## API Endpoints

- `POST /upload`: Upload and process documents
- `POST /query`: Submit queries and get analysis
- `GET /chat-history`: Retrieve conversation history

## Architecture

- Backend: FastAPI with AWS Bedrock integration
- Frontend: React with Material-UI
- Database: PostgreSQL with pgvector
- Vector Store: AWS Bedrock embeddings
- Document Processing: LangChain

## Security Considerations

- Store AWS credentials securely
- Implement proper authentication
- Use environment variables for sensitive data
- Enable CORS only for trusted origins

## License

MIT 