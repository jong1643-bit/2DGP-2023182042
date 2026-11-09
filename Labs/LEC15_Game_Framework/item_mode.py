from pico2d import *
import game_framework

image = None


def init():
    global image
    image = load_image('item_select.png')


def finish():
    global image
    del image


def update():
    pass


def render():
    clear_canvas()
    image.draw(400, 300)
    update_canvas()


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.pop_mode()
            return
        elif event.type == SDL_KEYDOWN and event.key in (SDLK_0, SDLK_1, SDLK_2):
            import play_mode

            selected_size = event.key - SDLK_0
            play_mode.ball_size = selected_size
            play_mode.boy.ball_size = selected_size
            game_framework.pop_mode()
            return
