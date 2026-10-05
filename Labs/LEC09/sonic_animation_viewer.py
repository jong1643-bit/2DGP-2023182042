"""Classic Sonic sprite animation viewer (pico2d)."""

import pico2d as p2d

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


def handle_events():
    """Keep processing events during both playback and waiting."""
    for event in p2d.get_events():
        if event.type == p2d.SDL_QUIT:
            return False
        if event.type == p2d.SDL_KEYDOWN and event.key == p2d.SDLK_ESCAPE:
            return False
    return True


def main():
    """Application entry point."""
    p2d.open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)
    try:
        while handle_events():
            p2d.clear_canvas()
            p2d.update_canvas()
            p2d.delay(0.01)
    finally:
        p2d.close_canvas()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
