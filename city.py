import pygame
from config import *

class City():
    def __init__(self, number, max_cities):
        self.pos = (number * SCREENSIZE[0] // (max_cities + 1), SCREENSIZE[1] - GROUND_LEVEL)   # set position of the cities
        self.color = CITY
        self.size = 10
        self.destroyed = False      # might not be needed if I just remove city from list

    def draw(self, screen):
        # might not be needed if I just remove city from list
        if self.destroyed != True:
            # Draw a more city-like appearance with buildings
            city_x, city_y = self.pos
            
            # Draw multiple buildings of different heights
            building_width = 6
            buildings = [
                (city_x - 15, city_y - 20, building_width, 20),  # Tall building left
                (city_x - 8, city_y - 15, building_width, 15),   # Medium building
                (city_x - 1, city_y - 25, building_width, 25),   # Tallest building center  
                (city_x + 6, city_y - 18, building_width, 18),   # Medium-tall building
                (city_x + 13, city_y - 12, building_width, 12)   # Short building right
            ]
            
            # Draw each building
            for bx, by, bw, bh in buildings:
                # Main building body
                pygame.draw.rect(screen, self.color, (bx, by, bw, bh))
                
                # Building outline for definition
                outline_color = tuple(max(0, c - 50) for c in self.color)
                pygame.draw.rect(screen, outline_color, (bx, by, bw, bh), 1)
                
                # Add windows (small rectangles)
                window_color = tuple(min(255, c + 80) for c in outline_color)
                for row in range(1, bh // 4):
                    for col in range(1, bw // 3):
                        window_x = bx + col * 2 + 1
                        window_y = by + row * 3 + 1
                        if window_x < bx + bw - 1 and window_y < by + bh - 1:
                            pygame.draw.rect(screen, window_color, (window_x, window_y, 1, 1))
    
    def update(self):
        pass

    # might not be needed if I just remove city from list
    def set_destroyed(self, status):
        self.destroyed = status
    
    # might not be needed if I just remove city from list
    def get_destroyed(self):
        return self.destroyed

    def get_pos(self):
        return self.pos
