"""
Supercell Character Database
Contains voice characteristics for various Supercell game characters.
"""


class CharacterDatabase:
    """Database of Supercell gaming characters with voice characteristics."""
    
    def __init__(self):
        """Initialize character database with voice profiles."""
        self.characters = self._create_character_profiles()
    
    def _create_character_profiles(self):
        """
        Create voice profiles for Supercell characters.
        
        Characters from:
        - Clash of Clans
        - Clash Royale
        - Brawl Stars
        """
        return {
            # Clash of Clans / Clash Royale Characters
            'Barbarian': {
                'game': 'Clash of Clans',
                'description': 'Fierce warrior with a loud battle cry',
                'emoji': '🗡️',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/9/9b/Barbarian-xx.png/revision/latest?cb=20170703143506',
                'voice_profile': {
                    'pitch_range': (90, 140),  # Low, masculine
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Aggressive, loud, warrior-like'
                }
            },
            'Archer': {
                'game': 'Clash of Clans',
                'description': 'Quick and precise ranged attacker',
                'emoji': '🏹',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/2/24/Archer_Render2.png/revision/latest?cb=20150427011816',
                'voice_profile': {
                    'pitch_range': (200, 270),  # High, feminine
                    'energy_level': 'moderate',
                    'tempo': 'fast',
                    'personality': 'Quick-witted, sharp, focused'
                }
            },
            'Giant': {
                'game': 'Clash of Clans',
                'description': 'Slow but powerful heavy unit',
                'emoji': '👹',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/9/97/Giant_Portrait.png/revision/latest?cb=20170331014632',
                'voice_profile': {
                    'pitch_range': (70, 110),  # Very low
                    'energy_level': 'loud',
                    'tempo': 'slow',
                    'personality': 'Powerful, slow, intimidating'
                }
            },
            'Wizard': {
                'game': 'Clash of Clans',
                'description': 'Magical spellcaster with mystical powers',
                'emoji': '🧙',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/2/28/Wizard_action_figure.jpg/revision/latest/scale-to-width-down/1200?cb=20210705182101',
                'voice_profile': {
                    'pitch_range': (140, 180),  # Medium-low
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Wise, mysterious, calculated'
                }
            },
            'P.E.K.K.A': {
                'game': 'Clash of Clans',
                'description': 'Robotic warrior with mechanical voice',
                'emoji': '🤖',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/e/e9/Avatar_PEKKA_Beta.png/revision/latest?cb=20250415033024',
                'voice_profile': {
                    'pitch_range': (180, 220),  # Medium-high, robotic
                    'energy_level': 'loud',
                    'tempo': 'moderate',
                    'personality': 'Mechanical, powerful, mysterious'
                }
            },
            'Hog Rider': {
                'game': 'Clash of Clans',
                'description': 'Fast-moving warrior on a hog',
                'emoji': '🐗',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/8/84/Hog_rider.jpg/revision/latest?cb=20140711085735',
                'voice_profile': {
                    'pitch_range': (120, 160),  # Medium
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Wild, enthusiastic, reckless'
                }
            },
            
            # Brawl Stars Characters
            'Shelly': {
                'game': 'Brawl Stars',
                'description': 'Tough and confident shotgunner',
                'emoji': '🔫',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/shelly.webp',
                'voice_profile': {
                    'pitch_range': (190, 230),  # Medium-high
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Confident, tough, determined'
                }
            },
            'Colt': {
                'game': 'Brawl Stars',
                'description': 'Cool and cocky sharpshooter',
                'emoji': '😎',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/colt.webp',
                'voice_profile': {
                    'pitch_range': (130, 170),  # Medium
                    'energy_level': 'moderate',
                    'tempo': 'fast',
                    'personality': 'Cocky, cool, flashy'
                }
            },
            'Bull': {
                'game': 'Brawl Stars',
                'description': 'Tough brawler with deep voice',
                'emoji': '🐂',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/bull.webp',
                'voice_profile': {
                    'pitch_range': (80, 120),  # Low
                    'energy_level': 'loud',
                    'tempo': 'slow',
                    'personality': 'Tough, intimidating, strong'
                }
            },
            'Poco': {
                'game': 'Brawl Stars',
                'description': 'Musical skeleton with cheerful voice',
                'emoji': '🎸',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/poco.webp',
                'voice_profile': {
                    'pitch_range': (160, 200),  # Medium
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Musical, cheerful, supportive'
                }
            },
            'Nita': {
                'game': 'Brawl Stars',
                'description': 'Young shaman with bear companion',
                'emoji': '🐻',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/nita.webp',
                'voice_profile': {
                    'pitch_range': (220, 270),  # High, youthful
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Youthful, nature-connected, fierce'
                }
            },
            'Crow': {
                'game': 'Brawl Stars',
                'description': 'Mysterious assassin with raspy voice',
                'emoji': '🦅',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/crow.webp',
                'voice_profile': {
                    'pitch_range': (110, 150),  # Low-medium
                    'energy_level': 'soft',
                    'tempo': 'moderate',
                    'personality': 'Mysterious, stealthy, calculating'
                }
            },
            'Spike': {
                'game': 'Brawl Stars',
                'description': 'Silent cactus (no voice, just sounds)',
                'emoji': '🌵',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/spike.webp',
                'voice_profile': {
                    'pitch_range': (200, 280),  # High, squeaky
                    'energy_level': 'soft',
                    'tempo': 'slow',
                    'personality': 'Cute, silent, mysterious'
                }
            },
            'Leon': {
                'game': 'Brawl Stars',
                'description': 'Sneaky assassin with youthful voice',
                'emoji': '🥷',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/leon.webp',
                'voice_profile': {
                    'pitch_range': (210, 260),  # High, young
                    'energy_level': 'moderate',
                    'tempo': 'fast',
                    'personality': 'Sneaky, playful, energetic'
                }
            },
            'Mortis': {
                'game': 'Brawl Stars',
                'description': 'Dashing vampire with dramatic voice',
                'emoji': '🧛',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/mortis.webp',
                'voice_profile': {
                    'pitch_range': (120, 160),  # Medium
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Dramatic, elegant, theatrical'
                }
            },
            'El Primo': {
                'game': 'Brawl Stars',
                'description': 'Wrestler with loud, booming voice',
                'emoji': '🤼',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/el_primo.webp',
                'voice_profile': {
                    'pitch_range': (100, 140),  # Low
                    'energy_level': 'loud',
                    'tempo': 'moderate',
                    'personality': 'Loud, proud, showman'
                }
            },
            
            # Clash Royale Specific
            'Knight': {
                'game': 'Clash Royale',
                'description': 'Noble defender with steady voice',
                'emoji': '🛡️',
                'image_url': 'https://www.noff.gg/clash-royale/res/img/cards/knight.webp',
                'voice_profile': {
                    'pitch_range': (120, 160),  # Medium
                    'energy_level': 'moderate',
                    'tempo': 'slow',
                    'personality': 'Noble, steady, reliable'
                }
            },
            'Princess': {
                'game': 'Clash Royale',
                'description': 'Elegant archer with refined voice',
                'emoji': '👸',
                'image_url': 'https://www.noff.gg/clash-royale/res/img/cards/princess.webp',
                'voice_profile': {
                    'pitch_range': (210, 260),  # High
                    'energy_level': 'soft',
                    'tempo': 'moderate',
                    'personality': 'Elegant, refined, graceful'
                }
            },
            'Goblin': {
                'game': 'Clash Royale',
                'description': 'Mischievous creature with squeaky voice',
                'emoji': '👺',
                'image_url': 'https://www.noff.gg/clash-royale/res/img/cards/goblin.webp',
                'voice_profile': {
                    'pitch_range': (240, 300),  # Very high
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Mischievous, chaotic, hyper'
                }
            },
            
            # More Clash of Clans Characters
            'Valkyrie': {
                'game': 'Clash of Clans',
                'description': 'Fierce warrior maiden with battle spirit',
                'emoji': '⚔️',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/f/f7/ValkyrieCoC.png/revision/latest?cb=20140620210121',
                'voice_profile': {
                    'pitch_range': (170, 210),  # Medium-high, feminine warrior
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Fierce, warrior spirit, confident'
                }
            },
            'Dragon': {
                'game': 'Clash of Clans',
                'description': 'Powerful flying beast with roaring voice',
                'emoji': '🐉',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/2/29/Dragon_Mayhem.png/revision/latest?cb=20171224082311',
                'voice_profile': {
                    'pitch_range': (60, 100),  # Very deep, monstrous
                    'energy_level': 'loud',
                    'tempo': 'moderate',
                    'personality': 'Powerful, intimidating, primal'
                }
            },
            'Witch': {
                'game': 'Clash of Clans',
                'description': 'Dark spellcaster with cackling voice',
                'emoji': '🧙‍♀️',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/1/11/Witching_Hour.png/revision/latest?cb=20171224082528',
                'voice_profile': {
                    'pitch_range': (190, 240),  # High, cackling
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Mysterious, dark, mischievous'
                }
            },
            'Golem': {
                'game': 'Clash of Clans',
                'description': 'Massive rock creature with rumbling voice',
                'emoji': '🗿',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/3/3f/Golem.jpeg/revision/latest?cb=20150315220344',
                'voice_profile': {
                    'pitch_range': (50, 90),  # Extremely deep
                    'energy_level': 'loud',
                    'tempo': 'slow',
                    'personality': 'Massive, slow, powerful'
                }
            },
            'Miner': {
                'game': 'Clash of Clans',
                'description': 'Underground digger with gruff voice',
                'emoji': '⛏️',
                'image_url': 'https://static.wikia.nocookie.net/clashofclans/images/d/d2/Miner.png',
                'voice_profile': {
                    'pitch_range': (110, 150),  # Low-medium, gruff
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Determined, hardworking, tough'
                }
            },
            
            # More Clash Royale Characters
            'Musketeer': {
                'game': 'Clash Royale',
                'description': 'Elite ranged fighter with confident voice',
                'emoji': '💂‍♀️',
                'image_url': 'https://static.wikia.nocookie.net/clashroyale/images/e/ee/MusketeerCard.png/revision/latest?cb=20171212203619',
                'voice_profile': {
                    'pitch_range': (180, 220),  # Medium-high
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Confident, skilled, professional'
                }
            },
            'Mini P.E.K.K.A': {
                'game': 'Clash Royale',
                'description': 'Small but fierce armored warrior',
                'emoji': '🤖',
                'image_url': 'https://static.wikia.nocookie.net/clashroyale/images/7/7b/MiniPEKKACard.png/revision/latest?cb=20250908165647',
                'voice_profile': {
                    'pitch_range': (200, 250),  # Higher pitched than P.E.K.K.A
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Energetic, aggressive, cute-but-deadly'
                }
            },
            'Ice Wizard': {
                'game': 'Clash Royale',
                'description': 'Cold mage with chilling voice',
                'emoji': '❄️',
                'image_url': 'https://static.wikia.nocookie.net/clashroyale/images/d/d3/IceWizardCard.png/revision/latest?cb=20171212204923',
                'voice_profile': {
                    'pitch_range': (130, 170),  # Medium, cold
                    'energy_level': 'soft',
                    'tempo': 'slow',
                    'personality': 'Calm, cold, calculated'
                }
            },
            'Mega Knight': {
                'game': 'Clash Royale',
                'description': 'Massive armored knight with booming voice',
                'emoji': '🛡️',
                'image_url': 'https://static.wikia.nocookie.net/clashroyale/images/0/0b/MegaKnightCard.png/revision/latest?cb=20171212204943',
                'voice_profile': {
                    'pitch_range': (70, 110),  # Very deep
                    'energy_level': 'loud',
                    'tempo': 'slow',
                    'personality': 'Powerful, intimidating, heavy'
                }
            },
            'Electro Wizard': {
                'game': 'Clash Royale',
                'description': 'Electric mage with energetic voice',
                'emoji': '⚡',
                'image_url': 'https://static.wikia.nocookie.net/clashroyale/images/1/12/ElectroWizardCard.png/revision/latest?cb=20171212203437',
                'voice_profile': {
                    'pitch_range': (150, 190),  # Medium, energetic
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Energetic, chaotic, electric'
                }
            },
            'Bandit': {
                'game': 'Clash Royale',
                'description': 'Swift rogue with sly voice',
                'emoji': '🗡️',
                'image_url': 'https://static.wikia.nocookie.net/clashroyale/images/7/76/BanditCard.png/revision/latest?cb=20171212203309',
                'voice_profile': {
                    'pitch_range': (170, 210),  # Medium-high
                    'energy_level': 'moderate',
                    'tempo': 'fast',
                    'personality': 'Sly, quick, mischievous'
                }
            },
            
            # More Brawl Stars Characters
            'Dynamike': {
                'game': 'Brawl Stars',
                'description': 'Explosive miner with wild voice',
                'emoji': '💣',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/dynamike.webp',
                'voice_profile': {
                    'pitch_range': (140, 180),  # Medium, old man
                    'energy_level': 'loud',
                    'tempo': 'moderate',
                    'personality': 'Wild, explosive, crazy'
                }
            },
            'Barley': {
                'game': 'Brawl Stars',
                'description': 'Robot bartender with friendly voice',
                'emoji': '🍺',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/barley.webp',
                'voice_profile': {
                    'pitch_range': (150, 190),  # Medium, robotic-friendly
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Friendly, polite, cheerful'
                }
            },
            'Jessie': {
                'game': 'Brawl Stars',
                'description': 'Young engineer with bright voice',
                'emoji': '🔧',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/jessie.webp',
                'voice_profile': {
                    'pitch_range': (230, 280),  # High, young
                    'energy_level': 'moderate',
                    'tempo': 'fast',
                    'personality': 'Smart, cheerful, inventive'
                }
            },
            'Brock': {
                'game': 'Brawl Stars',
                'description': 'Cool rocket launcher with confident voice',
                'emoji': '🚀',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/brock.webp',
                'voice_profile': {
                    'pitch_range': (130, 170),  # Medium
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Cool, confident, explosive'
                }
            },
            'Piper': {
                'game': 'Brawl Stars',
                'description': 'Elegant sniper with refined voice',
                'emoji': '💄',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/piper.webp',
                'voice_profile': {
                    'pitch_range': (200, 250),  # High, elegant
                    'energy_level': 'soft',
                    'tempo': 'moderate',
                    'personality': 'Elegant, sophisticated, graceful'
                }
            },
            'Pam': {
                'game': 'Brawl Stars',
                'description': 'Tough healer with motherly voice',
                'emoji': '🔨',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/pam.webp',
                'voice_profile': {
                    'pitch_range': (160, 200),  # Medium, motherly
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Tough, caring, protective'
                }
            },
            'Frank': {
                'game': 'Brawl Stars',
                'description': 'Massive tank with deep rumbling voice',
                'emoji': '💪',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/frank.webp',
                'voice_profile': {
                    'pitch_range': (60, 100),  # Very deep
                    'energy_level': 'loud',
                    'tempo': 'slow',
                    'personality': 'Massive, powerful, unstoppable'
                }
            },
            'Bibi': {
                'game': 'Brawl Stars',
                'description': 'Fierce batter with energetic voice',
                'emoji': '⚾',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/bibi.webp',
                'voice_profile': {
                    'pitch_range': (190, 230),  # Medium-high, energetic
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Energetic, tough, sporty'
                }
            },
            '8-Bit': {
                'game': 'Brawl Stars',
                'description': 'Retro arcade character with robotic voice',
                'emoji': '🎮',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/8_bit.webp',
                'voice_profile': {
                    'pitch_range': (100, 140),  # Low, robotic
                    'energy_level': 'soft',
                    'tempo': 'slow',
                    'personality': 'Retro, robotic, slow-moving'
                }
            },
            'Emz': {
                'game': 'Brawl Stars',
                'description': 'Influencer with sassy voice',
                'emoji': '📱',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/emz.webp',
                'voice_profile': {
                    'pitch_range': (200, 250),  # High, sassy
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Sassy, trendy, social-media-savvy'
                }
            },
            'Amber': {
                'game': 'Brawl Stars',
                'description': 'Fire performer with energetic voice',
                'emoji': '🔥',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/amber.webp',
                'voice_profile': {
                    'pitch_range': (210, 260),  # High, energetic
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Energetic, fiery, enthusiastic'
                }
            },
            'Edgar': {
                'game': 'Brawl Stars',
                'description': 'Edgy teen with moody voice',
                'emoji': '🧣',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/edgar.webp',
                'voice_profile': {
                    'pitch_range': (140, 180),  # Medium, teenage
                    'energy_level': 'moderate',
                    'tempo': 'moderate',
                    'personality': 'Moody, edgy, teenage-angst'
                }
            },
            'Colette': {
                'game': 'Brawl Stars',
                'description': 'Obsessed fan with excited voice',
                'emoji': '📖',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/colette.webp',
                'voice_profile': {
                    'pitch_range': (210, 270),  # High, excited
                    'energy_level': 'loud',
                    'tempo': 'fast',
                    'personality': 'Obsessed, excited, fan-girl'
                }
            },
            'Sandy': {
                'game': 'Brawl Stars',
                'description': 'Sleepy sand character with drowsy voice',
                'emoji': '😴',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/sandy.webp',
                'voice_profile': {
                    'pitch_range': (220, 270),  # High, sleepy
                    'energy_level': 'soft',
                    'tempo': 'slow',
                    'personality': 'Sleepy, calm, drowsy'
                }
            },
            'Surge': {
                'game': 'Brawl Stars',
                'description': 'Superhero robot with heroic voice',
                'emoji': '🦸',
                'image_url': 'https://www.noff.gg/brawl-stars/res/img/brawlers/surge.webp',
                'voice_profile': {
                    'pitch_range': (120, 160),  # Medium, heroic
                    'energy_level': 'loud',
                    'tempo': 'moderate',
                    'personality': 'Heroic, energetic, robotic'
                }
            },
        }
    
    def get_all_characters(self):
        """Get all characters in the database."""
        return self.characters
    
    def get_character(self, name):
        """Get a specific character by name."""
        return self.characters.get(name)
    
    def get_characters_by_game(self, game):
        """Get all characters from a specific game."""
        return {
            name: char for name, char in self.characters.items()
            if char['game'] == game
        }

