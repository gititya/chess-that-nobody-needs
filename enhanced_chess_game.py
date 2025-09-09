import pygame
import chess
import chess.engine
import os

# === Settings ===
BOARD_WIDTH = 512
SQUARE_SIZE = BOARD_WIDTH // 8
FPS = 60
MENU_WIDTH = 200
TOTAL_WIDTH = BOARD_WIDTH + MENU_WIDTH

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

# === Load Images ===
def load_images():
    mapping = {
        'K': 'wK.png', 'Q': 'wQ.png', 'R': 'wR.png', 'B': 'wB.png', 'N': 'wN.png', 'P': 'wP.png',
        'k': 'bK.png', 'q': 'bQ.png', 'r': 'bR.png', 'b': 'bB.png', 'n': 'bN.png', 'p': 'bP.png'
    }
    images = {}
    for piece, filename in mapping.items():
        images[piece] = pygame.transform.scale(
            pygame.image.load(f"assetsv1/{filename}"), (SQUARE_SIZE, SQUARE_SIZE))
    return images

# === Draw Legal Moves ===
def draw_legal_moves(screen, board, selected_square):
    if selected_square is None:
        return
    
    # Get all legal moves from the selected square
    legal_moves_from_square = [move for move in board.legal_moves if move.from_square == selected_square]
    
    # Draw green circles on target squares
    for move in legal_moves_from_square:
        target_row = 7 - move.to_square // 8
        target_col = move.to_square % 8
        center_x = target_col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y = target_row * SQUARE_SIZE + SQUARE_SIZE // 2
        
        # Check if target square has an enemy piece (capture move)
        target_piece = board.piece_at(move.to_square)
        if target_piece:
            # Red circle for captures
            pygame.draw.circle(screen, pygame.Color(255, 100, 100), (center_x, center_y), 15, 3)
        else:
            # Green circle for regular moves
            pygame.draw.circle(screen, pygame.Color(100, 255, 100), (center_x, center_y), 8)

