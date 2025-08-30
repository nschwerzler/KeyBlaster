import pygame
from config import *

class CityBonus:
    """Animated bonus points that fade in and out above cities"""
    
    def __init__(self, city_pos):
        self.city_pos = city_pos
        self.points = 100
        self.timer = 0
        self.max_timer = 90  # 3 seconds at 30 FPS
        self.font = pygame.font.Font('data/fnt/PressStart2P-Regular.ttf', 14)
        
        # Happy colors - bright and cheerful
        self.colors = [
            (255, 215, 0),   # Gold
            (255, 165, 0),   # Orange
            (50, 205, 50),   # Lime green
            (0, 191, 255),   # Deep sky blue
            (255, 20, 147),  # Deep pink
        ]
        self.color_index = 0
        self.color_timer = 0
        
    def update(self):
        """Update animation timer and color cycling"""
        self.timer += 1
        self.color_timer += 1
        
        # Change color every 15 frames for rainbow effect
        if self.color_timer >= 15:
            self.color_timer = 0
            self.color_index = (self.color_index + 1) % len(self.colors)
        
        # Return False when animation is done
        return self.timer < self.max_timer
    
    def draw(self, screen):
        """Draw the animated bonus points"""
        if self.timer >= self.max_timer:
            return
        
        # Calculate fade in/out effect
        progress = self.timer / self.max_timer
        if progress < 0.3:  # Fade in
            alpha = progress / 0.3
        elif progress > 0.7:  # Fade out
            alpha = (1.0 - progress) / 0.3
        else:  # Full visibility
            alpha = 1.0
        
        # Calculate floating position
        float_offset = -30 - (progress * 20)  # Float upward
        pos_y = self.city_pos[1] + float_offset
        
        # Get current color
        current_color = self.colors[self.color_index]
        fade_color = tuple(int(c * alpha) for c in current_color)
        
        # Render and draw the bonus text
        bonus_text = self.font.render('+100', False, fade_color)
        text_rect = bonus_text.get_rect()
        text_rect.centerx = self.city_pos[0]
        text_rect.y = int(pos_y)
        
        screen.blit(bonus_text, text_rect)