import os
import random
import pygame

size = width, height = 1750, 750
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
pygame.init()
levels = ['1.txt', '2.txt', '3.txt', '4.txt', '5.txt', '6.txt', '7,txt']

running = True
all_sprites = pygame.sprite.Group()
ai_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
fire_group = pygame.sprite.Group()
TIME_TURN= 100

def load_image(fullname, color_key=None):
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', fullname)
        raise SystemExit(message)
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    image = image.convert_alpha()
    return image


class Tile(pygame.sprite.Sprite):

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = load_image("Bodies/tile.png")
        self.rect = pygame.Rect(pos_x, pos_y, 250, 100)

    def defence(self,damage):
        pass



class Fire(pygame.sprite.Sprite):

    def __init__(self, start_pos, damage, target, type_fire):
        super().__init__(fire_group, all_sprites)
        self.image = load_image("Fire/"+str(type_fire)+".png")
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos
        self.damage = damage
        if type_fire == 1:
            self.vx = int((target[0]-start_pos[0]) / 10)
            self.vy = int((target[1]-start_pos[1]) / 10)
        else:
            self.vx = -int((start_pos[0]-target[0]) / 10)
            self.vy = -int((start_pos[1]-target[1]) / 10)

    def update(self):
        self.rect.left += self.vx
        self.rect.top += self.vy

        for obj in ai_group:
            if pygame.sprite.collide_rect(self, obj):
                obj.defence(self.damage)
                self.kill()
        for obj in player_group:
            if pygame.sprite.collide_rect(self, obj):
                obj.defence(self.damage)
                self.kill()

    def defence(self,damage):
        pass

class HPBar(pygame.sprite.Sprite):

    def __init__(self, rect, hp):
        super().__init__(all_sprites)
        self.value = hp
        self.image = load_image("Bars/hp"+str(self.value)+".bmp")
        self.ship = rect
        self.rect = self.image.get_rect().move(self.ship.left +30, self.ship.top)
    def defence(self,damage):
        self.value -= damage
    def goto_postition(self,rect):
        self.ship = rect
    def update(self):
        self.rect = self.image.get_rect().move(self.ship.left +30, self.ship.top)

        self.image = load_image("Bars/hp"+str(self.value)+".bmp")
        if self.value <=0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = load_image("Bodies/main.png", -1)
        self.rect = self.image.get_rect().move(pos_x * 250, pos_y * 100 )
        self.pos = pos_x, pos_y
        self.next_pos = pos_x, pos_y
        self.hp = 5
        self.damage = 1
        self.hp_bar = HPBar(self.rect,self.hp)


    def defence(self, damage):
        self.hp -= damage
        self.hp_bar.defence((damage))

    def my_position(self):
        return self.pos

    def goto_cell(self, x_new, y_new):
        if (board.get_cell(x_new,y_new)) != (None,None) and self.pos != (x_new, y_new):

            self.next_pos = min(x_new,self.pos[0]+1), min(y_new,self.pos[1]+1)
            board.level_map[self.pos[0]][self.pos[1]] = '*'

    def my_damage(self):
        return self.damage

    def update(self):
        if self.pos < self.next_pos:
            dx = int((self.next_pos[0]*250-self.pos[0]*250)/50)
            dy = int((self.next_pos[1]*100-self.pos[1]*100)/50)
            self.rect.left += dx
            self.rect.top += dy
            if abs(self.rect.left-self.next_pos[0]*250)<5 and abs(self.rect.top-self.next_pos[1]*100)<5:
                self.pos = self.next_pos
                board.level_map[self.pos[0]][self.pos[1]] = 'P'
        self.hp_bar.goto_postition(self.rect)
        if self.hp <= 0:
            self.kill()
            print("game over")
            running = False


