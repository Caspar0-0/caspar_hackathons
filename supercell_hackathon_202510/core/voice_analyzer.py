"""
Voice Analyzer Module
Extracts voice features for character matching.
"""
import numpy as np
import librosa


class VoiceAnalyzer:
    """Analyzes voice recordings and extracts features."""
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the voice analyzer.
        
        Args:
            sample_rate: Sample rate of the audio
        """
        self.sample_rate = sample_rate
    
    def extract_features(self, audio_data):
        """
        Extract voice features from audio data.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dictionary of voice features
        """
        # Ensure audio is not empty
        if len(audio_data) == 0 or np.all(audio_data == 0):
            raise ValueError("Audio data is empty or silent")
        
        features = {}
        
        # 1. Pitch (fundamental frequency)
        pitches, magnitudes = librosa.piptrack(
            y=audio_data,
            sr=self.sample_rate,
            fmin=50,
            fmax=500
        )
        # Get the pitch with highest magnitude at each frame
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if pitch_values:
            features['mean_pitch'] = np.mean(pitch_values)
            features['pitch_variance'] = np.var(pitch_values)
        else:
            features['mean_pitch'] = 150  # Default neutral pitch
            features['pitch_variance'] = 100
        
        # 2. Energy/Volume
        rms = librosa.feature.rms(y=audio_data)[0]
        features['mean_energy'] = np.mean(rms)
        features['energy_variance'] = np.var(rms)
        
        # 3. Tempo (speaking rate)
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
        features['tempo'] = tempo
        
        # 4. Spectral characteristics
        spectral_centroids = librosa.feature.spectral_centroid(
            y=audio_data,
            sr=self.sample_rate
        )[0]
        features['spectral_centroid'] = np.mean(spectral_centroids)
        
        # 5. Zero crossing rate (roughness/smoothness)
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        features['zero_crossing_rate'] = np.mean(zcr)
        
        # 6. MFCC (Mel-frequency cepstral coefficients) - voice timbre
        mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
        for i in range(5):  # Use first 5 MFCCs
            features[f'mfcc_{i}'] = np.mean(mfccs[i])
        
        return features
    
    def categorize_voice(self, features):
        """
        Categorize voice into descriptive terms.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Dictionary of voice characteristics
        """
        characteristics = {}
        
        # Pitch categories
        pitch = features['mean_pitch']
        if pitch < 120:
            characteristics['pitch_category'] = 'very_low'
            characteristics['pitch_description'] = 'Deep, bass-like'
        elif pitch < 160:
            characteristics['pitch_category'] = 'low'
            characteristics['pitch_description'] = 'Low, masculine'
        elif pitch < 200:
            characteristics['pitch_category'] = 'medium'
            characteristics['pitch_description'] = 'Neutral, balanced'
        elif pitch < 250:
            characteristics['pitch_category'] = 'high'
            characteristics['pitch_description'] = 'High, feminine'
        else:
            characteristics['pitch_category'] = 'very_high'
            characteristics['pitch_description'] = 'Very high, childlike'
        
        # Energy categories
        energy = features['mean_energy']
        if energy < 0.01:
            characteristics['energy_category'] = 'soft'
            characteristics['energy_description'] = 'Quiet, gentle'
        elif energy < 0.05:
            characteristics['energy_category'] = 'moderate'
            characteristics['energy_description'] = 'Moderate, calm'
        else:
            characteristics['energy_category'] = 'loud'
            characteristics['energy_description'] = 'Loud, energetic'
        
        # Tempo categories
        tempo = features['tempo']
        if tempo < 80:
            characteristics['tempo_category'] = 'slow'
            characteristics['tempo_description'] = 'Slow, deliberate'
        elif tempo < 120:
            characteristics['tempo_category'] = 'moderate'
            characteristics['tempo_description'] = 'Moderate pace'
        else:
            characteristics['tempo_category'] = 'fast'
            characteristics['tempo_description'] = 'Fast, energetic'
        
        return characteristics

