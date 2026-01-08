// Voice Character Matcher - Web Recorder
let mediaRecorder;
let audioChunks = [];
let audioBlob;
let recordingTimeout;

// DOM Elements
const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const recordingStatus = document.getElementById('recordingStatus');
const audioPlayer = document.getElementById('audioPlayer');
const audioPlayback = document.getElementById('audioPlayback');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');

// Start Recording
recordBtn.addEventListener('click', async () => {
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                channelCount: 1,
                sampleRate: 44100
            }
        });
        
        // Initialize MediaRecorder with best available format
        let mimeType = 'audio/webm';
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
            mimeType = 'audio/ogg;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/wav')) {
            mimeType = 'audio/wav';
        }
        
        mediaRecorder = new MediaRecorder(stream, { mimeType });
        
        audioChunks = [];
        
        // Collect audio data
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        // Handle recording stop
        mediaRecorder.onstop = () => {
            // Create audio blob with the same mime type
            audioBlob = new Blob(audioChunks, { type: mimeType });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            audioPlayer.style.display = 'block';
            recordingStatus.textContent = '✅ Recording complete! Listen and click Analyze.';
            recordingStatus.style.background = '#d1fae5';
            recordingStatus.style.color = '#065f46';
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        // Start recording
        mediaRecorder.start();
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        recordingStatus.textContent = '🔴 Recording... Speak now!';
        recordingStatus.style.background = '#fee2e2';
        recordingStatus.style.color = '#991b1b';
        
        // Auto-stop after 5 seconds
        recordingTimeout = setTimeout(() => {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                stopBtn.disabled = true;
                recordBtn.disabled = false;
            }
        }, 5000);
        
    } catch (error) {
        console.error('Microphone error:', error);
        recordingStatus.textContent = '❌ Microphone access denied. Please allow microphone access and try again.';
        recordingStatus.style.background = '#fee2e2';
        recordingStatus.style.color = '#991b1b';
    }
});

// Manual Stop
stopBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        clearTimeout(recordingTimeout);
        mediaRecorder.stop();
        stopBtn.disabled = true;
        recordBtn.disabled = false;
    }
});

// Analyze Voice
analyzeBtn.addEventListener('click', async () => {
    if (!audioBlob) {
        alert('Please record your voice first!');
        return;
    }
    
    // Show loading
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    window.scrollTo({ top: loadingSection.offsetTop - 100, behavior: 'smooth' });
    
    try {
        // Convert blob to base64
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        
        reader.onloadend = async () => {
            const base64Audio = reader.result;
            
            // Send to backend
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ audio: base64Audio })
            });
            
            const data = await response.json();
            
            loadingSection.style.display = 'none';
            
            if (data.success) {
                displayResults(data);
                resultsSection.style.display = 'block';
                window.scrollTo({ top: resultsSection.offsetTop - 100, behavior: 'smooth' });
            } else {
                alert('Error analyzing voice: ' + (data.error || 'Unknown error'));
            }
        };
        
    } catch (error) {
        loadingSection.style.display = 'none';
        console.error('Analysis error:', error);
        alert('Error analyzing voice. Please try again.');
    }
});

// Try Again
tryAgainBtn.addEventListener('click', () => {
    resultsSection.style.display = 'none';
    audioPlayer.style.display = 'none';
    recordingStatus.textContent = '';
    audioBlob = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Display Results
function displayResults(data) {
    // Voice Analysis
    const voiceAnalysis = document.getElementById('voiceAnalysis');
    voiceAnalysis.innerHTML = `
        <h3>📊 Your Voice Analysis</h3>
        <div class="analysis-cards">
            <div class="card">
                <div class="card-title">🎵 Pitch</div>
                <div class="card-value">${data.voice_analysis.pitch.toFixed(1)}</div>
                <div class="card-desc">Hz - ${data.voice_analysis.pitch_description}</div>
            </div>
            <div class="card">
                <div class="card-title">🔊 Energy</div>
                <div class="card-value">${(data.voice_analysis.energy * 100).toFixed(1)}</div>
                <div class="card-desc">${data.voice_analysis.energy_description}</div>
            </div>
            <div class="card">
                <div class="card-title">⏱️ Tempo</div>
                <div class="card-value">${data.voice_analysis.tempo.toFixed(0)}</div>
                <div class="card-desc">BPM - ${data.voice_analysis.tempo_description}</div>
            </div>
        </div>
    `;
    
    // Best Match
    const bestMatch = data.matches[0];
    const bestMatchEl = document.getElementById('bestMatch');
    
    // Use proxy endpoint to avoid CORS issues
    const imageHtml = bestMatch.image_url ? 
        `<img src="/api/image/${encodeURIComponent(bestMatch.character)}" alt="${bestMatch.character}" 
              onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
         <div class="emoji" style="display: none;">${bestMatch.emoji}</div>` :
        `<div class="emoji">${bestMatch.emoji}</div>`;
    
    bestMatchEl.innerHTML = `
        <h3>🏆 Your Best Match!</h3>
        <div class="best-match-card">
            <div class="character-image">
                ${imageHtml}
            </div>
            <div class="character-info">
                <h4>${bestMatch.emoji} ${bestMatch.character}</h4>
                <div class="character-game">${bestMatch.game}</div>
                <div class="character-description">${bestMatch.description}</div>
                <div class="character-personality">💭 ${bestMatch.personality}</div>
                
                <div class="match-score">
                    <div class="score-value">${bestMatch.score.toFixed(1)}%</div>
                    <div class="score-breakdown">
                        <div class="score-item">
                            <div class="score-label">🎵 Pitch</div>
                            <div class="score-percent">${bestMatch.breakdown.pitch_match.toFixed(0)}%</div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">🔊 Energy</div>
                            <div class="score-percent">${bestMatch.breakdown.energy_match.toFixed(0)}%</div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">⏱️ Tempo</div>
                            <div class="score-percent">${bestMatch.breakdown.tempo_match.toFixed(0)}%</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // All Matches
    const allMatchesEl = document.getElementById('allMatches');
    const matchesHtml = data.matches.slice(1).map((match, index) => {
        // Use proxy endpoint to avoid CORS issues
        const matchImageHtml = match.image_url ?
            `<img src="/api/image/${encodeURIComponent(match.character)}" alt="${match.character}"
                  onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
             <div class="emoji" style="display: none;">${match.emoji}</div>` :
            `<div class="emoji">${match.emoji}</div>`;
        
        return `
            <div class="match-card">
                <div class="match-rank">${index + 2}</div>
                <div class="match-card-image">
                    ${matchImageHtml}
                </div>
                <h4>${match.character}</h4>
                <div class="match-card-game">${match.game}</div>
                <div class="match-card-description">${match.description}</div>
                <div class="match-card-score">${match.score.toFixed(1)}%</div>
            </div>
        `;
    }).join('');
    
    allMatchesEl.innerHTML = `
        <h3>🎯 Other Top Matches</h3>
        <div class="matches-grid">
            ${matchesHtml}
        </div>
    `;
}

