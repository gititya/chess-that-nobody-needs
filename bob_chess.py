import pygame
import chess
import chess.engine
import os

# === Settings ===
BOARD_WIDTH = 512
SQUARE_SIZE = BOARD_WIDTH // 8
FPS = 60

# === Update this with the path to your Stockfish binary ===
STOCKFISH_PATH = "/Users/aditya/Documents/programming/chess/stockfish/stockfish-macos-m1-apple-silicon"

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

# === Main Function ===> PLAYABILITY
def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
    pygame.display.set_caption("Chess vs Stockfish")
    clock = pygame.time.Clock()

    board = chess.Board()
    images = load_images()

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    selected_square = None
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if selected_square is None:
                    # Only select a white piece when it's your turn
                    square = get_square_from_pos(pygame.mouse.get_pos())
                    piece = board.piece_at(square)
                    if piece and piece.color == chess.WHITE and board.turn == chess.WHITE:
                        selected_square = square
                else:
                    target_square = get_square_from_pos(pygame.mouse.get_pos())
                    move = chess.Move(selected_square, target_square)
                    if move in board.legal_moves:
                        board.push(move)
                        selected_square = None

                        if not board.is_game_over():
                            # Stockfish (black) replies
                            result = engine.play(board, chess.engine.Limit(time=0.5))
                            board.push(result.move)
                    else:
                        selected_square = None

        draw_board(screen)
        draw_pieces(screen, board, images)
        pygame.display.flip()

    engine.quit()
    pygame.quit()

if __name__ == "__main__":
    main()

    #### ==== CHANGES NEEDED ==####
# 1. UPDATE THE STOCKFISH BINARY FROM M1 TO THE BREW VERSION - https://stockfishchess.org/download/
# 2. UPDATE CHESS PIECES - MAYBE V2/V3
# 3. ADD A FUNCTION TO CHECK IF THE GAME IS OVER AND DISPLAY THE RESULT. ALSO, REDUCE THE SPEED. 