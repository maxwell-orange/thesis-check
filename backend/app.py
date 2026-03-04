"""
Flask application for Thesis Check System
"""
import os
import uuid
import threading
from datetime import datetime
import io
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from config import Config
from utils.file_handler import save_uploaded_file, delete_file, get_file_path, format_file_size
from utils.llm_client import LLMClient, get_available_providers
from utils.pdf_generator import generate_pdf_report
from services.doc_parser import DocParser
from services.format_checker import FormatChecker
from services.ai_checker import AIChecker
from models.report import CheckReport, FormatCheckResult, AICheckResult, save_report, get_report

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=Config.CORS_ORIGINS)

# In-memory storage for API configurations
# In production, use proper session or database storage
api_config_storage = {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})


@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Get available LLM providers"""
    return jsonify({
        'code': 0,
        'data': get_available_providers()
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload thesis file"""
    if 'file' not in request.files:
        return jsonify({'code': 1, 'message': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 1, 'message': 'No file selected'}), 400

    try:
        file_info = save_uploaded_file(file)

        return jsonify({
            'code': 0,
            'message': 'File uploaded successfully',
            'data': {
                'file_id': file_info['file_id'],
                'filename': file_info['filename'],
                'file_size': file_info['file_size'],
                'file_size_formatted': format_file_size(file_info['file_size']),
                'upload_time': datetime.now().isoformat()
            }
        })

    except ValueError as e:
        return jsonify({'code': 1, 'message': str(e)}), 400
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Upload failed with error: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return jsonify({'code': 1, 'message': f'Upload failed: {str(e)}'}), 500


@app.route('/api/config', methods=['POST'])
def save_config():
    """Save API configuration"""
    data = request.json

    if not data:
        return jsonify({'code': 1, 'message': 'No configuration provided'}), 400

    provider = data.get('provider')
    api_key = data.get('api_key')
    model = data.get('model')
    enabled_checks = data.get('enabled_checks', ['format', 'language', 'content', 'citation'])

    if not provider or not api_key:
        return jsonify({'code': 1, 'message': 'Provider and API key are required'}), 400

    # Validate provider
    if provider not in Config.LLM_PROVIDERS:
        return jsonify({'code': 1, 'message': f'Unknown provider: {provider}'}), 400

    # Store configuration (in production, encrypt this)
    session_id = str(uuid.uuid4())
    api_config_storage[session_id] = {
        'provider': provider,
        'api_key': api_key,
        'model': model or Config.LLM_PROVIDERS[provider]['default_model'],
        'enabled_checks': enabled_checks
    }

    return jsonify({
        'code': 0,
        'message': 'Configuration saved successfully',
        'data': {
            'sessionId': session_id,
            'provider': provider,
            'model': api_config_storage[session_id]['model'],
            'enabled_checks': enabled_checks
        }
    })


@app.route('/api/config/<session_id>', methods=['GET'])
def get_config(session_id):
    """Get API configuration (without sensitive data)"""
    config = api_config_storage.get(session_id)

    if not config:
        return jsonify({'code': 1, 'message': 'Configuration not found'}), 404

    return jsonify({
        'code': 0,
        'data': {
            'provider': config['provider'],
            'model': config['model'],
            'enabled_checks': config['enabled_checks']
        }
    })


def perform_check(check_id, file_path, check_types, session_id):
    """Perform checks in background thread"""
    report = get_report(check_id)
    if not report:
        print(f"Report not found: {check_id}")
        return

    try:
        # Get API config if AI check is requested
        llm_client = None
        if 'ai' in check_types and session_id:
            config = api_config_storage.get(session_id)
            if config:
                try:
                    llm_client = LLMClient(
                        provider=config['provider'],
                        api_key=config['api_key'],
                        model=config['model']
                    )
                except Exception as e:
                    print(f"Failed to initialize LLM client: {e}")

        # Parse document
        print(f"[{check_id}] Parsing document...")
        parser = DocParser(file_path)
        parser.parse()
        print(f"[{check_id}] Document parsed. Found {len(parser.paragraphs)} paragraphs.")

        # Format check
        if 'format' in check_types:
            print(f"[{check_id}] Starting format check...")
            report.format_check.status = 'processing'
            save_report(report)

            format_checker = FormatChecker(parser)
            format_issues = format_checker.check_all()
            report.format_check.issues = [issue.to_dict() for issue in format_issues]
            report.format_check.status = 'completed'
            report.format_check.check_time = datetime.now().isoformat()
            save_report(report)
            print(f"[{check_id}] Format check completed. Found {len(format_issues)} issues.")

        # AI check
        if 'ai' in check_types and llm_client and session_id:
            print(f"[{check_id}] Starting AI check...")
            report.ai_check.status = 'processing'
            save_report(report)

            config = api_config_storage.get(session_id, {})
            enabled_checks = config.get('enabled_checks', ['language', 'content', 'citation'])
            ai_checker = AIChecker(parser, llm_client)

            # Use the enhanced method if references checking is enabled
            if 'references' in enabled_checks:
                ai_result = ai_checker.check_all_with_references(enabled_checks)
            else:
                ai_result = ai_checker.check_all(enabled_checks)

            report.ai_check.issues = ai_result.get('issues', [])
            if ai_result.get('summary'):
                report.ai_check.summary = ai_result['summary']
            report.ai_check.status = 'completed'
            report.ai_check.check_time = datetime.now().isoformat()
            save_report(report)
            print(f"[{check_id}] AI check completed. Found {len(ai_result.get('issues', []))} issues.")

        # Update report status
        report.status = 'completed'
        report.check_time = datetime.now().isoformat()
        report.update_total_issues()
        save_report(report)
        print(f"[{check_id}] Check completed. Total issues: {report.total_issues}")

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[{check_id}] Check failed with error: {str(e)}")
        print(f"[{check_id}] Traceback: {error_traceback}")

        report.status = 'failed'
        if 'format' in check_types:
            report.format_check.status = 'failed'
            report.format_check.error_message = str(e)
        if 'ai' in check_types:
            report.ai_check.status = 'failed'
            report.ai_check.error_message = str(e)
        save_report(report)


