import pygame
import random
import math
from config import *
from missile import Missile
from explosion import Explosion

class AutoTurret():
    def __init__(self, pos):
        self.pos = pos  # Position where the turret was spawned
        self.lifetime = -1  # Infinite lifetime - lasts entire level
        self.shoot_timer = 0
        self.shoot_interval = 15  # Shoot every 0.5 seconds (much faster!)
        self.destroyed = False
        self.barrel_angle = 0  # Current barrel angle for aiming
        self.target_angle = 0  # Target angle to rotate towards
        self.rotation_speed = 0.2  # Faster barrel rotation for quicker targeting
        self.flash_timer = 0
        
    def update(self, missile_list, explosion_list):
        if self.destroyed:
            return False
            
        # Update timers
        self.shoot_timer += 1
        self.flash_timer += 1
        
        # Turret lasts entire level - only removed manually at level transitions
            
        # Find nearest missile to target
        nearest_missile = None
        nearest_distance = float('inf')
        
        for missile in missile_list:
            if hasattr(missile, 'incoming') and missile.incoming == 1:  # Only target incoming missiles
                if not missile.detonated:
                    missile_pos = missile.pos if hasattr(missile, 'pos') else (0, 0)
                    distance = math.sqrt((missile_pos[0] - self.pos[0])**2 + (missile_pos[1] - self.pos[1])**2)
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_missile = missile
        
        # Aim at nearest missile
        if nearest_missile:
            missile_pos = nearest_missile.pos
            # Calculate angle to target
            dx = missile_pos[0] - self.pos[0]
            dy = missile_pos[1] - self.pos[1]
            self.target_angle = math.atan2(dy, dx)
            
            # Rotate barrel towards target
            angle_diff = self.target_angle - self.barrel_angle
            # Normalize angle difference to -pi to pi
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Rotate towards target
            if abs(angle_diff) > self.rotation_speed:
                self.barrel_angle += self.rotation_speed if angle_diff > 0 else -self.rotation_speed
            else:
                self.barrel_angle = self.target_angle
            
            # Shoot at target if aimed and timer is ready
            if abs(angle_diff) < 0.2 and self.shoot_timer >= self.shoot_interval:
                # Create direct explosion at missile position instead of grenade
                explosion_list.append(Explosion(missile_pos, 0, INTERCEPT_RADIUS + 10, (50, 255, 50)))
                
                # Add poison gas effect - multiple small green explosions
                for i in range(3):
                    offset_x = random.randint(-10, 10)
                    offset_y = random.randint(-10, 10)
                    gas_pos = (missile_pos[0] + offset_x, missile_pos[1] + offset_y)
                    gas_explosion = Explosion(gas_pos, 0, INTERCEPT_RADIUS // 2, (100, 255, 100))
                    explosion_list.append(gas_explosion)
                
                self.shoot_timer = 0
                
                # Play sound effect if available
                try:
                    from functions import play_random_explode
                    play_random_explode()
                except Exception:
                    pass
        
        return True  # Keep turret active
    
    def shoot_poison_grenade(self, target_pos, explosion_list):
        # Create a poison grenade missile from turret to target
        try:
            # Calculate lead position for moving target
            lead_pos = target_pos
            
            # Create poison grenade with green trail and warhead
            poison_grenade = Missile(
                self.pos, 
                lead_pos, 
                incoming=False,  # This is our defensive missile
                speed=3.0,  # Faster than normal missiles
                points=0,  # No points for auto-turret kills
                trail_color=(50, 255, 50),  # Bright green trail
                warhead_color=(100, 255, 100),  # Light green warhead
                label=None  # No typing required for auto-turret missiles
            )
            
            # Add special poison gas explosion effect when it detonates
            poison_grenade.poison_gas = True
            
            return poison_grenade
            
        except Exception:
            # Failsafe - create basic explosion at target
            explosion_list.append(Explosion(target_pos, 0, INTERCEPT_RADIUS, (50, 255, 50)))
            return None
    
    def draw(self, screen):
        if not self.destroyed:
            center_x, center_y = int(self.pos[0]), int(self.pos[1])
            
            # Draw turret base (dark green circle)
            pygame.draw.circle(screen, (30, 120, 30), (center_x, center_y), 12)
            pygame.draw.circle(screen, (50, 200, 50), (center_x, center_y), 10)
            
            # Draw rotating barrel
            barrel_length = 20
            barrel_end_x = center_x + int(barrel_length * math.cos(self.barrel_angle))
            barrel_end_y = center_y + int(barrel_length * math.sin(self.barrel_angle))
            
            # Draw barrel line (thick green line)
            pygame.draw.line(screen, (100, 255, 100), (center_x, center_y), (barrel_end_x, barrel_end_y), 4)
            
            # Draw barrel tip (small circle)
            pygame.draw.circle(screen, (150, 255, 150), (barrel_end_x, barrel_end_y), 3)
            
            # Flash effect when shooting
            if self.shoot_timer < 5:  # Flash for first 5 frames after shooting (faster flash)
                flash_color = (255, 255, 255)
                pygame.draw.circle(screen, flash_color, (barrel_end_x, barrel_end_y), 5)
            
            # Draw permanent indicator (small green dot above turret)
            pygame.draw.circle(screen, (50, 255, 50), (center_x, center_y - 18), 4)
            pygame.draw.circle(screen, (100, 255, 100), (center_x, center_y - 18), 2)
    
    def get_pos(self):
        return self.pos
        
    def is_destroyed(self):
        return self.destroyed


class PoisonGrenade(Missile):
    """Special missile class for poison grenades that create poison gas explosions"""
    
    def __init__(self, origin_pos, target_pos, speed=3.0):
        super().__init__(
            origin_pos, 
            target_pos, 
            incoming=False, 
            speed=speed, 
            points=0, 
            trail_color=(50, 255, 50), 
            warhead_color=(100, 255, 100)
        )
        self.poison_gas = True
    
    def explode(self, explosion_list):
        """Create poison gas explosion instead of normal explosion"""
        self.detonated = True
        # Create larger poison gas explosion
        poison_explosion = Explosion(
            self.pos, 
            0,  # No points multiplier for auto-turret
            INTERCEPT_RADIUS + 20,  # Larger radius than normal
            (50, 255, 50)  # Green poison gas color
        )
        explosion_list.append(poison_explosion)
        
        # Add poison gas visual effect - multiple small green explosions
        import random
        for i in range(5):
            offset_x = random.randint(-15, 15)
            offset_y = random.randint(-15, 15)
            gas_pos = (self.pos[0] + offset_x, self.pos[1] + offset_y)
            gas_explosion = Explosion(
                gas_pos,
                0,
                INTERCEPT_RADIUS // 2,
                (100, 255, 100)
            )
            explosion_list.append(gas_explosion)