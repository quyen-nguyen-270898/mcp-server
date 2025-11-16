import os
import json
import subprocess
from flask import Flask, request, jsonify
from functools import wraps
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5000))
API_KEY = os.environ.get('API_KEY', '')  # Optional: Add API key for security

def require_api_key(f):
    """Decorator to check API key if set"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if API_KEY and request.args.get('key') != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_soundcloud_stream(url):
    """
    Extract audio stream URL from SoundCloud link using yt-dlp
    
    Args:
        url (str): SoundCloud URL
        
    Returns:
        dict: Contains stream_url and metadata or error message
    """
    try:
        # Use yt-dlp to extract stream information
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=m4a]/best',  # Get best audio format
            '-j',  # Output as JSON
            '--no-warnings',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logger.error(f"yt-dlp error: {result.stderr}")
            return {
                'success': False,
                'error': 'Failed to extract stream URL',
                'details': result.stderr
            }
        
        data = json.loads(result.stdout)
        
        # Extract relevant information
        response = {
            'success': True,
            'stream_url': data.get('url'),
            'title': data.get('title'),
            'duration': data.get('duration'),
            'artist': data.get('uploader'),
            'thumbnail': data.get('thumbnail'),
            'ext': data.get('ext'),
        }
        
        return response
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return {
            'success': False,
            'error': 'Invalid response from stream extractor'
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Request timeout - URL extraction took too long'
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'SoundCloud Stream URL Extractor',
        'version': '1.0',
        'usage': {
            'endpoint': '/stream',
            'method': 'POST',
            'body': {
                'url': 'https://soundcloud.com/...'
            },
            'example': 'curl -X POST http://localhost:5000/stream -H "Content-Type: application/json" -d \'{"url":"https://soundcloud.com/..."}\''
        }
    })

@app.route('/stream', methods=['POST'])
@require_api_key
def get_stream():
    """
    Get audio stream URL from SoundCloud
    
    Request body:
    {
        "url": "https://soundcloud.com/user/track-name"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing URL in request body'}), 400
        
        url = data['url'].strip()
        
        # Validate URL
        if 'soundcloud.com' not in url:
            return jsonify({'error': 'URL must be a valid SoundCloud link'}), 400
        
        logger.info(f"Processing SoundCloud URL: {url}")
        
        result = get_soundcloud_stream(url)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in /stream endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check for Render deployment"""
    return jsonify({'status': 'ok'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False
    )
