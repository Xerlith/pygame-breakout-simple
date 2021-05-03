import pygame
from pygame.locals import QUIT, K_ESCAPE, K_LEFT, K_RIGHT, K_SPACE, K_UP, K_DOWN
import math
import os.path

pygame.init()

CLOCK = pygame.time.Clock()

SCREEN_HEIGHT = 640
SCREEN_WIDTH = 480

PLAYER_SPEED = 3

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Breakout UJ")
font = pygame.font.Font(None, 36)
background = pygame.Surface(screen.get_size())

game_over = False
game_running = True


# pygame.mixer.music.load("sounds/intro.mp3")
# pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1)


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.width = 60
        self.height = 15

        self.surf = pygame.Surface([self.width, self.height])
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=(x, y))

    def update(self, pressed_keys):
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-3, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(3, 0)

        if self.rect.left <= 0:
            self.rect.left = 0
        elif self.rect.right >= SCREEN_WIDTH - 30:
            self.rect.right = SCREEN_WIDTH - 30


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((0, 0, 255))
        self.rect = self.surf.get_rect(center=(x, y))

    def set_color(self, color):
        self.surf.fill(color)


class Ball(pygame.sprite.Sprite):
    speed = 2.0
    x = 0.0
    y = 180.0
    direction = 200

    width = 10
    height = 10

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((5, 5))
        self.rect = self.surf.get_rect(center=(x, y))
        self.surf.fill((255, 255, 255))

    def bounce(self, diff):
        """ This function will bounce the ball
            off a horizontal surface (not a vertical one) """

        self.direction = (180 - self.direction) % 360
        self.direction -= diff

    def update(self):
        direction_radians = math.radians(self.direction)

        self.x += self.speed * math.sin(direction_radians)
        self.y -= self.speed * math.cos(direction_radians)

        # Move the image to where our x and y are
        self.rect.x = self.x
        self.rect.y = self.y

        if self.y <= 0:
            self.bounce(0)
            self.y = 1

        if self.x <= 0:
            self.direction = (360 - self.direction) % 360
            self.x = 1

        if self.x > SCREEN_WIDTH - self.width:
            self.direction = (360 - self.direction) % 360
            self.x = SCREEN_WIDTH - self.width - 1


def generate_level(level):
    file = open("levels/" + str(level) + ".txt", "r")
    blocks = pygame.sprite.Group()
    level_data = file.readlines()
    i = 0
    while i < len(level_data):
        level_info = level_data[i].split(',')
        block = Block(int(level_info[0]), int(level_info[1]))
        blocks.add(block)
        i += 1
    return blocks


level = 1
blocks = generate_level(level)
player = Player(305, 450)
ball = Ball(315, 440)
balls = pygame.sprite.Group()
balls.add(ball)
lives = 3
points = 0


# blocks = pygame.sprite.Group()
# block = Block(20, 20)
# blocks.add(block)

def setup_new_game(lvl):
    global blocks, lives, player, ball, balls

    blocks = generate_level(lvl)
    lives = 3
    ball = Ball(315, 440)
    player = Player(305, 450)
    balls = pygame.sprite.Group()
    balls.add(ball)


def start_game():
    global game_running
    game_running = True


def pause_game():
    global game_running
    game_running = False


def ball_loss():
    global ball
    global lives
    global game_running
    ball.kill()
    ball = Ball(315, 440)
    balls.add(ball)
    lives -= 1
    game_running = False


def render_counters():
    lives_counter = font.render("Lives: " + str(lives), True, (255, 0, 0))
    counter_pos = lives_counter.get_rect()
    counter_pos.top = 600
    screen.blit(lives_counter, counter_pos)

    points_counter = font.render("Points: " + str(points), True, (0, 255, 0))
    points_pos = points_counter.get_rect()
    points_pos.left = 200
    points_pos.top = 600
    screen.blit(points_counter, points_pos)


def write_score(score):
    with open('scores.txt', "w") as f:
        f.write("%s\n" % score)


