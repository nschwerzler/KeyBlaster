import pygame
import random
from config import *
from functions import *
from missile import Missile

class McGame():
    def __init__(self, difficulty = 1, high_score = 0):
        self.player_score = 0
        self.high_score = high_score
        self.high_score_text = game_font.render('HIGH: {}'.format(self.high_score), False, INTERFACE_SEC)
        self.high_score_text_pos = SCREENSIZE[0] - self.high_score_text.get_width() - 5
        self.max_missile_count = 8
        self.missile_count = 0
        self.difficulty = difficulty
        self.difficulty_increment = 3
        self.missile_loop = 7
        self.missile_frequency = self.missile_loop - self.difficulty
        self.missile_interval = 1
        self.ground_level = SCREENSIZE[1] - GROUND_LEVEL
        
        # Powerup system
        self.point_multiplier = 1.0  # Normal scoring
        self.multiplier_timer = 0    # How long multiplier lasts
        self.powerup_spawn_timer = 0 # When to spawn next powerup
        self.flash_timer = 0         # For flashing effect
        
        # Freeze system
        self.freeze_timer = 0        # How long freeze lasts
        self.is_frozen = False       # Whether game elements are frozen
        
        # Create smaller font for bonus text
        self.small_font = pygame.font.Font('data/fnt/PressStart2P-Regular.ttf', 10)

    def draw(self, screen, defense):
        # draw the HUD, score, etc
        pygame.draw.line(screen, INTERFACE_PRI, [0, SKY_LEVEL], [SCREENSIZE[0], SKY_LEVEL], 2)
        pygame.draw.rect(screen, INTERFACE_PRI, (0, SCREENSIZE[1] - GROUND_LEVEL, SCREENSIZE[0], SCREENSIZE[1]))
        score_text = game_font.render('SCORE: {}'.format(self.player_score), False, INTERFACE_SEC)
        screen.blit(score_text, (5, 10))
        screen.blit(self.high_score_text, (self.high_score_text_pos, 10))
        ammo_text = game_font.render('AMMO: {}'.format(defense.get_ammo()), False, INTERFACE_SEC)
        screen.blit(ammo_text, (SCREENSIZE[0] // 2 - (ammo_text.get_width() // 2), 10))
        
        # Position for powerup effects near turret (center horizontally, above the turret)
        turret_x = SCREENSIZE[0] // 2
        turret_y = SCREENSIZE[1] - GROUND_LEVEL
        effect_y_offset = -60  # Start position above turret
        
        # Show freeze status if active
        if self.is_frozen:
            # Create pulsing alpha effect based on flash timer
            flash_phase = self.flash_timer / 60.0  # 0 to 1 over 2 seconds
            alpha_multiplier = 0.7 + 0.3 * abs(1 - 2 * flash_phase)  # Smooth pulse between 0.7 and 1.0
            
            # Calculate flashing blue color
            base_color = (0, 150, 255)  # Blue
            flash_color = (
                int(base_color[0] * alpha_multiplier),
                int(base_color[1] * alpha_multiplier), 
                int(base_color[2] * alpha_multiplier)
            )
            
            # Show freeze text
            freeze_text = self.small_font.render('FREEZE!', False, flash_color)
            text_x = turret_x - freeze_text.get_width() // 2  # Center text horizontally
            text_y = turret_y + effect_y_offset
            screen.blit(freeze_text, (text_x, text_y))
            
            # Show freeze timer
            timer_seconds = self.freeze_timer // 30
            timer_alpha = 0.8 + 0.2 * abs(1 - 2 * ((self.flash_timer + 15) % 60) / 60.0)
            timer_color = (
                int(base_color[0] * timer_alpha),
                int(base_color[1] * timer_alpha),
                int(base_color[2] * timer_alpha)
            )
            timer_text = self.small_font.render('{}s'.format(timer_seconds), False, timer_color)
            timer_x = turret_x - timer_text.get_width() // 2  # Center timer horizontally
            timer_y = text_y + 15  # Position below the freeze text
            screen.blit(timer_text, (timer_x, timer_y))
            
            effect_y_offset -= 35  # Adjust position for multiplier display if both are active
        
        # Show multiplier status if active with cool flashing effect
        if self.point_multiplier > 1.0:
            # Create pulsing alpha effect based on flash timer
            flash_phase = self.flash_timer / 60.0  # 0 to 1 over 2 seconds
            alpha_multiplier = 0.7 + 0.3 * abs(1 - 2 * flash_phase)  # Smooth pulse between 0.7 and 1.0
            
            # Calculate flashing color with slight color variation
            base_color = (255, 215, 0)  # Gold
            flash_color = (
                int(base_color[0] * alpha_multiplier),
                int(base_color[1] * alpha_multiplier), 
                int(min(255, base_color[2] + 50 * (1 - alpha_multiplier)))  # Add blue tint when dimmed
            )
            
            # Use smaller font for bonus text with dynamic multiplier
            multiplier_value = int(self.point_multiplier)
            multiplier_text = self.small_font.render('{}X POINTS!'.format(multiplier_value), False, flash_color)
            text_x = turret_x - multiplier_text.get_width() // 2  # Center text horizontally
            text_y = turret_y + effect_y_offset  # Position above turret, accounting for freeze display
            screen.blit(multiplier_text, (text_x, text_y))
            
            # Show timer with same effect but slightly different phase
            timer_seconds = self.multiplier_timer // 30
            timer_alpha = 0.8 + 0.2 * abs(1 - 2 * ((self.flash_timer + 15) % 60) / 60.0)
            timer_color = (
                int(base_color[0] * timer_alpha),
                int(base_color[1] * timer_alpha),
                int(base_color[2] * timer_alpha)
            )
            timer_text = self.small_font.render('{}s'.format(timer_seconds), False, timer_color)
            timer_x = turret_x - timer_text.get_width() // 2  # Center timer horizontally
            timer_y = text_y + 15  # Position below the multiplier text
            screen.blit(timer_text, (timer_x, timer_y))
        # TBC - draw the remaining ammo

    def update(self, missile_list, explosion_list, city_list):
        # generate incoming missiles
        if self.missile_frequency % self.missile_interval == 0 and self.missile_count < self.max_missile_count:
            # pick a key label for this missile (home row weighted)
            label = self._choose_key_label()
            # Calculate missile speed based on difficulty level
            missile_speed = self._calculate_missile_speed()
            missile_list.append(Missile(self.get_origin(), self.get_target(), True, missile_speed, 10, WARHEAD_TRAIL, WARHEAD, label))
            self.missile_count += 1
        # increment the frequency count
        self.missile_interval += 1
        if self.missile_interval > self.missile_loop:
            self.missile_interval = 1

        # check for collisions
        self.player_score += check_collisions(missile_list, explosion_list, city_list)

        # check if all cities have been destroyed
        if city_list == []:
            return GAME_STATE_OVER

        # start next level - check if all threats are cleared including mega explosions
        import __main__
        mega_explosion_list = getattr(__main__, 'mega_explosion_list', [])
        if missile_list == [] and explosion_list == [] and mega_explosion_list == []:
            return GAME_STATE_NEW_LEVEL

        return GAME_STATE_RUNNING

    # start new level
    def new_level(self, screen, defense):
        # set new level difficulty parameters
        self.max_missile_count += self.difficulty_increment
        self.missile_count = 0
        self.difficulty += 1
        self.difficulty_increment += self.difficulty
        self.missile_frequency = self.missile_loop - self.difficulty
        self.missile_interval = 1
        defense.set_ammo(30)

        # Inspirational quotes
        inspirational_quotes = [
            "Hard things get easier every time you try.",
            "Winners are just kids who didn't quit.",
            "Being brave doesn't mean you aren't scared—it means you try anyway.",
            "Mistakes are proof you are trying.",
            "A challenge is not a wall—it's a ladder.",
            "Believe in yourself first, and others will too.",
            "The strongest people smile even when things are hard.",
            "I believe there comes a time, when everything just falls in line, we live and learn from our mistakes, the deepest cuts are healed by FAITH!",
            "The difference between winners and losers is that winners get back up after getting kicked in the teeth."
        ]

        # display prompt for next level and give short pause
        new_level = game_font.render('NEW INBOUND MISSILES DETECTED', False, INTERFACE_SEC)
        get_ready = game_font.render('GET READY', False, INTERFACE_SEC)
        
        # Choose a random inspirational quote
        selected_quote = random.choice(inspirational_quotes)
        
        # Create larger, readable font for the quote
        quote_font = pygame.font.Font('data/fnt/PressStart2P-Regular.ttf', 12)  # Much bigger font for readability
        
        # Split quote into multiple lines if too long to fit on screen
        max_chars_per_line = 45  # Reduced for larger font to fit screen width
        quote_lines = []
        words = selected_quote.split()
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars_per_line:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    quote_lines.append(current_line)
                current_line = word
        if current_line:
            quote_lines.append(current_line)
        
        # Position elements to avoid overlap - move main text higher to make room
        new_level_pos = (SCREENSIZE[0] // 2 - (new_level.get_width() // 2),
                            SCREENSIZE[1] // 2 - (new_level.get_height() // 2) - 60)  # Moved up more
        get_ready_pos = (SCREENSIZE[0] // 2 - (get_ready.get_width() // 2),
                            new_level_pos[1] + new_level.get_height() + 15)  # More spacing
        
        # Draw main level text
        screen.blit(new_level, new_level_pos)
        screen.blit(get_ready, get_ready_pos)
        
        # Draw inspirational quote below the main text with generous spacing
        quote_start_y = get_ready_pos[1] + get_ready.get_height() + 40  # More spacing from main text
        for i, line in enumerate(quote_lines):
            quote_surface = quote_font.render(line, False, (255, 215, 0))  # Gold color for better visibility
            quote_pos = (SCREENSIZE[0] // 2 - (quote_surface.get_width() // 2),
                        quote_start_y + i * (quote_surface.get_height() + 5))  # More line spacing
            screen.blit(quote_surface, quote_pos)
    
    # game over - all cities destroyed
    def game_over(self, screen):
        # display prompt for next level and give short pause
        game_over_msg = game_font.render('YOU\'RE CITIES HAVE BEEN ANNIHILATED', False, INTERFACE_SEC)
        score_msg = game_font.render('SCORE: {}'.format(self.player_score), False, INTERFACE_SEC)
        game_over_msg_pos = (SCREENSIZE[0] // 2 - (game_over_msg.get_width() // 2),
                            SCREENSIZE[1] // 2 - (game_over_msg.get_height() // 2))
        score_msg_pos = (SCREENSIZE[0] // 2 - (score_msg.get_width() // 2),
                            SCREENSIZE[1] // 2 - (score_msg.get_height() // 2) + game_over_msg.get_height())
        screen.blit(game_over_msg, game_over_msg_pos)
        screen.blit(score_msg, score_msg_pos)

    # returns a target for new incoming nukes
    def get_target(self):
        # select a random point along the x axis at ground level
        return (random.randint(0, SCREENSIZE[0]), self.ground_level)
    
    def get_origin(self):
        # select a random entry point for nuke
        return (random.randint(0, SCREENSIZE[0]), SKY_LEVEL)

    def set_difficulty(self, new_difficulty):
        self.difficulty = new_difficulty
    
    def get_player_score(self):
        return self.player_score
    
    def activate_powerup(self, defense=None, powerup_type="multiplier", powerup_pos=None):
        if powerup_type == "freeze":
            # Activate freeze effect for 6 seconds
            self.freeze_timer = 180  # 6 seconds at 30 FPS (increased by 2 seconds)
            self.is_frozen = True
            
            # Turn turret blue when freeze is active
            if defense is not None:
                defense.activate_freeze()
                
        elif powerup_type == "explosion":
            # Create massive explosion at powerup position
            # The explosion effect is handled in the main game loop
            # This method just returns the signal to create the explosion
            return {"create_mega_explosion": True, "position": powerup_pos}
            
        else:  # multiplier powerup
            # Stack multiplier if already active, otherwise start at 2x
            if self.point_multiplier > 1.0:
                self.point_multiplier += 1.0  # Stack: 2x -> 3x -> 4x etc.
            else:
                self.point_multiplier = 2.0   # First powerup: 1x -> 2x
            
            # Reset timer to 10 seconds (extends duration)
            self.multiplier_timer = 300  # 10 seconds at 30 FPS
            
            # Turn turret orange when multiplier powerup is active
            if defense is not None:
                defense.activate_powerup()
                
        return None
        
    def update_powerup_system(self, defense=None):
        # Update multiplier timer
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer <= 0:
                self.point_multiplier = 1.0  # Reset to normal
                # Reset turret color when powerup expires (only if not frozen)
                if defense is not None and not self.is_frozen:
                    defense.deactivate_powerup()
        
        # Update freeze timer
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.is_frozen = False
                # Reset turret color when freeze expires (unless multiplier is active)
                if defense is not None:
                    if self.point_multiplier > 1.0:
                        defense.activate_powerup()  # Return to multiplier color
                    else:
                        defense.deactivate_freeze()  # Return to normal
        
        # Update flash timer for cool effects
        self.flash_timer += 1
        if self.flash_timer > 60:  # Reset every 2 seconds at 30 FPS
            self.flash_timer = 0
        
        # Update powerup spawn timer
        self.powerup_spawn_timer += 1
        
    def should_spawn_powerup(self):
        # Spawn powerup roughly every 20-30 seconds, randomly
        if self.powerup_spawn_timer > random.randint(600, 900):  # 20-30 seconds at 30 FPS
            self.powerup_spawn_timer = 0
            return True
        return False
    
    def add_score(self, points):
        # Add points with current multiplier
        self.player_score += int(points * self.point_multiplier)
    
    def award_city_bonuses(self, city_list):
        # Award 100 points for each surviving city at level end
        city_bonus = len(city_list) * 100
        self.player_score += city_bonus
        return city_bonus

    # choose a keyboard key label with home-row bias, or words for higher levels
    def _choose_key_label(self):
        if self.difficulty == 1:
            # Level 1: Only home row characters (easiest)
            home_row = list("asdfghjkl")
            return random.choice(home_row)
        elif self.difficulty == 2:
            # Level 2: All single characters with home row bias
            top_row = list("qwertyuiop")
            home_row = list("asdfghjkl")
            bottom_row = list("zxcvbnm")
            keys = top_row + home_row + bottom_row
            weights = ([1] * len(top_row)) + ([5] * len(home_row)) + ([2] * len(bottom_row))
            try:
                return random.choices(keys, weights=weights, k=1)[0]
            except Exception:
                # fallback if choices unavailable
                bag = top_row + home_row * 5 + bottom_row * 2
                return random.choice(bag)
        else:
            # Multi-character words for level 3+
            return self._choose_word()
    
    def _choose_word(self):
        # Import conflict checking functions from main module
        import __main__
        can_add_word = getattr(__main__, 'can_add_word', lambda x: True)
        
        # Word lists based on difficulty level with Gen Alpha shorthand
        # Home row biased 2-letter words (easy to type)
        two_letter_words = ["as", "ad", "ah", "if", "is", "of", "go", "do", "so", "to", "at", "it", "up", "hi", "he", "ha", "fr", "np", "ig", "fs"]
        three_letter_words = ["cat", "dog", "run", "car", "sun", "red", "big", "hot", "old", "new", "win", "try", "get", "hit", "riz", "sus", "mid", "lit", "cap", "fax", "bet", "ong", "idc", "lol", "imo", "ngl", "rip", "say", "bye", "omg"]
        four_letter_words = ["fire", "help", "jump", "fast", "slow", "cold", "blue", "dark", "long", "safe", "game", "time", "stop", "vibe", "flex", "slay", "yeet", "chad", "goat", "stan", "mood", "fomo", "simp", "cope", "edgy", "king", "giga", "poke"]
        five_letter_words = ["power", "laser", "blast", "storm", "quick", "magic", "space", "fight", "brave", "peace", "skill", "vibes", "based", "bruh", "sigma", "alpha", "ratio", "cringe", "queen", "chief", "slaps", "bussin", "lowkey", "highkey"]
        six_letter_words = ["defend", "shield", "attack", "weapon", "strong", "danger", "flight", "battle", "energy", "launch", "locked", "salty", "savage", "clutch", "periodt", "whatev"]
        long_words = ["missile", "defense", "protect", "freedom", "victory", "command", "destroy", "counter", "nuclear", "warfare", "periodt", "ghosted", "lowkey", "highkey", "cappin", "snatched", "pressed"]
        
        # Helper function to choose word without conflicts
        def choose_without_conflict(word_list, max_attempts=50):
            for _ in range(max_attempts):
                word = random.choice(word_list)
                if can_add_word(word):
                    return word
            # Fallback: return first available word or any word if none available
            for word in word_list:
                if can_add_word(word):
                    return word
            return random.choice(word_list)  # Last resort
        
        # Progressive difficulty: start with 2-letter, gradually add longer words
        if self.difficulty <= 3:
            # Levels 3: Only 2-letter words
            return choose_without_conflict(two_letter_words)
        elif self.difficulty <= 5:
            # Levels 4-5: Mix of 2 and 3 letter words
            return choose_without_conflict(two_letter_words + three_letter_words)
        elif self.difficulty <= 7:
            # Levels 6-7: Mostly 3-letter, some 2-letter
            return choose_without_conflict(two_letter_words + three_letter_words * 3)  # Weight 3-letter more
        elif self.difficulty <= 9:
            # Levels 8-9: 3 and 4 letter words
            return choose_without_conflict(three_letter_words + four_letter_words)
        elif self.difficulty <= 12:
            # Levels 10-12: 4 and 5 letter words
            return choose_without_conflict(four_letter_words + five_letter_words)
        elif self.difficulty <= 16:
            # Levels 13-16: 5 and 6 letter words
            return choose_without_conflict(five_letter_words + six_letter_words)
        else:
            # Level 17+: 6+ letter words
            return choose_without_conflict(six_letter_words + long_words)
    
    def _calculate_missile_speed(self):
        # Progressive speed scaling: slow start, medium at level 10, very fast at level 20+
        if self.difficulty == 1:
            return 0.5  # Very slow for level 1
        elif self.difficulty <= 3:
            return 0.7  # Still slow for early levels
        elif self.difficulty <= 6:
            return 1.0  # Normal speed
        elif self.difficulty <= 10:
            return 1.3  # Medium difficulty at level 10
        elif self.difficulty <= 15:
            return 1.7  # Getting harder
        elif self.difficulty <= 20:
            return 2.2  # Very hard at level 20
        else:
            return 2.5 + (self.difficulty - 20) * 0.2  # Mega hard beyond level 20
