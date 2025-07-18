from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from io import BytesIO

# Import our modules
from modules.pdf_handler import PDFHandler
from modules.content_generator import ContentGenerator
from modules.pdf_generator import PDFGenerator
from modules.api_tracker import APITracker
from modules.validators import InputValidator
from config import get_config

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config.from_object(get_config())
CORS(app, origins=app.config['CORS_ORIGINS'])

# Configure Google API
import google.generativeai as genai
genai.configure(api_key=app.config['GOOGLE_API_KEY'])

# Initialize modules
pdf_handler = PDFHandler(api_key=app.config['GOOGLE_API_KEY'])
content_generator = ContentGenerator(api_key=app.config['GOOGLE_API_KEY'])
pdf_generator = PDFGenerator()
api_tracker = APITracker()
input_validator = InputValidator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/docs', methods=['GET'])
def swagger_ui():
    """Serve Swagger UI documentation"""
    return send_from_directory('static', 'swagger-ui.html')

@app.route('/docs/swagger.json', methods=['GET'])
def swagger_json():
    """Serve Swagger JSON specification"""
    return send_from_directory('static', 'swagger.json')

@app.route('/api-docs', methods=['GET'])
def api_docs_redirect():
    """Redirect to Swagger UI"""
    return jsonify({
        'message': 'API Documentation',
        'swagger_ui': '/docs',
        'swagger_json': '/docs/swagger.json',
        'endpoints': {
            'health': '/health',
            'generate_paper': '/api/generate-paper',
            'upload_pdf': '/api/upload-pdf',
            'generate_pdf': '/api/generate-pdf',
            'stats': '/api/stats',
            'reset_stats': '/api/reset-stats',
            'validate_inputs': '/api/validate-inputs'
        }
    })

@app.route('/', methods=['GET'])
def index():
    """Serve the main API documentation page"""
    return send_from_directory('static', 'index.html')

@app.route('/api/generate-paper', methods=['POST'])
def generate_paper():
    """Main endpoint to generate IEEE conference paper"""
    try:
        # Track API call
        api_tracker.increment_call('generate_paper')
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract required fields
        title = data.get('title', '').strip()
        research_field = data.get('research_field', '').strip()
        methodology = data.get('methodology', '').strip()
        expected_results = data.get('expected_results', '').strip()
        additional_context = data.get('additional_context', '').strip()
        custom_parameters = data.get('custom_parameters', {})
        
        # Validate inputs
        validation_result = input_validator.validate_paper_inputs(
            title, research_field, methodology, expected_results
        )
        
        if not validation_result['valid']:
            return jsonify({
                'error': 'Validation failed',
                'errors': validation_result['errors'],
                'warnings': validation_result['warnings']
            }), 400
        
        # Generate content
        generated_content = content_generator.generate_paper_content(
            title=title,
            research_field=research_field,
            methodology=methodology,
            expected_results=expected_results,
            additional_context=additional_context,
            custom_parameters=custom_parameters
        )
        
        if not generated_content:
            return jsonify({'error': 'Failed to generate content'}), 500
        
        # Parse content into sections
        content_sections = content_generator.parse_generated_content(generated_content)
        content_sections['title'] = title  # Use original title
        
        # Validate equations in the generated content
        equation_validation = content_generator.validate_equations_in_content(generated_content)
        
        return jsonify({
            'success': True,
            'content': generated_content,
            'sections': content_sections,
            'word_count': len(generated_content.split()),
            'character_count': len(generated_content),
            'equation_validation': equation_validation,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload and analyze PDF file"""
    try:
        # Track API call
        api_tracker.increment_call('upload_pdf')
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Extract text from PDF
        pdf_text = pdf_handler.extract_text_from_pdf(file)
        if not pdf_text:
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Analyze PDF content
        analysis_result = pdf_handler.analyze_pdf_content(pdf_text)
        
        return jsonify({
            'success': True,
            'extracted_text': pdf_text,
            'analysis': analysis_result,
            'text_length': len(pdf_text),
            'uploaded_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF from content"""
    try:
        # Track API call
        api_tracker.increment_call('generate_pdf')
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content_sections = data.get('sections', {})
        author_info = data.get('author_info', {})
        
        if not content_sections:
            return jsonify({'error': 'No content sections provided'}), 400
        
        # Generate PDF
        pdf_buffer = pdf_generator.create_ieee_pdf(
            content_sections, 
            "generated_paper.pdf", 
            author_info
        )
        
        # Return PDF as file
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='generated_paper.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_api_stats():
    """Get API usage statistics"""
    try:
        stats = api_tracker.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-stats', methods=['POST'])
def reset_api_stats():
    """Reset API usage statistics"""
    try:
        success = api_tracker.reset_stats()
        if success:
            return jsonify({'success': True, 'message': 'Statistics reset successfully'})
        else:
            return jsonify({'error': 'Failed to reset statistics'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-equations', methods=['POST'])
def validate_equations():
    """Validate equations for proper mathematical notation"""
    try:
        # Track API call
        api_tracker.increment_call('validate_equations')
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        # Validate equations in the content
        validation_results = content_generator.validate_equations_in_content(content)
        
        # Format content with proper mathematical notation
        formatted_content = content_generator.format_content_with_math(content)
        
        return jsonify({
            'success': True,
            'original_content': content,
            'formatted_content': formatted_content,
            'validation_results': validation_results,
            'has_issues': len([r for r in validation_results if r['issues']]) > 0,
            'has_warnings': len([r for r in validation_results if r['warnings']]) > 0,
            'validated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-inputs', methods=['POST'])
def validate_inputs():
    """Validate paper inputs"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        title = data.get('title', '').strip()
        research_field = data.get('research_field', '').strip()
        methodology = data.get('methodology', '').strip()
        expected_results = data.get('expected_results', '').strip()
        
        validation_result = input_validator.validate_paper_inputs(
            title, research_field, methodology, expected_results
        )
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 
