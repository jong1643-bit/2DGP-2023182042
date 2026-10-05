"""Classic Sonic sprite animation viewer (pico2d)."""

from pathlib import Path
import sys
from dataclasses import dataclass
from math import isfinite
from time import perf_counter

import pico2d as p2d

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
IMAGE_PATH = Path(__file__).resolve().with_name('sonic-sprite.png')
DEFAULT_FPS = 10
DISPLAY_SCALE = 8
REPEAT_COUNT = 5
WAIT_SECONDS = 1.0
# Feet at y=240 place a typical 40-pixel-tall pose around screen center.
ANCHOR_X = WINDOW_WIDTH / 2
ANCHOR_Y = WINDOW_HEIGHT / 2 - 20 * DISPLAY_SCALE


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


def frames_from_boxes(boxes):
    return tuple(Frame(x, y, w, h, w / 2, h) for x, y, w, h in boxes)


# Measured from the 399x525 RGBA source. No uniform grid assumption.
FRAME_ROWS = (
    ((1,39,29,39), (31,40,26,38), (58,39,29,39), (87,40,29,38),
     (118,40,30,38), (150,40,30,38), (182,40,32,38), (214,39,28,38),
     (242,39,27,38), (270,45,24,32), (302,51,29,26)),
    ((8,80,26,37), (37,80,27,37), (65,80,31,38), (97,80,37,37),
     (135,80,32,35), (170,79,32,38), (206,79,26,38), (238,80,24,37),
     (263,80,30,37), (295,80,36,37), (334,80,32,36), (370,79,29,38)),
    ((1,124,33,40), (39,124,35,39), (89,125,35,38), (130,121,34,42),
     (181,122,34,41), (228,122,33,40)),
    ((1,169,29,30), (35,167,29,31), (67,169,30,29), (98,169,31,29),
     (131,168,29,30), (162,168,29,31), (193,170,30,29), (230,170,31,29),
     (268,170,30,30)),
    ((1,206,30,27), (36,206,29,27), (70,206,29,27), (105,206,29,27),
     (139,206,29,27), (174,206,29,27)),
    ((1,239,29,35), (36,239,30,35), (74,239,31,35), (111,238,31,36),
     (149,239,30,35), (186,238,31,36)),
    ((1,283,29,35), (36,283,30,35), (72,286,39,31), (123,285,39,32),
     (172,286,39,31), (218,285,38,32)),
    ((1,326,24,45), (31,327,29,44), (65,327,20,44), (90,327,25,43),
     (119,327,25,43), (149,327,20,44), (184,341,40,28), (232,341,39,27)),
    ((1,379,27,38), (31,379,31,36), (64,379,31,36), (99,377,33,38),
     (136,379,32,36), (176,379,33,36), (217,379,33,36), (254,378,33,36)),
    ((6,429,34,40), (49,426,34,43), (96,427,23,39), (125,427,23,39)),
)
GROUP_BOXES = (
    FRAME_ROWS[0][:3], FRAME_ROWS[0][3:7], FRAME_ROWS[0][7:9],
    FRAME_ROWS[0][9:10], FRAME_ROWS[0][10:], FRAME_ROWS[1],
    FRAME_ROWS[2][:2], FRAME_ROWS[2][2:4], FRAME_ROWS[2][4:],
    FRAME_ROWS[3][:8], FRAME_ROWS[3][8:], FRAME_ROWS[4], FRAME_ROWS[5],
    FRAME_ROWS[6], FRAME_ROWS[7][:6], FRAME_ROWS[7][6:], FRAME_ROWS[8],
    FRAME_ROWS[9][:2], FRAME_ROWS[9][2:],
)
ANIMATIONS = tuple(Animation(name, frames_from_boxes(boxes))
                   for name, boxes in zip(ANIMATION_NAMES, GROUP_BOXES))


