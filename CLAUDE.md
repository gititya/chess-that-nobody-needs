# Chess Web App - Architecture & Development Guide

This file provides guidance to Claude Code when working with this chess application repository.

---

## Project Vision

A personality-driven chess web application where users:
1. Customize game settings (pieces, board, sounds, difficulty) **before** the board appears
2. Play against an AI engine trained on specific player datasets (e.g., Bobby Fischer)
3. Receive real-time commentary in the personality's voice during gameplay
4. Experience an immersive, conversational chess opponent

---

## Current State

### **Existing Implementation (Pygame Desktop App)**
- File: `chess_game.py` (main active implementation)
- Technology: Python + Pygame + python-chess + Stockfish
- Features:
  - Human vs Stockfish gameplay
  - Visual move indicators (green circles for moves, red for captures)
  - Captured pieces tracking
  - Dynamic ELO selection (800-2800)
  - Multiple piece sets (Classic/Modern/Elegant)
  - Board flipping capability
  - Sound effects support
  - Resizable window

### **Migration Goal**
Convert to browser-based web application with personality-driven AI commentary.

---

## Technology Stack (Web App)

### **Backend: FastAPI** ✅
**Decision Rationale:**
- Native async support for non-blocking AI moves and LLM commentary
- Built-in WebSocket support (no additional libraries needed)
- 5-10x better performance than Flask for I/O operations
- Handles 3,200+ concurrent WebSocket connections vs Flask's 2,100
- Future-proof for LLM API integration (async calls to OpenAI/Claude)

### **Communication: WebSockets** ✅
**Decision Rationale:**
- Real-time bidirectional communication (move → validation → AI response → commentary)
- Single persistent connection maintains game context for personality
- No polling overhead, instant updates
- Perfect for turn-based games with AI commentary
- Flow: User move → WebSocket → Server validates → Stockfish move → LLM commentary → all pushed back instantly

### **Frontend: HTML5 + CSS3 + Vanilla JavaScript**
- Responsive design for browser-based play
- HTML5 Canvas or CSS Grid for board rendering
- Web Audio API for sound effects
- WebSocket client for real-time communication

### **Game Logic: Python (Keep Existing)**
- Preserve `python-chess` library (excellent, proven)
- Keep Stockfish binary integration (no need for stockfish.js)
- Minimal changes to existing chess_game.py logic
- **80% of current code can be reused**

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     BROWSER (Frontend)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Phase 1: Customization Menu (Static HTML)          │  │
│  │  - Piece style, board theme, sounds, player color   │  │
│  │  - Engine difficulty (ELO)                          │  │
│  │  - **Personality selection** (Bobby Fischer, etc.)  │  │
│  │  - "Start Game" button                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓ (Start Game)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Phase 2: Game Interface (WebSocket connection)     │  │
│  │  - Chess board (HTML/CSS/Canvas)                    │  │
│  │  - Move validation UI                               │  │
│  │  - Captured pieces display                          │  │
│  │  - **Commentary box** (personality chat)            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ WebSocket
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  WebSocket Handler (/ws)                            │  │
│  │  - Receive moves, validate, broadcast updates       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Game Engine Layer                                   │  │
│  │  - python-chess (existing logic from chess_game.py) │  │
│  │  - Stockfish binary (move generation)               │  │
│  │  - **Opening book** (personality-specific PGNs)     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  **Personality Layer** (Phase 3 - Future)           │  │
│  │  - LLM API client (Claude/GPT)                      │  │
│  │  - Personality prompts + game context               │  │
│  │  - Commentary generation (async)                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### **Phase 1: Web App Foundation** (Current Priority)

#### 1.1 Customization Menu (HTML/CSS)
- **Board hidden initially** - Only menu visible on page load
- Settings to include:
  - Sound toggle (Enable/Disable)
  - Piece set selector (Classic/Modern/Elegant)
  - Board theme selector (coordinated with piece sets)
  - Player color (White/Black)
  - Engine strength (ELO: 800-2800)
  - AI thinking time (0.1s - 5.0s)
  - **Personality dropdown** (placeholder for Phase 3)
- "Start Game" button triggers:
  - Menu slides away or hides
  - Board appears with selected settings
  - WebSocket connection established

#### 1.2 Backend Migration (FastAPI)
- Extract game logic from `chess_game.py` into modular classes
- Create FastAPI application structure
- Implement WebSocket endpoints:
  - `/ws` - Main game communication
  - `POST /game/new` - Initialize game with settings (optional REST endpoint)
- Preserve existing functions:
  - `configure_engine_elo()`
  - `get_captured_pieces()`
  - `get_game_result_text()`
  - Move validation logic
  - Stockfish integration

