import pygame
import random
import math
from config import *
from functions import *

class Defense():
    def __init__(self):
        self.pos = (SCREENSIZE[0] // 2, SCREENSIZE[1] - GROUND_LEVEL)  # set initial position of gun
        self.target_pos = (SCREENSIZE[0] // 2, SKY_LEVEL)   # default target point (straight up)
        self.angle = 0                                       # angle of gun relative to vertical
        self.ammo = 30                                       # initial amount of ammo
        self.base_color = DEFENCE                            # normal gun colour
        self.powerup_color = (255, 140, 0)                   # orange color for powerup mode
        self.current_color = self.base_color                 # current color state
        self.gun_radius = 12                                 # radius of gun base circle (bigger)
        self.gun_size = 28                                   # length of gun barrel (bigger)
        self.destroyed = False                               # has the defense been destroyed
        self.powerup_active = False                          # tracks powerup state
        
        # New targeting system
        self.current_target = None                           # current target object (missile/powerup)
        self.is_aiming = False                               # is turret currently aiming at target
        self.aiming_timer = 0                                # timer for aiming animation
        self.aiming_duration = 15                            # frames to complete aiming (0.5 seconds at 30 FPS)
        
        # Laser beam system
        self.laser_active = False                            # is laser beam currently visible
        self.laser_timer = 0                                 # timer for laser beam duration
        self.laser_duration = 10                             # frames to show laser (0.33 seconds at 30 FPS)
        self.laser_target_pos = None                         # position where laser should end
        
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
        # Handle aiming animation
        if self.is_aiming and self.current_target:
            # Get target position
            if hasattr(self.current_target, 'get_pos'):
                target_center = self.current_target.get_pos()
            elif hasattr(self.current_target, 'pos'):
                # For missiles, get center position
                target_center = (
                    self.current_target.pos[0], 
                    self.current_target.pos[1]
                )
            else:
                target_center = self.target_pos
            
            # Animate towards target position
            if self.aiming_timer < self.aiming_duration:
                # Interpolate between current target_pos and actual target
                progress = self.aiming_timer / self.aiming_duration
                # Use easing function for smooth animation
                eased_progress = 1 - (1 - progress) ** 3  # Ease-out cubic
                
                start_x, start_y = self.target_pos
                end_x, end_y = target_center
                
                new_x = start_x + (end_x - start_x) * eased_progress
                new_y = start_y + (end_y - start_y) * eased_progress
                
                self.target_pos = (new_x, new_y)
                self.aiming_timer += 1
            else:
                # Aiming complete
                self.target_pos = target_center
        
        # Handle laser beam animation
        if self.laser_active:
            self.laser_timer += 1
            if self.laser_timer >= self.laser_duration:
                self.laser_active = False
                self.laser_timer = 0
                self.laser_target_pos = None
        
        # Calculate angle based on current target position
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
        
        # Draw laser beam when active
        if self.laser_active and self.laser_target_pos:
            # Calculate laser fade based on timer
            fade_progress = self.laser_timer / self.laser_duration
            laser_alpha = int(255 * (1 - fade_progress))  # Fade out over time
            
            # Create bright blue laser color
            laser_color = (100, 150, 255)  # Bright blue
            core_color = (200, 220, 255)   # Bright white-blue core
            
            # Draw laser beam with multiple layers for glow effect
            # Outer glow (thicker, more transparent)
            outer_surface = pygame.Surface((abs(self.laser_target_pos[0] - self.gun_end[0]) + 20, 
                                          abs(self.laser_target_pos[1] - self.gun_end[1]) + 20))
            outer_surface.set_alpha(laser_alpha // 3)
            
            # Main beam (medium thickness)
            pygame.draw.line(screen, laser_color, self.gun_end, self.laser_target_pos, 4)
            
            # Inner core (thin, brightest)
            core_alpha = min(255, laser_alpha + 50)
            if core_alpha > 0:
                core_surface = pygame.Surface((2, 2))
                core_surface.set_alpha(core_alpha)
                pygame.draw.line(screen, core_color, self.gun_end, self.laser_target_pos, 2)
        
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
    
    def aim_at_target(self, target):
        """Start aiming animation towards a target (missile or powerup)"""
        self.current_target = target
        self.is_aiming = True
        self.aiming_timer = 0
        # Store starting position for smooth interpolation
        self.aiming_start_pos = self.target_pos
    
    def stop_aiming(self):
        """Stop aiming but keep current position"""
        self.is_aiming = False
        self.current_target = None
        self.aiming_timer = 0
        # Keep current target_pos - don't reset to default
    
    def is_aiming_complete(self):
        """Check if the aiming animation is complete"""
        return self.is_aiming and self.aiming_timer >= self.aiming_duration
    
    def fire_laser(self, target_pos):
        """Activate laser beam towards target position"""
        self.laser_active = True
        self.laser_timer = 0
        self.laser_target_pos = target_pos