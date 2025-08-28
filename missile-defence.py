import pygame
import sys
#from pygame.locals import *
#import os
import random
#import math
import time

from config import *
from functions import *
from city import City
from missile import Missile
from explosion import Explosion
from defence import Defence
from mcgame import McGame
from text import InputBox


# Initialize game engine, screen and clock
pygame.init()
#pygame.mixer.init()
screen = pygame.display.set_mode(SCREENSIZE)
pygame.mouse.set_visible(SHOW_MOUSE)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
try:
    from functions import init_audio
    init_audio()
except Exception:
    pass

# Typing keys allowed (matches label generation; excludes 'p' pause key)
ALLOWED_TYPING_KEYS = set(list("qwertyuio") + list("asdfghjkl;") + list("zxcvbnm"))


def main():
    global current_game_state

    # load high-score file
    high_scores = load_scores("scores.json")
    
    # set the random seed - produces more random trajectories
    random.seed()

    #  list of all active explosions
    explosion_list = []
    # list of all active missiles
    missile_list = []
    # TBC - generate the cities
    # need to be replaced with working cities
    city_list = []
    for i in range(1, 8):   # 8 == Max num cities plus defence plus one
        if i == 8 // 2:     # find centre point for gun
            pass
        else:
            city_list.append(City(i, 7))   # 7 == max num cities plus guns
    # Intercepter gun
    defence = Defence()

    # set the game running
    current_game_state = GAME_STATE_RUNNING

    show_high_scores(screen, high_scores)

    # setup the MCGAME AI
    mcgame = McGame(1, high_scores["1"]["score"])

    while True:
        # write event handlers here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    # primary mouse button
                    defence.shoot(missile_list)
                if event.button == 2:
                    # middle mouse button
                    pass
                if event.button == 3:
                    # right mouse button
                    pass
            if event.type == KEYDOWN:
                # Always allow immediate exit
                if event.key == K_ESCAPE:
                    exit_game(screen)

                handled = False
                # typing-driven interception: if a labeled key is pressed, trigger an explosion
                # use event.unicode for character; ignore non-printable keys
                if hasattr(event, 'unicode') and event.unicode:
                    ch = event.unicode.lower()
                    # only react to typing keys used for labels
                    valid_typing_key = ch in ALLOWED_TYPING_KEYS
                    # find the best matching missile (closest to impact)
                    target_missile = None
                    closest_remaining = None
                    if valid_typing_key:
                        for m in missile_list:
                            if getattr(m, 'label', None) and str(m.label).lower() == ch:
                                remaining = max(0, m.dist_to_target - m.travel_dist)
                                if closest_remaining is None or remaining < closest_remaining:
                                    closest_remaining = remaining
                                    target_missile = m
                    if target_missile is not None:
                        # spawn an intercept explosion slightly ahead of the missile to lead it
                        lead_pos = target_missile.get_future_pos(pixels_ahead=20)
                        explosion_list.append(Explosion(lead_pos, 1, INTERCEPT_RADIUS, INTERCEPT_EXPLOSION))
                        # optionally, clear label so repeated keypresses don't spam
                        target_missile.label = None
                        handled = True
                        try:
                            from functions import play_random_explode
                            play_random_explode()
                        except Exception:
                            pass
                    elif valid_typing_key:
                        # wrong typing key (not present on screen): play annoying system sound
                        try:
                            from functions import sfx_wrong_key
                            sfx_wrong_key()
                        except Exception:
                            pass

                # legacy controls only if not handled by typing action
                if not handled and event.key == K_SPACE:
                    defence.shoot(missile_list)
                if not handled and event.key == K_p:
                    pause_game(screen)
            if event.type == KEYUP:
                pass

        # clear the screen before drawing
        screen.fill(BACKGROUND)

        # Game logic and draws
        
        # --- cities
        for city in city_list:
            city.draw(screen)
        
        # --- interceptor turret
        defence.update()
        defence.draw(screen)
        
        # --- missiles
        for missile in missile_list[:]:
            missile.update(explosion_list)
            missile.draw(screen)
            if missile.detonated:
                missile_list.remove(missile)
        
        # --- explosions
        for explosion in explosion_list[:]:
            explosion.update()
            explosion.draw(screen)
            if explosion.complete:
                explosion_list.remove(explosion)

        # --- Draw the interface 
        mcgame.draw(screen, defence)

        # --- update game mcgame
        if current_game_state == GAME_STATE_RUNNING:
            current_game_state = mcgame.update(missile_list, explosion_list, city_list)

        # load message for Game Over and proceed to high-score / menu
        if current_game_state == GAME_STATE_OVER:
            mcgame.game_over(screen)

        # load a message and set new game values for start new level
        if current_game_state == GAME_STATE_NEW_LEVEL:
            mcgame.new_level(screen, defence)
        
        # Update the display
        pygame.display.update()

        # hold for few seconds before starting new level
        if current_game_state == GAME_STATE_NEW_LEVEL:
            time.sleep(3)
            current_game_state = GAME_STATE_RUNNING
        
        # hold for few seconds before proceeding to high-score or back to menu or game over splash
        if current_game_state == GAME_STATE_OVER:
            input_box = InputBox(100, 100, 140, 32)
            while input_box.check_finished() == False:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    input_box.handle_event(event)
                input_box.update()
                input_box.draw(screen)
                
            current_game_state = GAME_STATE_MENU
        
        # display the high scores
        if current_game_state == GAME_STATE_MENU:
            show_high_scores(screen, high_scores)
            current_game_state = 0

        # run at pre-set fps
        clock.tick(FPS)


if __name__ == '__main__':
    main()
