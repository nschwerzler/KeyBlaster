import json
import time
import random
import pygame
import os
from datetime import datetime

def get_replay_directory():
    """Get or create the replay directory in %APPDATA%"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    replay_dir = os.path.join(appdata, 'KeyBlaster', 'Replays')
    
    # Create directory if it doesn't exist
    os.makedirs(replay_dir, exist_ok=True)
    
    return replay_dir

def get_timestamp_filename():
    """Generate a Windows-compatible timestamp filename"""
    # Use format: YYYY-MM-DD_HH-MM-SS (Windows compatible)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"replay_{timestamp}.json"

class ReplayRecorder:
    def __init__(self, filename=None):
        self.events = []
        self.start_time = time.time()
        self.initial_seed = None
        
        if filename:
            self.filename = filename
        else:
            replay_dir = get_replay_directory()
            timestamp_name = get_timestamp_filename()
            self.filename = os.path.join(replay_dir, timestamp_name)
        
        self.recording = True
        
    def set_initial_seed(self, seed):
        """Record the initial random seed for deterministic replay"""
        self.initial_seed = seed
        self.record_event("seed", {"value": seed})
    
    def record_event(self, event_type, data):
        """Record a game event with timestamp"""
        if not self.recording:
            return
            
        timestamp = time.time() - self.start_time
        event = {
            "time": timestamp,
            "type": event_type,
            "data": data
        }
        self.events.append(event)
    
    def record_keypress(self, key_char, pygame_key):
        """Record a key press event"""
        self.record_event("keypress", {
            "char": key_char,
            "key": pygame_key,
            "unicode": key_char
        })
    
    def record_game_state(self, missiles, powerups, typed_sequence, level, score):
        """Record current game state for verification"""
        missile_data = []
        for m in missiles:
            if hasattr(m, 'label') and m.label:
                missile_data.append({
                    "label": m.label,
                    "pos": list(m.pos) if hasattr(m, 'pos') else [0, 0]
                })
        
        powerup_data = []
        for p in powerups:
            if hasattr(p, 'label') and p.label:
                powerup_data.append({
                    "label": p.label,
                    "pos": list(p.pos) if hasattr(p, 'pos') else [0, 0]
                })
        
        self.record_event("game_state", {
            "missiles": missile_data,
            "powerups": powerup_data,
            "typed_sequence": typed_sequence,
            "level": level,
            "score": score
        })
    
    def record_word_match(self, word, target_type, success):
        """Record word matching attempts"""
        self.record_event("word_match", {
            "word": word,
            "type": target_type,
            "success": success
        })
    
    def record_level_change(self, new_level):
        """Record level transitions"""
        self.record_event("level_change", {"level": new_level})
    
    def save(self):
        """Save replay to file with AI debug annotations"""
        # Generate AI-friendly debug summary
        debug_summary = self._generate_debug_summary()
        
        replay_data = {
            "version": "1.0",
            "start_time": self.start_time,
            "initial_seed": self.initial_seed,
            "events": self.events,
            "ai_debug_info": debug_summary
        }
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(replay_data, f, indent=2)
            print(f"Replay saved to {self.filename}")
            return self.filename
        except Exception as e:
            print(f"Failed to save replay: {e}")
            return None
    
    def _generate_debug_summary(self):
        """Generate AI-friendly debug annotations"""
        if not self.events:
            return {"error": "No events recorded"}
        
        # Analyze events for common patterns
        keystrokes = []
        word_matches = []
        failed_matches = []
        game_states = []
        level_changes = []
        
        for event in self.events:
            if event["type"] == "keypress":
                keystrokes.append(event["data"].get("char", ""))
            elif event["type"] == "word_match":
                if event["data"]["success"]:
                    word_matches.append(event["data"]["word"])
                else:
                    failed_matches.append(event["data"]["word"])
            elif event["type"] == "game_state":
                game_states.append(event["data"])
            elif event["type"] == "level_change":
                level_changes.append(event["data"]["level"])
        
        # Build keystroke sequence
        keystroke_sequence = "".join(keystrokes)
        
        # Find potential issues
        issues = []
        
        # Look for repeated failed keystrokes
        if len(keystroke_sequence) > 10:
            for i in range(len(keystroke_sequence) - 2):
                substr = keystroke_sequence[i:i+3]
                if keystroke_sequence.count(substr) > 2:
                    issues.append(f"Repeated keystroke pattern: '{substr}'")
        
        # Look for available words that weren't matched
        if game_states:
            last_state = game_states[-1]
            available_words = []
            for missile in last_state.get("missiles", []):
                available_words.append(missile["label"].lower())
            for powerup in last_state.get("powerups", []):
                available_words.append(powerup["label"].lower())
            
            # Check if typed sequence could form available words
            typed_seq = last_state.get("typed_sequence", "").lower()
            if typed_seq and available_words:
                for word in available_words:
                    if all(char in typed_seq for char in word):
                        if word not in [m.lower() for m in word_matches]:
                            issues.append(f"Available word '{word}' not matched despite having all letters in sequence '{typed_seq}'")
        
        return {
            "session_duration": self.events[-1]["time"] if self.events else 0,
            "total_keystrokes": len(keystrokes),
            "keystroke_sequence": keystroke_sequence,
            "successful_matches": word_matches,
            "failed_matches": failed_matches,
            "levels_reached": level_changes,
            "final_game_state": game_states[-1] if game_states else None,
            "potential_issues": issues,
            "common_debugging_hints": {
                "word_matching": "Check if keystroke sequence contains all letters for available words",
                "prefix_conflicts": "Look for words with same 2-letter prefix causing conflicts",
                "sequence_reset": "Check if typed sequence is being reset when it shouldn't be",
                "timing_issues": "Look for rapid keystrokes that might be processed out of order"
            }
        }
    
    def stop_recording(self):
        """Stop recording and save"""
        self.recording = False
        self.save()


class ReplayPlayer:
    def __init__(self, filename):
        self.filename = filename
        self.events = []
        self.current_event_index = 0
        self.start_time = None
        self.initial_seed = None
        
    def load(self):
        """Load replay from file"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.events = data["events"]
                self.initial_seed = data.get("initial_seed")
                print(f"Loaded replay with {len(self.events)} events")
                print(f"Initial seed: {self.initial_seed}")
                return True
        except Exception as e:
            print(f"Failed to load replay: {e}")
            return False
    
    def start_playback(self):
        """Start replay playback"""
        self.start_time = time.time()
        self.current_event_index = 0
        
        # Set the random seed for deterministic behavior
        if self.initial_seed is not None:
            random.seed(self.initial_seed)
    
    def get_next_events(self):
        """Get all events that should have occurred by now"""
        if not self.start_time:
            return []
        
        current_time = time.time() - self.start_time
        events = []
        
        while (self.current_event_index < len(self.events) and 
               self.events[self.current_event_index]["time"] <= current_time):
            events.append(self.events[self.current_event_index])
            self.current_event_index += 1
        
        return events
    
    def is_complete(self):
        """Check if replay is finished"""
        return self.current_event_index >= len(self.events)
    
    def get_summary(self):
        """Get summary of replay contents"""
        if not self.events:
            return "No events loaded"
        
        event_types = {}
        for event in self.events:
            event_type = event["type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        duration = self.events[-1]["time"] if self.events else 0
        
        summary = f"Replay Duration: {duration:.2f}s\n"
        summary += f"Events:\n"
        for event_type, count in sorted(event_types.items()):
            summary += f"  {event_type}: {count}\n"
        
        return summary


# Global replay recorder instance
replay_recorder = None

def start_recording(filename=None):
    """Start recording a new replay"""
    global replay_recorder
    replay_recorder = ReplayRecorder(filename)
    # Set initial seed for deterministic behavior
    seed = int(time.time() * 1000) % 1000000  # Use microseconds for variety
    replay_recorder.set_initial_seed(seed)
    random.seed(seed)
    print(f"Started recording replay: {replay_recorder.filename}")
    print(f"Replay auto-saves every 30 seconds and when game ends")
    print(f"Press F12 to copy current replay path to clipboard for debugging")
    return replay_recorder

def stop_recording():
    """Stop recording and save replay"""
    global replay_recorder
    if replay_recorder:
        replay_recorder.stop_recording()
        filename = replay_recorder.filename
        replay_recorder = None
        return filename
    return None

def get_recorder():
    """Get current replay recorder"""
    global replay_recorder
    return replay_recorder