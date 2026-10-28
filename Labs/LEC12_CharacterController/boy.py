from pico2d import load_image
from transitions import Machine


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['IDLE'],
            initial='IDLE',
            auto_transitions=False,
            transitions=[
                dict(trigger='tick', source='IDLE', dest=None,
                     after='animate_idle'),
            ],
        )

    def update(self):
        self.tick()

    def animate_idle(self):
        # Advance the idle animation without leaving the IDLE state.
        self.frame = (self.frame + 1) % 8

    def draw(self):
        if self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
