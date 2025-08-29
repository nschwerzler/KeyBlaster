import pygame
import sys
#from pygame.locals import *
import os
import random
#import math
import time
import atexit
import glob

from config import *
from functions import *
from city import City
from missile import Missile
from explosion import Explosion
from defense import Defense
from mcgame import McGame
from powerup import Powerup
from text import InputBox
from replay import start_recording, stop_recording, get_recorder, ReplayPlayer


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

# Global variable to track typed sequence
typed_sequence = ""  # Current sequence of typed characters

# Global set to track active word prefixes (first 2 characters) to avoid conflicts
active_word_prefixes = set()

# Delayed destruction system for turret animation
pending_destruction = None  # Target waiting for destruction
destruction_timer = 0       # Timer for destruction delay
destruction_queue = []      # Queue of targets waiting for destruction

# Temporary turbo mode system
turbo_timer = 0             # Timer for temporary turbo mode
turbo_duration = 15         # Frames for turbo mode (0.5 seconds at 30 FPS)

def get_word_prefix(word):
    """Get the first 2 characters of a word for conflict checking"""
    if not word or len(word) < 2:
        return word.lower() if word else ""
    return word[:2].lower()

def can_add_word(word):
    """Check if a word can be added without prefix conflicts"""
    prefix = get_word_prefix(word)
    return prefix not in active_word_prefixes

def add_word_prefix(word):
    """Add a word's prefix to the active set"""
    prefix = get_word_prefix(word)
    if prefix:
        active_word_prefixes.add(prefix)

def remove_word_prefix(word):
    """Remove a word's prefix from the active set"""
    prefix = get_word_prefix(word)
    if prefix and prefix in active_word_prefixes:
        active_word_prefixes.discard(prefix)


