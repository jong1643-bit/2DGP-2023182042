from pico2d import *
import game_world
import game_framework
import title_mode
from boy import Boy
from grass import Grass

ball_size = 1


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
            return
        else:
            boy.handle_event(event)



def init():
    global boy


    boy = Boy(ball_size)
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)



def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()


