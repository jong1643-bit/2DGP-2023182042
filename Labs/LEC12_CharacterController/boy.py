import time
from pico2d import load_image, SDL_KEYDOWN, SDLK_SPACE
from transitions import Machine


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.idle_time = 0.0
        self.last_time = time.time()
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP'],
            initial='IDLE',
            auto_transitions=False,
            transitions=[
                dict(trigger='tick', source='IDLE', dest=None,
                     after='animate_idle'),
                dict(trigger='sleep', source='IDLE', dest='SLEEP',
                     after='enter_sleep'),
                dict(trigger='wake_up', source='SLEEP', dest='IDLE',
                     after='enter_idle'),
            ],
        )

    def update(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if self.state != 'IDLE':
            return
        self.idle_time += dt
        if self.idle_time >= 5.0:
            self.sleep()
        else:
            self.tick()

    def animate_idle(self):
        # Advance the idle animation without leaving the IDLE state.
        self.frame = (self.frame + 1) % 8

    def enter_sleep(self):
        self.idle_time = 0.0
        self.frame = 0

    def enter_idle(self):
        self.idle_time = 0.0
        self.last_time = time.time()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            if self.state == 'SLEEP':
                self.wake_up()

    def draw(self):
        if self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
