"""Classic Sonic sprite animation viewer (pico2d)."""

from pathlib import Path
import sys
from dataclasses import dataclass

import pico2d as p2d

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
IMAGE_PATH = Path(__file__).resolve().with_name('sonic-sprite.png')
DEFAULT_FPS = 10


@dataclass(frozen=True)
class Frame:
    """Source rectangle and anchor, both using top-left coordinates."""
    x: int
    y: int
    width: int
    height: int
    anchor_x: float
    anchor_y: float


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    fps: float = DEFAULT_FPS


# Visual groups in reading order. Names describe poses, not game mechanics.
# Footer credit mascots and title lettering are not animation frames.
ANIMATION_NAMES = (
    'idle_blink', 'waiting', 'look_up', 'crouch', 'curl',
    'walk', 'run', 'fast_run', 'dash', 'roll', 'ball', 'spin_ball',
    'running_turn', 'spin_dash', 'turn_around', 'hurt', 'balance',
    'surprised', 'victory',
)


def load_sprite(path=IMAGE_PATH):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'Sprite image not found: {path}')
    try:
        return p2d.load_image(str(path))
    except (OSError, RuntimeError) as error:
        raise OSError(f'Cannot load sprite image: {path} ({error})') from error


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
        sprite = load_sprite()
        while handle_events():
            p2d.clear_canvas()
            p2d.update_canvas()
            p2d.delay(0.01)
    except (OSError, ValueError) as error:
        print(f'Animation viewer: {error}', file=sys.stderr)
        return 1
    finally:
        p2d.close_canvas()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
