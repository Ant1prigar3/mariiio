import pygame
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map.map")
args = parser.parse_args()
map_file = args.map


def load_image(name, color_key=None):
    fullname = os.path.join('data4', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
size = (600, 600)
display = pygame.display.set_mode(size)
FPS = 50

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

width = height = 50


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def shift(self, vector):
        global lvl_map
        if vector == "up":
            max_lay_y = max(self, key=lambda sprite:
            sprite.abs_pos[1]).abs_pos[1]
            for sprite in self:
                sprite.abs_pos[1] -= (height * max_y
                                      if sprite.abs_pos[1] == max_lay_y else 0)
        elif vector == "down":
            min_lay_y = min(self, key=lambda sprite:
            sprite.abs_pos[1]).abs_pos[1]
            for sprite in self:
                sprite.abs_pos[1] += (height * max_y
                                      if sprite.abs_pos[1] == min_lay_y else 0)
        elif vector == "left":
            max_lay_x = max(self, key=lambda sprite:
            sprite.abs_pos[0]).abs_pos[0]
            for sprite in self:
                if sprite.abs_pos[0] == max_lay_x:
                    sprite.abs_pos[0] -= width * max_x
        elif vector == "right":
            min_lay_x = min(self, key=lambda sprite:
            sprite.abs_pos[0]).abs_pos[0]
            for sprite in self:
                sprite.abs_pos[0] += (height * max_x
                                      if sprite.abs_pos[0] == min_lay_x else 0)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sp_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            width * pos_x, height * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]

    def set_pos(self, x, y):
        self.abs_pos = [x, y]


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(h_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            width * pos_x + 15, height * pos_y + 5)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= width * (x - self.pos[0])
        camera.dy -= height * (y - self.pos[1])
        print(camera.dx, camera.dy)
        self.pos = (x, y)
        for sprite in sp_group:
            camera.apply(sprite)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


player = None
running = True
clock = pygame.time.Clock()
sp_group = SpriteGroup()
h_group = SpriteGroup()


def terminate():
    pygame.quit()
    sys.exit


def start_screen():
    intro_text = ["Перемещение героя", "",
                  "",
                  "На торе"]

    fon = pygame.transform.scale(load_image('fon.jpg'), size)
    display.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        display.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data4/" + filename
    with open(filename, 'r') as mapFile:
        lvl_map = [line.strip() for line in mapFile]
    max_width = max(map(len, lvl_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), lvl_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
    return new_player, x, y


def move(hero, movem):
    x, y = hero.pos
    if movem == "up":
        prev_y = y - 1 if y != 0 else max_y
        if lvl_map[prev_y][x] == ".":
            if prev_y == max_y:
                for i in range(max_y - 1):
                    sp_group.shift("down")
                hero.move(x, prev_y - 1)
            else:
                sp_group.shift("up")
                hero.move(x, prev_y)
    elif movem == "down":
        next_y = y + 1 if y != max_y else 0
        if lvl_map[next_y][x] == ".":
            if next_y == 0:
                for i in range(max_y - 1):
                    sp_group.shift("up")
                hero.move(x, next_y + 1)
            else:
                sp_group.shift("down")
                hero.move(x, next_y)
    elif movem == "left":
        prev_x = x - 1 if x != 0 else max_x
        if lvl_map[y][prev_x] == ".":
            if prev_x == max_x:
                for i in range(max_x - 1):
                    sp_group.shift("right")
                hero.move(prev_x - 1, y)
            else:
                sp_group.shift("left")
                hero.move(prev_x, y)
    elif movem == "right":
        next_x = x + 1 if x != max_x else 0
        if lvl_map[y][next_x] == ".":
            if next_x == 0:
                for i in range(max_x - 1):
                    sp_group.shift("left")
                hero.move(next_x + 1, y)
            else:
                sp_group.shift("right")
                hero.move(next_x, y)


start_screen()
camera = Camera()
lvl_map = load_level(map_file)
hero, max_x, max_y = generate_level(lvl_map)
camera.update(hero)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(hero, "up")
            elif event.key == pygame.K_DOWN:
                move(hero, "down")
            elif event.key == pygame.K_LEFT:
                move(hero, "left")
            elif event.key == pygame.K_RIGHT:
                move(hero, "right")
    display.fill(pygame.Color("black"))
    sp_group.draw(display)
    h_group.draw(display)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
