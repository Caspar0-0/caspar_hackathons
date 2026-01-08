#!/usr/bin/env python3
"""
Flask Web Application for Voice Character Matcher
"""
import sys
import os

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from flask import Flask, render_template, request, jsonify
import numpy as np
import librosa
import io
import base64
from core import VoiceAnalyzer, CharacterMatcher

app = Flask(__name__)

# Initialize components
analyzer = VoiceAnalyzer()
matcher = CharacterMatcher()


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_voice():
    """
    API endpoint to analyze voice recording.
    Expects audio data as base64-encoded audio file.
    """
    try:
        # Get audio data from request
        data = request.get_json()
        audio_base64 = data.get('audio')
        
        if not audio_base64:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64.split(',')[1])
        
        # Save to temporary file (librosa handles various formats better from file)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name
        
        try:
            # Load audio using librosa (it will handle webm via ffmpeg)
            audio_data, sr = librosa.load(temp_path, sr=44100, mono=True)
        finally:
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        # Analyze voice
        features = analyzer.extract_features(audio_data)
        characteristics = analyzer.categorize_voice(features)
        
        # Match to characters
        matches = matcher.get_top_matches(features, characteristics, top_n=5)
        
        # Prepare response
        response = {
            'success': True,
            'voice_analysis': {
                'pitch': float(features['mean_pitch']),
                'pitch_description': characteristics['pitch_description'],
                'energy': float(features['mean_energy']),
                'energy_description': characteristics['energy_description'],
                'tempo': float(features['tempo']),
                'tempo_description': characteristics['tempo_description'],
                'spectral_centroid': float(features['spectral_centroid'])
            },
            'matches': [
                {
                    'character': m['character'],
                    'game': m['game'],
                    'emoji': m['emoji'],
                    'description': m['description'],
                    'personality': m['personality'],
                    'score': float(m['score']),
                    'image_url': m['image_url'],
                    'breakdown': {
                        'pitch_match': float(m['breakdown']['pitch_match']),
                        'energy_match': float(m['breakdown']['energy_match']),
                        'tempo_match': float(m['breakdown']['tempo_match'])
                    }
                }
                for m in matches
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/characters')
def get_characters():
    """Get all character data for display."""
    db = matcher.db
    characters = db.get_all_characters()
    
    char_list = [
        {
            'name': name,
            'game': data['game'],
            'emoji': data['emoji'],
            'description': data['description'],
            'image_url': data['image_url']
        }
        for name, data in characters.items()
    ]
    
    return jsonify({'characters': char_list})


@app.route('/api/image/<path:character_name>')
def get_character_image(character_name):
    """
    Proxy endpoint to serve character images.
    Downloads image from external URL and serves it to avoid CORS issues.
    """
    import urllib.request
    import os
    from flask import send_file
    
    # Get character data
    db = matcher.db
    char_data = db.get_character(character_name)
    
    if not char_data or not char_data.get('image_url'):
        return jsonify({'error': 'Character not found or no image'}), 404
    
    # Create cache directory
    cache_dir = os.path.join(os.path.dirname(__file__), 'static', 'character_images')
    os.makedirs(cache_dir, exist_ok=True)
    
    # Determine file extension from URL
    image_url = char_data['image_url']
    ext = '.webp' if '.webp' in image_url else '.png'
    cache_file = os.path.join(cache_dir, f"{character_name.replace(' ', '_')}{ext}")
    
    # Download and cache if not exists
    if not os.path.exists(cache_file):
        try:
            urllib.request.urlretrieve(image_url, cache_file)
        except Exception as e:
            print(f"Error downloading image for {character_name}: {e}")
            return jsonify({'error': 'Image download failed'}), 500
    
    # Serve the cached image
    return send_file(cache_file, mimetype=f'image/{ext[1:]}')


if __name__ == '__main__':
    print("\n🎮 Voice Character Matcher Web Server 🎤")
    print("=" * 60)
    print("✅ Server starting on http://localhost:5000")
    print("✅ Open your browser and visit: http://localhost:5000")
    print("=" * 60 + "\n")
    
    # Get debug mode from environment variable (default: False for production)
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

