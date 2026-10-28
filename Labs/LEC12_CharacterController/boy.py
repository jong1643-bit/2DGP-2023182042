import time
from pico2d import (
    load_image, get_canvas_width,
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE,
)
from transitions import Machine, State


class AutoRun(State):
    def __init__(self, boy):
        self.boy = boy
        self.elapsed = 0.0
        self.direction = 1
        self.speed = 250.0
        self.scale = 1.0
        super().__init__(
            name='AUTO_RUN',
            on_enter=self.enter_state,
            on_exit=self.exit_state,
        )

    def enter_state(self):
        self.elapsed = 0.0
        self.direction = self.boy.face_dir
        self.boy.face_dir = self.direction

    def exit_state(self):
        pass

    def update(self, dt):
        return False


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.scale = 1.0
        self.image = load_image('animation_sheet.png')
        self.screen_width = get_canvas_width()
        self.idle_time = 0.0
        self.last_time = time.time()
        self.run_speed = 250.0
        self.run_dir = 0
        self.left_pressed = False
        self.right_pressed = False
        self.auto_run = AutoRun(self)
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN', self.auto_run],
            initial='IDLE',
            auto_transitions=False,
            transitions=[
                dict(trigger='tick', source='IDLE', dest=None,
                     after='animate_idle'),
                dict(trigger='sleep', source='IDLE', dest='SLEEP',
                     after='enter_sleep'),
                dict(trigger='wake_up', source='SLEEP', dest='IDLE',
                     after='enter_idle'),
                dict(trigger='start_run', source='IDLE', dest='RUN',
                     after='enter_run'),
                dict(trigger='stop_run', source='RUN', dest='IDLE',
                     after='enter_idle'),
            ],
        )

    def update(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if self.state == 'IDLE':
            self.idle_time += dt
            if self.idle_time >= 5.0:
                self.sleep()
            else:
                self.tick()
        elif self.state == 'RUN':
            self.update_run(dt)

    def animate_idle(self):
        # Advance the idle animation without leaving the IDLE state.
        self.frame = (self.frame + 1) % 8

    def enter_sleep(self):
        self.idle_time = 0.0
        self.frame = 0

    def enter_idle(self):
        self.idle_time = 0.0
        self.last_time = time.time()

    def enter_run(self):
        self.face_dir = self.run_dir
        self.frame = 0

    def update_run(self, dt):
        if self.run_dir == 0:
            return
        self.x += self.run_dir * self.run_speed * dt
        half = 50 * self.scale
        self.x = max(half, min(self.screen_width - half, self.x))
        self.face_dir = self.run_dir
        self.frame = (self.frame + 1) % 8

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.left_pressed = True
                self.run_dir = -1
                if self.state == 'IDLE':
                    self.start_run()
            elif event.key == SDLK_RIGHT:
                self.right_pressed = True
                self.run_dir = 1
                if self.state == 'IDLE':
                    self.start_run()
            elif event.key == SDLK_SPACE and self.state == 'SLEEP':
                self.wake_up()
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                self.left_pressed = False
            elif event.key == SDLK_RIGHT:
                self.right_pressed = False
            if self.state == 'RUN' and not (self.left_pressed or self.right_pressed):
                self.stop_run()

    def draw(self):
        if self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
        else:
            row = 300 if self.face_dir == 1 else 200
        self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
