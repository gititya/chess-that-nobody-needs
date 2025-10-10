import pygame
import chess
import chess.engine
import os

# === Settings ===
MIN_BOARD_WIDTH = 400
DEFAULT_BOARD_WIDTH = 512
MARGIN = 30  # Space around the board for labels
FPS = 60
MENU_WIDTH_RATIO = 0.35  # Menu width as ratio of total window width
MIN_WINDOW_WIDTH = 700
MIN_WINDOW_HEIGHT = 500

# Dynamic sizing variables (will be set in main)
BOARD_WIDTH = DEFAULT_BOARD_WIDTH
SQUARE_SIZE = BOARD_WIDTH // 8
MENU_WIDTH = 200
TOTAL_WIDTH = BOARD_WIDTH + MENU_WIDTH
TOTAL_HEIGHT = BOARD_WIDTH + 2 * MARGIN

# === Update this with the path to your Stockfish binary ===
STOCKFISH_PATH = "/Users/aditya/Documents/programming/chess/stockfish/stockfish-macos-m1-apple-silicon"

# === ELO Settings ===
ELO_LEVELS = {
    "Beginner (800)": 800,
    "Amateur (1200)": 1200,
    "Intermediate (1600)": 1600,
    "Advanced (2000)": 2000,
    "Expert (2400)": 2400,
    "Master (2800)": 2800
}

# === AI Thinking Time Settings ===
THINKING_TIMES = {
    "Instant (0.1s)": 0.1,
    "Fast (0.5s)": 0.5,
    "Normal (1.0s)": 1.0,
    "Slow (2.0s)": 2.0,
    "Deep (5.0s)": 5.0
}

# === Player Color Options ===
PLAYER_COLORS = {
    "Play as White": chess.WHITE,
    "Play as Black": chess.BLACK
}

# === Piece Set Options ===
PIECE_SETS = {
    "Classic": "assets-classic",
    "Anarchy": "assets-anarchy",
    "Modern Hoofare": "assets-Modern Hoofare"
}

# === Load Sound Effects ===
def load_sounds():
    try:
        sounds = {
            'move': pygame.mixer.Sound('sounds/move.wav'),
            'capture': pygame.mixer.Sound('sounds/capture.wav'),
            'check': pygame.mixer.Sound('sounds/check.wav'),
            'game_end': pygame.mixer.Sound('sounds/game_end.wav')
        }
        return sounds
    except:
        # Return empty dict if sound files not found
        return {}

# === Load Images ===
def load_images(asset_folder="assets-classic"):
    mapping = {
        'K': 'wK.png', 'Q': 'wQ.png', 'R': 'wR.png', 'B': 'wB.png', 'N': 'wN.png', 'P': 'wP.png',
        'k': 'bK.png', 'q': 'bQ.png', 'r': 'bR.png', 'b': 'bB.png', 'n': 'bN.png', 'p': 'bP.png'
    }
    images = {}
    for piece, filename in mapping.items():
        try:
            images[piece] = pygame.transform.scale(
                pygame.image.load(f"{asset_folder}/{filename}"), (SQUARE_SIZE, SQUARE_SIZE))
        except pygame.error:
            # Fallback to assets-classic if piece not found in selected set
            images[piece] = pygame.transform.scale(
                pygame.image.load(f"assets-classic/{filename}"), (SQUARE_SIZE, SQUARE_SIZE))
    return images

