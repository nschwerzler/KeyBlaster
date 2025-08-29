import pygame
import random
import math
from config import *
from functions import *

class Defense():
    def __init__(self):
        self.pos = (SCREENSIZE[0] // 2, SCREENSIZE[1] - GROUND_LEVEL)  # set initial position of gun
        self.target_pos = pygame.mouse.get_pos()            # mouse pointer is target point
        self.angle = 0                                       # angle of gun relative to vertical
        self.ammo = 30                                       # initial amount of ammo
        self.base_color = DEFENCE                            # normal gun colour
        self.powerup_color = (255, 140, 0)                   # orange color for powerup mode
        self.current_color = self.base_color                 # current color state
        self.gun_radius = 12                                 # radius of gun base circle (bigger)
        self.gun_size = 28                                   # length of gun barrel (bigger)
        self.destroyed = False                               # has the defense been destroyed
        self.powerup_active = False                          # tracks powerup state
        
        # calculate initial angle and gun_end
        self.x = self.target_pos[0] - self.pos[0]
        self.y = self.target_pos[1] - self.pos[1]
        if self.y != 0:
            self.m = self.x / self.y                        # slope of gun barrel
        else:
            self.m = 0
        self.angle = math.atan(self.m) + math.pi             # angle of gun barrel
        self.gun_end = (self.pos[0] + int(self.gun_size * math.sin(self.angle)), 
                        self.pos[1] + int(self.gun_size * math.cos(self.angle)))

    def update(self):
        # update target point to wherever mouse is pointed
        self.target_pos = pygame.mouse.get_pos()
        # calculate line to target point
        self.x = self.target_pos[0] - self.pos[0]       # distance from x origin to x target
        self.y = self.target_pos[1] - self.pos[1]       # distance from y origin to y target
        if self.y != 0:
            self.m = self.x / self.y                    # slope of gun barrel
        else:
            self.m = 0
        self.angle = math.atan(self.m) + math.pi        # angle of gun barrel
        self.gun_end = (self.pos[0] + int(self.gun_size * math.sin(self.angle)), 
                        self.pos[1] + int(self.gun_size * math.cos(self.angle)))

    def draw(self, screen):
        # Enhanced turret design with multiple components
        
        # Draw base foundation (darker ring)
        foundation_color = tuple(max(0, c - 40) for c in self.current_color)
        pygame.draw.circle(screen, foundation_color, self.pos, self.gun_radius + 3)
        
        # Draw main base
        pygame.draw.circle(screen, self.current_color, self.pos, self.gun_radius)
        
        # Draw inner highlight circle
        highlight_color = tuple(min(255, c + 30) for c in self.current_color)
        pygame.draw.circle(screen, highlight_color, self.pos, self.gun_radius - 3)
        
        # Draw main gun barrel (thicker)
        pygame.draw.line(screen, self.current_color, self.pos, self.gun_end, 6)
        
        # Draw barrel highlight line (slightly offset)
        offset_x = int(2 * math.cos(self.angle + math.pi/2))
        offset_y = int(2 * math.sin(self.angle + math.pi/2))
        highlight_start = (self.pos[0] + offset_x, self.pos[1] + offset_y)
        highlight_end = (self.gun_end[0] + offset_x, self.gun_end[1] + offset_y)
        pygame.draw.line(screen, highlight_color, highlight_start, highlight_end, 2)
        
        # Draw muzzle tip
        muzzle_color = tuple(min(255, c + 50) for c in self.current_color)
        pygame.draw.circle(screen, muzzle_color, self.gun_end, 3)
        
        # Add powerup glow effect when active
        if self.powerup_active:
            # Draw pulsing glow rings
            import time
            pulse = abs(math.sin(time.time() * 4))  # Pulse 4 times per second
            glow_alpha = int(60 + 40 * pulse)
            glow_radius = int(self.gun_radius + 8 + 4 * pulse)
            
            # Create surface for glow effect
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2))
            glow_surface.set_alpha(glow_alpha)
            pygame.draw.circle(glow_surface, (255, 200, 0), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.pos[0] - glow_radius, self.pos[1] - glow_radius))

    def shoot(self, missile_list):
        if self.ammo > 0:
            # create new missile(origin, target, false=launch up, speed, points, trail color, warhead color)
            missile_list.append(Missile(self.pos, self.target_pos, False, 8, 0, INTERCEPTER_TRAIL, INTERCEPTER))
            self.ammo -= 1
            try:
                from functions import sfx_shoot
                sfx_shoot()
            except Exception:
                pass

    def get_ammo(self):
        return self.ammo
    
    def set_ammo(self, ammo):
        self.ammo = ammo
    
    def activate_powerup(self):
        """Activate powerup mode - turns turret orange with glow effect"""
        self.powerup_active = True
        self.current_color = self.powerup_color
    
    def deactivate_powerup(self):
        """Deactivate powerup mode - returns turret to normal color"""
        self.powerup_active = False
        self.current_color = self.base_color