class AI(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, fraction, param):
        super().__init__(ai_group, all_sprites)
        print(param)
        self.name,self.hp, self.weapon1, self.weapon2 = param
        if self.name[0] == "E":
            self.image = load_image("Bodies/" + fraction + ".png", -1)
        elif self.name[0] == "A":
            self.image = load_image("Bodies/abaddon.png", -1)

        self.pos = pos_x, pos_y
        self.next_pos = pos_x, pos_y
        self.rect = self.image.get_rect().move(pos_x * 250, pos_y * 100, )

        self.status_anim = False
        self.hp = 5
        self.damage = 1 #рассчитывать относительно оружия
        self.hp_bar = HPBar(self.rect,self.hp)

    def my_position(self):
        return self.pos

    def defence(self, damage):
        self.hp -= damage
        self.hp_bar.defence((damage))
        board.score += damage

    def next_turn(self):
        p_x, p_y = board.player.my_position()
        a_x, a_y = self.my_position()
        if abs(a_x - p_x) <3 and abs(a_y - p_y) <3:
            fires.append(Fire((a_x*250, a_y*100), self.damage, (p_x*250+100, p_y*100+20), 2))
        else:
            self.status_anim = True
            if abs(a_x - p_x) > abs(a_y - p_y):
                self.next_pos = a_x-1, a_y
                board.level_map[a_x][a_y] = '*'
                board.level_map[a_x-1][a_y] = 'E'
            else:
                self.next_pos = a_x, a_y+1
                board.level_map[a_x][a_y] = '*'
                board.level_map[a_x][a_y+1] = 'E'


    def goto_cell(self, x_new, y_new):
        if (board.get_cell(x_new,y_new)) != (None,None) and self.pos != (x_new, y_new):
            self.next_pos = x_new, y_new
            board.level_map[self.pos[0]][self.pos[1]] = '*'


    def update(self):
        if self.pos > self.next_pos:
            dx = int((self.next_pos[0]*250-self.pos[0]*250)/50)
            dy = int((self.next_pos[1]*100-self.pos[1]*100)/50)
            self.rect.left += dx
            self.rect.top += dy
            if abs(self.rect.left-self.next_pos[0]*250)<5 and abs(self.rect.top-self.next_pos[1]*100)<5:
                self.pos = self.next_pos
                board.level_map[self.pos[0]][self.pos[1]] = 'P'
        self.hp_bar.goto_postition(self.rect)
        if self.hp <= 0:
            self.kill()



class Board():

    def __init__(self, width, height, level):
        self.width = width
        self.height = height
        self.level_map, self.fraction_ai, self.ai_param = self.level = self.load_level(str(level) + ".txt")
        self.player = None
        self.ai = []
        self.generate_level(self.level_map)
        self.score = 0

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(23, 255, 23), (
                    x * 250, y * 100, 250, 100), 1)

    def load_level(self, filename):

        filename = "Levels/" + filename
        with open(filename, 'r') as mapFile:
            info = [line.strip() for line in mapFile]

        level_map = [list(i) for i in info[:7]]
        ai = []
        for i in range(7, len(info) - 1):
            ai.append(info[i].split(","))
        fraction_ai = info[-1]
        return level_map, fraction_ai, ai

    def generate_level(self, level):
        number_ai = 0
        print(level)
        for y in range(7):
            for x in range(7):
                if level[y][x] == '*':
                    Tile('empty', x, y)

                elif level[y][x] == 'P':
                    Tile('empty', x, y)
                    self.player = Player(x, y)

                elif level[y][x] == 'E':
                    Tile('empty', x, y)
                    self.ai.append(AI(x, y, self.fraction_ai, self.ai_param[number_ai%len(self.ai_param)]))
                    number_ai += 1

                elif level[y][x] == 'A':
                    Tile('empty', x, y)
                    self.ai.append(AI(x, y, self.fraction_ai, self.ai_param[number_ai%len(self.ai_param)]))
                    number_ai += 1
    def get_cell(self,x,y):
        cell_x, cell_y = x//250, y//100
        if 0<=cell_x<=6 and  0<=cell_y<=6:
            return cell_x, cell_y
        return None,None



board = Board(7, 7, 7)

fires = []
player_turn = True
ai_turn = False
time = 0
while running:
    if player_turn:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                        x_new, y_new = event.pos
                        player_x, player_y = board.player.my_position()
                        fires.append(Fire((player_x*250+240, player_y*100+50),board.player.my_damage(), (x_new, y_new), 1))
                        player_turn = False
                        ai_turn = True
                elif event.button == 3:
                        x_new, y_new = board.get_cell(*event.pos)
                        board.player.goto_cell(x_new, y_new)
                        player_turn = False
                        ai_turn = True



            elif event.type == pygame.QUIT:
                running = False

    else:
        time +=1
        if time > TIME_TURN and board.player.pos == board.player.next_pos:
            if ai_turn:
                time = 0
                # for ai in board.ai:
                #   ai.next_turn()
                #   ai_turn = not ai_turn
                index = random.randint(0,len(board.ai)-1)

                board.ai[index].next_turn()
                ai_turn = False
            else:

                time += 1
                if time >= TIME_TURN:
                    player_turn = True
    #    time +=1
     #   if time >=TIME_TURN:
     #       ai_turn = not ai_turn
    '''
    else:
        time +=1
        if time >=TIME_TURN:
            player_turn = not player_turn
    '''
    screen.fill(pygame.Color(0, 0, 0))

    board.render()
    all_sprites.draw(screen)
    all_sprites.update()

    pygame.display.flip()
    clock.tick(35)
    if board.player.hp <=0:
        fon = pygame.transform.scale(load_image('data/20Izsw.jpg'), (width, height))
        screen.fill(pygame.Color(0, 0, 0))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        string_rendered = font.render("Score    " + str(board.score), 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        screen.blit(string_rendered, intro_rect)
        running = False


running2 = True
while running2:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running2 = False
        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            running2 = False
    pygame.display.flip()
pygame.quit()
