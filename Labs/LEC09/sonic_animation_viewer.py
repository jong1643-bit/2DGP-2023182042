"""Classic Sonic sprite animation viewer (pico2d)."""

import pico2d as p2d

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


def main():
    """Application entry point."""
    p2d.open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)
    try:
        p2d.clear_canvas()
        p2d.update_canvas()
    finally:
        p2d.close_canvas()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
