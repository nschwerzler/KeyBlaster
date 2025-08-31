import pygame
import random
from config import *

class Powerup():
    def __init__(self, start_side="left", powerup_type="multiplier"):
        # Spaceship appearance - different from missiles
        self.size = 15
        self.width = 40
        self.height = 20
        self.powerup_type = powerup_type  # "multiplier" or "freeze"
        
        # Set colors based on powerup type
        if powerup_type == "freeze":
            self.color = (0, 150, 255)  # Blue color for freeze powerup
            self.trail_color = (100, 200, 255)  # Light blue trail
        elif powerup_type == "explosion":
            self.color = (255, 50, 50)  # Red color for explosion powerup
            self.trail_color = (255, 100, 100)  # Light red trail
        else:  # multiplier (default)
            self.color = (255, 215, 0)  # Gold color for multiplier powerup
            self.trail_color = (255, 255, 0)  # Yellow trail
        
        # Horizontal movement across screen
        self.speed = 1.5  # Slightly slower so it's on screen longer (more tempting but riskier)
        
        # Calculate safe Y range for powerup (closer to cities, but still in safe zone)
        min_y = SCREENSIZE[1] // 3  # Start from upper third of screen
        max_y = SCREENSIZE[1] - GROUND_LEVEL - 100  # Stay well above cities/ground
        
        if start_side == "left":
            self.pos = [-self.width, random.randint(min_y, max_y)]  # Start left of screen
            self.direction = 1  # Moving right
        else:
            self.pos = [SCREENSIZE[0] + self.width, random.randint(min_y, max_y)]  # Start right of screen
            self.direction = -1  # Moving left
        
        self.destroyed = False
        self.points = 1000  # Base points for powerup
        
        # Hard word selection (minimum 7 characters)
        self.label = self._choose_hard_word()
        
        # Visual effects
        self.flash_timer = 0
        
    def _choose_hard_word(self):
        # Import conflict checking functions from main module
        import __main__
        can_add_word = getattr(__main__, 'can_add_word', lambda x: True)
        
        # RISKY words - intentionally difficult to type quickly (all 7+ characters minimum)
        # Mix of uncommon words, tricky spelling, and awkward finger combinations
        risky_words = [
            # 7-letter challenging words  
            "rhyming", "psyched", "blazing", "oxygens", "wizards", "rhythms",
            "lymphed", "nymphed", "glyphed", "zygotes", "fjorded", "sphinxed",
            "cryptic", "jackets", "waxiest", "quizzed", "zithers", "fizzled",
            "puzzled", "jazzing", "buzzard", "grizzly", "pretzels", "frenzied",
            # Gen Alpha risky shorthand (7+ chars only)
            "periodt", "ghosted", "cappin", "snatched", "pressed", "lowkeys", "highkey",
            "slaying", "savaged", "clutched", "bushing", "vibing", "flexing",
            # 8+ letter high-risk words (long = more time vulnerable)
            "xylophone", "byzantine", "schizoid", "rhapsody", "labyrinth", 
            "synchrony", "toxicity", "xerophyte", "zygomata", "rhythmic",
            "rhapsodic", "labyrinthine", "synchronize", "toxicology", "mystique",
            "adjacent", "quixotic", "buzzword", "zestiest", "blizzard", "jazziest",
            "frazzled", "grizzled", "dazzling", "sizzling", "puzzling", "fizzling",
            "muzzling", "guzzling", "nuzzling", "drizzled", "crizzled", "frizzled"
        ]
        
        # Try to find a word without conflicts
        for _ in range(50):  # Max attempts
            word = random.choice(risky_words)
            if can_add_word(word):
                return word
        
        # Fallback: try each word in order
        for word in risky_words:
            if can_add_word(word):
                return word
                
        # Last resort: return any word
        return random.choice(risky_words)
    
    def update(self):
        if not self.destroyed:
            # Move horizontally across screen
            self.pos[0] += self.speed * self.direction
            
            # Flash effect
            self.flash_timer += 1
            
            # Remove if goes off screen
            if (self.direction > 0 and self.pos[0] > SCREENSIZE[0] + self.width) or \
               (self.direction < 0 and self.pos[0] < -self.width):
                return False  # Signal to remove from list
        
        return True  # Keep in list
    
    def draw(self, screen):
        if not self.destroyed:
            if self.powerup_type == "explosion":
                # Draw diamond/star shape for explosion powerup
                center_x = self.pos[0] + self.width // 2
                center_y = self.pos[1] + self.height // 2
                
                # Create diamond points
                diamond_points = [
                    (center_x, center_y - self.height // 2),  # Top point
                    (center_x + self.width // 2, center_y),   # Right point
                    (center_x, center_y + self.height // 2),  # Bottom point
                    (center_x - self.width // 2, center_y)    # Left point
                ]
                
                # Draw main diamond body
                pygame.draw.polygon(screen, self.color, diamond_points)
                
                # Draw inner diamond for detail
                inner_points = [
                    (center_x, center_y - self.height // 4),  # Top point
                    (center_x + self.width // 4, center_y),   # Right point
                    (center_x, center_y + self.height // 4),  # Bottom point
                    (center_x - self.width // 4, center_y)    # Left point
                ]
                inner_color = tuple(min(255, c + 50) for c in self.color)
                pygame.draw.polygon(screen, inner_color, inner_points)
                
                # Flashing effect
                if self.flash_timer % 20 < 10:  # Flash every 20 frames
                    flash_color = (255, 255, 255)  # White flash
                    pygame.draw.polygon(screen, flash_color, inner_points)
            
            else:
                # Draw spaceship body (oval shape for multiplier/freeze)
                # Main body - elongated oval
                pygame.draw.ellipse(screen, self.color, 
                                  (self.pos[0], self.pos[1], self.width, self.height))
                
                # Wings/side parts (different colors based on type)
                if self.powerup_type == "freeze":
                    wing_color = tuple(max(0, c - 50) for c in self.color)  # Darker blue
                else:  # multiplier
                    wing_color = (200, 200, 0)  # Darker gold
                    
                pygame.draw.ellipse(screen, wing_color,
                                  (self.pos[0] - 5, self.pos[1] + 5, 10, 10))
                pygame.draw.ellipse(screen, wing_color,
                                  (self.pos[0] + self.width - 5, self.pos[1] + 5, 10, 10))
                
                # Flashing effect
                if self.flash_timer % 20 < 10:  # Flash every 20 frames
                    flash_color = (255, 255, 255)  # White flash
                    pygame.draw.ellipse(screen, flash_color,
                                      (self.pos[0] + 5, self.pos[1] + 3, self.width - 10, self.height - 6))
            
            # Draw trail
            trail_length = 30
            for i in range(5):
                trail_x = self.pos[0] - (self.direction * (i * 8))
                trail_alpha = 255 - (i * 50)
                if trail_alpha > 0:
                    trail_surface = pygame.Surface((6, 3))
                    trail_surface.set_alpha(trail_alpha)
                    trail_surface.fill(self.trail_color)
                    screen.blit(trail_surface, (trail_x, self.pos[1] + self.height // 2))
            
            # Draw the word label above spaceship
            if self.label:
                try:
                    # Show label with typed sequence highlighting
                    full_label = str(self.label).upper()
                    
                    label_y = self.pos[1] - 25
                    
                    # Get global typed sequence from main module
                    import __main__
                    typed_seq = getattr(__main__, 'typed_sequence', '').upper()
                    
                    # Find if any part of typed sequence matches this word
                    typed_portion = ""
                    if typed_seq:
                        for i in range(len(typed_seq), 0, -1):
                            seq_part = typed_seq[-i:]
                            if full_label.startswith(seq_part):
                                typed_portion = seq_part
                                break
                    
                    if len(typed_portion) > 0:
                        # Create larger font for typed portion
                        large_font = pygame.font.Font('data/fnt/PressStart2P-Regular.ttf', 20)  # Bigger font for typed letters
                        
                        # Show typed chars in bright green with larger font, remaining chars dimmed
                        typed_surface = large_font.render(typed_portion, False, (0, 255, 100))  # Bright green for typed
                        remaining = full_label[len(typed_portion):]
                        remaining_surface = game_font.render(remaining, False, (120, 120, 120))  # Dimmed gray for remaining
                        
                        # Position both parts (account for different font heights)
                        total_width = typed_surface.get_width() + remaining_surface.get_width()
                        start_x = self.pos[0] + self.width // 2 - (total_width // 2)
                        
                        # Add background highlight for typed portion
                        typed_bg = pygame.Surface((typed_surface.get_width() + 4, typed_surface.get_height() + 2))
                        typed_bg.fill((0, 50, 0))  # Dark green background
                        screen.blit(typed_bg, (start_x - 2, label_y - 3))
                        
                        # Draw typed portion with larger font
                        screen.blit(typed_surface, (start_x, label_y - 2))
                        # Draw remaining portion aligned to baseline
                        screen.blit(remaining_surface, (start_x + typed_surface.get_width(), label_y))
                    else:
                        # Show untyped words - single letters stay bright, longer words are dimmed
                        if len(full_label) == 1:
                            color = (255, 255, 255)  # Bright white for single letters
                        else:
                            color = (160, 160, 160)  # Light gray for longer untyped words
                        
                        label_surface = game_font.render(full_label, False, color)
                        screen.blit(label_surface, (self.pos[0] + self.width // 2 - (label_surface.get_width() // 2), label_y))
                except Exception:
                    # fail-safe: ignore label draw issues
                    pass
    
    def get_pos(self):
        return (self.pos[0] + self.width // 2, self.pos[1] + self.height // 2)
    
    def get_rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
    
    def destroy(self):
        self.destroyed = True
        return self.points