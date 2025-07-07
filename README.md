# IEEE Conference Paper Generator - Flask API

A modular Flask API for generating IEEE conference paper content using Google's Gemini AI. This API provides endpoints for paper generation, PDF upload and analysis, and PDF generation in IEEE format.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **PDF Processing**: Upload and analyze PDF files for content extraction
- **Content Generation**: Generate IEEE conference paper content using AI
- **PDF Generation**: Create properly formatted IEEE conference papers
- **API Tracking**: Monitor API usage and costs
- **Input Validation**: Comprehensive validation for all inputs
- **CORS Support**: Cross-origin resource sharing enabled

## Project Structure

```
blog_gen_tool-research-paper-v1/
├── app.py                 # Main Flask application
├── modules/               # Modular components
│   ├── __init__.py
│   ├── pdf_handler.py     # PDF processing and analysis
│   ├── content_generator.py # AI content generation
│   ├── pdf_generator.py   # PDF creation in IEEE format
│   ├── api_tracker.py     # API usage tracking
│   └── validators.py      # Input validation
├── requirements.txt       # Python dependencies
├── instructions.txt       # IEEE formatting instructions
├── ieee-conference-template.pdf # IEEE template
└── README.md             # This file
```

## Installation

### Quick Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd blog_gen_tool-research-paper-v1
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Configure your API key**:
   Edit the `.env` file and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

### Manual Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd blog_gen_tool-research-paper-v1
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file**:
   ```bash
   cp .env.example .env  # if .env.example exists
   # or create .env manually with:
   echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:5001`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns API status and version information

### Generate Paper Content
- **POST** `/api/generate-paper`
- Generates IEEE conference paper content

**Request Body**:
```json
{
  "title": "Your Paper Title",
  "research_field": "Description of your research field",
  "methodology": "Description of your methodology",
  "expected_results": "Description of expected results",
  "additional_context": "Optional additional context",
  "custom_parameters": {
    "Author Name": "John Doe",
    "Email ID": "john.doe@university.edu",
    "Institution/Organization": "University of Technology",
    "Parameter 1": "Additional parameter value"
  }
}
```

**Response**:
```json
{
  "success": true,
  "content": "Generated paper content...",
  "sections": {
    "title": "Paper Title",
    "abstract": "Abstract content...",
    "keywords": "keyword1, keyword2, keyword3",
    "introduction": "Introduction content...",
    "methodology": "Methodology content...",
    "results": "Results content...",
    "conclusion": "Conclusion content..."
  },
  "word_count": 1500,
  "character_count": 8500,
  "generated_at": "2024-01-01T12:00:00"
}
```

### Upload and Analyze PDF
- **POST** `/api/upload-pdf`
- Uploads a PDF file and extracts/analyzes its content

**Request**: Multipart form data with `file` field containing PDF

**Response**:
```json
{
  "success": true,
  "extracted_text": "First 1000 characters of extracted text...",
  "analysis": "TITLE: Suggested Title\nFIELD: Research Field\nMETHODOLOGY: Methodology\nRESULTS: Expected Results\nKEYWORDS: keywords",
  "text_length": 5000,
  "uploaded_at": "2024-01-01T12:00:00"
}
```

### Generate PDF
- **POST** `/api/generate-pdf`
- Creates a PDF file from content sections

**Request Body**:
```json
{
  "sections": {
    "title": "Paper Title",
    "abstract": "Abstract content...",
    "keywords": "keywords...",
    "introduction": "Introduction content...",
    "methodology": "Methodology content...",
    "results": "Results content...",
    "conclusion": "Conclusion content..."
  },
  "author_info": {
    "Author Name": "John Doe",
    "Email ID": "john.doe@university.edu",
    "Institution/Organization": "University of Technology"
  }
}
```

**Response**: PDF file download

### Validate Inputs
- **POST** `/api/validate-inputs`
- Validates paper generation inputs

**Request Body**:
```json
{
  "title": "Paper Title",
  "research_field": "Research field description",
  "methodology": "Methodology description",
  "expected_results": "Expected results description"
}
```

**Response**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Paper title seems too short"],
  "validated_at": "2024-01-01T12:00:00"
}
```

### API Statistics
- **GET** `/api/stats`
- Returns API usage statistics

**Response**:
```json
{
  "summary": {
    "total_calls": 150,
    "today_calls": 5,
    "last_call_time": "2024-01-01T12:00:00",
    "estimated_cost": {
      "input_tokens": 300000,
      "output_tokens": 150000,
      "input_cost_usd": 0.0225,
      "output_cost_usd": 0.0450,
      "total_cost_usd": 0.0675
    }
  },
  "function_breakdown": {
    "generate_paper": 100,
    "upload_pdf": 30,
    "generate_pdf": 20
  },
  "recent_calls": [...]
}
```

### Reset Statistics
- **POST** `/api/reset-stats`
- Resets API usage statistics

## Modules Overview

### PDF Handler (`modules/pdf_handler.py`)
- Extracts text from uploaded PDF files
- Analyzes PDF content using AI to extract relevant information
- Parses analysis results into structured data
- Reads IEEE formatting instructions

### Content Generator (`modules/content_generator.py`)
- Generates IEEE conference paper content using Google Gemini AI
- Parses generated content into sections (abstract, introduction, etc.)
- Handles custom parameters and additional context
- Manages content formatting and structure

### PDF Generator (`modules/pdf_generator.py`)
- Creates IEEE format PDFs with two-column layout
- Handles proper formatting, fonts, and spacing
- Supports author information inclusion
- Provides fallback simple PDF generation

### API Tracker (`modules/api_tracker.py`)
- Tracks API call usage and statistics
- Calculates estimated costs based on token usage
- Provides export functionality for statistics
- Maintains call history and function breakdown

### Validators (`modules/validators.py`)
- Validates all API inputs
- Checks for required fields and content quality
- Validates PDF uploads and file formats
- Sanitizes inputs to prevent security issues

## Usage Examples

### Python Client Example
```python
import requests
import json

# Generate paper content
url = "http://localhost:5001/api/generate-paper"
data = {
    "title": "Machine Learning in Healthcare",
    "research_field": "Healthcare AI and machine learning applications",
    "methodology": "Deep learning approach using neural networks",
    "expected_results": "Improved diagnosis accuracy and patient outcomes"
}

response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
    print(f"Generated {result['word_count']} words")
    print(result['content'])
```

### cURL Examples
```bash
# Generate paper content
curl -X POST http://localhost:5001/api/generate-paper \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning in Healthcare",
    "research_field": "Healthcare AI applications",
    "methodology": "Deep learning approach",
    "expected_results": "Improved diagnosis accuracy"
  }'

# Upload PDF
curl -X POST http://localhost:5001/api/upload-pdf \
  -F "file=@your_paper.pdf"

# Get API statistics
curl http://localhost:5001/api/stats
```

## Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key (required)

### File Requirements
- `instructions.txt`: IEEE formatting instructions
- `ieee-conference-template.pdf`: IEEE conference template (optional)

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `500`: Internal Server Error

All error responses include a descriptive message:
```json
{
  "error": "Description of the error"
}
```

## Rate Limiting and Costs

- API calls are tracked and cost estimates are provided
- Google Gemini 2.0 Flash pricing: $0.075 per 1M input tokens, $0.30 per 1M output tokens
- Estimated costs are calculated based on average token usage per call

## Security Features

- Input sanitization to prevent injection attacks
- File upload validation and size limits
- Suspicious content detection
- CORS configuration for cross-origin requests

## Development

### Running in Development Mode
```bash
python app.py
```

### Running in Production
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 