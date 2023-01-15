import os
import sys
import pygame
import sqlite3
import math

#импортируем все модули

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 50
WIDTH = 800
HEIGHT = 600
STEP = 10

#задаём постоянные

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
wall = pygame.sprite.Group()
spike = pygame.sprite.Group()
stop = pygame.sprite.Group()

#создаем несколько групп спрайтов

lvl = ''

pos_x0 = 0
pos_y0 = 0

t = 1

percentage = 0

#метод вычисления процента побед по данным из БД

def get_procent():
    global attempts, percentage
    #подключаем базу данных
    con = sqlite3.connect('БД.db')
    cur = con.cursor()
    #получаем необходимые значения
    res1 = cur.execute('''SELECT result FROM statistic
                                    WHERE name = 'attemmps' ''').fetchall()
    res2 = cur.execute('''SELECT result FROM statistic
                                    WHERE name = 'wins' ''').fetchall()
    for i in res1:
        att = i[0]

    for i in res2:
        wins = i[0]

    #вычисляем процентное соотношение
    percentage = (wins / att) * 100


#метод загрузки фото
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


#загрузка уровней
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


#генерация уровня
def generate_level(level):
    global pos_x0
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            if level[y][x] == '[':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '*':
                Tile('finish', x, y)
            elif level[y][x] == '^':
                Tile('killwall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


#стартовое окно
def start_screen():
    global lvl
    intro_text = ["GEOMETRY DASH", "",
                  "Доберитесь до финиша, проходя через приграды",
                  "Нажимайте на пробел, чтобы совершить прыжок",
                  "",
                  'Чтобы поставить на паузу, во время игры нажмите на "ESCAPE"',
                  'Для запуска первого уровня нажмите на "1"',
                  'Для запуска второго уровня нажмите на "2"']

    fon = pygame.transform.scale(load_image('fon1.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('violet'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    #запускаем окно
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            key = pygame.key.get_pressed()
            if key[pygame.K_1]:
                lvl = 'level1'
                return
            if key[pygame.K_2]:
                lvl = 'level2'
                return


        pygame.display.flip()
        clock.tick(FPS)


all_p = 0
wins = 0


#окно паузы/окончания игры
def end_screen():
    global lvl, t, attempts, all_p, wins
    intro_text = []
    if t == 1:
        con = sqlite3.connect('БД.db')
        cur = con.cursor()
        res1 = cur.execute('''SELECT result FROM statistic
                                WHERE name = 'attemmps' ''').fetchall()
        for i in res1:
            all_p = i[0]

        cur.execute(f'''UPDATE statistic
                        SET result = {all_p + attempts}
                        WHERE name = 'attemmps' ''').fetchall()

        con.commit()
        con.close()

        intro_text = ["ПАУЗА", "",
                      f"Количество попыток: {attempts}",
                      " ",
                      'Начать сначала на первом уровне "1"',
                      'Начать сначала на втором уровне "2"']

    if t == 2:
        con = sqlite3.connect('БД.db')
        cur = con.cursor()
        res = cur.execute('''SELECT result FROM statistic
                                        WHERE name = 'attemmps' ''').fetchall()
        for i in res:
            all_p = i[0]

        cur.execute(f'''UPDATE statistic
                                SET result = {all_p + attempts}
                                WHERE name = 'attemmps' ''').fetchall()

        res2 = cur.execute('''SELECT result FROM statistic
                                                WHERE name = 'wins' ''').fetchall()
        for i in res2:
            wins = i[0]

        cur.execute(f'''UPDATE statistic
                                        SET result = {wins + 1}
                                        WHERE name = 'wins' ''').fetchall()

        con.commit()
        con.close()

        get_procent()

        intro_text = ["ПОБЕДА!!!", "",
                      f"Количество попыток: {attempts}",
                      f"Процент побед: {round(percentage, 2)}%",
                      " ",
                      'Первый уровень "1"',
                      'Второй уровень "2"']

    fon = pygame.transform.scale(load_image('fon1.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('violet'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 25
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            key = pygame.key.get_pressed()
            if t == 1:
                if key[pygame.K_1]:
                    lvl = 'level1'
                    return
                if key[pygame.K_2]:
                    lvl = 'level2'
                    return
            if t == 2:
                if key[pygame.K_1]:
                    lvl = 'level1'
                    return
                if key[pygame.K_2]:
                    lvl = 'level2'
                    return

        pygame.display.flip()
        clock.tick(FPS)

#список всех картинок
tile_images = {'wall': load_image('wall.png'), 'finish': load_image('finish.png'), 'killwall': load_image('killwall.png', (132, 128, 130)),
               'empty': load_image('empty.png')}
player_image = load_image('mario.png')

tile_width = tile_height = 30


#отображение элементов карты

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        global pos_x0, t
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if tile_type == 'wall':
            self.mask = pygame.mask.from_surface(self.image)
            wall.add(self)
        if tile_type == 'killwall':
            self.mask = pygame.mask.from_surface(self.image)
            spike.add(self)
        if tile_type == 'finish':
            self.mask = pygame.mask.from_surface(self.image)
            stop.add(self)


#класс игрока

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)

#класс камеры

class Camera:
    # зададим начальный сдвиг камеры и размер поля для возможности реализации циклического сдвига
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        # вычислим координату клитки, если она уехала влево за границу экрана
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (self.field_size[0] + 1) * obj.rect.width
        # вычислим координату клитки, если она уехала вправо за границу экрана
        if obj.rect.x >= (self.field_size[0]) * obj.rect.width:
            obj.rect.x += -obj.rect.width * (1 + self.field_size[0])
        obj.rect.y += self.dy
        # вычислим координату клитки, если она уехала вверх за границу экрана
        if obj.rect.y < -obj.rect.height:
            obj.rect.y += (self.field_size[1] + 1) * obj.rect.height
        # вычислим координату клитки, если она уехала вниз за границу экрана
        if obj.rect.y >= (self.field_size[1]) * obj.rect.height:
            obj.rect.y += -obj.rect.height * (1 + self.field_size[1])

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


start_screen()

#создание объектов игрока, камеры и загрузка уровня

player, level_x, level_y = generate_level(load_level((lvl)))
camera = Camera((level_x, level_y))


attempts = 1
JumpCount = 6
isJump = False

running = True

#начало игры
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        keys = pygame.key.get_pressed()

        #пауза

        if keys[pygame.K_ESCAPE]:
            t = 1
            for i in all_sprites:
                i.kill()
            running = False
            end_screen()
            player, level_x, level_y = generate_level(load_level((lvl)))
            camera = Camera((level_x, level_y))
            running = True
            attempts = 1
        if keys[pygame.K_SPACE]:
            isJump = True

    #движение игрока

    player.rect.x += 550 / FPS
    clock.tick(FPS)

    #проверка условия: совершается ли прыжок?

    if isJump:
        if JumpCount >= -6:
            JumpCount -= 1
            if JumpCount >= 0:
                player.rect.y -= JumpCount ** 2
                print(JumpCount)
                if pygame.sprite.spritecollideany(player, wall):
                    isJump = False
                    JumpCount = 6
            if JumpCount < 0:
                if not pygame.sprite.spritecollideany(player, wall) and JumpCount > -6:
                    player.rect.y += JumpCount ** 2
                    print(JumpCount)
                else:
                    isJump = False
                    JumpCount = 6
        else:
            JumpCount = 6
            isJump = False
    if not pygame.sprite.spritecollideany(player, wall) and not isJump:
        player.rect.y += (JumpCount ** 2) - 5

    #обработка столкновения игрока с шипами

    if pygame.sprite.spritecollideany(player, spike):
        attempts += 1
        for i in all_sprites:
            i.kill()
        player, level_x, level_y = generate_level(load_level((lvl)))
        camera = Camera((level_x, level_y))
        running = True

    #победа, загрузка окна окончания

    if pygame.sprite.spritecollideany(player, stop):
        t = 2
        for i in all_sprites:
            i.kill()
        running = False
        end_screen()
        player, level_x, level_y = generate_level(load_level((lvl)))
        camera = Camera((level_x, level_y))
        running = True


    #обновление камеры

    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)
    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    wall.draw(screen)
    spike.draw(screen)
    stop.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

terminate()