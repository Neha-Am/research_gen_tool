/**
 * IEEE Conference Paper Generator API Client
 * A simple JavaScript client for interacting with the API
 */

class IEEEPaperGeneratorAPI {
    constructor(baseURL = 'http://localhost:5001') {
        this.baseURL = baseURL;
        this.endpoints = {
            health: '/health',
            generatePaper: '/api/generate-paper',
            uploadPDF: '/api/upload-pdf',
            generatePDF: '/api/generate-pdf',
            stats: '/api/stats',
            resetStats: '/api/reset-stats',
            validateInputs: '/api/validate-inputs'
        };
    }

    /**
     * Make HTTP request to the API
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} - Response promise
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const requestOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, requestOptions);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            // Handle PDF responses
            if (response.headers.get('content-type')?.includes('application/pdf')) {
                return response.blob();
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * Check API health
     * @returns {Promise<Object>} Health status
     */
    async checkHealth() {
        return this.request(this.endpoints.health, { method: 'GET' });
    }

    /**
     * Generate IEEE conference paper
     * @param {Object} paperData - Paper generation data
     * @returns {Promise<Object>} Generated paper content
     */
    async generatePaper(paperData) {
        const requiredFields = ['title', 'research_field', 'methodology', 'expected_results'];
        
        // Validate required fields
        for (const field of requiredFields) {
            if (!paperData[field] || !paperData[field].trim()) {
                throw new Error(`Missing required field: ${field}`);
            }
        }

        return this.request(this.endpoints.generatePaper, {
            method: 'POST',
            body: JSON.stringify(paperData)
        });
    }

    /**
     * Upload and analyze PDF file
     * @param {File} file - PDF file to upload
     * @returns {Promise<Object>} Analysis results
     */
    async uploadPDF(file) {
        if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
            throw new Error('Please provide a valid PDF file');
        }

        const formData = new FormData();
        formData.append('file', file);

        return this.request(this.endpoints.uploadPDF, {
            method: 'POST',
            headers: {}, // Let browser set Content-Type for FormData
            body: formData
        });
    }

    /**
     * Generate PDF from content sections
     * @param {Object} contentData - Content sections and author info
     * @returns {Promise<Blob>} Generated PDF blob
     */
    async generatePDF(contentData) {
        if (!contentData.sections) {
            throw new Error('Content sections are required');
        }

        return this.request(this.endpoints.generatePDF, {
            method: 'POST',
            body: JSON.stringify(contentData)
        });
    }

    /**
     * Get API usage statistics
     * @returns {Promise<Object>} Usage statistics
     */
    async getStats() {
        return this.request(this.endpoints.stats, { method: 'GET' });
    }

    /**
     * Reset API usage statistics
     * @returns {Promise<Object>} Reset confirmation
     */
    async resetStats() {
        return this.request(this.endpoints.resetStats, { method: 'POST' });
    }

    /**
     * Validate paper inputs
     * @param {Object} inputData - Input data to validate
     * @returns {Promise<Object>} Validation results
     */
    async validateInputs(inputData) {
        const requiredFields = ['title', 'research_field', 'methodology', 'expected_results'];
        
        for (const field of requiredFields) {
            if (!inputData[field] || !inputData[field].trim()) {
                throw new Error(`Missing required field: ${field}`);
            }
        }

        return this.request(this.endpoints.validateInputs, {
            method: 'POST',
            body: JSON.stringify(inputData)
        });
    }

    /**
     * Download generated PDF
     * @param {Blob} pdfBlob - PDF blob from generatePDF
     * @param {string} filename - Filename for download
     */
    downloadPDF(pdfBlob, filename = 'generated_paper.pdf') {
        const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

// Example usage:
/*
const api = new IEEEPaperGeneratorAPI();

// Generate a paper
const paperData = {
    title: "Machine Learning Approaches for Climate Change Prediction",
    research_field: "Computer Science - Machine Learning",
    methodology: "Deep learning with convolutional neural networks and LSTM models",
    expected_results: "Improved accuracy in climate prediction models by 15%",
    additional_context: "Focus on recent developments in the field"
};

try {
    const result = await api.generatePaper(paperData);
    console.log('Generated paper:', result);
} catch (error) {
    console.error('Error generating paper:', error);
}

// Upload and analyze PDF
const fileInput = document.getElementById('pdf-file');
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        try {
            const analysis = await api.uploadPDF(file);
            console.log('PDF analysis:', analysis);
        } catch (error) {
            console.error('Error analyzing PDF:', error);
        }
    }
});

// Generate PDF from content
const contentData = {
    sections: {
        title: "Sample Paper Title",
        abstract: "This is the abstract...",
        introduction: "This is the introduction...",
        methodology: "This is the methodology...",
        results: "This is the results section...",
        conclusion: "This is the conclusion...",
        references: "References..."
    },
    author_info: {
        name: "John Doe",
        email: "john.doe@example.com",
        affiliation: "University of Example",
        department: "Computer Science"
    }
};

try {
    const pdfBlob = await api.generatePDF(contentData);
    api.downloadPDF(pdfBlob, 'my_paper.pdf');
} catch (error) {
    console.error('Error generating PDF:', error);
}
*/

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IEEEPaperGeneratorAPI;
} 