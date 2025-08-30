import pygame
import random
import math
from config import *

class MegaExplosion:
    """Massive explosion that covers half the screen and destroys missiles"""
    
    def __init__(self, center_pos):
        self.center_x, self.center_y = center_pos
        self.max_radius = SCREENSIZE[0] // 2  # Half screen width
        self.current_radius = 0
        self.growth_speed = 15  # How fast the explosion grows
        self.timer = 0
        self.max_timer = 60  # 2 seconds at 30 FPS
        self.complete = False
        
        # Visual effects
        self.particles = []
        self.shockwave_rings = []
        self.screen_flash = 255  # White flash effect
        self.shake_intensity = 10  # Screen shake intensity
        
        # Create initial particle burst
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            self.particles.append({
                'x': self.center_x,
                'y': self.center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(30, 60),
                'max_life': random.randint(30, 60)
            })
    
    def update(self):
        """Update explosion animation and effects"""
        self.timer += 1
        
        # Grow explosion radius
        if self.current_radius < self.max_radius:
            self.current_radius += self.growth_speed
        
        # Create shockwave rings
        if self.timer % 10 == 0 and len(self.shockwave_rings) < 3:
            self.shockwave_rings.append({
                'radius': 0,
                'alpha': 255,
                'speed': random.uniform(8, 12)
            })
        
        # Update shockwave rings
        for ring in self.shockwave_rings[:]:
            ring['radius'] += ring['speed']
            ring['alpha'] -= 4
            if ring['alpha'] <= 0:
                self.shockwave_rings.remove(ring)
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3  # Gravity
            particle['vx'] *= 0.98  # Air resistance
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Update visual effects
        if self.screen_flash > 0:
            self.screen_flash -= 8  # Fade white flash quickly
        
        if self.shake_intensity > 0:
            self.shake_intensity -= 0.3  # Reduce shake intensity over time
        
        # Check if explosion is complete
        if self.timer >= self.max_timer:
            self.complete = True
    
    def draw(self, screen):
        """Draw the massive explosion effect"""
        if self.complete:
            return
            
        # Calculate explosion progress (0 to 1)
        progress = min(1.0, self.current_radius / self.max_radius)
        
        # Draw main explosion circle with gradient effect
        explosion_colors = [
            (255, 255, 255),  # White hot center
            (255, 200, 50),   # Yellow-orange
            (255, 100, 50),   # Orange-red
            (200, 50, 50),    # Dark red
            (100, 25, 25)     # Very dark red
        ]
        
        # Draw multiple circles for gradient effect
        for i, color in enumerate(explosion_colors):
            if self.current_radius > i * 20:
                alpha = max(0, 255 - (self.timer * 4))  # Fade out over time
                fade_color = tuple(int(c * alpha / 255) for c in color)
                
                circle_radius = max(1, int(self.current_radius - i * 15))
                if circle_radius > 0:
                    # Create surface for alpha blending
                    temp_surface = pygame.Surface((circle_radius * 2, circle_radius * 2))
                    temp_surface.set_alpha(alpha)
                    pygame.draw.circle(temp_surface, color, (circle_radius, circle_radius), circle_radius)
                    screen.blit(temp_surface, (self.center_x - circle_radius, self.center_y - circle_radius))
        
        # Draw shockwave rings
        for ring in self.shockwave_rings:
            if ring['radius'] > 0:
                ring_color = (255, 150, 150)
                alpha = max(0, min(255, ring['alpha']))
                
                # Create surface for alpha blending
                temp_surface = pygame.Surface((ring['radius'] * 2, ring['radius'] * 2))
                temp_surface.set_alpha(alpha)
                pygame.draw.circle(temp_surface, ring_color, (int(ring['radius']), int(ring['radius'])), int(ring['radius']), 3)
                screen.blit(temp_surface, (self.center_x - ring['radius'], self.center_y - ring['radius']))
        
        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                life_ratio = particle['life'] / particle['max_life']
                
                # Particle color fades from white to red to black
                if life_ratio > 0.7:
                    color = (255, 255, 255)  # White
                elif life_ratio > 0.4:
                    color = (255, int(255 * (life_ratio - 0.4) / 0.3), 0)  # Yellow to red
                else:
                    intensity = int(255 * life_ratio / 0.4)
                    color = (intensity, 0, 0)  # Red to black
                
                # Draw particle as small circle
                particle_size = max(1, int(3 * life_ratio))
                pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), particle_size)
        
        # Draw screen flash overlay
        if self.screen_flash > 0:
            flash_surface = pygame.Surface((SCREENSIZE[0], SCREENSIZE[1]))
            flash_surface.set_alpha(int(self.screen_flash))
            flash_surface.fill((255, 255, 255))
            screen.blit(flash_surface, (0, 0))
    
    def get_blast_radius(self):
        """Get current blast radius for collision detection"""
        return self.current_radius
    
    def is_in_blast_radius(self, pos):
        """Check if a position is within the current blast radius"""
        dx = pos[0] - self.center_x
        dy = pos[1] - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.current_radius
    
    def get_screen_shake(self):
        """Get current screen shake offset for camera effects"""
        if self.shake_intensity <= 0:
            return (0, 0)
        
        shake_x = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
        shake_y = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
        return (shake_x, shake_y)