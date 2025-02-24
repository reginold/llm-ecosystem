# LLM Ecosystem Project

A full-stack application for processing invoices using AI agents, built with React, Flask, and PostgreSQL.

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)
- OpenAI API key

## Project Structure
```
llm-ecosystem/
├── backend/
│   ├── ai_agents/
│   │   ├── __init__.py
│   │   ├── crew.py
│   │   └── tools.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── UploadInvoice.tsx
│   │   │   └── ReconciliationResults.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── App.test.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
│
├── .gitignore
└── README.md
```
## Quick Start

1. Clone the repository:

```bash
git clone <repository-url>
cd llm-ecosystem
```

2. Create backend environment file:
```bash
# Create .env file in backend directory
cat > backend/.env << EOL
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://admin:adminpassword@postgres:5432/llm_ecosystem
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=your-openai-api-key-here
EOL
```

3. Start the application:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Services

### Frontend (React)
- Modern React application with TypeScript
- React Query for data fetching
- Tailwind CSS for styling
- Running on port 3000

### Backend (Flask)
- RESTful API with Flask
- Celery for asynchronous tasks
- SQLAlchemy for database ORM
- Running on port 5000

### Database (PostgreSQL)
- PostgreSQL 14
- Persistent data storage
- Running on port 5432

### Cache (Redis)
- Redis for Celery task queue
- Running on port 6379

## API Endpoints

### Upload Invoice
```http
POST /api/upload-invoice
Content-Type: multipart/form-data

file: invoice_file
```

### Get Results
```http
GET /api/results/<task_id>
```

### Get Invoice
```http
GET /api/invoice/<invoice_id>
```

## Development

### Local Frontend Development
```bash
cd frontend
npm install
npm start
```

### Local Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

### Running Tests
```bash
# Frontend tests
cd frontend
npm test

# Backend tests (if implemented)
cd backend
python -m pytest
```

## File Upload Support

Supported file formats:
- PDF (.pdf)
- CSV (.csv)
- JSON (.json)
- Images (.jpg, .jpeg, .png)

Maximum file size: 10MB

## Environment Variables

### Backend
- `FLASK_APP`: Flask application entry point
- `FLASK_ENV`: Flask environment (development/production)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key for AI processing

### Frontend
- `REACT_APP_API_URL`: Backend API URL

## Common Issues and Solutions

1. Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up --build
```

2. Redis Connection Issues
```bash
# Check Redis logs
docker-compose logs redis

# Reset Redis
docker-compose restart redis
```

3. File Upload Issues
- Ensure the uploads directory exists in backend/
- Check file size limits
- Verify file format support

## Maintenance

### Backup Database
```bash
docker-compose exec postgres pg_dump -U admin llm_ecosystem > backup.sql
```

## Database Design

```
graph TD
    A[Invoice Collection] --> B[Report Collection]
    A --> C[Reconciliation Collection]
    D[PurchaseOrder Collection] --> C
```

# Invoice Collection
{
    "_id": ObjectId,
    "file_path": str,
    "upload_date": datetime,
    "status": str,  # PENDING, PROCESSING, COMPLETED
    "extracted_data": {
        "bill_to": str,
        "emailing_address": str,
        "invoice_number": str,
        "invoice_date": str,
        "invoice_amount": str,
        "services": [{
            "service": str,
            "quantity": str,
            "unit_price": str,
            "amount": str
        }]
    },
    "user_edited_data": {  # Store user modifications
        # Same structure as extracted_data
    },
    "metadata": {
        "file_type": str,
        "file_size": int,
        "processing_time": float
    }
}

# Report Collection
{
    "_id": ObjectId,
    "invoice_id": ObjectId,
    "created_at": datetime,
    "processing_status": str,
    "ocr_confidence": float,
    "processing_time": float,
    "error_logs": [str],
    "validation_results": {
        "field_accuracy": float,
        "missing_fields": [str],
        "warnings": [str]
    }
}
