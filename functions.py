import pygame
import sys
from pygame.locals import *
import os
import math
from config import *
import json
import random
import glob

# System sound helpers (Windows)
try:
    import winsound
    _HAS_WINSOUND = True
except Exception:
    winsound = None
    _HAS_WINSOUND = False

def play_system_sound(alias):
    # Play a Windows system sound by alias (non-blocking). No-op on non-Windows.
    if _HAS_WINSOUND and os.name == 'nt':
        try:
            winsound.PlaySound(alias, winsound.SND_ALIAS | winsound.SND_ASYNC)
        except Exception:
            pass

def sfx_shoot():
    # softer blip for firing
    play_system_sound('SystemDefault')

def sfx_intercept():
    # pleasant chime for successful intercept
    play_system_sound('SystemAsterisk')

def sfx_nuke():
    play_system_sound('SystemHand')

# Optional: load custom explode SFX from data/sfx
_AUDIO_READY = False
_EXPLODE_SOUNDS = []   # list[pygame.mixer.Sound]
_EXPLODE_BAG = []      # shuffled bag to reduce repeats
_LAST_EXPLODE = None   # last Sound object played
_EXPLODE_FILES = []    # file path fallbacks
_CITYDOWN_SOUNDS = []  # list[pygame.mixer.Sound]
_CITYDOWN_BAG = []     # shuffled bag to reduce repeats
_LAST_CITYDOWN = None  # last Sound object played
_CITYDOWN_FILES = []   # file path fallbacks
_MISS_SOUNDS = []      # list[pygame.mixer.Sound]
_MISS_BAG = []         # shuffled bag to reduce repeats
_LAST_MISS = None      # last Sound object played
_MISS_FILES = []       # file path fallbacks
_POWERUP_SOUNDS = []   # list[pygame.mixer.Sound]
_POWERUP_BAG = []      # shuffled bag to reduce repeats
_LAST_POWERUP = None   # last Sound object played
_POWERUP_FILES = []    # file path fallbacks

def init_audio():
    global _AUDIO_READY
    # Ensure we mutate module-level state, not locals
    global _EXPLODE_SOUNDS, _EXPLODE_BAG, _LAST_EXPLODE, _EXPLODE_FILES
    global _CITYDOWN_SOUNDS, _CITYDOWN_BAG, _LAST_CITYDOWN, _CITYDOWN_FILES
    global _MISS_SOUNDS, _MISS_BAG, _LAST_MISS, _MISS_FILES
    global _POWERUP_SOUNDS, _POWERUP_BAG, _LAST_POWERUP, _POWERUP_FILES
    if _AUDIO_READY:
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        # Support both data/sfx and sfx directories
        base_dirs = [os.path.join('data', 'sfx'), 'sfx']
        # Load all explode sounds with common extensions
        files = []
        for base in base_dirs:
            patterns = [
                os.path.join(base, 'Explode*.mp3'),
                os.path.join(base, 'Explode*.ogg'),
                os.path.join(base, 'Explode*.wav'),
            ]
            for pat in patterns:
                try:
                    files.extend(glob.glob(pat))
                except Exception:
                    pass
        # Deduplicate while preserving order
        seen = set()
        ordered = []
        for f in files:
            if f not in seen:
                seen.add(f)
                ordered.append(f)
        _EXPLODE_SOUNDS = []
        _EXPLODE_FILES = ordered.copy()
        for p in ordered:
            if os.path.exists(p):
                try:
                    _EXPLODE_SOUNDS.append(pygame.mixer.Sound(p))
                except Exception:
                    # ignore files pygame can't load
                    pass
        # Prepare a shuffled bag to avoid frequent repeats
        _EXPLODE_BAG = _EXPLODE_SOUNDS.copy()
        random.shuffle(_EXPLODE_BAG)

        # Load all city-down sounds with common extensions
        files_cd = []
        for base in base_dirs:
            patterns_cd = [
                os.path.join(base, 'CityDown*.mp3'),
                os.path.join(base, 'CityDown*.ogg'),
                os.path.join(base, 'CityDown*.wav'),
            ]
            for pat in patterns_cd:
                try:
                    files_cd.extend(glob.glob(pat))
                except Exception:
                    pass
        seen_cd = set()
        ordered_cd = []
        for f in files_cd:
            if f not in seen_cd:
                seen_cd.add(f)
                ordered_cd.append(f)
        _CITYDOWN_SOUNDS = []
        _CITYDOWN_FILES = ordered_cd.copy()
        for p in ordered_cd:
            if os.path.exists(p):
                try:
                    _CITYDOWN_SOUNDS.append(pygame.mixer.Sound(p))
                except Exception:
                    pass
        _CITYDOWN_BAG = _CITYDOWN_SOUNDS.copy()
        random.shuffle(_CITYDOWN_BAG)

        # Load all miss sounds with common extensions
        files_miss = []
        for base in base_dirs:
            patterns_miss = [
                os.path.join(base, 'Miss*.mp3'),
                os.path.join(base, 'Miss*.ogg'),
                os.path.join(base, 'Miss*.wav'),
            ]
            for pat in patterns_miss:
                try:
                    files_miss.extend(glob.glob(pat))
                except Exception:
                    pass
        seen_miss = set()
        ordered_miss = []
        for f in files_miss:
            if f not in seen_miss:
                seen_miss.add(f)
                ordered_miss.append(f)
        _MISS_SOUNDS = []
        _MISS_FILES = ordered_miss.copy()
        for p in ordered_miss:
            if os.path.exists(p):
                try:
                    _MISS_SOUNDS.append(pygame.mixer.Sound(p))
                except Exception:
                    pass
        _MISS_BAG = _MISS_SOUNDS.copy()
        random.shuffle(_MISS_BAG)

        # Load all powerup sounds with common extensions
        files_powerup = []
        for base in base_dirs:
            patterns_powerup = [
                os.path.join(base, 'powerup*.mp3'),
                os.path.join(base, 'Powerup*.mp3'),
                os.path.join(base, 'PowerUp*.mp3'),
                os.path.join(base, 'powerup*.ogg'),
                os.path.join(base, 'powerup*.wav'),
            ]
            for pat in patterns_powerup:
                try:
                    files_powerup.extend(glob.glob(pat))
                except Exception:
                    pass
        seen_powerup = set()
        ordered_powerup = []
        for f in files_powerup:
            if f not in seen_powerup:
                seen_powerup.add(f)
                ordered_powerup.append(f)
        _POWERUP_SOUNDS = []
        _POWERUP_FILES = ordered_powerup.copy()
        for p in ordered_powerup:
            if os.path.exists(p):
                try:
                    _POWERUP_SOUNDS.append(pygame.mixer.Sound(p))
                except Exception:
                    pass
        _POWERUP_BAG = _POWERUP_SOUNDS.copy()
        random.shuffle(_POWERUP_BAG)
        _AUDIO_READY = True
    except Exception:
        # mixer not available; keep using system sounds
        _AUDIO_READY = False

