#!/usr/bin/env python3
"""
Replay Viewer for KeyBlaster Debug Replays

Usage: 
  python view_replay.py <replay_file.json>     # Analyze specific replay
  python view_replay.py --list                 # List recent replays
  python view_replay.py --latest               # Analyze most recent replay
"""

import sys
import json
import os
import glob
from replay import ReplayPlayer, get_replay_directory

def format_event(event):
    """Format an event for display"""
    timestamp = f"[{event['time']:7.3f}s]"
    event_type = event['type'].ljust(12)
    
    if event['type'] == 'keypress':
        data = event['data']
        return f"{timestamp} {event_type} Key: '{data.get('char', '')}' (pygame key: {data.get('key', 'unknown')})"
    
    elif event['type'] == 'word_match':
        data = event['data']
        success = "✓" if data['success'] else "✗"
        return f"{timestamp} {event_type} {success} '{data['word']}' ({data['type']})"
    
    elif event['type'] == 'game_state':
        data = event['data']
        missiles = [m['label'] for m in data.get('missiles', [])]
        powerups = [p['label'] for p in data.get('powerups', [])]
        return f"{timestamp} {event_type} Level: {data.get('level', '?')} Score: {data.get('score', 0)} Typed: '{data.get('typed_sequence', '')}' Missiles: {missiles} Powerups: {powerups}"
    
    elif event['type'] == 'level_change':
        data = event['data']
        return f"{timestamp} {event_type} New Level: {data['level']}"
    
    elif event['type'] == 'seed':
        data = event['data']
        return f"{timestamp} {event_type} Initial Seed: {data['value']}"
    
    else:
        return f"{timestamp} {event_type} {event['data']}"

def analyze_replay(filename):
    """Analyze and display replay contents"""
    player = ReplayPlayer(filename)
    
    if not player.load():
        print(f"Failed to load replay: {filename}")
        return
    
    print("=" * 80)
    print(f"KEYBLASTER REPLAY ANALYSIS: {filename}")
    print("=" * 80)
    
    # Show AI debug info if available
    try:
        with open(filename, 'r') as f:
            replay_data = json.load(f)
            ai_debug = replay_data.get("ai_debug_info")
            
            if ai_debug:
                print("AI DEBUG SUMMARY:")
                print("=" * 80)
                print(f"Session Duration: {ai_debug.get('session_duration', 0):.1f}s")
                print(f"Total Keystrokes: {ai_debug.get('total_keystrokes', 0)}")
                print(f"Keystroke Sequence: '{ai_debug.get('keystroke_sequence', '')}'")
                print(f"Successful Matches: {ai_debug.get('successful_matches', [])}")
                print(f"Failed Matches: {ai_debug.get('failed_matches', [])}")
                print(f"Levels Reached: {ai_debug.get('levels_reached', [])}")
                
                issues = ai_debug.get('potential_issues', [])
                if issues:
                    print("\nPOTENTIAL ISSUES DETECTED:")
                    for i, issue in enumerate(issues, 1):
                        print(f"{i}. {issue}")
                
                final_state = ai_debug.get('final_game_state')
                if final_state:
                    print(f"\nFinal Game State:")
                    print(f"  Level: {final_state.get('level', '?')}")
                    print(f"  Score: {final_state.get('score', 0)}")
                    print(f"  Typed Sequence: '{final_state.get('typed_sequence', '')}'")
                    missiles = [m['label'] for m in final_state.get('missiles', [])]
                    powerups = [p['label'] for p in final_state.get('powerups', [])]
                    print(f"  Available Words: {missiles + powerups}")
                
                print("=" * 80)
    except:
        pass  # Continue with regular analysis if debug info fails
    
    print(player.get_summary())
    print("=" * 80)
    print("EVENT LOG:")
    print("=" * 80)
    
    # Group events for better readability
    current_second = -1
    for event in player.events:
        event_second = int(event['time'])
        if event_second != current_second:
            if current_second >= 0:
                print()  # Add blank line between seconds
            current_second = event_second
        
        print(format_event(event))
    
    print("=" * 80)
    print("END OF REPLAY")
    print("=" * 80)

