# 🚀 KeyBlaster - Typing Defense Game

## 📖 Description

KeyBlaster is a typing tutor game inspired by the classic Missile Command arcade game. Instead of using a mouse to aim and shoot missiles, players must type characters and words to destroy incoming threats before they reach your cities. This combines the excitement of arcade action with practical typing skill development.

Originally forked from a traditional missile defense game, KeyBlaster has evolved into an educational typing game that progressively challenges players with increasingly complex words and faster-paced action.

## 📜 Story

You are the local Missile Commander for the Missile Intercept Launch Function. 

You are responsible for the safety of millions of citizens in six nearby cities. Nuclear war has just broken out. Wave after wave of nuclear warheads have been detected re-entering the atmosphere in your zone of control.

All that stands between the last remaining citizens of your country and a fireball of death are your lightning-fast typing skills and accurate keystrokes.

Get ready to type for your life!

## ⭐ Game Features

- **Progressive Difficulty**: Start with home row characters and advance to complex multi-letter words
- **Sequence-Based Typing**: Type complete words in any order - no lock-on required
- **Typing Skills Development**: Improve speed and accuracy through gameplay
- **Visual Feedback**: Real-time green highlighting shows correctly typed portions
- **Sound Effects**: Audio feedback for hits, misses, explosions, and powerups
- **Score System**: Track performance with bonus multipliers from powerups
- **Multiple Levels**: Each level increases speed and word complexity
- **Powerup System**: Golden spaceships provide bonus challenges and rewards
- **Automatic Replay Recording**: Built-in debugging system for issue analysis
- **Turbo Mode**: Temporary speed boost for enhanced challenge

## 🎮 How to Play

### 🎯 Gameplay Mechanics

1. **Level 1**: Type home row characters (a, s, d, f, g, h, j, k, l) - easiest start
2. **Level 2**: Type any single characters with home row bias - expanded practice  
3. **Level 3+**: Type complete words to destroy missiles:
   - **Level 3**: 2-letter words (it, go, do, hi, up, etc.)
   - **Levels 4-5**: Mix of 2 and 3-letter words (cat, dog, run, is, to)
   - **Levels 6-7**: Mostly 3-letter words (cat, dog, run, hit, get)
   - **Levels 8-9**: 3 and 4-letter words (fire, help, jump, game)
   - **Levels 10-12**: 4 and 5-letter words (power, laser, blast, shield)
   - **Levels 13-16**: 5 and 6-letter words (defend, attack, weapon, target)
   - **Level 17+**: Complex 6+ letter words (missile, defense, warfare, destroy)

3. **Sequence-Based Typing**: Type complete words in any order to destroy targets
   - Type any word that appears on screen (missiles or powerups)
   - Words can be typed rapidly in sequence without waiting
   - Correctly typed portions show in green highlighting
   - Multiple words can be queued and destroyed automatically

4. **Powerups**: Golden spaceships occasionally fly across the screen
   - Contain challenging words (often longer or more complex)
   - Award bonus points and temporary score multipliers
   - Can carry over between levels if not destroyed
   - Higher risk/reward - harder to type but valuable

5. **Speed Scaling**: Missile speed increases with each level
   - Level 1: Very slow (0.5x speed) - easy start
   - Level 10: Medium difficulty (1.3x speed)  
   - Level 20: Very hard (2.2x speed)
   - Level 20+: Mega hard (escalating difficulty)

### ⌨️ Controls

- **Typing**: Type the characters/words shown on missiles and powerups to destroy them
- **ESC**: Pause game
- **SPACE**: Hold for temporary turbo mode (10x game speed for 0.5 seconds)
- **F12**: Copy current replay file path to clipboard for debugging

**Note**: This is a keyboard-only game. Mouse controls are disabled to focus on typing skills.

### Objective

Protect your cities by typing the correct characters or words before missiles impact. Destroy powerups for bonus points and score multipliers. The game ends when all cities are destroyed. Try to achieve the highest score possible!

## Installation and Running

### Automatic Setup (Recommended)

The easiest way to run KeyBlaster is using the included launcher:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd KeyBlaster
   ```

2. **Run the game**:
   ```bash
   StartGame.cmd
   ```

The `StartGame.cmd` script will automatically:
- Detect or install Python 3
- Create a virtual environment
- Install all dependencies (pygame, etc.)
- Launch the game

### Manual Setup

If you prefer manual installation:

1. **Prerequisites**: 
   - Python 3.7 or higher
   - pip (Python package installer)

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd KeyBlaster
   ```

3. **Create virtual environment**:
   ```bash
   python -m venv .venv
   ```

4. **Activate virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the game**:
   ```bash
   python missile-defence.py
   ```