def play_random_explode():
    # Prefer custom sounds if loaded, else fallback to system alias
    global _EXPLODE_BAG, _LAST_EXPLODE
    try:
        if _EXPLODE_SOUNDS:
            if not _EXPLODE_BAG:
                _EXPLODE_BAG = _EXPLODE_SOUNDS.copy()
                random.shuffle(_EXPLODE_BAG)
                # avoid immediate repeat if possible
                if _LAST_EXPLODE is not None and len(_EXPLODE_BAG) > 1 and _EXPLODE_BAG[0] is _LAST_EXPLODE:
                    _EXPLODE_BAG.append(_EXPLODE_BAG.pop(0))
            s = _EXPLODE_BAG.pop()
            _LAST_EXPLODE = s
            s.play()
            return
    except Exception:
        pass
    # Fallback: try music channel with file paths
    try:
        if _EXPLODE_FILES:
            pygame.mixer.music.load(random.choice(_EXPLODE_FILES))
            pygame.mixer.music.play()
            return
    except Exception:
        pass
    # final fallback
    sfx_intercept()

def play_random_citydown():
    # Prefer custom city-down sounds, else fallback to a distinct system sound
    global _CITYDOWN_BAG, _LAST_CITYDOWN
    try:
        if _CITYDOWN_SOUNDS:
            if not _CITYDOWN_BAG:
                _CITYDOWN_BAG = _CITYDOWN_SOUNDS.copy()
                random.shuffle(_CITYDOWN_BAG)
                if _LAST_CITYDOWN is not None and len(_CITYDOWN_BAG) > 1 and _CITYDOWN_BAG[0] is _LAST_CITYDOWN:
                    _CITYDOWN_BAG.append(_CITYDOWN_BAG.pop(0))
            s = _CITYDOWN_BAG.pop()
            _LAST_CITYDOWN = s
            s.play()
            return
    except Exception:
        pass
    # Fallback: try music channel with file paths
    try:
        if _CITYDOWN_FILES:
            pygame.mixer.music.load(random.choice(_CITYDOWN_FILES))
            pygame.mixer.music.play()
            return
    except Exception:
        pass
    # final fallback: stay silent (avoid Windows ding)
    return

