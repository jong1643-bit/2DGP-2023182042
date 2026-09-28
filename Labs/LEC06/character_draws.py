# 실습 과제 진행
from pico2d import*
import math

open_canvas(800,600)

character = load_image('character.png')



def move_circle():
  for degree in range(360):
   theta=math.radians(degree)
   x=400+200*math.cos(theta)
   y=300+200*math.sin(theta)

   clear_canvas()
   character.draw(x,y)
   update_canvas()
   delay(0.001)

def draw_rectangle(x,y):
   clear_canvas()
   character.draw(x,y)
   update_canvas()
   delay(0.001)

def move_top():
   for x in range(200,601,4):
      y=450
      draw_rectangle(x,y)

def move_right():
   for y in range(450,149,-3):
      x=600
      draw_rectangle(x,y)

def move_bottom():
    for x in range(600,199,-4):
        y=150
        draw_rectangle(x,y)

def move_left():
    for y in range(150,451,3):
        x=200
        draw_rectangle(x,y)



def move_rectangle():
    move_top()
    move_right()
    move_bottom()
    move_left()
    pass

def draw_triangle(x,y):
    clear_canvas()
    character.draw(x,y)
    update_canvas()
    delay(0.001)




def move_triangle():
    move_triangle_bottom()
    move_triangle_right()
    move_triangle_left()
    pass

while True:
    move_circle()
    move_rectangle()
    move_triangle()
    pass


close_canvas()