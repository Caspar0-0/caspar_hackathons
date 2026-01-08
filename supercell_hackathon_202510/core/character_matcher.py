"""
Character Matcher Module
Matches voice features to Supercell characters.
"""
import numpy as np
from character_database import CharacterDatabase


class CharacterMatcher:
    """Matches voice characteristics to Supercell game characters."""
    
    def __init__(self):
        """Initialize the character matcher."""
        self.db = CharacterDatabase()
    
    def _calculate_pitch_similarity(self, user_pitch, character_pitch_range):
        """
        Calculate how similar the user's pitch is to a character's pitch range.
        
        Args:
            user_pitch: User's mean pitch
            character_pitch_range: Tuple of (min, max) pitch for character
            
        Returns:
            Similarity score (0-100)
        """
        min_pitch, max_pitch = character_pitch_range
        mid_pitch = (min_pitch + max_pitch) / 2
        
        # Calculate distance from character's typical pitch
        distance = abs(user_pitch - mid_pitch)
        
        # Normalize to 0-100 scale (closer = higher score)
        # Maximum expected distance is about 150 Hz
        max_distance = 150
        similarity = max(0, 100 - (distance / max_distance * 100))
        
        return similarity
    
    def _calculate_energy_similarity(self, user_energy, character_energy):
        """
        Calculate similarity in energy levels.
        
        Args:
            user_energy: User's energy category ('soft', 'moderate', 'loud')
            character_energy: Character's energy level
            
        Returns:
            Similarity score (0-100)
        """
        if user_energy == character_energy:
            return 100
        elif (user_energy == 'moderate' and character_energy in ['soft', 'loud']) or \
             (character_energy == 'moderate' and user_energy in ['soft', 'loud']):
            return 60
        else:
            return 30
    
    def _calculate_tempo_similarity(self, user_tempo, character_tempo):
        """
        Calculate similarity in tempo/pace.
        
        Args:
            user_tempo: User's tempo category ('slow', 'moderate', 'fast')
            character_tempo: Character's tempo
            
        Returns:
            Similarity score (0-100)
        """
        if user_tempo == character_tempo:
            return 100
        elif (user_tempo == 'moderate' and character_tempo in ['slow', 'fast']) or \
             (character_tempo == 'moderate' and user_tempo in ['slow', 'fast']):
            return 60
        else:
            return 30
    
    def match_character(self, voice_features, voice_characteristics):
        """
        Find the best matching Supercell character based on voice.
        
        Args:
            voice_features: Dictionary of extracted voice features
            voice_characteristics: Dictionary of voice characteristics
            
        Returns:
            List of tuples (character_name, character_info, match_score)
        """
        matches = []
        
        for char_name, char_data in self.db.get_all_characters().items():
            profile = char_data['voice_profile']
            
            # Calculate individual similarities
            pitch_sim = self._calculate_pitch_similarity(
                voice_features['mean_pitch'],
                profile['pitch_range']
            )
            
            energy_sim = self._calculate_energy_similarity(
                voice_characteristics['energy_category'],
                profile['energy_level']
            )
            
            tempo_sim = self._calculate_tempo_similarity(
                voice_characteristics['tempo_category'],
                profile['tempo']
            )
            
            # Weighted average (pitch is most important)
            total_score = (
                pitch_sim * 0.5 +
                energy_sim * 0.3 +
                tempo_sim * 0.2
            )
            
            match_info = {
                'character': char_name,
                'game': char_data['game'],
                'description': char_data['description'],
                'personality': profile['personality'],
                'emoji': char_data.get('emoji', '🎮'),
                'ascii_art': char_data.get('ascii_art', ''),
                'image_url': char_data.get('image_url', ''),
                'score': round(total_score, 2),
                'breakdown': {
                    'pitch_match': round(pitch_sim, 2),
                    'energy_match': round(energy_sim, 2),
                    'tempo_match': round(tempo_sim, 2)
                }
            }
            
            matches.append(match_info)
        
        # Sort by score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def get_top_matches(self, voice_features, voice_characteristics, top_n=5):
        """
        Get the top N character matches.
        
        Args:
            voice_features: Dictionary of extracted voice features
            voice_characteristics: Dictionary of voice characteristics
            top_n: Number of top matches to return
            
        Returns:
            List of top N matches
        """
        all_matches = self.match_character(voice_features, voice_characteristics)
        return all_matches[:top_n]