@app.route('/api/check', methods=['POST'])
def start_check():
    """Start thesis checking - returns immediately, processing continues in background"""
    data = request.json

    if not data:
        return jsonify({'code': 1, 'message': 'No data provided'}), 400

    file_id = data.get('file_id')
    session_id = data.get('session_id')
    check_types = data.get('check_types', ['format', 'ai'])

    if not file_id:
        return jsonify({'code': 1, 'message': 'File ID is required'}), 400

    # Get file path
    file_path = get_file_path(file_id)
    if not file_path:
        return jsonify({'code': 1, 'message': 'File not found'}), 404

    # Validate API config if AI check is requested
    if 'ai' in check_types:
        if not session_id:
            return jsonify({'code': 1, 'message': 'Session ID is required for AI check'}), 400

        config = api_config_storage.get(session_id)
        if not config:
            return jsonify({'code': 1, 'message': 'API configuration not found'}), 404

    # Create check report
    check_id = str(uuid.uuid4())
    report = CheckReport(
        check_id=check_id,
        file_id=file_id,
        file_name=os.path.basename(file_path),
        status='processing'
    )
    save_report(report)

    # Start background thread for checking
    thread = threading.Thread(
        target=perform_check,
        args=(check_id, file_path, check_types, session_id)
    )
    thread.daemon = True
    thread.start()

    print(f"[{check_id}] Check started in background thread")

    return jsonify({
        'code': 0,
        'message': 'Check started',
        'data': {
            'check_id': check_id,
            'status': 'processing',
            'estimated_time': 60
        }
    })


@app.route('/api/check/<check_id>/status', methods=['GET'])
def get_check_status(check_id):
    """Get check status"""
    report = get_report(check_id)

    if not report:
        return jsonify({'code': 1, 'message': 'Check not found'}), 404

    return jsonify({
        'code': 0,
        'data': {
            'check_id': check_id,
            'status': report.status,
            'format_check_status': report.format_check.status,
            'ai_check_status': report.ai_check.status
        }
    })


@app.route('/api/check/<check_id>/report', methods=['GET'])
def get_check_report(check_id):
    """Get check report"""
    report = get_report(check_id)

    if not report:
        return jsonify({'code': 1, 'message': 'Report not found'}), 404

    return jsonify({
        'code': 0,
        'data': report.to_dict()
    })


@app.route('/api/check/<check_id>/report/pdf', methods=['GET'])
def download_pdf_report(check_id):
    """Download check report as PDF"""
    report = get_report(check_id)

    if not report:
        return jsonify({'code': 1, 'message': 'Report not found'}), 404

    # Check if report is completed
    if report.status != 'completed':
        return jsonify({
            'code': 1,
            'message': 'Report is not ready yet. Please wait for the check to complete.'
        }), 400

    try:
        # Generate PDF
        report_data = report.to_dict()
        pdf_bytes = generate_pdf_report(report_data)

        # Create filename
        safe_filename = report.file_name.replace('.docx', '').replace('.doc', '')
        download_name = f'thesis_check_report_{safe_filename}_{check_id[:8]}.pdf'

        # Return PDF file
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"PDF generation failed: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return jsonify({
            'code': 1,
            'message': f'PDF generation failed: {str(e)}'
        }), 500


@app.route('/api/upload/<file_id>', methods=['DELETE'])
def delete_upload(file_id):
    """Delete uploaded file"""
    if delete_file(file_id):
        return jsonify({
            'code': 0,
            'message': 'File deleted successfully'
        })
    else:
        return jsonify({
            'code': 1,
            'message': 'File not found'
        }), 404


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'code': 1,
        'message': f'File too large. Maximum size is {format_file_size(Config.MAX_CONTENT_LENGTH)}'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({
        'code': 1,
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