#### 1.3 Frontend Board Rendering
- Replace Pygame rendering with browser-based UI
- Options:
  - **HTML5 Canvas** - Pixel-perfect control, smooth animations
  - **CSS Grid** - Simpler DOM-based approach
- JavaScript handles:
  - Mouse clicks → WebSocket messages
  - Board state updates from server
  - Legal move visualization (green/red circles)
  - Piece dragging (optional enhancement)
- Sound effects via Web Audio API

#### 1.4 Board Theme Coordination
Create 3 board color schemes matching piece sets:
- **Classic**: Traditional brown/beige colors (current pygame colors)
  - Light squares: `#F0D9B5`
  - Dark squares: `#B58863`
- **Modern**: Blue/grey tones
  - Light squares: `#E8EDF9`
  - Dark squares: `#7B92C0`
- **Elegant**: Minimal black/white or muted tones
  - Light squares: `#FFFFFF`
  - Dark squares: `#8CA2AD`

---

### **Phase 2: Opening Book Integration** (Future)

#### Data Format: PGN (Portable Game Notation)
Standard chess game format:
```pgn
[Event "Fischer vs Spassky"]
[White "Fischer, Robert J."]
[Black "Spassky, Boris V."]
[Result "1-0"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6...
```

#### Implementation Steps:
1. **Collect PGN files** for target personality (Bobby Fischer, Kasparov, etc.)
2. **Parse PGN** using `python-chess.pgn` library
3. **Build opening book**:
   - Structure: `position (FEN) → {move: frequency}`
   - Example:
     ```json
     {
       "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": {
         "e2e4": 0.45,  // 45% Fischer played e4
         "d2d4": 0.30,  // 30% d4
         "c2c4": 0.25   // 25% c4
       }
     }
     ```
4. **Stockfish integration**: Consult book first, fall back to engine
5. **Storage**: `data/opening_books/bobby_fischer.json`

#### Training Data Sources:
- `/Users/aditya/Documents/programming/chess/training/Bobby Fischer Teaches Chess.pdf`
- `/Users/aditya/Documents/programming/chess/training/My 60 Memorable Games - Bobby Fischer 2008.pdf`
- Public PGN databases (lichess.org, chess.com, pgnmentor.com)

---

### **Phase 3: LLM Personality Commentary** (Future)

#### System Design:
After each move, send context to LLM:
```json
{
  "personality": "bobby_fischer",
  "board_fen": "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
  "last_move": "e7e5",
  "move_number": 2,
  "game_phase": "opening",
  "move_quality": "good",  // Calculated by comparing to Stockfish eval
  "position_eval": "+0.2",  // Stockfish centipawn evaluation
  "player_time_taken": 3.5  // seconds
}
```

#### LLM Response (personality's voice):
- **Good moves**: "Excellent! The King's Pawn opening - chess is simple!" (Fischer style)
- **Mistakes**: "Hmm, dubious. You're giving me too much center control." (Fischer criticism)
- **Tactical moments**: "You see that fork coming? I hope you do!" (playful warning)