# === Update Window Dimensions ===
def update_dimensions(window_width, window_height):
    global BOARD_WIDTH, SQUARE_SIZE, MENU_WIDTH, TOTAL_WIDTH, TOTAL_HEIGHT

    # Calculate optimal board width based on window size
    available_width = window_width * (1 - MENU_WIDTH_RATIO)
    BOARD_WIDTH = max(MIN_BOARD_WIDTH, min(available_width - 2 * MARGIN, window_height - 2 * MARGIN))
    BOARD_WIDTH = (BOARD_WIDTH // 8) * 8  # Ensure divisible by 8
    SQUARE_SIZE = BOARD_WIDTH // 8

    MENU_WIDTH = max(200, window_width - BOARD_WIDTH - 2 * MARGIN)
    TOTAL_WIDTH = window_width
    TOTAL_HEIGHT = window_height

# === Draw Board Labels (Ranks and Files) ===
def draw_board_labels(screen, font, flipped=False):
    if flipped:
        files = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
    else:
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
    label_color = pygame.Color(80, 80, 80)

    # Files: top and bottom
    for i, file_label in enumerate(files):
        x_center = MARGIN + i * SQUARE_SIZE + SQUARE_SIZE // 2

        # Top
        text_top = font.render(file_label, True, label_color)
        screen.blit(text_top, text_top.get_rect(center=(x_center, MARGIN // 2)))

        # Bottom
        text_bottom = font.render(file_label, True, label_color)
        screen.blit(text_bottom, text_bottom.get_rect(center=(x_center, MARGIN + BOARD_WIDTH + MARGIN // 2)))

    # Ranks: left and right
    for i, rank_label in enumerate(ranks):
        y_center = MARGIN + i * SQUARE_SIZE + SQUARE_SIZE // 2

        # Left
        text_left = font.render(rank_label, True, label_color)
        screen.blit(text_left, text_left.get_rect(center=(MARGIN // 2, y_center)))

        # Right
        text_right = font.render(rank_label, True, label_color)
        screen.blit(text_right, text_right.get_rect(center=(MARGIN + BOARD_WIDTH + MARGIN // 2, y_center)))

# === Draw Legal Moves ===
def draw_legal_moves(screen, board, selected_square, flipped=False):
    if selected_square is None:
        return
    
    # Get all legal moves from the selected square
    legal_moves_from_square = [move for move in board.legal_moves if move.from_square == selected_square]
    
    # Draw green circles on target squares
    for move in legal_moves_from_square:
        if flipped:
            target_row = move.to_square // 8
            target_col = 7 - (move.to_square % 8)
        else:
            target_row = 7 - move.to_square // 8
            target_col = move.to_square % 8
        center_x = MARGIN + target_col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y = MARGIN + target_row * SQUARE_SIZE + SQUARE_SIZE // 2
        
        # Check if target square has an enemy piece (capture move)
        target_piece = board.piece_at(move.to_square)
        if target_piece:
            # Red circle for captures
            pygame.draw.circle(screen, pygame.Color(255, 100, 100), (center_x, center_y), 15, 3)
        else:
            # Green circle for regular moves
            pygame.draw.circle(screen, pygame.Color(100, 255, 100), (center_x, center_y), 8)

# === Draw Selected Square Highlight ===
def draw_selected_square(screen, selected_square, flipped=False):
    if selected_square is None:
        return
    
    if flipped:
        row = selected_square // 8
        col = 7 - (selected_square % 8)
    else:
        row = 7 - selected_square // 8
        col = selected_square % 8
    # Yellow highlight for selected square
    pygame.draw.rect(screen, pygame.Color(255, 255, 0),
                    pygame.Rect(MARGIN + col*SQUARE_SIZE, MARGIN + row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)
    
# === Draw Board ===
def draw_board(screen):
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(MARGIN + col*SQUARE_SIZE, MARGIN + row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# === Draw Pieces ===
def draw_pieces(screen, board, images, flipped=False):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if flipped:
                row = square // 8
                col = 7 - (square % 8)
            else:
                row = 7 - square // 8
                col = square % 8
            screen.blit(images[piece.symbol()], pygame.Rect(MARGIN + col*SQUARE_SIZE, MARGIN + row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# === Convert pixel position to square index ===
def get_square_from_pos(pos, flipped=False):
    x, y = pos
    # Adjust for margin
    x -= MARGIN
    y -= MARGIN
    if x < 0 or y < 0 or x >= BOARD_WIDTH or y >= BOARD_WIDTH:
        return None
    if flipped:
        col = int(7 - (x // SQUARE_SIZE))
        row = int(y // SQUARE_SIZE)
    else:
        col = int(x // SQUARE_SIZE)
        row = int(7 - (y // SQUARE_SIZE))
    return chess.square(col, row)

# === Track and Draw Captured Pieces ===
def get_captured_pieces(board):
    """Returns lists of captured pieces for both sides"""
    all_pieces = {'P': 8, 'R': 2, 'N': 2, 'B': 2, 'Q': 1, 'K': 1,
                  'p': 8, 'r': 2, 'n': 2, 'b': 2, 'q': 1, 'k': 1}
    
    # Count pieces still on board
    current_pieces = {}
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            current_pieces[symbol] = current_pieces.get(symbol, 0) + 1
    
    # Calculate captured pieces
    white_captured = []
    black_captured = []
    
    for piece_type in ['p', 'r', 'n', 'b', 'q']:  # Don't show captured kings
        # White pieces captured by black
        missing_white = all_pieces[piece_type.upper()] - current_pieces.get(piece_type.upper(), 0)
        white_captured.extend([piece_type.upper()] * missing_white)
        
        # Black pieces captured by white  
        missing_black = all_pieces[piece_type] - current_pieces.get(piece_type, 0)
        black_captured.extend([piece_type] * missing_black)
    
    return white_captured, black_captured

def draw_captured_pieces(screen, font, font_small, images, board, y_start, menu_start_x):
    """Draw captured pieces in the menu panel"""
    white_captured, black_captured = get_captured_pieces(board)

    # Title
    title_text = font.render("Captured Pieces:", True, pygame.Color(0, 0, 0))
    screen.blit(title_text, (menu_start_x + 10, y_start))
    y_offset = y_start + 25
    
    # White pieces captured by black (you lost these)
    if white_captured:
        label_text = font_small.render("You lost:", True, pygame.Color(150, 0, 0))
        screen.blit(label_text, (menu_start_x + 10, y_offset))
        y_offset += 20

        x_offset = menu_start_x + 10
        piece_size = 25
        for i, piece in enumerate(white_captured):
            if i > 0 and i % 6 == 0:  # New row every 6 pieces
                y_offset += piece_size + 2
                x_offset = menu_start_x + 10
            
            # Scale down the piece image
            small_image = pygame.transform.scale(images[piece], (piece_size, piece_size))
            screen.blit(small_image, (x_offset, y_offset))
            x_offset += piece_size + 2
        
        y_offset += piece_size + 10
    
    # Black pieces captured by white (you captured these)
    if black_captured:
        label_text = font_small.render("You captured:", True, pygame.Color(0, 150, 0))
        screen.blit(label_text, (menu_start_x + 10, y_offset))
        y_offset += 20

        x_offset = menu_start_x + 10
        piece_size = 25
        for i, piece in enumerate(black_captured):
            if i > 0 and i % 6 == 0:  # New row every 6 pieces
                y_offset += piece_size + 2
                x_offset = menu_start_x + 10
            
            # Scale down the piece image
            small_image = pygame.transform.scale(images[piece], (piece_size, piece_size))
            screen.blit(small_image, (x_offset, y_offset))
            x_offset += piece_size + 2
        
        y_offset += piece_size + 10
    
    return y_offset  # Return new y position for next elements

# === Draw Move History ===
def draw_move_history(screen, font, font_small, board, y_start, menu_start_x):
    """Draw the last 10 moves in the menu panel"""
    title_text = font.render("Move History:", True, pygame.Color(0, 0, 0))
    screen.blit(title_text, (menu_start_x + 10, y_start))
    y_offset = y_start + 25

    # Get last 10 moves
    moves = list(board.move_stack)[-10:]

    for i, move in enumerate(moves):
        move_num = len(board.move_stack) - len(moves) + i + 1
        if move_num % 2 == 1:  # White move
            move_text = f"{(move_num + 1) // 2}. {move}"
        else:  # Black move
            move_text = f"   {move}"

        text_surface = font_small.render(move_text, True, pygame.Color(0, 0, 0))
        screen.blit(text_surface, (menu_start_x + 10, y_offset))
        y_offset += 20

    return y_offset + 10

# === Draw Menu Panel ===
def draw_menu_panel(screen, font, font_small, images, board, selected_elo, selected_thinking_time, player_color, board_flipped, selected_piece_set, game_over, game_result, game_started):
    # Fill menu area with gray background
    menu_start_x = MARGIN + BOARD_WIDTH + MARGIN
    menu_rect = pygame.Rect(menu_start_x, 0, MENU_WIDTH, TOTAL_HEIGHT)
    pygame.draw.rect(screen, pygame.Color(240, 240, 240), menu_rect)

    y_offset = 20
    section_spacing = max(15, TOTAL_HEIGHT // 40)
    item_spacing = max(8, TOTAL_HEIGHT // 80)

    # Player Color Selection (only if game not started)
    if not game_started:
        title_text = font.render("Play as:", True, pygame.Color(0, 0, 0))
        screen.blit(title_text, (menu_start_x + 10, y_offset))
        y_offset += 25

        for label, color in PLAYER_COLORS.items():
            text_color = pygame.Color(0, 100, 0) if color == player_color else pygame.Color(50, 50, 50)
            color_text = font_small.render(label, True, text_color)
            screen.blit(color_text, (menu_start_x + 10, y_offset))
            y_offset += 20

        y_offset += section_spacing
    else:
        # Show current player color when game is active
        current_color = "White" if player_color == chess.WHITE else "Black"
        title_text = font.render(f"Playing as: {current_color}", True, pygame.Color(0, 100, 0))
        screen.blit(title_text, (menu_start_x + 10, y_offset))
        y_offset += 30

    # ELO Selection
    title_text = font.render("Difficulty (ELO):", True, pygame.Color(0, 0, 0))
    screen.blit(title_text, (menu_start_x + 10, y_offset))
    y_offset += 25

    for i, (label, elo) in enumerate(ELO_LEVELS.items()):
        color = pygame.Color(0, 100, 0) if elo == selected_elo else pygame.Color(50, 50, 50)
        elo_text = font_small.render(label, True, color)
        screen.blit(elo_text, (menu_start_x + 10, y_offset))
        y_offset += 20

    y_offset += section_spacing

    # Thinking Time Selection
    title_text = font.render("Game Speed:", True, pygame.Color(0, 0, 0))
    screen.blit(title_text, (menu_start_x + 10, y_offset))
    y_offset += 25

    for label, time_val in THINKING_TIMES.items():
        color = pygame.Color(0, 100, 0) if time_val == selected_thinking_time else pygame.Color(50, 50, 50)
        time_text = font_small.render(label, True, color)
        screen.blit(time_text, (menu_start_x + 10, y_offset))
        y_offset += 20

    y_offset += section_spacing

    # Piece Set Selection
    title_text = font.render("Chess Piece:", True, pygame.Color(0, 0, 0))
    screen.blit(title_text, (menu_start_x + 10, y_offset))
    y_offset += 25

    for label, folder in PIECE_SETS.items():
        color = pygame.Color(0, 100, 0) if folder == selected_piece_set else pygame.Color(50, 50, 50)
        piece_text = font_small.render(label, True, color)
        screen.blit(piece_text, (menu_start_x + 10, y_offset))
        y_offset += 20

    y_offset += section_spacing

    # Board Flip Button
    flip_text = "Flip Board" + (" ✓" if board_flipped else "")
    button_width = MENU_WIDTH - 20
    flip_rect = pygame.Rect(menu_start_x + 10, y_offset, button_width, 30)
    pygame.draw.rect(screen, pygame.Color(150, 200, 255), flip_rect)
    pygame.draw.rect(screen, pygame.Color(0, 0, 0), flip_rect, 2)
    flip_button_text = font.render(flip_text, True, pygame.Color(0, 0, 0))
    screen.blit(flip_button_text, (menu_start_x + 15, y_offset + 6))

    y_offset += 45

    # Resign Button (only during active game)
    resign_rect = None
    if game_started and not game_over:
        resign_rect = pygame.Rect(menu_start_x + 10, y_offset, button_width, 30)
        pygame.draw.rect(screen, pygame.Color(255, 150, 150), resign_rect)
        pygame.draw.rect(screen, pygame.Color(0, 0, 0), resign_rect, 2)
        resign_text = font.render("Resign Game", True, pygame.Color(0, 0, 0))
        screen.blit(resign_text, (menu_start_x + 15, y_offset + 6))
        y_offset += 45
    
    # New Game Button
    new_game_rect = pygame.Rect(menu_start_x + 10, y_offset, button_width, 30)
    pygame.draw.rect(screen, pygame.Color(100, 150, 255), new_game_rect)
    pygame.draw.rect(screen, pygame.Color(0, 0, 0), new_game_rect, 2)
    new_game_text = font.render("New Game", True, pygame.Color(0, 0, 0))
    screen.blit(new_game_text, (menu_start_x + 15, y_offset + 6))

    y_offset += 45

    # Captured Pieces Section
    y_offset = draw_captured_pieces(screen, font, font_small, images, board, y_offset, menu_start_x)
    y_offset += section_spacing
    
    # Game Status
    if game_over:
        status_text = font.render("Game Over!", True, pygame.Color(255, 0, 0))
        screen.blit(status_text, (menu_start_x + 10, y_offset))
        y_offset += 30

        result_text = font.render(game_result, True, pygame.Color(0, 0, 0))
        screen.blit(result_text, (menu_start_x + 10, y_offset))
    else:
        status_text = font.render("Game Active", True, pygame.Color(0, 150, 0))
        screen.blit(status_text, (menu_start_x + 10, y_offset))

    y_offset += 30  # Add spacing after game status

    # Move History
    y_offset = draw_move_history(screen, font, font_small, board, y_offset, menu_start_x)

    return new_game_rect, flip_rect, resign_rect

# === Get Game Result Text ===
def get_game_result_text(board):
    result = board.result()
    if result == "1-0":
        return "You Won!"
    elif result == "0-1":
        return "Stockfish Won!"
    elif result == "1/2-1/2":
        if board.is_stalemate():
            return "Draw - Stalemate"
        elif board.is_insufficient_material():
            return "Draw - Insufficient Material"
        elif board.is_seventyfive_moves():
            return "Draw - 75 Move Rule"
        elif board.is_fivefold_repetition():
            return "Draw - Repetition"
        else:
            return "Draw"
    else:
        return "Game Ongoing"

# === Play Sound Effect ===
def play_sound(sounds, sound_name):
    """Play a sound effect if available"""
    if sound_name in sounds:
        try:
            sounds[sound_name].play()
        except:
            pass  # Ignore sound errors

# === Handle Menu Clicks ===
def handle_menu_click(pos, selected_elo, selected_thinking_time, player_color, board_flipped, selected_piece_set, game_started):
    x, y = pos
    menu_start_x = MARGIN + BOARD_WIDTH + MARGIN
    if x < menu_start_x:
        return selected_elo, selected_thinking_time, player_color, board_flipped, selected_piece_set, False, False, False

    y_offset = 20
    section_spacing = max(15, TOTAL_HEIGHT // 40)
    item_spacing = max(8, TOTAL_HEIGHT // 80)

    # Check Player Color selection clicks (only if game not started)
    if not game_started:
        y_offset += 25
        for label, color in PLAYER_COLORS.items():
            if y_offset <= y <= y_offset + 20:
                return selected_elo, selected_thinking_time, color, board_flipped, selected_piece_set, False, False, False
            y_offset += 20
        y_offset += section_spacing
    else:
        y_offset += 30

    # Check ELO selection clicks
    y_offset += 25
    for label, elo in ELO_LEVELS.items():
        if y_offset <= y <= y_offset + (item_spacing * 2 + 12):
            return elo, selected_thinking_time, player_color, board_flipped, selected_piece_set, False, False, False
        y_offset += item_spacing * 2 + 12
    y_offset += section_spacing

    # Check Thinking Time selection clicks
    y_offset += 25
    for label, time_val in THINKING_TIMES.items():
        if y_offset <= y <= y_offset + (item_spacing * 2 + 12):
            return selected_elo, time_val, player_color, board_flipped, selected_piece_set, False, False, False
        y_offset += item_spacing * 2 + 12
    y_offset += section_spacing

    # Check Piece Set selection clicks
    y_offset += 25
    for label, folder in PIECE_SETS.items():
        if y_offset <= y <= y_offset + 20:
            return selected_elo, selected_thinking_time, player_color, board_flipped, folder, False, False, False
        y_offset += 20
    y_offset += section_spacing

    # Check Flip Board button
    if y_offset <= y <= y_offset + 30:
        return selected_elo, selected_thinking_time, player_color, not board_flipped, selected_piece_set, False, True, False
    y_offset += 45

    # Check Resign button (only during active game)
    if game_started:
        if y_offset <= y <= y_offset + 30:
            return selected_elo, selected_thinking_time, player_color, board_flipped, selected_piece_set, False, False, True
        y_offset += 45

    # Check New Game button
    if y_offset <= y <= y_offset + 30:
        return selected_elo, selected_thinking_time, player_color, board_flipped, selected_piece_set, True, False, False

    return selected_elo, selected_thinking_time, player_color, board_flipped, selected_piece_set, False, False, False

# === Configure Engine ELO ===
def configure_engine_elo(engine, target_elo):
    try:
        # Set skill level based on ELO (0-20 scale, where 20 is strongest)
        if target_elo <= 1000:
            skill_level = 0
        elif target_elo <= 1200:
            skill_level = 3
        elif target_elo <= 1400:
            skill_level = 6
        elif target_elo <= 1600:
            skill_level = 10
        elif target_elo <= 1800:
            skill_level = 13
        elif target_elo <= 2000:
            skill_level = 16
        elif target_elo <= 2200:
            skill_level = 18
        else:
            skill_level = 20
        
        engine.configure({"Skill Level": skill_level})
        
        # Also limit depth for lower ELOs
        if target_elo < 1600:
            engine.configure({"Depth": min(10, max(1, target_elo // 200))})
            
    except:
        # If configuration fails, continue with default settings
        pass

# === Main Function ===> VIEW ONLY BOARD
# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
#     pygame.display.set_caption("Chess vs Stockfish")
#     clock = pygame.time.Clock()

#     board = chess.Board()
#     images = load_images()

#     engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

#     selected_square = None
#     running = True

#     while running:
#         clock.tick(FPS)
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#                 break

#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 if selected_square is None:
#                     selected_square = get_square_from_pos(pygame.mouse.get_pos())
#                 else:
#                     target_square = get_square_from_pos(pygame.mouse.get_pos())
#                     move = chess.Move(selected_square, target_square)
#                     if move in board.legal_moves:
#                         board.push(move)

#                         if not board.is_game_over():
#                             result = engine.play(board, chess.engine.Limit(time=0.5))
#                             board.push(result.move)

#                     selected_square = None

#         draw_board(screen)
#         draw_pieces(screen, board, images)
#         pygame.display.flip()

#     engine.quit()
#     pygame.quit()

# if __name__ == "__main__":
#     main()

# === Main Function ===> ENHANCED PLAYABILITY
def main():
    pygame.init()
    pygame.mixer.init()  # Initialize sound mixer

    # Initialize with default size but make resizable
    initial_width = DEFAULT_BOARD_WIDTH + 200 + 2 * MARGIN
    initial_height = DEFAULT_BOARD_WIDTH + 2 * MARGIN
    screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
    pygame.display.set_caption("Enhanced Chess vs Stockfish")

    # Update dimensions based on initial window size
    update_dimensions(initial_width, initial_height)

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)  # Heading font
    font_small = pygame.font.Font(None, 20)  # Menu item font

    # Initialize game state
    board = chess.Board()
    selected_piece_set = "assets-classic"  # Default piece set
    images = load_images(selected_piece_set)
    sounds = load_sounds()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    selected_square = None
    selected_elo = 1200  # Default ELO
    selected_thinking_time = 0.5  # Default thinking time
    player_color = chess.WHITE  # Default: play as white
    board_flipped = False  # Default: not flipped
    game_over = False
    game_result = ""
    game_started = False  # Track if moves have been made
    running = True
    ai_thinking = False

    # Configure initial engine strength
    configure_engine_elo(engine, selected_elo)

    while running:
        clock.tick(FPS)
        
        # Check if game just ended
        if not game_over and board.is_game_over():
            game_over = True
            game_result = get_game_result_text(board)
            play_sound(sounds, 'game_end')

        # Handle AI move when it's AI's turn
        if not game_over and not ai_thinking and board.turn != player_color:
            ai_thinking = True
            result = engine.play(board, chess.engine.Limit(time=selected_thinking_time))

            # Check if it's a capture
            is_capture = board.piece_at(result.move.to_square) is not None

            board.push(result.move)
            ai_thinking = False

            # Play appropriate sound
            if board.is_check():
                play_sound(sounds, 'check')
            elif is_capture:
                play_sound(sounds, 'capture')
            else:
                play_sound(sounds, 'move')
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                new_width = max(MIN_WINDOW_WIDTH, event.w)
                new_height = max(MIN_WINDOW_HEIGHT, event.h)
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                update_dimensions(new_width, new_height)
                # Reload images with new square size
                images = load_images(selected_piece_set)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle menu clicks
                new_elo, new_thinking_time, new_player_color, new_board_flipped, new_piece_set, start_new_game, flip_clicked, resign_clicked = handle_menu_click(
                    mouse_pos, selected_elo, selected_thinking_time, player_color, board_flipped, selected_piece_set, game_started)

                # Update settings
                if new_elo != selected_elo:
                    selected_elo = new_elo
                    configure_engine_elo(engine, selected_elo)

                if new_thinking_time != selected_thinking_time:
                    selected_thinking_time = new_thinking_time

                if new_player_color != player_color and not game_started:
                    player_color = new_player_color
                    # Auto-flip board when switching colors
                    board_flipped = (player_color == chess.BLACK)

                if new_piece_set != selected_piece_set:
                    selected_piece_set = new_piece_set
                    print(f"Loading piece set: {selected_piece_set}")
                    images = load_images(selected_piece_set)
                    print(f"Images reloaded successfully")

                if flip_clicked:
                    board_flipped = new_board_flipped

                if resign_clicked:
                    # Handle resignation
                    game_over = True
                    game_result = "You Resigned - Stockfish Won!"
                    play_sound(sounds, 'game_end')

                if start_new_game:
                    # Reset game
                    board = chess.Board()
                    selected_square = None
                    game_over = False
                    game_result = ""
                    game_started = False
                    ai_thinking = False
                    configure_engine_elo(engine, selected_elo)
                    continue
                
                # Handle board clicks (only if game is not over, not AI thinking, and click is on board)
                square_clicked = get_square_from_pos(mouse_pos, board_flipped)
                if not game_over and not ai_thinking and square_clicked is not None and board.turn == player_color:
                    if selected_square is None:
                        # Select a piece of player's color when it's player's turn
                        piece = board.piece_at(square_clicked)
                        if piece and piece.color == player_color:
                            selected_square = square_clicked
                    else:
                        target_square = square_clicked

                        # If clicking the same square, deselect
                        if target_square == selected_square:
                            selected_square = None
                            continue

                        # Try to make the move
                        move = chess.Move(selected_square, target_square)

                        # Check for pawn promotion
                        piece = board.piece_at(selected_square)
                        if piece and piece.piece_type == chess.PAWN:
                            promotion_rank = 7 if player_color == chess.WHITE else 0
                            if chess.square_rank(target_square) == promotion_rank:
                                move = chess.Move(selected_square, target_square, promotion=chess.QUEEN)

                        if move in board.legal_moves:
                            # Check if it's a capture
                            is_capture = board.piece_at(target_square) is not None

                            board.push(move)
                            selected_square = None
                            game_started = True  # Mark game as started

                            # Play appropriate sound
                            if board.is_check():
                                play_sound(sounds, 'check')
                            elif is_capture:
                                play_sound(sounds, 'capture')
                            else:
                                play_sound(sounds, 'move')
                        else:
                            selected_square = None

        # Clear screen
        screen.fill(pygame.Color(50, 50, 50))  # Dark background

        # Draw everything
        draw_board(screen)
        draw_board_labels(screen, font, board_flipped)
        draw_selected_square(screen, selected_square, board_flipped)
        draw_legal_moves(screen, board, selected_square, board_flipped)
        draw_pieces(screen, board, images, board_flipped)

        # Draw menu panel
        new_game_rect, flip_rect, resign_rect = draw_menu_panel(screen, font, font_small, images, board, selected_elo,
                                                               selected_thinking_time, player_color, board_flipped,
                                                               selected_piece_set, game_over, game_result, game_started)

        
        pygame.display.flip()

    engine.quit()
    pygame.quit()

if __name__ == "__main__":
    main()

### ==== STAGE 1 AND 2 === ###
#1. BASIC PLAYABILITY WITH ADJUSTMENTS TO ELO, NEW GAME BUTTON, AND CAPTURED PIECES --> done
#2. INDICATIONS ON WHEN GAME IS OVER AND RESULT --> done

## -- WHAT IS NEEDED? -- ##
#1. BETTER CHESS PIECES - MAYBE V2/V3 - https://official-stockfish.github.io/docs/stockfish-wiki/Download-and-usage.html#install-in-a-chess-gui 
# 3. ABILITY TO SAVE AND LOAD GAMES
# 4. OPTION TO PLAY AS BLACK --> done
# 5. LABELS ON BOARD (RANKS AND FILES) --> done
# 6. BETTER UI/UX 
# 7. UPDATE THE STOCKFISH BINARY FROM M1 TO THE BREW VERSION - https://stockfishchess.org/download/
# 8. ADD SOUNDS
# 9. WHY IS THE ENGINE SO FAST? CAN WE SLOW IT DOWN A BIT? --> done
# 10. GAME ANALYSIS FEATURE - MAYBE LATER
# 11. CONSOLIDATE STAGE 2(THERE ARE TWO!!) --> done

### ==== MVP (Minimum Viable Product) === ###
# 1. Playability with 3 different chess piece sets --> done
# 2. Game controls with varied ELO, game speed, and playing as black/white --> done
# 3. Move history & captured pieces tracking --> done
# 4. Controls to flip board during gameplay and start new game --> done

## -- Future Enhancements -- ##
# 1. ADD SOUNDS
# 2. ABILITY TO SAVE AND LOAD GAMES
# 3. GAME ANALYSIS FEATURE
# 4. Training integration with Bobby Fischer materials
# 5. Web app (FastAPI + WebSocket + LLM personality)