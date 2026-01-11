# Active Context

## Current Focus
Testing and bug fixes before competition (January 16-17, 2026)

## Recent Changes (January 10, 2026)
1. Fixed AI paddle movement in Pong - now updates every frame instead of timed intervals
2. Removed distracting flashing border indicators from menu (replaced with subtle corners, then removed entirely)
3. Replaced Space Invaders with full Basketball 2v2 game
4. Improved paddle movement - smoother continuous motion for both players and AI
5. Added Miami Heat-inspired logo for Basketball game
6. Fixed class definition order bug in placeholder games module (since removed)

## Active Issues
- None currently identified

## Next Steps
1. Test all features thoroughly:
   - Boot screen animation
   - Menu carousel (both smooth and instant transitions)
   - Pong (1P and 2P modes)
   - Basketball (2v2 with AI)
   - LED style toggles and adjustments
2. Practice competition demo flow
3. Prepare talking points about technical implementation

## Key Decisions
- **No distracting UI elements**: Removed flashing indicators to keep focus on games
- **Smooth AI movement**: AI updates every frame for responsive gameplay
- **Basketball over Space Invaders**: More impressive to show 2v2 AI coordination
- **Both game modes supported**: 1P vs AI and 2P for maximum demonstration flexibility

## Important Patterns
- All games inherit from `Game` base class
- Grid manipulation through `LEDGrid` class methods
- State management via `GameManager`
- Sound generation using pygame.mixer with procedural beeps
- AI decision-making based on game state (has ball, teammate has ball, opponent has ball, loose ball)

## Learnings
- Flashing/animated UI elements can be distracting on LED grids
- AI responsiveness is crucial - update every frame, not on timers
- Smooth movement (0.8 pixels/frame) feels better than integer jumps
- Pixel art logos work well on 19×19 grid despite size constraints