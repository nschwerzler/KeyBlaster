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
# Ignore all mouse events to enforce keyboard-only controls
try:
    pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL])
except Exception:
    pass
try:
    from functions import init_audio
    init_audio()
except Exception:
    pass

# Typing behavior
ALLOWED_TYPING_KEYS = set(list("qwertyuiop") + list("asdfghjkl;") + list("zxcvbnm"))  # labels include 'p'
RESERVED_TYPING_KEYS = set()  # no reserved typing keys; only ESC pauses

# Global variable to track which missile is currently being typed
current_typing_target = None


def main():
    global current_game_state, current_typing_target

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
            if event.type == KEYDOWN:
                # ESC pauses the game (no exit prompt)
                if event.key == K_ESCAPE:
                    pause_game(screen)

                handled = False
                # typing-driven interception: if a labeled key is pressed, trigger an explosion
                # use event.unicode for character; ignore non-printable keys
                if hasattr(event, 'unicode') and event.unicode:
                    ch = event.unicode.lower()
                    # react to printable single characters that aren't reserved hotkeys
                    printable_key = len(ch) == 1 and ch.isprintable() and ch not in RESERVED_TYPING_KEYS
                    target_missile = None
                    
                    if printable_key:
                        # Check if we have a current typing target that's still valid
                        if current_typing_target is not None and current_typing_target in missile_list:
                            if getattr(current_typing_target, 'label', None):
                                label_str = str(current_typing_target.label).lower()
                                typed_str = getattr(current_typing_target, 'typed_chars', '').lower()
                                
                                # Check if this character continues the current target
                                next_expected_char = label_str[len(typed_str)] if len(typed_str) < len(label_str) else None
                                
                                if next_expected_char == ch:
                                    target_missile = current_typing_target
                                # If we have a current target but wrong character, don't look for new targets
                                # This prevents switching words mid-typing
                        
                        # Only find a new target if we don't have a current one
                        elif target_missile is None:
                            closest_remaining = None
                            # Find missiles that can start with this character (only fresh missiles)
                            for m in missile_list:
                                if getattr(m, 'label', None) and getattr(m, 'typed_chars', '') == '':
                                    label_str = str(m.label).lower()
                                    
                                    # Check if this character starts this missile's word
                                    if label_str.startswith(ch):
                                        remaining = max(0, m.dist_to_target - m.travel_dist)
                                        if closest_remaining is None or remaining < closest_remaining:
                                            closest_remaining = remaining
                                            target_missile = m
                    
                    if target_missile is not None:
                        # Set this as our current typing target
                        current_typing_target = target_missile
                        
                        # Add the typed character to the missile's progress
                        target_missile.typed_chars += ch
                        
                        # Check if the word is complete
                        if target_missile.typed_chars.lower() == str(target_missile.label).lower():
                            # Word complete - destroy missile and clear target
                            lead_pos = target_missile.get_future_pos(pixels_ahead=20)
                            explosion_list.append(Explosion(lead_pos, 1, INTERCEPT_RADIUS, INTERCEPT_EXPLOSION))
                            target_missile.label = None
                            current_typing_target = None
                            try:
                                from functions import play_random_explode
                                play_random_explode()
                            except Exception:
                                pass
                        handled = True
                    elif printable_key:
                        # wrong typing key: if we had a current target, clear it and reset that missile
                        if current_typing_target is not None and current_typing_target in missile_list:
                            current_typing_target.typed_chars = ""  # Reset the missile's progress
                            current_typing_target = None  # Clear the target
                        
                        # Play miss sound
                        try:
                            from functions import play_random_miss
                            play_random_miss()
                        except Exception:
                            pass

                # Spacebar firing disabled - typing only game
                # if not handled and event.key == K_SPACE:
                #     defence.shoot(missile_list)
                # 'p' no longer pauses; only ESC toggles pause
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
                # Clear typing target if this missile was being typed
                if missile == current_typing_target:
                    current_typing_target = None
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
            # Clear typing target when starting new level
            current_typing_target = None
            mcgame.new_level(screen, defence)
        
        # Update the display
        pygame.display.update()

        # hold for few seconds before starting new level
        if current_game_state == GAME_STATE_NEW_LEVEL:
            time.sleep(3)
            current_game_state = GAME_STATE_RUNNING
        
        # hold for few seconds before proceeding to high-score or back to menu or game over splash
        if current_game_state == GAME_STATE_OVER:
            # Create a wider input box and allow at least 10 chars
            input_box = InputBox(SCREENSIZE[0]//2 - 150, SCREENSIZE[1]//2 + 70, 300, 32, max_len=10)
            name = ""
            while input_box.check_finished() == False:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    if event.type == KEYDOWN and event.key == K_ESCAPE:
                        # allow pause on ESC during game over as well
                        pause_game(screen)
                    input_box.handle_event(event)
                input_box.update()

                # redraw game over screen + prompt each frame
                screen.fill(BACKGROUND)
                # draw game over text and score with spacing
                # use same text as mcgame.game_over but manage vertical spacing to avoid overlap
                game_over_msg = game_font.render("YOU'RE CITIES HAVE BEEN ANNIHILATED", False, INTERFACE_SEC)
                score_msg = game_font.render('SCORE: {}'.format(mcgame.get_player_score()), False, INTERFACE_SEC)
                go_y = SCREENSIZE[1]//2 - game_over_msg.get_height() - 20
                score_y = go_y + game_over_msg.get_height() + 10
                screen.blit(game_over_msg, (SCREENSIZE[0]//2 - (game_over_msg.get_width()//2), go_y))
                screen.blit(score_msg, (SCREENSIZE[0]//2 - (score_msg.get_width()//2), score_y))

                prompt = game_font.render('ENTER NAME (10) THEN PRESS ENTER', False, INTERFACE_SEC)
                prompt_y = score_y + score_msg.get_height() + 20
                screen.blit(prompt, (SCREENSIZE[0]//2 - (prompt.get_width()//2), prompt_y))
                input_box.draw(screen)
                pygame.display.update()

            name = input_box.text if input_box.text else "---"
            # update and save high scores
            try:
                score = mcgame.get_player_score()
                high_scores = update_high_scores(score, name, high_scores)
                save_high_scores("scores.json", high_scores)
            except Exception:
                pass

            current_game_state = GAME_STATE_MENU
        
        # display the high scores
        if current_game_state == GAME_STATE_MENU:
            show_high_scores(screen, high_scores)
            current_game_state = 0

        # run at pre-set fps
        clock.tick(FPS)


if __name__ == '__main__':
    main()
