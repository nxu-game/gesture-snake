"""
Snake game module - Implements the classic Snake game logic
"""

import pygame
import random
import numpy as np


class SnakeGame:
    """
    Snake game implementation with Pygame
    """
    def __init__(self, width, height):
        """
        Initialize the Snake game

        Args:
            width (int): Width of the game surface
            height (int): Height of the game surface
        """
        self.width = width
        self.height = height
        
        # Adjust cell size based on game area dimensions
        self.cell_size = max(20, min(30, width // 30, height // 30))
        
        # Initialize snake
        self.snake = [(width // 2, height // 2)]
        self.length = 1
        
        # Initialize direction (x, y)
        self.direction = (1, 0)  # Initial direction: right
        self.next_direction = (1, 0)
        
        # Initialize food
        self.food = self._generate_food()
        
        # Game state
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # Create game surface
        self.surface = pygame.Surface((width, height))
        
        # Color definitions
        self.colors = {
            "background": (0, 0, 0),
            "snake_head": (0, 200, 0),  # Snake head color
            "snake_body": (0, 255, 0),  # Snake body color
            "food": (255, 0, 0),
            "text": (255, 255, 255),
            "grid": (20, 20, 20),  # Grid line color
            "border": (100, 100, 255)  # Border color
        }
        
        # Initialize fonts
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.large_font = pygame.font.SysFont('Arial', 48)
        
        # Game speed (pixels moved per update) - lower initial speed
        self.speed = 0.5
        
        # Show grid option
        self.show_grid = True
        
        # Movement timer - controls snake movement frequency
        self.move_timer = 0
        self.move_delay = 5  # Move every N frames
        
        # Game mode
        self.wall_collision = True  # Whether wall collision is enabled
        
        # Food proximity threshold (in cells)
        self.food_proximity = 1  # How close the snake needs to be to eat food
    
    def _generate_food(self):
        """
        Generate new food, ensuring it's not on the snake

        Returns:
            tuple: (x, y) food coordinates
        """
        while True:
            x = random.randint(0, (self.width // self.cell_size) - 1) * self.cell_size
            y = random.randint(0, (self.height // self.cell_size) - 1) * self.cell_size
            food_pos = (x, y)
            
            if food_pos not in self.snake:
                return food_pos
    
    def change_direction(self, direction_name):
        """
        Change snake direction based on direction name

        Args:
            direction_name (str): Direction name ('UP', 'RIGHT', 'DOWN', 'LEFT')
        """
        direction_map = {
            "UP": (0, -1),
            "RIGHT": (1, 0),
            "DOWN": (0, 1),
            "LEFT": (-1, 0)
        }
        
        if direction_name in direction_map:
            new_direction = direction_map[direction_name]
            
            # Prevent 180-degree turns (can't go directly opposite)
            if (new_direction[0] != -self.direction[0] or 
                new_direction[1] != -self.direction[1]):
                self.next_direction = new_direction
    
    def toggle_wall_collision(self):
        """
        Toggle wall collision mode
        """
        self.wall_collision = not self.wall_collision
    
    def update(self):
        """
        Update game state
        """
        if self.game_over or self.paused:
            return
        
        # Use movement timer to control snake movement frequency
        self.move_timer += 1
        if self.move_timer < self.move_delay / self.speed:
            return
        
        # Reset timer
        self.move_timer = 0
        
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head_x = head_x + dir_x * self.cell_size
        new_head_y = head_y + dir_y * self.cell_size
        
        # Check for wall collision
        if self.wall_collision:
            if (new_head_x < 0 or new_head_x >= self.width or
                new_head_y < 0 or new_head_y >= self.height):
                self.game_over = True
                return
            
            new_head = (new_head_x, new_head_y)
        else:
            # If wall collision is disabled, wrap around boundaries
            new_head = (
                new_head_x % self.width,
                new_head_y % self.height
            )
        
        # Check for self collision
        if new_head in self.snake:
            self.game_over = True
            return
        
        # Move snake
        self.snake.insert(0, new_head)
        
        # Check if food is eaten - with proximity detection
        food_eaten = False
        
        # Calculate distance to food in grid cells
        head_cell_x, head_cell_y = new_head[0] // self.cell_size, new_head[1] // self.cell_size
        food_cell_x, food_cell_y = self.food[0] // self.cell_size, self.food[1] // self.cell_size
        
        # Check if snake head is within proximity threshold of food
        if (abs(head_cell_x - food_cell_x) <= self.food_proximity and 
            abs(head_cell_y - food_cell_y) <= self.food_proximity):
            self.score += 1
            self.food = self._generate_food()
            food_eaten = True
            
            # Increase speed every 5 points, but with a lower maximum
            if self.score % 5 == 0:
                self.speed = min(self.speed + 0.1, 1.5)
        
        # If food wasn't eaten, remove tail
        if not food_eaten:
            self.snake.pop()
    
    def toggle_pause(self):
        """
        Toggle game pause state
        """
        self.paused = not self.paused
    
    def toggle_grid(self):
        """
        Toggle grid display
        """
        self.show_grid = not self.show_grid
    
    def render(self):
        """
        Render game screen

        Returns:
            pygame.Surface: Rendered game surface
        """
        # Fill background
        self.surface.fill(self.colors["background"])
        
        # Draw grid
        if self.show_grid:
            for x in range(0, self.width, self.cell_size):
                pygame.draw.line(self.surface, self.colors["grid"], (x, 0), (x, self.height))
            for y in range(0, self.height, self.cell_size):
                pygame.draw.line(self.surface, self.colors["grid"], (0, y), (self.width, y))
        
        # Draw border
        if self.wall_collision:
            border_width = 3
            pygame.draw.rect(
                self.surface,
                self.colors["border"],
                pygame.Rect(0, 0, self.width, self.height),
                border_width
            )
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            color = self.colors["snake_head"] if i == 0 else self.colors["snake_body"]
            pygame.draw.rect(
                self.surface, 
                color,
                pygame.Rect(segment[0], segment[1], self.cell_size, self.cell_size)
            )
            
            # Draw border on snake segments for better visibility
            pygame.draw.rect(
                self.surface,
                (0, 100, 0),
                pygame.Rect(segment[0], segment[1], self.cell_size, self.cell_size),
                1
            )
        
        # Draw food
        pygame.draw.rect(
            self.surface,
            self.colors["food"],
            pygame.Rect(self.food[0], self.food[1], self.cell_size, self.cell_size)
        )
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, self.colors["text"])
        self.surface.blit(score_text, (10, 10))
        
        # Draw speed
        speed_text = self.font.render(f'Speed: {self.speed:.1f}x', True, self.colors["text"])
        self.surface.blit(speed_text, (10, 40))
        
        # Draw wall collision mode
        wall_text = self.font.render(
            f'Wall Collision: {"On" if self.wall_collision else "Off"}', 
            True, 
            self.colors["text"]
        )
        self.surface.blit(wall_text, (10, 70))
        
        # If game is paused, show pause information
        if self.paused:
            pause_text = self.large_font.render('GAME PAUSED', True, self.colors["text"])
            text_rect = pause_text.get_rect(center=(self.width//2, self.height//2))
            self.surface.blit(pause_text, text_rect)
            
            resume_text = self.font.render('Press P to continue', True, self.colors["text"])
            resume_rect = resume_text.get_rect(center=(self.width//2, self.height//2 + 60))
            self.surface.blit(resume_text, resume_rect)
        
        # If game is over, show game over information
        if self.game_over:
            game_over_text = self.large_font.render('GAME OVER!', True, self.colors["text"])
            text_rect = game_over_text.get_rect(center=(self.width//2, self.height//2))
            self.surface.blit(game_over_text, text_rect)
            
            restart_text = self.font.render('Press R to restart', True, self.colors["text"])
            restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 60))
            self.surface.blit(restart_text, restart_rect)
        
        return self.surface
    
    def reset(self):
        """
        Reset game state
        """
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self._generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.speed = 0.5  # Reset to lower initial speed
        self.move_timer = 0 