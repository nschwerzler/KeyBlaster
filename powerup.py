import pygame
import random
from config import *

class Powerup():
    def __init__(self, start_side="left"):
        # Spaceship appearance - different from missiles
        self.size = 15
        self.width = 40
        self.height = 20
        self.color = (255, 215, 0)  # Gold color for powerup
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
        
        # Hard word selection
        self.label = self._choose_hard_word()
        self.typed_chars = ""
        
        # Visual effects
        self.flash_timer = 0
        
    def _choose_hard_word(self):
        # Import conflict checking functions from main module
        import __main__
        can_add_word = getattr(__main__, 'can_add_word', lambda x: True)
        
        # RISKY words - intentionally difficult to type quickly
        # Mix of uncommon words, tricky spelling, and awkward finger combinations
        risky_words = [
            # Tricky finger combinations
            "zyx", "qaz", "wsx", "xqz", "jkl", "mnb", "zxc",
            # Challenging 4-5 letter words with difficult patterns
            "lynx", "jinx", "quiz", "fizz", "fuzz", "jazz", "buzz", "whiz",
            # Gen Alpha risky shorthand (tricky to type quickly)
            "periodt", "whatev", "istg", "tbh", "irl", "rn", "nvm", "ttyl", "brb", "smh",
            # 6-7 letter risky words
            "zygote", "rhythm", "psycho", "sphinx", "fjords", "glyph", "nymph",
            # Gen Alpha longer terms (risky because unfamiliar)
            "snatched", "pressed", "cappin", "ghosted", "bussin", "slayed",
            # 8+ letter high-risk words (long = more time vulnerable)
            "xylophone", "zephyr", "syzygy", "byzantine", "schizoid", "rhapsody",
            "labyrinth", "synchrony", "toxicity", "xerophyte"
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
            # Draw spaceship body (different shape from missiles)
            # Main body - elongated oval
            pygame.draw.ellipse(screen, self.color, 
                              (self.pos[0], self.pos[1], self.width, self.height))
            
            # Wings/side parts
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
                    # Show label with typed characters highlighted
                    full_label = str(self.label).upper()
                    typed_portion = self.typed_chars.upper()
                    
                    label_y = self.pos[1] - 25
                    
                    if len(typed_portion) > 0 and full_label.startswith(typed_portion):
                        # Show typed chars in different color, remaining chars in normal color
                        typed_surface = game_font.render(typed_portion, False, (0, 255, 0))  # Green for typed
                        remaining = full_label[len(typed_portion):]
                        remaining_surface = game_font.render(remaining, False, (255, 255, 255))  # White for remaining
                        
                        # Position both parts
                        total_width = typed_surface.get_width() + remaining_surface.get_width()
                        start_x = self.pos[0] + self.width // 2 - (total_width // 2)
                        screen.blit(typed_surface, (start_x, label_y))
                        screen.blit(remaining_surface, (start_x + typed_surface.get_width(), label_y))
                    else:
                        # Show normal label
                        label_surface = game_font.render(full_label, False, (255, 255, 255))
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