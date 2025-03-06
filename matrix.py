import pygame
import random
import ctypes
import os
import win32gui
import win32ui
import win32con
import threading
import time

# Initialize Pygame
pygame.init()

# Get screen dimensions for all monitors
user32 = ctypes.windll.user32

# Get total desktop area (all monitors)
TOTAL_WIDTH = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
TOTAL_HEIGHT = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
VIRTUAL_LEFT = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
VIRTUAL_TOP = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN

# Position our window to cover the entire virtual desktop (all monitors)
MONITOR_X = VIRTUAL_LEFT
MONITOR_Y = VIRTUAL_TOP
WIDTH = TOTAL_WIDTH
HEIGHT = TOTAL_HEIGHT

# Set up the display to cover the entire virtual desktop
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{MONITOR_X},{MONITOR_Y}"
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Matrix Background")

# Get window handle
hwnd = pygame.display.get_wm_info()['window']

# Make window transparent and click-through
ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                      ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_COLORKEY)

# Set window to bottom (behind other windows but above desktop)
try:
    # Use HWND_BOTTOM to place it at the bottom of the Z order
    win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, MONITOR_X, MONITOR_Y, WIDTH, HEIGHT, 0)
except Exception as e:
    print(f"Warning: Could not set window position: {e}")

# Colors and font settings
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
FONT_SIZE = 16
FONT = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE)

# Matrix effect settings
columns = WIDTH // FONT_SIZE
drops = [random.randint(-HEIGHT // FONT_SIZE, 0) for _ in range(columns)]  # Start at random heights
char_history = [[] for _ in range(columns)]  # Keep track of characters for each column

# Flag to control the main loop
running = True

# Function to check for ESC key to exit the program
def check_exit():
    global running
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        # Try to keep the window at the bottom of the Z-order periodically
        try:
            win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, MONITOR_X, MONITOR_Y, WIDTH, HEIGHT, 0)
        except:
            # Ignore errors during periodic positioning
            pass
            
        time.sleep(1)  # Check every second

# Start a thread to check for ESC key
exit_thread = threading.Thread(target=check_exit)
exit_thread.daemon = True
exit_thread.start()

# Main loop
clock = pygame.time.Clock()

try:
    while running:
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw the matrix effect
        for i in range(len(drops)):
            # Only process columns that are visible on screen (optimization)
            col_x = i * FONT_SIZE
            if col_x < 0 or col_x > WIDTH:
                continue
                
            # Update character history
            if drops[i] >= 0:  # Only add characters when they're on screen
                # Generate a new character and add it to history
                char = chr(random.randint(33, 126))
                if len(char_history[i]) < HEIGHT // FONT_SIZE:
                    char_history[i].append(char)
                else:
                    char_history[i].pop(0)
                    char_history[i].append(char)
            
            # Draw all characters in the column with varying brightness
            for j in range(len(char_history[i])):
                y_pos = (drops[i] - len(char_history[i]) + j) * FONT_SIZE
                
                # Only draw if it's on screen
                if 0 <= y_pos < HEIGHT:
                    # Fade characters based on position
                    if j == len(char_history[i]) - 1:
                        # Leading character is brightest
                        color = GRAY
                    elif j > len(char_history[i]) - 5:
                        # Last few characters are light gray
                        color = LIGHT_GRAY
                    else:
                        # Earlier characters are dark gray
                        color = DARK_GRAY
                    
                    char_surface = FONT.render(char_history[i][j], True, color)
                    screen.blit(char_surface, (col_x, y_pos))
            
            # Update drops position
            drops[i] += 1
            
            # Reset drop when it goes off screen with random delay
            if drops[i] * FONT_SIZE > HEIGHT + FONT_SIZE * 5:
                drops[i] = random.randint(-30, -5)  # Start above the screen with random delay
                char_history[i] = []  # Clear character history for this column
        
        pygame.display.flip()
        clock.tick(15)  # Reduced speed for better effect
        
except KeyboardInterrupt:
    running = False
except Exception as e:
    print(f"Error: {e}")
finally:
    pygame.quit()