class Playback:
    def __init__(self, animations):
        self.animations = animations
        self.animation_index = 0
        self.frame_index = 0
        self.frame_elapsed = 0.0
        self.completed_repeats = 0
        self.state = 'PLAYING'
        self.wait_elapsed = 0.0

    @property
    def wait_finished(self):
        return self.state == 'WAITING' and self.wait_elapsed >= WAIT_SECONDS

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def next_animation(self):
        if self.animation_index + 1 >= len(self.animations):
            return
        self.animation_index += 1
        self.frame_index = 0
        self.completed_repeats = 0
        self.frame_elapsed = 0.0
        self.wait_elapsed = 0.0
        self.state = 'PLAYING'

    def update(self, elapsed):
        if not isfinite(elapsed) or elapsed < 0:
            raise ValueError('Elapsed time must be finite and nonnegative')
        if self.state == 'WAITING':
            self.wait_elapsed += elapsed
            if self.wait_finished:
                self.next_animation()
            return
        self.frame_elapsed += elapsed
        duration = 1.0 / self.animation.fps
        while self.frame_elapsed + 1e-12 >= duration:
            self.frame_elapsed = max(0.0, self.frame_elapsed - duration)
            self.frame_index = (self.frame_index + 1) % len(self.animation.frames)
            if self.frame_index == 0:
                self.completed_repeats += 1
                if self.completed_repeats == REPEAT_COUNT:
                    self.frame_index = len(self.animation.frames) - 1
                    self.frame_elapsed = 0.0
                    self.state = 'WAITING'
                    self.wait_elapsed = 0.0
                    break


def validate_animations(animations, image_width, image_height):
    if not animations:
        raise ValueError('Animation list is empty')
    names = set()
    for animation in animations:
        if not animation.name or animation.name in names:
            raise ValueError(f'Invalid or duplicate animation name: {animation.name}')
        names.add(animation.name)
        if not isfinite(animation.fps) or animation.fps <= 0:
            raise ValueError(f'{animation.name}: fps must be positive and finite')
        if not animation.frames:
            raise ValueError(f'{animation.name}: frame list is empty')
        for index, frame in enumerate(animation.frames):
            label = f'{animation.name}, frame {index + 1}'
            values = (frame.x, frame.y, frame.width, frame.height)
            if any(not isinstance(value, int) for value in values):
                raise ValueError(f'{label}: rectangle must use integer pixels')
            if (frame.width <= 0 or frame.height <= 0 or frame.x < 0 or frame.y < 0
                    or frame.x + frame.width > image_width
                    or frame.y + frame.height > image_height):
                raise ValueError(f'{label}: rectangle outside sprite image')
            if not all(isfinite(value) for value in (frame.anchor_x, frame.anchor_y)):
                raise ValueError(f'{label}: anchor must be finite')


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


def clip_rectangle(frame, image_height):
    """Convert measured top-left coordinates to pico2d bottom-left coordinates."""
    return frame.x, image_height - frame.y - frame.height, frame.width, frame.height


def destination(frame):
    width, height = frame.width * DISPLAY_SCALE, frame.height * DISPLAY_SCALE
    x = ANCHOR_X + (frame.width / 2 - frame.anchor_x) * DISPLAY_SCALE
    y = ANCHOR_Y + (frame.anchor_y - frame.height / 2) * DISPLAY_SCALE
    return x, y, width, height


def draw_frame(sprite, frame):
    p2d.clear_canvas()
    sprite.clip_draw(*clip_rectangle(frame, sprite.h), *destination(frame))
    p2d.update_canvas()


def main():
    """Application entry point."""
    p2d.open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)
    try:
        sprite = load_sprite()
        validate_animations(ANIMATIONS, sprite.w, sprite.h)
        playback = Playback(ANIMATIONS)
        previous_time = perf_counter()
        while handle_events():
            current_time = perf_counter()
            playback.update(current_time - previous_time)
            previous_time = current_time
            draw_frame(sprite, playback.frame)
            p2d.delay(0.01)
    except (OSError, ValueError) as error:
        print(f'Animation viewer: {error}', file=sys.stderr)
        return 1
    finally:
        p2d.close_canvas()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
