# IEEE Conference Paper Generator API Documentation

This directory contains the API documentation and client libraries for the IEEE Conference Paper Generator API.

## 📁 Files Overview

- `index.html` - Main API documentation landing page
- `swagger-ui.html` - Interactive Swagger UI documentation
- `swagger.json` - OpenAPI 3.0 specification
- `api-client.js` - JavaScript client library
- `README.md` - This documentation file

## 🚀 Quick Start

### 1. View Documentation

- **Main Page**: Visit `http://localhost:5001/` for the overview page
- **Interactive Docs**: Visit `http://localhost:5001/docs` for Swagger UI
- **API Spec**: Visit `http://localhost:5001/docs/swagger.json` for the OpenAPI specification

### 2. Using the JavaScript Client

Include the client library in your HTML:

```html
<script src="http://localhost:5001/static/api-client.js"></script>
```

Or import it in your JavaScript:

```javascript
import IEEEPaperGeneratorAPI from './api-client.js';
```

### 3. Basic Usage

```javascript
// Initialize the API client
const api = new IEEEPaperGeneratorAPI('http://localhost:5001');

// Check API health
const health = await api.checkHealth();
console.log('API Status:', health.status);

// Generate a paper
const paperData = {
    title: "Machine Learning Approaches for Climate Change Prediction",
    research_field: "Computer Science - Machine Learning",
    methodology: "Deep learning with convolutional neural networks",
    expected_results: "Improved accuracy in climate prediction models by 15%"
};

const result = await api.generatePaper(paperData);
console.log('Generated paper:', result);
```

## 📋 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API health |
| POST | `/api/generate-paper` | Generate IEEE conference paper |
| POST | `/api/upload-pdf` | Upload and analyze PDF |
| POST | `/api/generate-pdf` | Generate PDF from content |
| GET | `/api/stats` | Get API statistics |
| POST | `/api/validate-inputs` | Validate paper inputs |

### Request/Response Examples

#### Generate Paper

**Request:**
```json
{
    "title": "Machine Learning Approaches for Climate Change Prediction",
    "research_field": "Computer Science - Machine Learning",
    "methodology": "Deep learning with convolutional neural networks",
    "expected_results": "Improved accuracy in climate prediction models by 15%",
    "additional_context": "Focus on recent developments in the field"
}
```

**Response:**
```json
{
    "success": true,
    "content": "Generated paper content...",
    "sections": {
        "title": "Machine Learning Approaches for Climate Change Prediction",
        "abstract": "Abstract content...",
        "introduction": "Introduction content...",
        "methodology": "Methodology content...",
        "results": "Results content...",
        "conclusion": "Conclusion content...",
        "references": "References..."
    },
    "word_count": 2500,
    "character_count": 15000,
    "generated_at": "2024-01-15T10:30:00Z"
}
```

#### Upload PDF

**Request:** Multipart form data with PDF file

**Response:**
```json
{
    "success": true,
    "extracted_text": "Extracted text from PDF...",
    "analysis": {
        "summary": "PDF analysis results...",
        "key_topics": ["topic1", "topic2"],
        "word_count": 5000
    },
    "text_length": 5000,
    "uploaded_at": "2024-01-15T10:30:00Z"
}
```

## 🔧 Error Handling

The API returns appropriate HTTP status codes and error messages:

```javascript
try {
    const result = await api.generatePaper(paperData);
} catch (error) {
    console.error('Error:', error.message);
    // Handle specific error types
    if (error.message.includes('Validation failed')) {
        // Handle validation errors
    } else if (error.message.includes('HTTP 500')) {
        // Handle server errors
    }
}
```

## 📊 API Statistics

Track API usage with the statistics endpoints:

```javascript
// Get current statistics
const stats = await api.getStats();
console.log('Total API calls:', stats.total_calls);
console.log('Calls by endpoint:', stats.calls_by_endpoint);

// Reset statistics (if needed)
await api.resetStats();
```

## 🎯 Frontend Integration Examples

### React Example

```jsx
import React, { useState } from 'react';
import IEEEPaperGeneratorAPI from './api-client.js';

function PaperGenerator() {
    const [paperData, setPaperData] = useState({
        title: '',
        research_field: '',
        methodology: '',
        expected_results: ''
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const api = new IEEEPaperGeneratorAPI();

    const generatePaper = async () => {
        setLoading(true);
        try {
            const response = await api.generatePaper(paperData);
            setResult(response);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <input
                type="text"
                placeholder="Paper Title"
                value={paperData.title}
                onChange={(e) => setPaperData({...paperData, title: e.target.value})}
            />
            {/* Add other form fields */}
            <button onClick={generatePaper} disabled={loading}>
                {loading ? 'Generating...' : 'Generate Paper'}
            </button>
            {result && (
                <div>
                    <h3>Generated Paper</h3>
                    <p>Word Count: {result.word_count}</p>
                    <pre>{result.content}</pre>
                </div>
            )}
        </div>
    );
}
```

### Vue.js Example

```vue
<template>
    <div>
        <form @submit.prevent="generatePaper">
            <input v-model="paperData.title" placeholder="Paper Title" required>
            <input v-model="paperData.research_field" placeholder="Research Field" required>
            <textarea v-model="paperData.methodology" placeholder="Methodology" required></textarea>
            <textarea v-model="paperData.expected_results" placeholder="Expected Results" required></textarea>
            <button type="submit" :disabled="loading">
                {{ loading ? 'Generating...' : 'Generate Paper' }}
            </button>
        </form>
        
        <div v-if="result">
            <h3>Generated Paper</h3>
            <p>Word Count: {{ result.word_count }}</p>
            <div v-html="formattedContent"></div>
        </div>
    </div>
</template>

<script>
import IEEEPaperGeneratorAPI from './api-client.js';

export default {
    data() {
        return {
            api: new IEEEPaperGeneratorAPI(),
            paperData: {
                title: '',
                research_field: '',
                methodology: '',
                expected_results: ''
            },
            result: null,
            loading: false
        };
    },
    computed: {
        formattedContent() {
            return this.result?.content?.replace(/\n/g, '<br>') || '';
        }
    },
    methods: {
        async generatePaper() {
            this.loading = true;
            try {
                this.result = await this.api.generatePaper(this.paperData);
            } catch (error) {
                console.error('Error:', error);
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>
```

## 🔒 Security Considerations

- The API currently doesn't require authentication
- Consider implementing rate limiting for production use
- Validate all inputs on both client and server side
- Use HTTPS in production environments

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the API server is running and CORS is properly configured
2. **File Upload Issues**: Make sure the file is a valid PDF and under the size limit
3. **Validation Errors**: Check that all required fields are provided and properly formatted

### Debug Mode

Enable debug mode to see detailed error messages:

```javascript
// Check API health first
const health = await api.checkHealth();
console.log('API Health:', health);

// Test with minimal data
const testData = {
    title: "Test Paper",
    research_field: "Test Field",
    methodology: "Test Method",
    expected_results: "Test Results"
};

try {
    const result = await api.generatePaper(testData);
    console.log('Test successful:', result);
} catch (error) {
    console.error('Test failed:', error);
}
```

## 📞 Support

For additional support or questions:

1. Check the interactive documentation at `/docs`
2. Review the OpenAPI specification at `/docs/swagger.json`
3. Test endpoints using the Swagger UI interface
4. Check the main project README for setup instructions

## 🔄 Version History

- **v1.0.0**: Initial API release with core functionality
- Added comprehensive Swagger documentation
- Included JavaScript client library
- Created interactive documentation interface 