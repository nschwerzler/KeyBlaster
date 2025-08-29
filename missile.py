import pygame
import math
from config import *
from functions import *
from explosion import Explosion


class Missile():
    def __init__(self, origin_pos, target_pos, incoming = True, speed = 1, points = 10, trail_color = WARHEAD_TRAIL, warhead_color = WARHEAD, label=None):
        self.origin_pos = origin_pos                # starting position of missile
        self.target_pos = target_pos                # end position of missile
        if incoming == True:                        # is this missile incoming (1 = yes[default], -1 = no)
            self.incoming = 1
        else:
            self.incoming = -1                  
        self.speed = speed                          # missile speed
        self.points = points                        # points awarded for destroying missile
        self.travel_dist = 1                        # distance traveled by missile
        self.warhead_color = warhead_color          # warhead colour
        self.trail_color = trail_color              # missile trail colour
        self.warhead_size = 2                       # warhead display size
        self.trail_width = 1                        # missile trail width
        self.pos = origin_pos                       # current position of warhead
        self.x = target_pos[0] - origin_pos[0]      # distance from x origin to x target
        self.y = target_pos[1] - origin_pos[1]      # distance from y origin to y target
        if self.y != 0 :
            self.m = self.x / self.y                # slop of missile trajectory
        else:
            self.m = 1
        self.angle = math.atan(self.m)              # angle of missile trajectory
        self.dist_to_target = distance(
                                origin_pos, 
                                target_pos)         # full distance to target position
        self.detonated = False                      # has the missile detonated
        self.label = label                          # optional key label for typing mode
        
    # draw the missile and trail
    def draw(self, screen):
        # draw the missile trail
        pygame.draw.line(screen, 
                        self.trail_color, 
                        self.origin_pos, 
                        self.pos, 
                        self.trail_width)
        # draw the warhead
        pygame.draw.circle(screen, 
                        self.warhead_color, 
                        self.pos, 
                        self.warhead_size)
        # draw the optional key label near the warhead
        if self.label:
            try:
                # Show label with typed sequence highlighting
                full_label = str(self.label).upper()
                
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
                    # Show typed chars in different color, remaining chars in normal color
                    typed_surface = game_font.render(typed_portion, False, (0, 255, 0))  # Green for typed
                    remaining = full_label[len(typed_portion):]
                    remaining_surface = game_font.render(remaining, False, INTERFACE_SEC)  # Normal color for remaining
                    
                    # Position both parts
                    total_width = typed_surface.get_width() + remaining_surface.get_width()
                    start_x = self.pos[0] - (total_width // 2)
                    screen.blit(typed_surface, (start_x, self.pos[1] - 20))
                    screen.blit(remaining_surface, (start_x + typed_surface.get_width(), self.pos[1] - 20))
                else:
                    # Show normal label
                    label_surface = game_font.render(full_label, False, INTERFACE_SEC)
                    screen.blit(label_surface, (self.pos[0] - (label_surface.get_width() // 2), self.pos[1] - 20))
            except Exception:
                # fail-safe: ignore label draw issues
                pass

    # update missile logic
    def update(self, explosion_list):
        if not self.detonated:
            self.pos = (self.origin_pos[0] + int(self.travel_dist * math.sin(self.angle) * self.incoming), 
                        self.origin_pos[1] + int(self.travel_dist * math.cos(self.angle) * self.incoming))
            self.travel_dist += self.speed
        # reached target point, now detonate
        if self.travel_dist > self.dist_to_target and not self.detonated:
            self.explode(explosion_list)
    
    # detonate and create explosion
    def explode(self, explosion_list):
        self.detonated = True
        if self.incoming != 1:
            points_multiplier = 1
            explosion_radius = INTERCEPT_RADIUS
            explosion_color = INTERCEPT_EXPLOSION
            try:
                from functions import sfx_intercept
                sfx_intercept()
            except Exception:
                pass
        else:
            points_multiplier = 0
            explosion_radius = NUKE_RADIUS
            explosion_color = NUKE_EXPLOSION

        explosion_list.append(Explosion(self.pos, points_multiplier, explosion_radius, explosion_color))

    # return the current position
    def get_pos(self):
        return self.pos

    def get_points(self):
        return self.points

    # predict a future position along trajectory, clamped to target
    def get_future_pos(self, pixels_ahead=20):
        future_dist = self.travel_dist + max(0, pixels_ahead)
        if future_dist > self.dist_to_target:
            future_dist = self.dist_to_target
        return (
            self.origin_pos[0] + int(future_dist * math.sin(self.angle) * self.incoming),
            self.origin_pos[1] + int(future_dist * math.cos(self.angle) * self.incoming)
        )