# === Draw Selected Square Highlight ===
def draw_selected_square(screen, selected_square):
    if selected_square is None:
        return
    
    row = 7 - selected_square // 8
    col = selected_square % 8
    # Yellow highlight for selected square
    pygame.draw.rect(screen, pygame.Color(255, 255, 0), 
                    pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

# === Draw Board ===
def draw_board(screen):
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# === Draw Pieces ===
def draw_pieces(screen, board, images):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - square // 8
            col = square % 8
            screen.blit(images[piece.symbol()], pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# === Convert pixel position to square index ===
def get_square_from_pos(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = 7 - (y // SQUARE_SIZE)
    return chess.square(col, row)

# === Draw Menu Panel ===
def draw_menu_panel(screen, font, selected_elo, game_over, game_result):
    # Fill menu area with gray background
    menu_rect = pygame.Rect(BOARD_WIDTH, 0, MENU_WIDTH, BOARD_WIDTH)
    pygame.draw.rect(screen, pygame.Color(200, 200, 200), menu_rect)
    
    y_offset = 20
    
    # ELO Selection
    title_text = font.render("Engine Strength:", True, pygame.Color(0, 0, 0))
    screen.blit(title_text, (BOARD_WIDTH + 10, y_offset))
    y_offset += 40
    
    for i, (label, elo) in enumerate(ELO_LEVELS.items()):
        color = pygame.Color(0, 100, 0) if elo == selected_elo else pygame.Color(0, 0, 0)
        elo_text = font.render(label, True, color)
        screen.blit(elo_text, (BOARD_WIDTH + 10, y_offset))
        y_offset += 25
    
    y_offset += 30
    
    # New Game Button
    new_game_rect = pygame.Rect(BOARD_WIDTH + 10, y_offset, 180, 30)
    pygame.draw.rect(screen, pygame.Color(100, 150, 255), new_game_rect)
    pygame.draw.rect(screen, pygame.Color(0, 0, 0), new_game_rect, 2)
    new_game_text = font.render("New Game", True, pygame.Color(0, 0, 0))
    screen.blit(new_game_text, (BOARD_WIDTH + 50, y_offset + 5))
    
    y_offset += 60
    
    # Game Status
    if game_over:
        status_text = font.render("Game Over!", True, pygame.Color(255, 0, 0))
        screen.blit(status_text, (BOARD_WIDTH + 10, y_offset))
        y_offset += 30
        
        result_text = font.render(game_result, True, pygame.Color(0, 0, 0))
        screen.blit(result_text, (BOARD_WIDTH + 10, y_offset))
    else:
        status_text = font.render("Game Active", True, pygame.Color(0, 150, 0))
        screen.blit(status_text, (BOARD_WIDTH + 10, y_offset))
    
    return new_game_rect

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

# === Handle Menu Clicks ===
def handle_menu_click(pos, selected_elo):
    x, y = pos
    if x < BOARD_WIDTH:
        return selected_elo, False
    
    # Check ELO selection clicks
    y_offset = 60
    for label, elo in ELO_LEVELS.items():
        if y_offset <= y <= y_offset + 25:
            return elo, False
        y_offset += 25
    
    # Check New Game button
    new_game_y = y_offset + 30
    if new_game_y <= y <= new_game_y + 30:
        return selected_elo, True
    
    return selected_elo, False

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

# === Main Function ===> PLAYABILITY WITH FEATURES
def main():
    pygame.init()
    screen = pygame.display.set_mode((TOTAL_WIDTH, BOARD_WIDTH))
    pygame.display.set_caption("Enhanced Chess vs Stockfish")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    # Initialize game state
    board = chess.Board()
    images = load_images()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    
    selected_square = None
    selected_elo = 1200  # Default ELO
    game_over = False
    game_result = ""
    running = True
    
    # Configure initial engine strength
    configure_engine_elo(engine, selected_elo)

    while running:
        clock.tick(FPS)
        
        # Check if game just ended
        if not game_over and board.is_game_over():
            game_over = True
            game_result = get_game_result_text(board)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle menu clicks
                new_elo, start_new_game = handle_menu_click(mouse_pos, selected_elo)
                if new_elo != selected_elo:
                    selected_elo = new_elo
                    configure_engine_elo(engine, selected_elo)
                
                if start_new_game:
                    # Reset game
                    board = chess.Board()
                    selected_square = None
                    game_over = False
                    game_result = ""
                    configure_engine_elo(engine, selected_elo)
                    continue
                
                # Handle board clicks (only if game is not over and click is on board)
                if not game_over and mouse_pos[0] < BOARD_WIDTH:
                    if selected_square is None:
                        # Only select a white piece when it's your turn
                        square = get_square_from_pos(mouse_pos)
                        piece = board.piece_at(square)
                        if piece and piece.color == chess.WHITE and board.turn == chess.WHITE:
                            selected_square = square
                    else:
                        target_square = get_square_from_pos(mouse_pos)
                        
                        # If clicking the same square, deselect
                        if target_square == selected_square:
                            selected_square = None
                            continue
                            
                        # Try to make the move
                        move = chess.Move(selected_square, target_square)
                        
                        # Check for pawn promotion
                        piece = board.piece_at(selected_square)
                        if (piece.piece_type == chess.PAWN and 
                            chess.square_rank(target_square) == 7):
                            move = chess.Move(selected_square, target_square, promotion=chess.QUEEN)
                        
                        if move in board.legal_moves:
                            board.push(move)
                            selected_square = None

                            if not board.is_game_over():
                                # Stockfish (black) replies
                                result = engine.play(board, chess.engine.Limit(time=0.5))
                                board.push(result.move)
                        else:
                            selected_square = None

        # Draw everything
        draw_board(screen)
        draw_selected_square(screen, selected_square)
        draw_legal_moves(screen, board, selected_square)
        draw_pieces(screen, board, images)
        
        # Draw menu panel
        draw_menu_panel(screen, font, selected_elo, game_over, game_result)
        
        pygame.display.flip()

    engine.quit()
    pygame.quit()

if __name__ == "__main__":
    main()

#### ==== FEATURES ADDED ====
# 1. Visual legal move indicators (green circles for moves, red circles for captures)
# 2. ELO rating selector with 6 difficulty levels (800-2800)
# 3. New Game button to restart anytime
# 4. Game over analysis and result display
# 5. Enhanced UI with side panel for controls