def play_random_miss():
    # Prefer custom miss sounds, else fallback to annoying system sound
    global _MISS_BAG, _LAST_MISS
    try:
        if _MISS_SOUNDS:
            if not _MISS_BAG:
                _MISS_BAG = _MISS_SOUNDS.copy()
                random.shuffle(_MISS_BAG)
                if _LAST_MISS is not None and len(_MISS_BAG) > 1 and _MISS_BAG[0] is _LAST_MISS:
                    _MISS_BAG.append(_MISS_BAG.pop(0))
            s = _MISS_BAG.pop()
            _LAST_MISS = s
            s.play()
            return
    except Exception:
        pass
    # Fallback: try music channel with file paths
    try:
        if _MISS_FILES:
            # stop any current music playback to ensure the miss sound is heard
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
            except Exception:
                pass
            pygame.mixer.music.load(random.choice(_MISS_FILES))
            pygame.mixer.music.play()
            return
    except Exception:
        pass
    # final fallback: use system exclamation so a sound is always heard
    sfx_wrong_key()

def play_random_powerup():
    # Play random powerup sound effect
    global _POWERUP_BAG, _LAST_POWERUP
    try:
        if _POWERUP_SOUNDS:
            if not _POWERUP_BAG:
                _POWERUP_BAG = _POWERUP_SOUNDS.copy()
                random.shuffle(_POWERUP_BAG)
                # avoid immediate repeat if possible
                if _LAST_POWERUP is not None and len(_POWERUP_BAG) > 1 and _POWERUP_BAG[0] is _LAST_POWERUP:
                    _POWERUP_BAG.append(_POWERUP_BAG.pop(0))
            s = _POWERUP_BAG.pop()
            _LAST_POWERUP = s
            s.play()
            return
    except Exception:
        pass
    # Fallback: try music channel with file paths
    try:
        if _POWERUP_FILES:
            pygame.mixer.music.load(random.choice(_POWERUP_FILES))
            pygame.mixer.music.play()
            return
    except Exception:
        pass
    # Final fallback - use a different sound if no powerup sounds found
    try:
        # Use a higher pitched version of explode sound as fallback
        if _EXPLODE_SOUNDS:
            random.choice(_EXPLODE_SOUNDS).play()
    except Exception:
        pass

def sfx_wrong_key():
    # Annoying error sound for wrong typing key
    play_system_sound('SystemExclamation')



# Define helper functions
def load_image(name, colorkey = None):
    fullname = os.path.join('data/img/', name)

    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    else:
        image = image.convert_alpha()

    return image # , image.get_rect()


