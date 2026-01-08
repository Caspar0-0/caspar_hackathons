# 🎮 Voice Character Matcher - Web Version 🎤

**A beautiful web interface to match your voice with 45 Supercell gaming characters!**

Record your voice in the browser and discover which Brawl Stars, Clash Royale, or Clash of Clans character you sound like using advanced voice analysis.

---

## ✨ Features

- 🎙️ **Browser-Based Recording** - No microphone software needed
- 🔬 **Real-Time Analysis** - Instant voice feature extraction
- 🎯 **45 Characters** - All Supercell characters with real images
- 📊 **Visual Results** - Beautiful cards showing your voice analysis
- 🏆 **Best Match** - Detailed breakdown of your top match
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 💾 **No Database Required** - All processing happens in memory

---

## 🚀 Quick Start

### 0. Install System Dependencies

Make sure ffmpeg is installed (required for audio processing):

```bash
brew install ffmpeg
```

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 3. Open in Browser

Visit **http://localhost:5000** in your web browser

---

## 📁 Project Structure

```
supercell_hackerthon_201510/
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── start_server.sh             # Server startup script
├── core/                       # Core voice analysis modules
│   ├── __init__.py
│   ├── voice_analyzer.py       # Audio feature extraction
│   ├── character_matcher.py    # Matching algorithm
│   └── character_database.py   # 45 character profiles
├── templates/
│   └── index.html             # Main web page
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   ├── js/
│   │   └── recorder.js         # Audio recording & UI logic
│   └── character_images/       # Character image assets
└── README.md                   # This file
```

---

## 🎤 How It Works

### 1. **Voice Recording**
- Browser captures audio using Web Audio API
- 5-second recording (can be stopped early)
- Audio stored as WebM format in browser

### 2. **Voice Analysis**
The Python backend analyzes:
- **Pitch** - Fundamental frequency (Hz)
- **Energy** - Volume/loudness (RMS)
- **Tempo** - Speaking rate (BPM)
- **Spectral Centroid** - Voice brightness

### 3. **Character Matching**
- Compares your voice to 45 character profiles
- Weighted algorithm:
  - 50% pitch similarity
  - 30% energy match
  - 20% tempo match
- Returns top 5 matches with detailed breakdowns

### 4. **Results Display**
- Voice analysis cards with your features
- Best match with character image and details
- Top 5 matches in a beautiful grid layout

---

## 🎮 Supported Characters

### Brawl Stars (25 Characters)
Shelly, Colt, Bull, Poco, Nita, Crow, Spike, Leon, Mortis, El Primo, Dynamike, Barley, Jessie, Brock, Piper, Pam, Frank, Bibi, 8-Bit, Emz, Amber, Edgar, Colette, Sandy, Surge

### Clash Royale (9 Characters)
Knight, Princess, Goblin, Musketeer, Mini P.E.K.K.A, Ice Wizard, Mega Knight, Electro Wizard, Bandit

### Clash of Clans (11 Characters)
Barbarian, Archer, Giant, Wizard, P.E.K.K.A, Hog Rider, Valkyrie, Dragon, Witch, Golem, Miner

**Total: 45 characters with 100% real images!**

---

## 🔧 Technical Stack

### Backend
- **Flask** - Web framework
- **librosa** - Audio analysis
- **NumPy** - Numerical computing

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern styling with gradients
- **JavaScript (ES6+)** - Recording & UI logic
- **Web Audio API** - Browser audio capture

### Audio Processing
- **Sample Rate**: 44.1 kHz
- **Channels**: Mono (1 channel)
- **Format**: WebM (browser) → WAV (backend)
- **Duration**: 5 seconds (default)

---

## 🎨 Character Voice Line Examples

The web interface shows these example lines to inspire users:

- **"Time to brawl!"** (Shelly)
- **"Too pretty for pain!"** (Colt)
- **"El Primo is here!"** (El Primo)
- **"I have NO idea what's going on!"** (Poco)
- **"Let's rock!"** (Mortis)
- **"For the clan!"** (Barbarian)

---

## 🌐 API Endpoints

### `GET /`
Returns the main web interface

### `POST /api/analyze`
Analyzes voice recording

**Request:**
```json
{
  "audio": "data:audio/webm;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "voice_analysis": {
    "pitch": 165.3,
    "pitch_description": "Neutral, balanced",
    "energy": 0.0324,
    "energy_description": "Moderate, calm",
    "tempo": 142.8,
    "tempo_description": "Fast, energetic",
    "spectral_centroid": 2341.5
  },
  "matches": [
    {
      "character": "Colt",
      "game": "Brawl Stars",
      "emoji": "😎",
      "description": "Cool and cocky sharpshooter",
      "personality": "Cocky, cool, flashy",
      "score": 87.3,
      "image_url": "https://...",
      "breakdown": {
        "pitch_match": 92.5,
        "energy_match": 80.0,
        "tempo_match": 100.0
      }
    }
    // ... 4 more matches
  ]
}
```

### `GET /api/characters`
Returns all 45 characters

---

## 💡 Tips for Best Results

1. **Good Audio Quality**
   - Use in a quiet environment
   - Speak clearly into your microphone
   - Hold microphone 6-12 inches from your mouth

2. **Try Different Styles**
   - Imitate character voice lines
   - Try different energy levels
   - Vary your pitch and tempo

3. **Browser Compatibility**
   - Works best in Chrome, Firefox, Safari (modern versions)
   - Requires HTTPS for microphone access (except localhost)
   - Enable microphone permissions when prompted

---

## 🐛 Troubleshooting

### Microphone Not Working
- **Check permissions**: Browser needs microphone access
- **HTTPS required**: Use localhost for development
- **Test microphone**: Try in browser settings first

### Analysis Errors
- **Speak louder**: Silent audio won't analyze
- **Minimum duration**: Record at least 2 seconds
- **Check console**: Look for error messages in browser DevTools

### Server Issues
- **Port in use**: Change port in `app.py` if 5000 is taken
- **Dependencies**: Make sure all requirements are installed
- **Python version**: Requires Python 3.8+

---

## 📊 Performance

- **Recording**: ~5 seconds
- **Upload**: < 1 second (local network)
- **Analysis**: 2-5 seconds (depends on CPU)
- **Total time**: ~10 seconds per analysis

---

## 🔒 Privacy

- ✅ All processing happens on your server
- ✅ No audio uploaded to external services
- ✅ No data stored after analysis
- ✅ Recordings deleted after browser refresh

---


## 📚 Related Documentation

- **Character Database**: `core/character_database.py`
- **API Documentation**: See "API Endpoints" section above

---

## 🙏 Credits

- **librosa** - Audio analysis library
- **Flask** - Web framework
- **Supercell** - Game artwork and characters
- **noff.gg** - Brawl Stars & Clash Royale images
- **Fandom Wiki** - Clash of Clans images

---

## 📝 License

Part of the Supercell Hackathon 2015-10 project.

---

## 🎉 Have Fun!

Discover which Supercell character you sound like and share your results with friends!

**Built with ❤️ for Supercell gaming fans**

---

**Status**: ✅ Production Ready  
**Last Updated**: October 26, 2025  
**Version**: 1.0.0