def analyze_word_matching_issues(filename):
    """Analyze potential word matching problems"""
    player = ReplayPlayer(filename)
    
    if not player.load():
        return
    
    print("\n" + "=" * 80)
    print("WORD MATCHING ANALYSIS")
    print("=" * 80)
    
    # Track typing sequences that didn't result in matches
    keystroke_buffer = ""
    last_game_state = None
    potential_issues = []
    
    for event in player.events:
        if event['type'] == 'keypress':
            char = event['data'].get('char', '')
            if char and char.isalpha():
                keystroke_buffer += char.lower()
        
        elif event['type'] == 'game_state':
            last_game_state = event['data']
        
        elif event['type'] == 'word_match':
            word = event['data']['word']
            if word in keystroke_buffer:
                # Remove matched word from buffer
                keystroke_buffer = keystroke_buffer.replace(word, "", 1)
        
        # Check for potential issues: long keystroke buffer with available words
        if len(keystroke_buffer) > 3 and last_game_state:
            available_words = []
            for missile in last_game_state.get('missiles', []):
                available_words.append(missile['label'])
            for powerup in last_game_state.get('powerups', []):
                available_words.append(powerup['label'])
            
            # Check if any available word could be formed from buffer
            for word in available_words:
                if all(char in keystroke_buffer for char in word.lower()):
                    potential_issues.append({
                        'time': event['time'],
                        'buffer': keystroke_buffer,
                        'missed_word': word,
                        'available_words': available_words
                    })
                    break
    
    if potential_issues:
        print("POTENTIAL WORD MATCHING ISSUES:")
        for issue in potential_issues[-5:]:  # Show last 5 issues
            print(f"Time {issue['time']:7.3f}s: Typed '{issue['buffer']}' but '{issue['missed_word']}' was available")
            print(f"                Available words: {issue['available_words']}")
    else:
        print("No obvious word matching issues detected.")

def list_replays():
    """List all available replay files"""
    replay_dir = get_replay_directory()
    pattern = os.path.join(replay_dir, "replay_*.json")
    replay_files = glob.glob(pattern)
    
    if not replay_files:
        print(f"No replay files found in: {replay_dir}")
        return []
    
    # Sort by modification time (newest first)
    replay_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"Replay files in: {replay_dir}")
    print("=" * 80)
    
    for i, filepath in enumerate(replay_files):
        filename = os.path.basename(filepath)
        mod_time = os.path.getmtime(filepath)
        size = os.path.getsize(filepath)
        
        from datetime import datetime
        time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{i+1:2d}. {filename}")
        print(f"    Created: {time_str}  Size: {size:,} bytes")
        
        # Show brief summary
        try:
            player = ReplayPlayer(filepath)
            if player.load():
                event_count = len(player.events)
                duration = player.events[-1]["time"] if player.events else 0
                print(f"    Duration: {duration:.1f}s  Events: {event_count}")
        except:
            print("    [Could not read file]")
        
        print()
    
    return replay_files

def get_latest_replay():
    """Get the path to the most recent replay file"""
    replay_dir = get_replay_directory()
    pattern = os.path.join(replay_dir, "replay_*.json")
    replay_files = glob.glob(pattern)
    
    if not replay_files:
        return None
    
    # Return the most recently modified file
    latest = max(replay_files, key=os.path.getmtime)
    return latest

def main():
    if len(sys.argv) < 2:
        print("Usage: python view_replay.py <replay_file.json|--list|--latest>")
        print("\nOptions:")
        print("  --list     List all available replay files")
        print("  --latest   Analyze the most recent replay file")
        print("  filename   Analyze specific replay file")
        return
    
    arg = sys.argv[1]
    
    if arg == "--list":
        list_replays()
        return
    
    elif arg == "--latest":
        latest = get_latest_replay()
        if not latest:
            print("No replay files found.")
            return
        filename = latest
        print(f"Analyzing latest replay: {os.path.basename(filename)}")
    
    else:
        filename = arg
        # If it's just a filename, look in the replay directory first
        if not os.path.exists(filename) and not os.path.isabs(filename):
            replay_dir = get_replay_directory()
            full_path = os.path.join(replay_dir, filename)
            if os.path.exists(full_path):
                filename = full_path
    
    analyze_replay(filename)
    analyze_word_matching_issues(filename)

if __name__ == '__main__':
    main()