def main():
    global current_game_state, typed_sequence, active_word_prefixes, pending_destruction, destruction_timer, destruction_queue, turbo_timer

    # Start replay recording
    recorder = start_recording()
    
    # Register exit handler to save replay on any program termination
    def save_replay_on_exit():
        if recorder and recorder.recording:
            recorder.record_event("program_exit", {"reason": "unexpected_termination"})
            filename = recorder.save()
            print(f"Replay auto-saved on exit: {filename}")
    
    atexit.register(save_replay_on_exit)
    
    # load high-score file
    high_scores = load_scores("scores.json")
    
    # set the random seed - this is now handled by replay system for deterministic recording
    # random.seed() - removed, replay system manages this

    #  list of all active explosions
    explosion_list = []
    # list of all active missiles
    missile_list = []
    powerup_list = []
    # TBC - generate the cities
    # need to be replaced with working cities
    city_list = []
    for i in range(1, 8):   # 8 == Max num cities plus defense plus one
        if i == 8 // 2:     # find centre point for gun
            pass
        else:
            city_list.append(City(i, 7))   # 7 == max num cities plus guns
    # Intercepter gun
    defense = Defense()

    # set the game running
    current_game_state = GAME_STATE_RUNNING

    show_high_scores(screen, high_scores)

    # setup the MCGAME AI
    mcgame = McGame(1, high_scores["1"]["score"])
    
    # Track turbo mode for testing
    turbo_mode = False
    
    # Auto-save timer for replays
    last_auto_save = time.time()
    auto_save_interval = 30  # Auto-save every 30 seconds

    while True:
        # write event handlers here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Auto-save replay before exiting
                if recorder:
                    filename = stop_recording()
                    print(f"Replay auto-saved as: {filename}")
                pygame.quit()
                sys.exit(0)
            if event.type == KEYDOWN:
                # Record keypress for replay
                if recorder:
                    key_char = getattr(event, 'unicode', '') if hasattr(event, 'unicode') else ''
                    recorder.record_keypress(key_char, event.key)
                
                # ESC pauses the game (no exit prompt)
                if event.key == K_SPACE:
                    turbo_mode = True  # Enable turbo mode when space pressed
                elif event.key == K_ESCAPE:
                    pause_game(screen)
                elif event.key == K_F12:  # F12 to copy latest replay path to clipboard
                    # Get the replay path to display/copy
                    replay_path = None
                    if recorder and recorder.filename:
                        # Use the current recording file path
                        replay_path = recorder.filename
                    else:
                        # Find the most recent replay file
                        from replay import get_replay_directory
                        replay_dir = get_replay_directory()
                        pattern = os.path.join(replay_dir, "replay_*.json")
                        replay_files = glob.glob(pattern)
                        
                        if replay_files:
                            # Get the most recently modified file
                            replay_path = max(replay_files, key=os.path.getmtime)
                    
                    if replay_path:
                        # Try to copy to clipboard
                        try:
                            import pyperclip
                            pyperclip.copy(replay_path)
                            print(f"Replay path copied to clipboard: {replay_path}")
                        except ImportError:
                            # Fallback: just display the path for manual copying
                            print("=" * 60)
                            print("REPLAY PATH (copy manually):")
                            print(replay_path)
                            print("=" * 60)
                            print("Note: Install 'pip install pyperclip' for automatic clipboard copy")
                        except Exception as e:
                            # Show path even if clipboard fails
                            print(f"Clipboard failed, but here's the path: {replay_path}")
                            print(f"Error: {e}")
                    else:
                        print("No replay files found")

                handled = False
                # typing-driven interception: sequence matching system
                if hasattr(event, 'unicode') and event.unicode:
                    ch = event.unicode.lower()
                    # react to printable single characters that aren't reserved hotkeys
                    printable_key = len(ch) == 1 and ch.isprintable() and ch not in RESERVED_TYPING_KEYS
                    
                    if printable_key and ch in ALLOWED_TYPING_KEYS:
                        # Add character to typed sequence
                        typed_sequence += ch
                        
                        # Check for complete word matches (find words within the sequence)
                        completed_targets = []
                        words_found = []
                        
                        # Collect all words on screen (normalize to lowercase for comparison)
                        all_words = []
                        for p in powerup_list:
                            if getattr(p, 'label', None):
                                all_words.append(('powerup', p, str(p.label).lower()))
                        for m in missile_list:
                            if getattr(m, 'label', None):
                                all_words.append(('missile', m, str(m.label).lower()))
                        
                        # Find completed words in the typed sequence (case insensitive)
                        sequence_to_check = typed_sequence.lower()  # Convert to lowercase for matching
                        
                        # Sort words by length (longest first) to prioritize longer matches
                        all_words.sort(key=lambda x: len(x[2]), reverse=True)
                        
                        # Check each word to see if it can be formed from the sequence characters
                        for target_type, target_obj, word in all_words:
                            # Check if all characters of the word can be found in the sequence
                            sequence_chars = list(sequence_to_check)
                            can_form_word = True
                            for char in word:
                                if char in sequence_chars:
                                    sequence_chars.remove(char)  # Remove used character
                                else:
                                    can_form_word = False
                                    break
                            
                            if can_form_word:
                                completed_targets.append((target_type, target_obj))
                                words_found.append(word)
                                # Record successful word match
                                if recorder:
                                    recorder.record_word_match(word, target_type, True)
                                # Remove word characters from sequence for future matches
                                for char in word:
                                    if char in sequence_to_check:
                                        sequence_to_check = sequence_to_check.replace(char, "", 1)
                        
                        # Process completed words
                        if completed_targets:
                            for target_type, target_obj in completed_targets:
                                if pending_destruction is None:
                                    # Start destruction immediately
                                    defense.aim_at_target(target_obj)
                                    pending_destruction = (target_type, target_obj)
                                    destruction_timer = 0
                                else:
                                    # Queue for later destruction
                                    destruction_queue.append((target_type, target_obj))
                            
                            # Clear the typed sequence since we found and processed matches
                            # In a queue system, once words are matched, we start fresh
                            typed_sequence = ""
                            handled = True
                        else:
                            # Check if current sequence has any potential matches (case insensitive)
                            has_potential_match = False
                            typed_lower = typed_sequence.lower()
                            for m in missile_list:
                                if getattr(m, 'label', None):
                                    if str(m.label).lower().find(typed_lower) != -1:
                                        has_potential_match = True
                                        break
                            if not has_potential_match:
                                for p in powerup_list:
                                    if getattr(p, 'label', None):
                                        if str(p.label).lower().find(typed_lower) != -1:
                                            has_potential_match = True
                                            break
                            
                            if not has_potential_match:
                                # No potential matches - check if key exists on screen at all
                                key_on_screen = False
                                for m in missile_list:
                                    if getattr(m, 'label', None) and ch in str(m.label).lower():
                                        key_on_screen = True
                                        break
                                if not key_on_screen:
                                    for p in powerup_list:
                                        if getattr(p, 'label', None) and ch in str(p.label).lower():
                                            key_on_screen = True
                                            break
                                
                                if not key_on_screen:
                                    # Key not on screen anywhere - activate temporary turbo mode
                                    turbo_timer = turbo_duration
                                
                                # Reset sequence and play miss sound
                                typed_sequence = ""
                                try:
                                    from functions import play_random_miss
                                    play_random_miss()
                                except Exception:
                                    pass
                                handled = True
                            # If has_potential_match is True, we don't reset the sequence and keep building it
                    elif printable_key:
                        # Invalid key - reset sequence
                        typed_sequence = ""
                        try:
                            from functions import play_random_miss
                            play_random_miss()
                        except Exception:
                            pass

                # Spacebar firing disabled - typing only game
                # if not handled and event.key == K_SPACE:
                #     defense.shoot(missile_list)
                # 'p' no longer pauses; only ESC toggles pause
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    turbo_mode = False  # Disable turbo mode when space released

        # clear the screen before drawing
        screen.fill(BACKGROUND)

        # Game logic and draws
        
        # Record game state periodically for replay verification
        if recorder and pygame.time.get_ticks() % 1000 < 50:  # Record every ~1 second
            current_level = getattr(mcgame, 'difficulty', 1) if 'mcgame' in locals() else 1
            current_score = getattr(mcgame, 'player_score', 0) if 'mcgame' in locals() else 0
            recorder.record_game_state(missile_list, powerup_list, typed_sequence, current_level, current_score)
        
        # Auto-save replay periodically
        current_time = time.time()
        if recorder and (current_time - last_auto_save) >= auto_save_interval:
            recorder.save()
            last_auto_save = current_time
        
        # --- cities
        for city in city_list:
            city.draw(screen)
        
        # --- interceptor turret
        defense.update()
        defense.draw(screen)
        
        # --- missiles
        for missile in missile_list[:]:
            missile.update(explosion_list)
            missile.draw(screen)
            if missile.detonated:
                # Remove word prefix from tracking
                if hasattr(missile, 'label') and missile.label:
                    remove_word_prefix(missile.label)
                missile_list.remove(missile)
        
        # --- powerups
        for powerup in powerup_list[:]:
            if not powerup.update():
                # Remove word prefix from tracking
                if hasattr(powerup, 'label') and powerup.label:
                    remove_word_prefix(powerup.label)
                powerup_list.remove(powerup)
            else:
                powerup.draw(screen)
        
        # --- explosions
        for explosion in explosion_list[:]:
            explosion.update()
            explosion.draw(screen)
            if explosion.complete:
                explosion_list.remove(explosion)

        # --- Draw the interface 
        mcgame.draw(screen, defense)

        # --- update game mcgame
        if current_game_state == GAME_STATE_RUNNING:
            # Update powerup system
            mcgame.update_powerup_system(defense)
            
            # Spawn powerup occasionally
            if mcgame.should_spawn_powerup():
                side = random.choice(["left", "right"])
                powerup_list.append(Powerup(side))
            
            current_game_state = mcgame.update(missile_list, explosion_list, city_list)
            
            # Track word prefixes for newly created missiles
            for missile in missile_list:
                if hasattr(missile, 'label') and missile.label and not hasattr(missile, '_prefix_tracked'):
                    add_word_prefix(missile.label)
                    missile._prefix_tracked = True
            
            # Track word prefixes for newly created powerups
            for powerup in powerup_list:
                if hasattr(powerup, 'label') and powerup.label and not hasattr(powerup, '_prefix_tracked'):
                    add_word_prefix(powerup.label)
                    powerup._prefix_tracked = True
            
            # Handle delayed destruction after turret aiming
            if pending_destruction is not None:
                destruction_timer += 1
                target_type, target_obj = pending_destruction
                
                # Check if turret has finished aiming
                if defense.is_aiming_complete():
                    if target_type == 'missile':
                        # Fire laser beam and destroy missile
                        lead_pos = target_obj.get_future_pos(pixels_ahead=20)
                        defense.fire_laser(lead_pos)
                        explosion_list.append(Explosion(lead_pos, 1, INTERCEPT_RADIUS, INTERCEPT_EXPLOSION))
                        # Remove word prefix from tracking before clearing label
                        if hasattr(target_obj, 'label') and target_obj.label:
                            remove_word_prefix(target_obj.label)
                        target_obj.label = None
                        try:
                            from functions import play_random_explode
                            play_random_explode()
                        except Exception:
                            pass
                    elif target_type == 'powerup':
                        # Fire laser beam and destroy powerup
                        if hasattr(target_obj, 'get_pos'):
                            powerup_pos = target_obj.get_pos()
                        else:
                            powerup_pos = (target_obj.pos[0], target_obj.pos[1])
                        defense.fire_laser(powerup_pos)
                        
                        # Add explosion effect for powerup destruction
                        explosion_list.append(Explosion(powerup_pos, 1, INTERCEPT_RADIUS, INTERCEPT_EXPLOSION))
                        
                        mcgame.activate_powerup(defense)
                        mcgame.add_score(target_obj.destroy())
                        # Remove word prefix from tracking
                        if hasattr(target_obj, 'label') and target_obj.label:
                            remove_word_prefix(target_obj.label)
                        powerup_list.remove(target_obj)
                        try:
                            from functions import play_random_powerup
                            play_random_powerup()
                        except Exception:
                            pass
                    
                    # Reset destruction system and process queue
                    pending_destruction = None
                    destruction_timer = 0
                    defense.stop_aiming()
                    
                    # Process next item in queue if any
                    if destruction_queue:
                        next_target_type, next_target_obj = destruction_queue.pop(0)
                        defense.aim_at_target(next_target_obj)
                        pending_destruction = (next_target_type, next_target_obj)
                        destruction_timer = 0
            
            # Update temporary turbo mode timer
            if turbo_timer > 0:
                turbo_timer -= 1

        # load message for Game Over and proceed to high-score / menu
        if current_game_state == GAME_STATE_OVER:
            # Auto-save replay when game ends
            if recorder:
                recorder.record_event("game_over", {"final_score": getattr(mcgame, 'player_score', 0)})
                filename = recorder.save()
            mcgame.game_over(screen)

        # load a message and set new game values for start new level
        if current_game_state == GAME_STATE_NEW_LEVEL:
            # Record level completion and save replay
            if recorder:
                current_level = getattr(mcgame, 'difficulty', 1) if 'mcgame' in locals() else 1
                current_score = getattr(mcgame, 'player_score', 0) if 'mcgame' in locals() else 0
                
                # Record level completion with detailed stats
                recorder.record_event("level_completed", {
                    "level": current_level,
                    "score": current_score,
                    "remaining_cities": len([city for city in city_list if not getattr(city, 'destroyed', False)]),
                    "powerups_on_screen": len(powerup_list),
                    "missiles_on_screen": len(missile_list)
                })
                
                # Save replay after each level completion
                filename = recorder.save()
                print(f"Level {current_level} completed - Replay saved: {os.path.basename(filename) if filename else 'Failed'}")
                
                # Record the start of new level (difficulty will increment after new_level call)
                recorder.record_level_change(current_level + 1)
            
            # Reset typing state and turbo mode when starting new level
            typed_sequence = ""
            turbo_mode = False
            turbo_timer = 0
            # Re-track all existing powerup word prefixes for the new level
            for powerup in powerup_list:
                if hasattr(powerup, 'label') and powerup.label:
                    # Remove old prefix tracking flag and re-add to system
                    if hasattr(powerup, '_prefix_tracked'):
                        delattr(powerup, '_prefix_tracked')
            mcgame.new_level(screen, defense)
        
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
            # Restart the game after showing high scores
            # Reset all game objects
            missile_list.clear()
            explosion_list.clear()
            powerup_list.clear()
            # Reset word prefix tracking
            active_word_prefixes.clear()
            # Reset delayed destruction system
            pending_destruction = None
            destruction_timer = 0
            destruction_queue.clear()
            # Recreate cities (match original positioning)
            city_list = []
            for i in range(1, 8):   # 8 == Max num cities plus defense plus one
                if i == 8 // 2:     # find centre point for gun
                    pass
                else:
                    city_list.append(City(i, 7))   # 7 == max num cities plus guns
            defense = Defense()
            mcgame = McGame(1, high_scores["1"]["score"])
            typed_sequence = ""  # Reset typed sequence
            current_game_state = GAME_STATE_RUNNING

        # run at pre-set fps (or turbo speed when space held or wrong key pressed)
        fps = FPS * 10 if (turbo_mode or turbo_timer > 0) else FPS  # 10x speed when space held or temporary turbo
        clock.tick(fps)


if __name__ == '__main__':
    main()