def show_scores():
    file = open("scores.txt", "r")
    scores = [int(i) for i in file.readlines()]
    file.close()

    screen.fill((0, 0, 0))

    scores.sort(reverse=True)
    best = scores[:10]

    header_surf = font.render("HIGH SCORES", True, (255, 255, 255))
    header_rect = header_surf.get_rect(center=(background.get_width() / 2, 20))
    screen.blit(header_surf, header_rect)

    for i, entry in enumerate(best):
        txt_surf = font.render(str(i+1) + " - " + str(entry), True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=(background.get_width() / 2, 80 + 30 * i))
        screen.blit(txt_surf, txt_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                return
        CLOCK.tick(15)


def quit_game():
    pygame.quit()
    quit()


class MenuEntry:

    def __init__(self, name, callback):
        self.name = name
        self.callback = callback
        self.text = font.render(name, True, (255, 0, 0))
        self.rect = self.text.get_rect(centerx=background.get_width() / 2)


def main_menu():
    menu = True
    menu_posX = 240

    menu_entries = [
        MenuEntry("start", game_loop),
        MenuEntry("scores", show_scores),
        MenuEntry("quit", quit_game)
    ]

    selected = 0
    while menu:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()

        screen.fill((0, 0, 0))

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_UP]:
            selected -= 1
        elif pressed_keys[K_DOWN]:
            selected += 1
        elif pressed_keys[K_SPACE]:
            menu_entries[selected].callback()

        if selected >= len(menu_entries):
            selected = 0
        if selected < 0:
            selected = len(menu_entries) - 1

        for index, entry in enumerate(menu_entries):
            entry.text = font.render(entry.name, True, (255, 0, 0) if index == selected else (0, 0, 255))
            entry.rect.top = menu_posX + index * 20
            screen.blit(entry.text, entry.rect)

        CLOCK.tick(15)
        pygame.display.flip()


def game_loop():
    global game_over
    global game_running
    global points, level

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()

        pressed_keys = pygame.key.get_pressed()
        screen.fill((0, 0, 0))

        if not game_over:
            if game_running:
                player.update(pressed_keys)
                ball.update()
                if ball.y > 600:
                    ball_loss()
            else:
                text = font.render("Paused", True, (255, 255, 255))
                textpos = text.get_rect(centerx=background.get_width() / 2)
                textpos.top = 300
                screen.blit(text, textpos)

            if pressed_keys[K_SPACE]:
                game_running = not game_running

            screen.blit(player.surf, player.rect)
            screen.blit(ball.surf, ball.rect)
            render_counters()
            game_over = lives == 0

        if game_over and lives == 0:
            text = font.render("Game Over", True, (255, 255, 255))
            textpos = text.get_rect(centerx=background.get_width() / 2)
            textpos.top = 300
            screen.blit(text, textpos)
            render_counters()
            write_score(points)
            if pressed_keys[K_SPACE]:
                return

        if game_over and lives > 0:
            text = font.render("Game Cleared!", True, (0, 255, 0))
            textpos = text.get_rect(centerx=background.get_width() / 2)
            textpos.top = 300
            screen.blit(text, textpos)
            render_counters()
            write_score(points)
            if pressed_keys[K_SPACE]:
                return

        if pygame.sprite.spritecollide(player, balls, False):
            diff = (player.rect.x + player.width / 2) - (ball.rect.x + ball.width / 2)

            ball.rect.y = screen.get_height() - player.rect.height - ball.rect.height - 1
            ball.bounce(diff)

        hit_blocks = pygame.sprite.spritecollide(ball, blocks, True)

        if len(hit_blocks) > 0:
            ball.bounce(0)
            points += 1

            if len(blocks) == 0:
                level += 1

                if os.path.exists("levels/" + str(level) + ".txt"):
                    setup_new_game(level)
                else:
                    game_over = True

        for block in blocks:
            screen.blit(block.surf, block.rect)

        if pygame.sprite.spritecollideany(ball, blocks):
            delete_block = pygame.sprite.spritecollideany(ball, blocks)
            delete_block.kill()

        CLOCK.tick(60)
        pygame.display.flip()


main_menu()
