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

    def draw(self, screen, defence):
        # draw the HUD, score, etc
        pygame.draw.line(screen, INTERFACE_PRI, [0, SKY_LEVEL], [SCREENSIZE[0], SKY_LEVEL], 2)
        pygame.draw.rect(screen, INTERFACE_PRI, (0, SCREENSIZE[1] - GROUND_LEVEL, SCREENSIZE[0], SCREENSIZE[1]))
        score_text = game_font.render('SCORE: {}'.format(self.player_score), False, INTERFACE_SEC)
        screen.blit(score_text, (5, 10))
        screen.blit(self.high_score_text, (self.high_score_text_pos, 10))
        ammo_text = game_font.render('AMMO: {}'.format(defence.get_ammo()), False, INTERFACE_SEC)
        screen.blit(ammo_text, (SCREENSIZE[0] // 2 - (ammo_text.get_width() // 2), 10))
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

        # start next level
        if missile_list == [] and explosion_list == []:
            return GAME_STATE_NEW_LEVEL

        return GAME_STATE_RUNNING

    # start new level
    def new_level(self, screen, defence):
        # set new level difficulty parameters
        self.max_missile_count += self.difficulty_increment
        self.missile_count = 0
        self.difficulty += 1
        self.difficulty_increment += self.difficulty
        self.missile_frequency = self.missile_loop - self.difficulty
        self.missile_interval = 1
        defence.set_ammo(30)


        # display prompt for next level and give short pause
        new_level = game_font.render('NEW INBOUND MISSILES DETECTED', False, INTERFACE_SEC)
        get_ready = game_font.render('GET READY', False, INTERFACE_SEC)
        new_level_pos = (SCREENSIZE[0] // 2 - (new_level.get_width() // 2),
                            SCREENSIZE[1] // 2 - (new_level.get_height() // 2))
        get_ready_pos = (SCREENSIZE[0] // 2 - (get_ready.get_width() // 2),
                            SCREENSIZE[1] // 2 - (get_ready.get_height() // 2) + new_level.get_height())
        screen.blit(new_level, new_level_pos)
        screen.blit(get_ready, get_ready_pos)
    
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

    # choose a keyboard key label with home-row bias, or words for higher levels
    def _choose_key_label(self):
        if self.difficulty < 3:
            # Single characters for levels 1-2
            top_row = list("qwertyuiop")
            home_row = list("asdfghjkl;")
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
        # Word lists based on difficulty level
        three_letter_words = ["cat", "dog", "run", "car", "sun", "red", "big", "hot", "old", "new"]
        four_letter_words = ["fire", "help", "jump", "fast", "slow", "cold", "blue", "dark", "long", "safe"]
        five_letter_words = ["power", "laser", "blast", "storm", "quick", "magic", "space", "fight", "brave", "peace"]
        six_letter_words = ["defend", "shield", "attack", "weapon", "strong", "danger", "flight", "battle", "energy", "launch"]
        long_words = ["missile", "defense", "protect", "freedom", "victory", "command", "destroy", "counter", "nuclear", "warfare"]
        
        if self.difficulty <= 5:
            return random.choice(three_letter_words)
        elif self.difficulty <= 8:
            return random.choice(three_letter_words + four_letter_words)
        elif self.difficulty <= 12:
            return random.choice(four_letter_words + five_letter_words)
        elif self.difficulty <= 16:
            return random.choice(five_letter_words + six_letter_words)
        else:
            return random.choice(six_letter_words + long_words)
    
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
