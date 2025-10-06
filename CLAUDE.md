# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a chess game implementation using Python, Pygame, and Stockfish integration. The project consists of two main Python files:

- `bob_chess.py` - **Main active file** with full chess game implementation
- `enhanced_chess_game.py` - Reference file (not to be used, as noted in comments)

## Running the Application

```bash
python bob_chess.py
```

## Dependencies

The project requires these Python packages:
- `pygame` - For GUI and graphics
- `python-chess` - For chess logic and board representation
- `chess.engine` - For Stockfish integration

## Project Architecture

### Core Components

**Main Game (`bob_chess.py`)**:
- Game loop with Pygame event handling
- Chess board rendering with coordinate labels (a-h, 1-8)
- Piece movement with legal move validation
- Stockfish AI integration with adjustable skill levels (800-2800 ELO)
- Side panel menu system for game controls

**Key Architecture Elements**:
- **Board Representation**: Uses `python-chess` library for game state and move validation
- **Graphics Pipeline**: Pygame-based rendering with separate functions for board, pieces, highlights, and UI
- **AI Integration**: Stockfish engine communication via UCI protocol
- **Game State Management**: Tracks selected pieces, game over conditions, captured pieces

### Stockfish Integration

- **Binary Location**: `stockfish/stockfish-macos-m1-apple-silicon` (M1 Mac specific)
- **Engine Configuration**: Dynamic skill level and depth adjustment based on selected ELO
- **Response Time**: Currently set to 0.5 seconds per move

### Asset Management

- **Piece Images**: Located in multiple asset directories (`assetsv1/`, `assetsv2/`, `assetsv3/`)
- **Image Format**: PNG files with naming convention (e.g., `wK.png` for white king, `bP.png` for black pawn)
- **Loading**: Images are scaled to match board square size during initialization
- **Piece Set Selection**: Players can choose from multiple piece styles before starting a game

## Game Features

**Current Implementation**:
- Human vs Stockfish gameplay (player can choose white or black)
- Visual move indicators (green circles for moves, red for captures)
- Captured pieces tracking and display
- Dynamic ELO selection (6 levels from 800-2800)
- Multiple piece set selection (Classic, Modern, Elegant)
- New game functionality
- Game over detection with result analysis
- Board flipping capability
- Sound effects support

**Planned Improvements** (from TODO in code):
1. ~~Play as black option~~ ✅ Completed
2. ~~Better piece graphics (upgrade from assetsv1)~~ ✅ Piece selection system implemented
3. Game save/load functionality
4. ~~Sound effects~~ ✅ Implemented
5. Improved Stockfish binary (brew version vs M1 binary)
6. Game analysis features
7. UI/UX enhancements

**Recent Updates**:
- **Piece Set Selection**: Added support for multiple piece sets with dynamic loading
- **Player Color Choice**: Can now play as white or black
- **Enhanced Menu System**: Organized menu with sections for game settings

## Code Structure

**Rendering Functions**:
- `draw_board()` - Chess board squares
- `draw_pieces()` - Piece sprites
- `draw_legal_moves()` - Move indicators
- `draw_menu_panel()` - Side panel UI
- `draw_captured_pieces()` - Fallen pieces display

**Game Logic**:
- `get_square_from_pos()` - Mouse click to board coordinate conversion
- `configure_engine_elo()` - Stockfish difficulty adjustment
- `get_game_result_text()` - End game analysis

**Key Constants**:
- `BOARD_WIDTH = 512` - Main board size
- `SQUARE_SIZE = 64` - Individual square size
- `MENU_WIDTH = 200` - Side panel width
- `STOCKFISH_PATH` - Engine binary location
- `PIECE_SETS` - Dictionary mapping piece set names to asset directories

## Development Notes

- The project uses a coordinate system where (0,0) is top-left, with chess coordinates mapped accordingly
- Move validation is handled by the `python-chess` library
- Engine strength is controlled via Stockfish's "Skill Level" (0-20) and "Depth" parameters
- Pawn promotion is automatically set to Queen
- Piece set loading includes fallback mechanism - if pieces aren't found in selected set, falls back to assetsv1
- Piece set selection is only available before starting a game to prevent mid-game changes

## File Structure
```
chess/
├── bob_chess.py          # Main game implementation
├── enhanced_chess_game.py # Reference file (deprecated)
├── CLAUDE.md            # This documentation file
├── stockfish/           # Stockfish engine binary
├── sounds/              # Sound effect files
├── assetsv1/            # Classic piece set (default)
├── assetsv2/            # Modern piece set
├── assetsv3/            # Elegant piece set
└── README.md            # Project readme
```