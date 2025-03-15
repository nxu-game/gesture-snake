#!/usr/bin/env python
"""
Gesture Snake Game - Main entry point
"""

import cv2
import pygame
import numpy as np
import sys
import os
import random

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gesture.detector import GestureDetector
from src.game.snake import SnakeGame

# Add sound directory
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

def main():
    """
    Main function to run the Gesture Snake game
    """
    # Set larger window dimensions
    window_width = 1280  # Increased window width
    window_height = 720  # Increased window height
    
    # Game area dimensions
    game_width = window_width // 2
    game_height = window_height
    
    # Initialize gesture detector
    gesture_detector = GestureDetector()
    
    # Initialize game
    snake_game = SnakeGame(game_width, game_height)
    
    # Initialize display
    pygame.init()
    pygame.mixer.init()  # Initialize sound mixer
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Gesture Controlled Snake Game")
    
    # Load sounds
    sounds = {}
    try:
        # Create sounds directory if it doesn't exist
        if not os.path.exists(SOUND_DIR):
            os.makedirs(SOUND_DIR)
            print(f"Created sounds directory at {SOUND_DIR}")
            print("Please add sound files to this directory and restart the game")
        
        # Try to load sounds if they exist
        sound_files = {
            "background": "background.mp3",
            "eat": "eat.mp3",
            "game_over": "game_over.mp3",
            "turn": "turn.mp3"
        }
        
        for sound_name, file_name in sound_files.items():
            sound_path = os.path.join(SOUND_DIR, file_name)
            if os.path.exists(sound_path):
                sounds[sound_name] = pygame.mixer.Sound(sound_path)
                if sound_name == "background":
                    sounds[sound_name].set_volume(0.3)  # Lower volume for background music
            else:
                print(f"Sound file not found: {sound_path}")
        
        # Start background music if available
        if "background" in sounds:
            sounds["background"].play(-1)  # Loop indefinitely
    except Exception as e:
        print(f"Error loading sounds: {e}")
        # Continue without sounds if there's an error
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    # Get original camera resolution
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Calculate video size maintaining original aspect ratio
    video_width = game_width
    video_height = int(original_height * (video_width / original_width))
    
    # If video height exceeds window height, scale by height
    if video_height > window_height:
        video_height = window_height
        video_width = int(original_width * (video_height / original_height))
    
    # Calculate video position in left area (centered)
    video_x = (game_width - video_width) // 2
    video_y = (window_height - video_height) // 2
    
    # Initialize clock and frame rate
    clock = pygame.time.Clock()
    base_fps = 30  # Higher base frame rate for smoother video
    running = True
    
    # Control variables
    show_help = True
    help_timeout = 300  # Number of frames to show help
    frame_count = 0
    
    # Game state tracking for sound effects
    previous_score = 0
    previous_direction = None
    previous_game_over = False
    
    try:
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and snake_game.game_over:
                        snake_game.reset()
                    elif event.key == pygame.K_p:
                        snake_game.toggle_pause()
                    elif event.key == pygame.K_g:
                        snake_game.toggle_grid()
                    elif event.key == pygame.K_w:
                        snake_game.toggle_wall_collision()
                    elif event.key == pygame.K_h:
                        show_help = not show_help
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        # Increase game speed
                        snake_game.speed = min(snake_game.speed + 0.1, 2.0)
                    elif event.key == pygame.K_MINUS:
                        # Decrease game speed
                        snake_game.speed = max(snake_game.speed - 0.1, 0.1)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_m:
                        # Toggle music
                        if "background" in sounds:
                            if pygame.mixer.get_busy():
                                pygame.mixer.pause()
                            else:
                                pygame.mixer.unpause()
            
            # Capture video frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Cannot read camera frame")
                break
                
            # Flip horizontally to create mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect gesture and get direction
            direction = gesture_detector.detect_direction(frame)
            if direction:
                # Play turn sound if direction changed
                if direction != previous_direction and "turn" in sounds:
                    sounds["turn"].play()
                previous_direction = direction
                snake_game.change_direction(direction)
            
            # Update game state
            snake_game.update()
            
            # Play sound effects based on game state changes
            if snake_game.score > previous_score:
                if "eat" in sounds:
                    sounds["eat"].play()
                previous_score = snake_game.score
            
            if snake_game.game_over and not previous_game_over:
                if "game_over" in sounds:
                    sounds["game_over"].play()
                previous_game_over = True
            elif not snake_game.game_over and previous_game_over:
                previous_game_over = False
            
            # Convert OpenCV image format to Pygame format, maintaining aspect ratio
            frame_resized = cv2.resize(frame, (video_width, video_height))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            video_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            
            # Get game screen
            game_surface = snake_game.render()
            
            # Fill background
            screen.fill((0, 0, 0))
            
            # Display video part (left)
            screen.blit(video_surface, (video_x, video_y))
            
            # Display game part (right)
            screen.blit(game_surface, (game_width, 0))
            
            # Add dividing line
            pygame.draw.line(screen, (255, 255, 255), (game_width, 0), (game_width, window_height), 2)
            
            # Show help information
            if show_help or frame_count < help_timeout:
                help_font = pygame.font.SysFont('Arial', 20)
                help_texts = [
                    "Controls:",
                    "- Use thumb and index finger to control direction",
                    "- P key: Pause/Resume game",
                    "- R key: Restart game when game over",
                    "- G key: Show/Hide grid",
                    "- W key: Enable/Disable wall collision",
                    "- H key: Show/Hide help",
                    "- M key: Toggle music",
                    "- +/- keys: Increase/Decrease game speed",
                    "- ESC key: Exit game"
                ]
                
                for i, text in enumerate(help_texts):
                    help_surface = help_font.render(text, True, (200, 200, 200))
                    screen.blit(help_surface, (video_x + 10, video_y + video_height - 240 + i * 25))
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            clock.tick(base_fps)
            
            # Update frame count
            frame_count += 1
    
    except KeyboardInterrupt:
        print("Game interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up resources
        if "background" in sounds:
            sounds["background"].stop()
        cap.release()
        gesture_detector.release()
        pygame.quit()
        print("Game exited")


if __name__ == "__main__":
    main() 