def exit_game(screen):
    # clear the screen
    screen.fill(BACKGROUND)
    pygame.display.update()

    pause = 0
    
    # pause music / sfx
    pygame.mixer.pause()

    # display message to confirm exit
    exit_msg = game_font.render('Quitting ... ', False, INTERFACE_SEC)
    question_msg = game_font.render('Are You Sure?', False, INTERFACE_SEC)
    confirm_msg = game_font.render('(Y/N)', False, INTERFACE_SEC)
   
    exit_msg_pos = (SCREENSIZE[0] // 2 - (exit_msg.get_width() // 2),
                        SCREENSIZE[1] // 2 - (exit_msg.get_height() // 2))
    
    question_msg_pos = (SCREENSIZE[0] // 2 - (question_msg.get_width() // 2),
                        SCREENSIZE[1] // 2 - (question_msg.get_height() // 2)+ exit_msg.get_height()) 
   
    confirm_msg_pos = (SCREENSIZE[0] // 2 - (confirm_msg.get_width() // 2),
                        SCREENSIZE[1] // 2 - (confirm_msg.get_height() // 2) + exit_msg.get_height() + question_msg.get_height() )
    
    screen.blit(exit_msg, exit_msg_pos)
    screen.blit(question_msg, question_msg_pos)
    screen.blit(confirm_msg, confirm_msg_pos)
    pygame.display.update()

    # wait for player to confirm exit or not
    while pause == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_y:
                    pygame.quit()
                    sys.exit(0)
                if event.key == K_n:
                    pause = -1

    # resume music ifplayer not exiting
    pygame.mixer.unpause()


def pause_game(screen):
    pause = 0
    
    # pause music / sfx
    pygame.mixer.pause()

    # display message that game is paused
    pause_msg = game_font.render('GAME PAUSED', False, INTERFACE_SEC)
    confirm_msg = game_font.render('PRESS \'P\' TO RESUME', False, INTERFACE_SEC)
    pause_msg_pos = (SCREENSIZE[0] // 2 - (pause_msg.get_width() // 2),
                        SCREENSIZE[1] // 2 - (pause_msg.get_height() // 2))
    confirm_msg_pos = (SCREENSIZE[0] // 2 - (confirm_msg.get_width() // 2),
                        SCREENSIZE[1] // 2 - (confirm_msg.get_height() // 2) + pause_msg.get_height())
    screen.blit(pause_msg, pause_msg_pos)
    screen.blit(confirm_msg, confirm_msg_pos)
    pygame.display.update()

    # wait for player to un-pause
    while pause == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_p:
                    pause = -1

    # resume music
    pygame.mixer.unpause()


def distance(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def check_collisions(missile_list, explosion_list, city_list):
    score = 0

    for explosion in explosion_list:
        for missile in missile_list[:]:
            if explosion.get_radius() > distance(explosion.get_center(), missile.get_pos()):
                score += missile.get_points() * explosion.get_points_multiplier()
                missile_list.remove(missile)
        for city in city_list[:]:
            if explosion.get_radius() > distance(explosion.get_center(), city.get_pos()):
                city.set_destroyed(True)    # might not be needed if I just remove city from list
                city_list.remove(city)
                try:
                    play_random_citydown()
                except Exception:
                    pass

    return score


def load_scores(file):
    # open a json file containing scores and return dict
    with open(file) as f:
        return json.load(f)
    

def update_high_scores(score, name, high_scores):
    # check if score made it into the top 10 and determine position
    score_pos = check_high_score(score, high_scores)
    
    # if it did make top 10, re-order the records
    if score_pos > 0:
        max_pos = 10
        
        # loop from max_pos up until I get to score_pos
        for pos in range(max_pos, score_pos, -1):
            # move the score down a pos
            if pos <= max_pos and pos > 1:
                high_scores[str(pos)]["name"] = high_scores[str(pos - 1)]["name"]
                high_scores[str(pos)]["score"] = high_scores[str(pos - 1)]["score"]

        # insert the new score
        high_scores[str(score_pos)]["name"] = name
        high_scores[str(score_pos)]["score"] = int(score)
        
    return high_scores


def check_high_score(score, high_scores):
    score_pos = 0

    # check if score made it into the top 10 and determine position
    for pos, record in high_scores.items():
        if score > int(record["score"]) and score_pos == 0:
            score_pos = int(pos)
    
    return score_pos

    
def save_high_scores(file, high_scores):
    # save high-scores to file
    j = json.dumps(high_scores)
    f = open(file, "w")
    f.write(j)
    f.close()


def show_high_scores(screen, high_scores):
    # clear the screen
    screen.fill(BACKGROUND)
    pygame.display.update()

    pause = 0

    # generate heading msg, position, blit
    high_score_heading = game_font.render('HIGH SCORES', False, INTERFACE_PRI)
    text_height = high_score_heading.get_height()
    text_y_pos_multiplier = 7
    wide_score = 0
    high_score_heading_pos = (SCREENSIZE[0] // 2 - (high_score_heading.get_width() // 2),
                            SCREENSIZE[1] // 2 - (text_height * text_y_pos_multiplier))
    screen.blit(high_score_heading, high_score_heading_pos)
    text_y_pos_multiplier -= 2

    # loop through dict 'high_scores'
    for pos, record in high_scores.items():
        # Format position with leading space for single digits
        pos_str = f"{pos:>2}"  # Right-align position in 2 characters
        
        # Format name with consistent width (strip extra spaces first)
        clean_name = str(record['name']).strip()
        name_str = f"{clean_name:<12}"  # Left-align name in 12 characters
        
        # Format score with consistent width and right-align
        score_str = f"{record['score']:>8,}"  # Right-align score in 8 chars with commas
        
        # Create the full line with proper spacing
        full_line = f"{pos_str}. {name_str} {score_str}"
        
        score_text = game_font.render(full_line, False, INTERFACE_SEC)
        score_text_pos = (SCREENSIZE[0] // 2 - (score_text.get_width() // 2),
                            SCREENSIZE[1] // 2 - (text_height * text_y_pos_multiplier))
        screen.blit(score_text, score_text_pos)
        text_y_pos_multiplier -= 1
    
    # generate instruction msg, position, blit
    text_y_pos_multiplier -= 1
    high_score_msg = game_font.render('PRESS \'SPACE\' TO CONTINUE', False, INTERFACE_SEC)
    high_score_msg_pos = (SCREENSIZE[0] // 2 - (high_score_msg.get_width() // 2),
                            SCREENSIZE[1] // 2 - (text_height * text_y_pos_multiplier))
    screen.blit(high_score_msg, high_score_msg_pos)

    # update the display
    pygame.display.update()

    # infinite loop to listen / wait for continue
    while pause == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    pause = -1
