import game_module as gm
import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode(gm.SIZESCREEN)
# ładowanie listy odzwierciedlającej mape

# rozmiar bloku. ekran na 20 blokow
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 4
score = 0


def reset_lvl(level):
    player.reset(100, screen.get_height() - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()

    game_map = gm.load_map(f'lvl{level}')
    # tworzenie mapy
    world = World(game_map)
    return world


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # pozycja kursora
        poz = pygame.mouse.get_pos()
        # najechanie na przycisk
        if self.rect.collidepoint(poz):
            # indeks 0 = lewy przycisk myszy
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # rysowanie przyciskow
        screen.blit(self.image, self.rect)

        return action


class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        movement_x = 0
        movement_y = 0
        walk_timer = 7
        col_hit = 20
        if game_over == 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                movement_x -= 5
                self.counter += 1
                self.course = -1
            if keys[pygame.K_RIGHT]:
                movement_x += 5
                self.counter += 1
                self.course = 1
            if keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False:
                self.counter = 0  # wyswietlanie pierwszego zdjęcia podczas stania
                self.index = 0
                self.image = self.images_right[self.index]
            if self.course == 1:
                self.image = self.images_right[self.index]
            if self.course == -1:
                self.image = self.images_left[self.index]
            if self.jump_count <= 2:
                if keys[pygame.K_SPACE] and self.jump == False and self.in_air == False:
                    gm.jump_sound.play()
                    self.air_speed = -15
                    self.jump = True
                    self.jump_count += 1
                if self.jump_count == 2 and self.in_air == False:
                    self.jump_count = 0
                    self.in_air = True
            if not keys[pygame.K_SPACE]:
                self.jump = False
            if self.air_speed < -1 and self.course == 1:
                self.image = gm.player_jump
            elif self.air_speed < -1 and self.course == -1:
                self.image = gm.player_jump_L
            if self.air_speed > 1 and self.course == 1:
                self.image = gm.player_fall
            elif self.air_speed > 1 and self.course == -1:
                self.image = gm.player_fall_L

                # zmiana kiernuku, obrazkow
            if self.counter > walk_timer:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.course == 1:
                    self.image = self.images_right[self.index]
                if self.course == -1:
                    self.image = self.images_left[self.index]

            # grawitacja
            self.air_speed += 1
            if self.air_speed > 10:
                self.air_speed = 10
            movement_y += self.air_speed

            # sprawdzanie czy gracz wyszedl poza ekran
            if self.rect.right > screen.get_width():
                self.rect.right = screen.get_width()
            if self.rect.left < 0:
                self.rect.left = 0

            # sprawdzanie kolizji przed updatem ramki postaci
            for tile in world.tile_list:
                # kolizja z osia x
                if tile[1].colliderect(self.rect.x + movement_x, self.rect.y, self.width, self.height):
                    movement_x = 0
                # kolizje z osia y
                if tile[1].colliderect(self.rect.x, self.rect.y + movement_y, self.width, self.height):
                    # kolizja z gorna, dolna krawędzią
                    if self.air_speed < 0:
                        movement_y = tile[1].bottom - self.rect.top  # redukcja odleglosci miedzy glowa a przeszkodą
                        self.air_speed = 0
                    elif self.air_speed >= 0:
                        movement_y = tile[1].top - self.rect.bottom  # redukcja odleglosci miedzy nogami a ziemią
                        self.air_speed = 0
                        self.in_air = False

            # kolizje z wrogami
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                gm.lost_sound.play()
            # kolizje z lawa
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                gm.lost_sound.play()
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
                gm.lvl_complete.play()

            for platform in platform_group:
                # kolizja w kieunku x
                if platform.rect.colliderect(self.rect.x + movement_x, self.rect.y, self.width, self.height):
                    movement_x = 0
                # kolizja w kieunku y
                if platform.rect.colliderect(self.rect.x, self.rect.y + movement_y, self.width, self.height):
                    # sprawdzenie czy pod platformą
                    if abs((self.rect.top + movement_y) - platform.rect.bottom) < col_hit:
                        self.air_speed = 0
                        movement_y = platform.rect.bottom - self.rect.top
                    # sprawdzenie czy na platformie
                    elif abs((self.rect.bottom + movement_y) - platform.rect.top) < col_hit:
                        self.rect.bottom = platform.rect.top
                        self.in_air = False
                        self.air_speed = 0
                        movement_y = 0
                    # poruszanie się na boki z platformą
                    if platform.move_x != 0:
                        self.rect.x += platform.move_dir
                    if platform.move_y != 0:
                        self.rect.y += platform.move_dir
                        self.in_air = False

            # wspolrzedne gracza
            self.rect.x += movement_x
            self.rect.y += movement_y

        elif game_over == -1:
            self.image = self.dead
            if self.rect.y > 200:
                self.rect.y -= 5
        # rysowanie gracza na ekranie
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.jump_count = 0
        # predkosc animacji
        self.counter = 0
        # animacja
        for number in range(1, 10):
            player_img_right = pygame.image.load(f'img/WR{number}.png')

            player_img_right = pygame.transform.scale(player_img_right, (50, 100))
            player_img_left = pygame.transform.flip(player_img_right, True, False)  # odbicie lustrzane skoku po X

            self.images_right.append(player_img_right)
            self.images_left.append(player_img_left)
        self.dead = gm.dead_img
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.air_speed = 0
        self.jump = False
        self.course = 1  # kierunek zwrotu
        self.in_air = True


class World:
    def __init__(self, data):
        self.tile_list = []
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == '1':
                    img = pygame.transform.scale(gm.dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == '2':
                    img = pygame.transform.scale(gm.grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == '3':
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == '4':  # ruch po x move_y=0 przez co self.rect.y sie nie zmienia
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == '5':  # ruch po y move_x=0 przez co self.rect.x sie nie zmienia
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == '6':
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == '7':
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == '8':
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


# wbudowana metoda draw
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = gm.blob_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_dir = 1
        self.counter = 0

    def update(self):
        self.rect.x += self.move_dir
        self.counter += 1
        if self.counter > 50 or self.counter < -50:
            self.move_dir *= -1  # odwrocenie kierunku po osiągnieciu wymiarów bloku
            self.counter *= -1


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        gm.platform_img = pygame.transform.scale(gm.platform_img, (tile_size, tile_size // 2))
        self.image = gm.platform_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_dir = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_dir * self.move_x
        self.rect.y += self.move_dir * self.move_y
        self.move_counter += 1
        if self.move_counter > 50 or self.move_counter < -50:
            self.move_dir *= -1  # odwrocenie kierunku po osiągnieciu wymiarów bloku
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        gm.lava_img = pygame.transform.scale(gm.lava_img, (tile_size, tile_size // 2))
        self.image = gm.lava_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        gm.coin_img = pygame.transform.scale(gm.coin_img, (tile_size // 2, tile_size // 2))
        self.image = gm.coin_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        gm.exit = pygame.transform.scale(gm.exit, (tile_size, int(tile_size * 1.5)))
        self.image = gm.exit
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# tworzenie gracza
player = Player(50, screen.get_height() - 125)

# grupa blobow
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

coin_pic = Coin(tile_size // 2, tile_size // 2)
coin_group.add(coin_pic)
if level <= max_levels:
    game_map = gm.load_map(f'lvl{level}')
    world = World(game_map)
else:
    gm.draw_text('YOU WIN!', gm.game_font, gm.red, (screen.get_width() // 2) - 140,
                 screen.get_height() // 2)
# inicializacja przyciskow
restart_b = Button(screen.get_width() // 2 - 50, screen.get_height() // 2 + 100, gm.restart_img)
start_b = Button(screen.get_width() // 2 - 350, screen.get_height() // 2, gm.start_img)
exit_b = Button(screen.get_width() // 2 + 150, screen.get_height() // 2, gm.exit_img)
run = True
while run:
    gm.clock.tick(gm.fps)
    if level == 1:
        screen.blit(gm.bg, (0, 0))
        screen.blit(gm.sun_img, (100, 100))
    elif level == 2:
        screen.blit(gm.bg2, (0, 0))
    elif level == 3:
        screen.blit(gm.bg3, (0, 0))
    elif level == 4:
        screen.blit(gm.bg4, (0, 0))
    if main_menu:

        if exit_b.draw():
            run = False
        if start_b.draw():
            main_menu = False
    else:
        world.draw()
        if game_over == 0:
            blob_group.update()
            platform_group.update()
            # score
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                gm.coin_sound.play()
            gm.draw_text('X ' + str(score), gm.font_score, gm.white, tile_size - 10, 10)
            gm.draw_text("Level " + str(level), gm.font_score, gm.white, 900, 10)

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)
        # wyswietlanie przycisku, tekstu jesli gracz umiera
        if game_over == -1:
            gm.draw_text('YOU LOST!', gm.game_font, gm.red, (screen.get_width() // 2) - 140,
                         screen.get_height() // 2)
            if restart_b.draw():
                player.reset(100, screen.get_height() - 125)
                reset_lvl(level)
                game_over = 0
                score = 0

        # przejscie poziomu
        if game_over == 1:
            level += 1
            if level <= max_levels:
                game_map = []
                world = reset_lvl(level)
                game_over = 0
            else:
                gm.draw_text('YOU WIN!', gm.game_font, gm.red, (screen.get_width() // 2) - 140,
                             screen.get_height() // 2)

                if restart_b.draw():
                    level = 1
                    game_map = []
                    world = reset_lvl(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

    pygame.display.update()
pygame.quit()