#### Training Data Sources:
1. **PGN games** (opening book + move patterns)
2. **Annotated games** (personality's own analysis)
3. **Interviews/articles** (speaking style, vocabulary)
4. **Books** (Fischer's writings, available in `training/` folder)

#### LLM Integration Options:
- **OpenAI GPT-4** with system prompt (easiest, good quality)
- **Claude Sonnet 4** with personality prompt (best conversational, nuanced)
- **Fine-tuned Llama 3.3** (most authentic voice, but complex setup)

#### Implementation:
```python
async def generate_commentary(game_state: dict, personality: str) -> str:
    """Generate personality-driven commentary using LLM"""
    system_prompt = load_personality_prompt(personality)

    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": format_game_context(game_state)
        }]
    )

    return response.content[0].text
```

---

### **Phase 4: Polish & Enhancements** (Future)

Optional UX/UI improvements:
1. **Move animations** - Pieces slide smoothly (CSS transitions or Canvas animation)
2. **Commentary text-to-speech** - Voice synthesis (ElevenLabs API or Web Speech API)
3. **Save/load games** - Export PGN with embedded commentary annotations
4. **Multiple personalities** - Switch commentator mid-game
5. **Game analysis** - Post-game review with personality breakdown
6. **Mobile responsive** - Touch controls for tablets/phones

---

## File Structure

```
chess/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── game.py                  # Chess logic (extracted from chess_game.py)
│   ├── engine.py                # Stockfish wrapper
│   ├── opening_book.py          # PGN parser & book builder (Phase 2)
│   ├── personality.py           # LLM integration (Phase 3)
│   ├── models.py                # Pydantic models for WebSocket messages
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── index.html               # Customization menu (landing page)
│   ├── game.html                # Board interface (appears after "Start")
│   ├── css/
│   │   ├── menu.css             # Customization menu styles
│   │   ├── board.css            # Chess board styles
│   │   ├── themes.css           # Board color themes (Classic/Modern/Elegant)
│   │   └── global.css           # Shared styles
│   └── js/
│       ├── app.js               # Main application logic
│       ├── websocket.js         # WebSocket client
│       ├── board.js             # Board rendering (Canvas or DOM)
│       ├── sounds.js            # Audio management
│       └── config.js            # Settings persistence (localStorage)
│
├── data/
│   ├── opening_books/
│   │   ├── bobby_fischer.pgn    # Source PGN files
│   │   └── bobby_fischer.json   # Processed opening book
│   └── personalities/
│       └── bobby_fischer/
│           ├── prompt.txt       # LLM system prompt
│           ├── examples.json    # Few-shot examples
│           └── training.jsonl   # Fine-tuning data (optional)
│
├── assets-classic/              # Existing piece images
├── assets-modern/               # Existing piece images
├── assets-minimalist/           # Existing piece images
├── sounds/                      # Existing sound files
│   ├── move.wav
│   ├── capture.wav
│   ├── check.wav
│   └── game_end.wav
│
├── stockfish/                   # Existing Stockfish binary
│   └── stockfish-macos-m1-apple-silicon
│
├── training/                    # Training data for personalities
│   ├── Bobby Fischer Teaches Chess.pdf
│   └── My 60 Memorable Games - Bobby Fischer 2008.pdf
│
├── chess_game.py                # Original Pygame version (reference)
├── claude.md                    # This file
└── README.md                    # User-facing documentation
```

---

## Migration Strategy (Codebase Impact)

### **What We Keep (80% of existing code):**
✅ All `python-chess` logic
✅ Stockfish integration (`chess.engine.SimpleEngine`)
✅ Move validation (`move in board.legal_moves`)
✅ ELO configuration (`configure_engine_elo()`)
✅ Game state management (`chess.Board()`)
✅ Captured pieces tracking (`get_captured_pieces()`)
✅ Game result detection (`get_game_result_text()`)
✅ Legal move generation (`board.legal_moves`)

### **What Changes:**
❌ Pygame rendering → Browser rendering (HTML/CSS/Canvas)
❌ Pygame event loop → WebSocket message loop
❌ Pygame sound (`pygame.mixer`) → HTML5 Audio / Web Audio API
❌ Window management → Responsive web design

### **Code Extraction Example:**

**Before (chess_game.py - Pygame):**
```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle move
                move = chess.Move(selected_square, target_square)
                if move in board.legal_moves:
                    board.push(move)

        draw_board(screen)
        draw_pieces(screen, board, images)
        pygame.display.flip()
```

**After (backend/game.py - FastAPI):**
```python
class ChessGame:
    def __init__(self, elo: int, player_color: bool, piece_set: str):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.elo = elo
        self.player_color = player_color
        self.piece_set = piece_set
        configure_engine_elo(self.engine, elo)  # Same function!

    def make_move(self, move_uci: str) -> bool:
        """Validate and execute player move"""
        move = chess.Move.from_uci(move_uci)
        if move in self.board.legal_moves:  # Same validation!
            self.board.push(move)
            return True
        return False

    async def get_ai_move(self) -> str:
        """Get Stockfish move (async wrapper)"""
        result = await asyncio.to_thread(
            self.engine.play,
            self.board,
            chess.engine.Limit(time=self.thinking_time)
        )
        self.board.push(result.move)
        return str(result.move)

    def get_state(self) -> dict:
        """Export board state for browser"""
        return {
            'fen': self.board.fen(),
            'legal_moves': [str(m) for m in self.board.legal_moves],
            'is_game_over': self.board.is_game_over(),
            'turn': 'white' if self.board.turn else 'black',
            'captured': get_captured_pieces(self.board)  # Same function!
        }

# FastAPI WebSocket endpoint
@app.websocket("/ws")
async def chess_websocket(websocket: WebSocket):
    await websocket.accept()
    game = None

    async for message in websocket.iter_json():
        if message['type'] == 'start_game':
            game = ChessGame(
                elo=message['elo'],
                player_color=chess.WHITE if message['color'] == 'white' else chess.BLACK,
                piece_set=message['piece_set']
            )
            await websocket.send_json({'type': 'game_state', 'state': game.get_state()})

        elif message['type'] == 'move':
            if game.make_move(message['move']):
                await websocket.send_json({'type': 'game_state', 'state': game.get_state()})

                # AI response
                ai_move = await game.get_ai_move()
                await websocket.send_json({'type': 'game_state', 'state': game.get_state()})
```

### **Net Result:**
- **Backend**: 80% function reuse + 20% FastAPI wrapper
- **Frontend**: 100% new (but UI only, not game logic)
- **Chess expertise in Python**: Fully preserved

---

## Key Design Decisions

1. **Keep Python backend** - Leverage existing chess_game.py (800+ lines of proven logic)
2. **FastAPI over Flask** - Better async, native WebSocket, 5-10x performance
3. **WebSockets over REST** - Real-time bidirectional, maintains game context
4. **PGN format for training** - Industry standard, easy to collect (lichess, chess.com)
5. **Phased implementation** - Working app at each milestone (Phase 1 = playable web app)
6. **Separation of concerns** - Game logic (Python) vs UI (Browser)
7. **Menu-first UX** - Customization before board appears (key requirement)

---

## Stockfish Integration

### Current Setup:
- **Binary**: `/Users/aditya/Documents/programming/chess/stockfish/stockfish-macos-m1-apple-silicon`
- **Protocol**: UCI (Universal Chess Interface)
- **Configuration**:
  - Skill Level: 0-20 (mapped from ELO)
  - Depth: 1-10 (limited for lower ELOs)
  - Thinking time: 0.1s - 5.0s (user-selectable)

### ELO Mapping:
```python
# From chess_game.py (keep this logic)
def configure_engine_elo(engine, target_elo):
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
```

---

## Asset Management

### Piece Sets:
- **assets-classic/** - Traditional Staunton-style pieces
- **assets-modern/** - Contemporary minimalist design
- **assets-minimalist/** - Elegant simplified pieces

### Naming Convention:
- White pieces: `wK.png`, `wQ.png`, `wR.png`, `wB.png`, `wN.png`, `wP.png`
- Black pieces: `bK.png`, `bQ.png`, `bR.png`, `bB.png`, `bN.png`, `bP.png`

### Sound Files:
- `sounds/move.wav` - Regular move
- `sounds/capture.wav` - Piece captured
- `sounds/check.wav` - King in check
- `sounds/game_end.wav` - Game over

---

## Development Workflow

### Phase 1 Next Steps:
1. ✅ Document architecture decisions (this file)
2. ⏳ Setup FastAPI project structure (`backend/` folder)
3. ⏳ Extract game logic from `chess_game.py` into `backend/game.py`
4. ⏳ Create WebSocket endpoints in `backend/main.py`
5. ⏳ Build customization menu (`frontend/index.html`)
6. ⏳ Implement board renderer (`frontend/js/board.js`)
7. ⏳ Test end-to-end: menu → settings → game start → move → AI response

### Testing Strategy:
- **Backend**: Unit tests for game logic (pytest)
- **WebSocket**: Test with `websocat` or Postman
- **Frontend**: Manual browser testing (Chrome DevTools)
- **Integration**: Full gameplay flow validation

---

## Resources & References

### Training Materials:
- Bobby Fischer Teaches Chess (PDF in `training/`)
- My 60 Memorable Games - Bobby Fischer 2008 (PDF in `training/`)

### External Resources:
- [python-chess documentation](https://python-chess.readthedocs.io/)
- [FastAPI WebSocket guide](https://fastapi.tiangolo.com/advanced/websockets/)
- [Stockfish UCI protocol](https://www.chessprogramming.org/UCI)
- [PGN format specification](https://www.chessclub.com/help/PGN-spec)
- [LLM Chess Commentary research](https://arxiv.org/html/2410.20811v1)

### PGN Databases:
- [lichess.org/games](https://lichess.org/) - Free, downloadable PGN files
- [pgnmentor.com](http://www.pgnmentor.com/) - Historical games database
- [chess.com/games](https://www.chess.com/games) - Modern games collection

---

## Important Notes for Claude Code

1. **Preserve game logic** - The chess rules, move validation, and Stockfish integration in `chess_game.py` are working correctly. Extract and reuse, don't rewrite.

2. **Menu-first design** - User MUST see customization options before the chess board appears. This is a core requirement.

3. **Board themes coordinate with pieces** - When user selects "Modern" pieces, board colors should also switch to modern theme.

4. **Phased development** - Focus on Phase 1 (playable web app) first. Phases 2-3 (opening books, LLM commentary) are future enhancements.

5. **WebSocket message format** - Design clear JSON structure for client-server communication:
   ```json
   // Client → Server
   {"type": "move", "from": "e2", "to": "e4"}

   // Server → Client
   {"type": "game_state", "fen": "...", "legal_moves": [...]}
   ```

6. **Async AI moves** - Stockfish calls should not block WebSocket. Use `asyncio.to_thread()` to run engine calculations.

7. **Session management** - Each WebSocket connection = one game session. Store game instances in memory (or Redis for production).

8. **Error handling** - Gracefully handle invalid moves, disconnections, engine crashes.

---

Last Updated: 2025-10-09