### Alternative Installation (Pipenv)

If you prefer using pipenv:

```bash
pip install pipenv
pipenv shell
pipenv install -r requirements.txt
python missile-defence.py
```

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.7 or higher
- **Dependencies**: pygame (automatically installed)
- **Display**: Any resolution (game window: 1280x720)

## Game Tips

1. **Focus on home row keys**: The game weights home row characters more heavily in early levels
2. **Type accurately**: Wrong keypresses play miss sounds and don't help
3. **Plan ahead**: Start typing words as soon as missiles appear
4. **Practice regularly**: The game helps improve both typing speed and accuracy
5. **Stay calm**: Higher levels require steady, accurate typing under pressure

## Development History

This game started as a recreation of the classic 1980 Atari Missile Command game and evolved into a typing tutor. The transformation from mouse-based targeting to keyboard-based gameplay makes it both educational and entertaining.

## Original Inspiration

Missile Command is a 1980 arcade game developed and published by Atari, Inc. It was designed by Dave Theurer, who also designed Atari's vector graphics game Tempest from the same year. The 1981 Atari 2600 port sold over 2.5 million copies and became the third most popular cartridge for the system.

- [Wikipedia article](https://en.wikipedia.org/wiki/Missile_Command)

## Replay System & Debugging

### Overview

KeyBlaster features a comprehensive replay recording and analysis system designed for debugging gameplay issues and understanding player behavior. The system automatically records all game events with precise timing and provides AI-assisted debugging capabilities.

### Automatic Replay Recording

**Recording is automatic** - no user intervention required:
- Starts automatically when game launches
- Records every keystroke, word match, game state change, and level transition
- Uses deterministic random seed for exact reproducibility
- Auto-saves every 30 seconds during gameplay
- Saves automatically on level completion and game end/exit
- Saves automatically when program terminates (crash, Alt+F4, window close, etc.)

**File Location**: 
- Windows: `%APPDATA%\KeyBlaster\Replays\`
- Format: `replay_YYYY-MM-DD_HH-MM-SS.json`
- Example: `replay_2025-01-15_14-30-45.json`

### Quick Access During Gameplay

**F12 Key**: Instantly copy current replay file path to clipboard
- For systems with pyperclip: Automatic clipboard copy
- For systems without pyperclip: Displays formatted path for manual copying
- Use to quickly share replay files when reporting bugs

### Replay File Contents

Each replay file contains:

#### 1. Core Event Data
```json
{
  "version": "1.0",
  "start_time": 1672531200.123,
  "initial_seed": 456789,
  "events": [...]
}
```

#### 2. Recorded Event Types
- **keypress**: Every key pressed with unicode character and pygame key code
- **word_match**: Successful and failed word matching attempts with word and target type
- **game_state**: Periodic snapshots (every ~1 second) containing:
  - Current level, score, typed sequence
  - All missiles on screen with labels and positions
  - All powerups on screen with labels and positions
- **level_completed**: Detailed level completion stats (cities remaining, objects on screen)
- **level_change**: Level transitions
- **game_over**: Final score and session end
- **program_exit**: Unexpected termination events

#### 3. AI Debug Annotations
Automatically generated analysis for AI assistants:
```json
"ai_debug_info": {
  "session_duration": 45.2,
  "total_keystrokes": 156,
  "keystroke_sequence": "ahitdogcatfshello...",
  "successful_matches": ["it", "dog", "cat"],
  "failed_matches": [],
  "levels_reached": [1, 2, 3],
  "final_game_state": {...},
  "potential_issues": [
    "Available word 'ah' not matched despite having all letters in sequence 'ahit'",
    "Repeated keystroke pattern: 'fs'"
  ],
  "common_debugging_hints": {
    "word_matching": "Check if keystroke sequence contains all letters for available words",
    "prefix_conflicts": "Look for words with same 2-letter prefix causing conflicts",
    "sequence_reset": "Check if typed sequence is being reset when it shouldn't be",
    "timing_issues": "Look for rapid keystrokes that might be processed out of order"
  }
}
```

### Replay Analysis Tools

#### Command Line Interface
```bash
# View the most recent replay (most common usage)
python view_replay.py --latest

# List all available replays with timestamps and stats
python view_replay.py --list

# Analyze a specific replay file
python view_replay.py replay_2025-01-15_14-30-45.json

# Analyze using full path (copied from F12)
python view_replay.py "C:\Users\username\AppData\Roaming\KeyBlaster\Replays\replay_2025-01-15_14-30-45.json"
```

#### Analysis Output Format
```
================================================================================
KEYBLASTER REPLAY ANALYSIS: replay_2025-01-15_14-30-45.json
================================================================================
AI DEBUG SUMMARY:
================================================================================
Session Duration: 45.2s
Total Keystrokes: 156
Keystroke Sequence: 'ahitdogcatfshello'
Successful Matches: ['it', 'dog', 'cat']
Failed Matches: []
Levels Reached: [1, 2, 3]

POTENTIAL ISSUES DETECTED:
1. Available word 'ah' not matched despite having all letters in sequence 'ahit'
2. Repeated keystroke pattern: 'fs'

Final Game State:
  Level: 3
  Score: 2400
  Typed Sequence: 'fs'
  Available Words: ['hello', 'ghosted']
================================================================================
Replay Duration: 45.2s
Events:
  keypress: 156
  word_match: 23
  game_state: 45
  level_change: 3
================================================================================
EVENT LOG:
================================================================================
[  2.451s] keypress     Key: 'a' (pygame key: 97)
[  2.852s] keypress     Key: 'h' (pygame key: 104)  
[  3.001s] game_state   Level: 2 Score: 1500 Typed: 'ah' Missiles: ['hello', 'cat'] Powerups: ['ghost']
[  3.002s] word_match   ✓ 'ah' (missile)
...
```

### Debugging Workflow for AI Assistants

When a user reports a bug:

#### 1. Immediate Analysis
- Request replay file path (user presses F12 to copy)
- Load and examine `ai_debug_info` section first
- Review `potential_issues` array for pre-identified problems
- Check `keystroke_sequence` vs `successful_matches` for patterns

#### 2. Issue Classification
Common problem categories automatically detected:
- **Word Matching Issues**: Available words not being matched despite correct letters
- **Prefix Conflicts**: Words with same 2-letter prefixes causing selection problems  
- **Sequence Reset Problems**: Typed sequences clearing when they shouldn't
- **Timing Issues**: Rapid keystrokes processed out of order
- **Powerup Carryover**: Flying saucers causing problems across level transitions
- **Performance Issues**: Game speed or responsiveness problems

#### 3. Detailed Event Analysis
For complex issues, examine event timeline:
- Correlate keystrokes with game state snapshots
- Look for state inconsistencies across level transitions
- Track word availability vs typing attempts
- Identify timing-sensitive interaction problems

#### 4. Code Investigation Focus Areas
Based on replay analysis, check:
- **Word matching logic**: `missile-defence.py` lines 160-225
- **Prefix conflict system**: `active_word_prefixes` management
- **Level transition handling**: `GAME_STATE_NEW_LEVEL` processing
- **Powerup carryover logic**: Prefix re-tracking in level transitions
- **Typing sequence management**: Global `typed_sequence` handling

### Troubleshooting Common Issues

#### Issue: "Word not being matched despite correct typing"
1. Check AI debug `potential_issues` for automatic detection
2. Verify keystroke sequence contains all word letters
3. Look for prefix conflicts with other on-screen words
4. Check if word prefix was properly tracked

#### Issue: "Powerup carries over levels and becomes untargetable"  
1. Check level completion events for "powerups_on_screen" count
2. Look for proper prefix cleanup in level transitions
3. Verify powerup word re-integration into new level

#### Issue: "Game becomes unresponsive to certain keys"
1. Check for repeated keystroke patterns in debug summary
2. Look for sequence reset issues
3. Verify no keys are getting "stuck" in processing queue

#### Issue: "Wrong keys activating turbo mode"
1. Check if typed characters exist in any on-screen words
2. Verify turbo activation logic (keys not visible anywhere)
3. Look for temporary turbo duration (should be 0.5 seconds)

### For Developers

#### Adding New Event Types
To record new event types in replays:
```python
if recorder:
    recorder.record_event("custom_event", {
        "custom_data": value,
        "timestamp": time.time()
    })
```

#### Extending AI Debug Analysis
Modify `_generate_debug_summary()` in `replay.py` to add new automatic issue detection patterns.

#### Replay File Compatibility
- Version field allows for future format changes
- All times are relative to session start (seconds as float)
- Events are chronologically ordered
- JSON format for easy parsing by any language/tool

## Technical Details

- **Language**: Python 3
- **Graphics**: pygame library
- **Architecture**: Object-oriented design with separate classes for missiles, explosions, cities, and game logic
- **Sound**: MP3 audio files for various game events
- **Fonts**: Retro-style pixel font (PressStart2P)
- **Replay System**: Deterministic recording with AI-assisted analysis

## Contributing

Feel free to contribute improvements, bug fixes, or new features. The codebase is well-structured with separate modules for different game components.

## License

This project is inspired by the classic Missile Command game and is intended for educational purposes.