# KeyBlaster - Typing Defense Game

## Description

KeyBlaster is a typing tutor game inspired by the classic Missile Command arcade game. Instead of using a mouse to aim and shoot missiles, players must type characters and words to destroy incoming threats before they reach your cities. This combines the excitement of arcade action with practical typing skill development.

Originally forked from a traditional missile defense game, KeyBlaster has evolved into an educational typing game that progressively challenges players with increasingly complex words and faster-paced action.

## Story

You are the local Missile Commander for the Missile Intercept Launch Function. 

You are responsible for the safety of millions of citizens in six nearby cities. Nuclear war has just broken out. Wave after wave of nuclear warheads have been detected re-entering the atmosphere in your zone of control.

All that stands between the last remaining citizens of your country and a fireball of death are your lightning-fast typing skills and accurate keystrokes.

Get ready to type for your life!

## Game Features

- **Progressive Difficulty**: Start with single characters and advance to complex words
- **Typing Skills Development**: Improve speed and accuracy through gameplay
- **Visual Feedback**: See your typing progress with character highlighting
- **Sound Effects**: Audio feedback for hits, misses, and explosions
- **Score System**: Track your performance and compete for high scores
- **Multiple Levels**: Each level increases speed and word complexity

## How to Play

### Gameplay Mechanics

1. **Early Levels (1-2)**: Type single characters (a, s, d, f, etc.) to destroy missiles
2. **Level 3+**: Type complete words to destroy missiles:
   - **Levels 3-5**: 3-letter words (cat, dog, run)
   - **Levels 6-8**: 3-4 letter words (fire, help, jump)
   - **Levels 9-12**: 4-5 letter words (power, laser, blast)
   - **Levels 13-16**: 5-6 letter words (defend, shield, attack)
   - **Level 17+**: Complex words (missile, defense, warfare)

3. **Progressive Typing**: For multi-character words, type each letter in sequence
   - Correctly typed characters appear in green
   - Remaining characters show in white
   - Complete the word to destroy the missile

4. **Speed Scaling**: Missile speed increases with each level
   - Level 1: Very slow (0.5x speed) - easy start
   - Level 10: Medium difficulty (1.3x speed)
   - Level 20: Very hard (2.2x speed)
   - Level 20+: Mega hard (escalating difficulty)

### Controls

- **Typing**: Type the characters/words shown on missiles to destroy them
- **ESC**: Pause game
- **Space**: Legacy firing mode (available as backup)

### Objective

Protect your cities by typing the correct characters or words before missiles impact. The game ends when all cities are destroyed. Try to achieve the highest score possible!

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

## Technical Details

- **Language**: Python 3
- **Graphics**: pygame library
- **Architecture**: Object-oriented design with separate classes for missiles, explosions, cities, and game logic
- **Sound**: MP3 audio files for various game events
- **Fonts**: Retro-style pixel font (PressStart2P)

## Contributing

Feel free to contribute improvements, bug fixes, or new features. The codebase is well-structured with separate modules for different game components.

## License

This project is inspired by the classic Missile Command game and is intended for educational purposes.