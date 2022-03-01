import pygame
from pygame.locals import *
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
clock = pygame.time.Clock()
fps = 60

font_score = pygame.font.SysFont("arial", 30, bold=True)
game_font = pygame.font.SysFont('arial', 70, bold=True)
white = (255, 255, 255)
red = (255, 0, 0)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


SIZESCREEN = WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode(SIZESCREEN)
pygame.display.set_caption('Gra Platformowa')
# obrazki
sun_img = pygame.image.load('img/sun.png')
bg = pygame.image.load('img/sky.png')
bg2 = pygame.image.load('img/bg2.png')
bg3 = pygame.image.load('img/bg3.png')
bg4 = pygame.image.load('img/bg4.png')
dirt_img = pygame.image.load('img/dirt.png')
grass_img = pygame.image.load('img/grass.png')
blob_img = pygame.image.load('img/blob.png')
lava_img = pygame.image.load('img/lava.png')
dead_img = pygame.image.load('img/ghost.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
exit = pygame.image.load('img/exit.png')
coin_img = pygame.image.load('img/coin.png')
platform_img = pygame.image.load('img/platform.png')
player_jump = pygame.image.load('img/PJ_R.png')
player_jump = pygame.transform.scale(player_jump, (50, 100))
player_fall = pygame.image.load('img/PF_R.png')
player_fall = pygame.transform.scale(player_fall, (50, 100))
player_jump_L = pygame.transform.flip(player_jump, True, False)
player_fall_L = pygame.transform.flip(player_fall, True, False)
# dźwięki
pygame.mixer.music.load('sounds/background.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
pygame.mixer.music.set_volume(0.02)
coin_sound = pygame.mixer.Sound('sounds/coin.wav')
coin_sound.set_volume(0.2)
jump_sound = pygame.mixer.Sound('sounds/jump.wav')
jump_sound.set_volume(0.2)
lost_sound = pygame.mixer.Sound('sounds/lose.wav')
lost_sound.set_volume(0.2)
lvl_complete = pygame.mixer.Sound('sounds/lvl_complete.wav')
lvl_complete.set_volume(0.3)


# funkcja ladowania mapy
def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map
