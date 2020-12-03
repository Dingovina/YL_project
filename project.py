import pygame
import math
import random
import sqlite3

con = sqlite3.connect('scoreboard.db')
cur = con.cursor()


# Функция, возвращающая координаты для отрисовки вращающейся палки (на этапе игры STAGE1)
def where(range, ang, cords):
    ang = math.radians(ang)
    return int(cords[0] - range * math.cos(ang)), int(cords[1] - range * math.sin(ang))


# Функция, сохранияющая результат игрока
def save(id, player_name, player_points):
    try:
        id = cur.execute("""SELECT id FROM best_players""").fetchall()
        id = max(id)[-1] + 1
        cur.execute(
            f"""INSERT INTO best_players(id, player_name, score) VALUES({id}, '{player_name}', {player_points})""")
        con.commit()
    except Exception:
        exit(1)


# Функция добавляющая очки игроку после поломки кирпича
def add_points(points):
    global player_points
    player_points += points


# Класс отвечающий за создание и передвижение мячика с бонусом Multiball
class Bonus_ball:
    def __init__(self, x, y):
        self.x = x - 10
        self.y = y
        self.r = 10
        self.on_field = True
        self.color = (0, 255, 0)


# Класс отвечающий за создание и передвижение мячика с бонусом Long_stick
class Bouns_long_stick:
    def __init__(self, x, y):
        self.x = x + 10
        self.y = y
        self.r = 10
        self.on_field = True
        self.color = (0, 100, 255)


# Класс отвечающий за создание, проверку прочности и другие характеристики кичпичей
class Brick:
    def __init__(self, x, y, width, height, row):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.hp = math.ceil(row / 5)
        if random.randint(1, 9) == 5:
            self.bonus_ball = True
        else:
            self.bonus_ball = False
        if random.randint(1, 10) == 1:
            self.bonus_long_stick = True
        else:
            self.bonus_long_stick = False
        self.broken = False
        self.points = self.hp * 50

    def check(self):
        self.color = (255, 0, 255 / 4 * self.hp)
        if self.bonus_ball:
            self.color = (0, 255, 255 / 4 * self.hp)
        elif self.bonus_long_stick:
            self.color = (0, 0, 255 / 4 * self.hp)
        if self.bonus_long_stick and self.bonus_ball:
            self.color = (255, 255, 255 / 4 * self.hp)
        pygame.draw.rect(screen, (self.color), (self.x, self.y, self.width, self.height))

        for ball in balls:
            if 0 <= self.x - ball.x <= rad and self.y <= ball.y <= self.y + self.height:
                ball.reverse_x()
                self.hit()
                ball.x -= rad
            if 0 <= ball.x - (self.x + self.width) <= rad and self.y <= ball.y <= self.y + self.height:
                ball.reverse_x()
                ball.x += rad
                self.hit()
            if 0 <= ball.y - (self.y + self.height) <= rad and self.x <= ball.x <= self.x + self.width:
                ball.reverse_y()
                ball.y += rad
                self.hit()
            if 0 <= self.y - ball.y <= rad and self.x <= ball.x <= self.x + self.width:
                ball.reverse_y()
                ball.y -= rad
                self.hit()

    def hit(self):
        self.hp -= 1
        if self.hp == 0:
            self.breakk()

    def breakk(self):
        self.broken = True
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height))
        if self.bonus_ball:
            bonus_balls.append(Bonus_ball(self.x + self.width // 2, self.y))
        if self.bonus_long_stick:
            bonus_long_stick.append(Bouns_long_stick(self.x + self.width // 2, self.y))
        add_points(self.points)


# Класс отвечающий за создание и отрисовку игровой палки
class Stick:
    def __init__(self):
        self.size = width // 5.5
        self.h = 10
        self.x = width // 2 - self.size
        self.y = height - 20 - self.h

    def get_rect(self):
        return tuple([self.x, self.y, self.size, self.h])


# Класс отвечающий за создание, расчёт угла полёта и другие характеристики белых мячей
class Ball:
    def __init__(self, cords):
        self.x, self.y = cords
        self.y -= 30
        self.speed = balls_speed
        self.on_field = True

    def move(self):
        self.speed = balls_speed
        if self.x >= width - (rad // 2 + 2):
            self.x_move = False
        if self.x <= (rad // 2 + 2):
            self.x_move = True
        if self.y >= height - (rad // 2 + 2):
            self.signal_lose()
        if self.y <= (rad // 2 + 2):
            self.y_move = True

        if self.y >= stick.y - rad:
            if stick.x < self.x < stick.x + stick.size:
                self.y_move = False
                self.y -= 1
                a = 180 * ((self.x - stick.x) / stick.size)  # чем ближе к центру палки - тем прямее угол
                self.ang = 180 - max(min(a, 155), 25)

        if self.x_move:
            self.x += abs(int((math.cos(math.radians(self.ang))) * self.speed))
        else:
            self.x -= abs(int((math.cos(math.radians(self.ang))) * self.speed))
        if self.y_move:
            self.y += abs(int((math.sin(math.radians(self.ang))) * self.speed))
        else:
            self.y -= abs(int((math.sin(math.radians(self.ang))) * self.speed))

        pygame.draw.circle(screen, pygame.Color('white'), (self.x, self.y), rad)

    def get_cords(self):
        return self.x, self.y

    def signal_lose(self):
        self.on_field = False

    def reverse_y(self):
        if self.y_move:
            self.y_move = False
        else:
            self.y_move = True

    def reverse_x(self):
        if self.x_move:
            self.x_move = False
        else:
            self.x_move = True


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    size = width, height = 777, 500
    screen = pygame.display.set_mode(size)
    in_game = True
    start_screen = True
    score_screen = False
    help_screen = False
    button_x = 0
    button_y = 0
    button_x1 = 0
    button_y1 = 0
    # Основной игровой цикл
    while in_game:
        # Начальный экран
        while start_screen:
            screen.fill((0, 0, 0))

            font = pygame.font.Font(None, 100)
            text = font.render("Начать игру", True, (100, 255, 100))
            text_x = width // 2 - text.get_width() // 2
            text_y = height // 2 - 2 * text.get_height()
            text_w = text.get_width()
            text_h = text.get_height()
            screen.blit(text, (text_x, text_y))
            pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                                   text_w + 20, text_h + 20), 1)

            font = pygame.font.Font(None, 100)
            text = font.render("Таблица лидеров", True, (100, 255, 100))
            text_x1 = width // 2 - text.get_width() // 2
            text_y1 = height // 2
            text_w1 = text.get_width()
            text_h1 = text.get_height()
            screen.blit(text, (text_x1, text_y1))
            pygame.draw.rect(screen, (0, 255, 0), (text_x1 - 10, text_y1 - 10,
                                                   text_w1 + 20, text_h1 + 20), 1)
            font = pygame.font.Font(None, 80)
            text = font.render("Помощь", True, (100, 255, 100))
            text_x2 = width // 2 - text.get_width() // 2
            text_y2 = height - height // 5
            text_w2 = text.get_width()
            text_h2 = text.get_height()
            screen.blit(text, (text_x2, text_y2))
            pygame.draw.rect(screen, (0, 255, 0), (text_x2 - 10, text_y2 - 10,
                                                   text_w2 + 20, text_h2 + 20), 1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_game = False
                    start_screen = False
                    running = False

                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    if text_x1 <= x <= text_x1 + text_w1 and text_y1 <= y <= text_y1 + text_h1:
                        start_screen = False
                        score_screen = True
                    if text_x <= x <= text_x + text_w and text_y <= y <= text_y + text_h:
                        start_screen = False
                        stage0 = True
                    if text_x2 <= x <= text_x2 + text_w2 and text_y2 <= y <= text_y2 + text_h2:
                        start_screen = False
                        help_screen = True

            pygame.display.flip()
        try:
            screen.fill((0, 0, 0))
        except Exception:
            exit(1)

        # Экран Помощи
        while help_screen:
            screen.fill((0, 0, 0))

            font = pygame.font.Font(None, 40)
            text = font.render("Таблица лидеров", True, (100, 255, 100))
            text_x = width // 2 - text.get_width()
            text_y = height - text.get_height() - height // 15
            text_w = text.get_width()
            text_h = text.get_height()
            screen.blit(text, (text_x, text_y))
            pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                                   text_w + 20, text_h + 20), 1)

            font = pygame.font.Font(None, 40)
            text = font.render("Начать игру", True, (100, 255, 100))
            text_x1 = width // 2 - text.get_width() + height // 2.25
            text_y1 = height - text.get_height() - height // 15
            text_w1 = text.get_width()
            text_h1 = text.get_height()
            screen.blit(text, (text_x1, text_y1))
            pygame.draw.rect(screen, (0, 255, 0), (text_x1 - 10, text_y1 - 10,
                                                   text_w1 + 20, text_h1 + 20), 1)

            # Отрисовка всех фигур в разделе HELP
            pygame.draw.rect(screen, (255, 0, 255 // 4 * 1), (30, 10, width // 6, 35))
            pygame.draw.rect(screen, (255, 0, 255 // 4 * 2), (30, 50, width // 6, 35))
            pygame.draw.rect(screen, (255, 0, 255 // 4 * 3), (30, 90, width // 6, 35))
            pygame.draw.rect(screen, (255, 0, 255 // 4 * 4), (30, 130, width // 6, 35))
            pygame.draw.rect(screen, (0, 255, 255 // 4 * 1), (30, 170, width // 6, 35))
            pygame.draw.rect(screen, (0, 0, 255 // 4 * 1), (30, 210, width // 6, 35))
            pygame.draw.rect(screen, (255, 255, 255 // 4 * 1), (30, 250, width // 6, 35))
            pygame.draw.circle(screen, pygame.Color('white'), (95, 310), 15)
            pygame.draw.circle(screen, (0, 255, 0), (95, 350), 15)
            pygame.draw.circle(screen, (0, 100, 255), (95, 390), 15)

            font = pygame.font.Font(None, 40)
            # Комментарии ко всем фигурам в разделе HELP
            text = font.render("Кирич с одной единицой прочноти", True, (100, 255, 100))
            text_x = 200
            text_y = 15
            screen.blit(text, (text_x, text_y))
            text = font.render("Кирич с двумя единицами прочности", True, (100, 255, 100))
            text_x = 200
            text_y = 55
            screen.blit(text, (text_x, text_y))
            text = font.render("Кирич с тремя единицами прочности", True, (100, 255, 100))
            text_x = 200
            text_y = 95
            screen.blit(text, (text_x, text_y))
            text = font.render("Кирич с четырьмя единицами прочности", True, (100, 255, 100))
            text_x = 200
            text_y = 135
            screen.blit(text, (text_x, text_y))
            text = font.render("Кирич с бонусом Multiball", True, (100, 255, 100))
            text_x = 200
            text_y = 175
            screen.blit(text, (text_x, text_y))
            text = font.render("Кирич с бонусом Long_stick", True, (100, 255, 100))
            text_x = 200
            text_y = 215
            screen.blit(text, (text_x, text_y))
            text = font.render("Кирич с обоими бонусами", True, (100, 255, 100))
            text_x = 200
            text_y = 255
            screen.blit(text, (text_x, text_y))
            text = font.render("Мяч игрока", True, (100, 255, 100))
            text_x = 200
            text_y = 300
            screen.blit(text, (text_x, text_y))
            text = font.render("Мяч с бонусом Multiball", True, (100, 255, 100))
            text_x = 200
            text_y = 340
            screen.blit(text, (text_x, text_y))
            text = font.render("Мяч с бонусом Long_stick", True, (100, 255, 100))
            text_x = 200
            text_y = 380
            screen.blit(text, (text_x, text_y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_game = False
                    help_screen = False
                    running = False

                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    if text_x <= x <= text_x + text_w and text_y <= y <= text_y + text_h:
                        help_screen = False
                        score_screen = True
                        screen.fill((0, 0, 0))
                    if text_x1 <= x <= text_x1 + text_w1 and text_y1 <= y <= text_y1 + text_h1:
                        help_screen = False
                        stage0 = True
                        screen.fill((0, 0, 0))

            pygame.display.flip()

        # Экран Таблицы очков
        while score_screen:

            font = pygame.font.Font(None, 100)
            text = font.render("Начать игру", True, (100, 255, 100))
            text_x1 = width // 2 - text.get_width() // 2
            text_y1 = height // 1.25
            text_w1 = text.get_width()
            text_h1 = text.get_height()
            screen.blit(text, (text_x1, text_y1))
            pygame.draw.rect(screen, (0, 255, 0), (text_x1 - 10, text_y1 - 10,
                                                   text_w1 + 20, text_h1 + 20), 1)

            names = cur.execute("""SELECT player_name FROM best_players""").fetchall()
            scores = cur.execute("""SELECT score FROM best_players""").fetchall()
            table = dict()
            for i in range(len(names)):
                table[scores[i][0]] = names[i][0]
            names = []
            scores = []
            table = list(table.items())
            table.sort(reverse=True)
            for i in range(min(5, len(table))):
                names.append(table[i][-1])
                scores.append(table[i][0])

            for i in range(min(5, len(names))):
                string = str(names[i]) + ' - ' + str((scores[i]))
                font = pygame.font.Font(None, 50)
                text = font.render(string, True, (100, 255, 100))
                text_x = width // 2 - text.get_width() // 2
                text_y = height // 7 * (i + 1) - 40
                screen.blit(text, (text_x, text_y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_game = False
                    score_screen = False
                    running = False

                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    if text_x1 <= x <= text_x1 + text_w1 and text_y1 <= y <= text_y1 + text_h1:
                        start_screen = False
                        score_screen = False
                        stage0 = True

            pygame.display.flip()

        rad = 10
        flag = True
        x_size = 20
        balls_speed = 8
        ball = Ball((width // 2, height - rad))
        stick = Stick()
        ang = 0
        stage1 = False
        stage2 = False
        running = True
        player_name = ''

        clock = pygame.time.Clock()
        if in_game:
            # Стадия до начала игры: ввод имени игрока
            while stage0:
                fps = 180
                if not running:
                    pygame.quit()
                    break
                try:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.unicode in 'qwertyuiopasdfghjklzxcvbnm[]-_()1234567890!@$&*+=/~':
                                player_name += event.unicode
                            elif event.key == 8:
                                player_name = player_name[:-1]
                            if event.key == 13:
                                stage0 = False
                                stage1 = True
                                break
                except Exception:
                    exit(1)
                screen.fill((0, 0, 0))
                if len(player_name) > 10:
                    player_name = player_name[:10]
                font = pygame.font.Font(None, 80)
                text = font.render("Enter your name: {}".format(player_name), True, (100, 255, 100))
                text_x = width // 2 - text.get_width() // 2
                text_y = height // 2 - text.get_height() // 2
                text_w = text.get_width()
                text_h = text.get_height()
                screen.blit(text, (text_x, text_y))

                pygame.display.flip()
                clock.tick(fps)

            if running:
                # Первая стадия игра: выбор угла для запуска мяча
                while stage1:
                    fps = 120
                    if not running:
                        pygame.quit()
                    if ang == 180:
                        flag = False
                    if ang == 0:
                        flag = True
                    if flag:
                        ang += 0.5
                    else:
                        ang -= 0.5
                    screen.fill((0, 0, 0))
                    pygame.draw.circle(screen, pygame.Color('white'), (ball.x, ball.y), rad)
                    pygame.draw.line(screen, (255, 255, 255), (ball.x, ball.y), where(75, ang, (ball.x, ball.y)), 2)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if (event.type == pygame.KEYUP and event.key == 32) or event.type == pygame.MOUSEBUTTONUP:
                            stage2 = True
                            stage1 = False

                    pygame.display.flip()
                    clock.tick(fps)

                if ang <= 90:
                    ball.x_move, ball.y_move = False, False
                else:
                    ball.x_move, ball.y_move = True, False
                stop = False
                fps = 60
                player_points = 0
                ball.ang = ang
                bricks = []
                balls = [ball]
                bonus_balls = []
                brick_height = 35
                brick_width = width // 6
                row = 5
                long_stick_time = 0
                bonus_long_stick = []
                for i in range(6):
                    for j in range(5):
                        if random.randint(1, 100) <= 70:
                            bricks.append(
                                Brick(brick_width * i, brick_height * j, brick_width - 1, brick_height - 1, row))
                t = 0  # счётчик тиков
                sec = 0  # счётчик секунд
                for brick in bricks:
                    brick.check()
                if running:
                    # Вторая стадия игры: Основной игровой процесс
                    while stage2:
                        if not stop:
                            if not running:
                                pygame.quit()
                                stage2 = False
                            t += 1
                            if t % fps == 0:
                                sec += 1
                                long_stick_time -= 1
                                if long_stick_time == 0:
                                    stick.size -= 50
                                if sec % 8 == 0:
                                    balls_speed += 0.5
                                    row += 1
                                    for brick in bricks:
                                        brick.y += brick_height
                                        for ball in balls:
                                            if ball.y <= brick.y:
                                                ball.y += brick.y - ball.y + 5
                                    for i in range(6):
                                        if random.randint(1, 8) != 1:
                                            bricks.append(
                                                Brick(brick_width * i, 0, brick_width - 1, brick_height - 1, row))

                            screen.fill((0, 0, 0))
                            pygame.draw.rect(screen, (255, 255, 255), stick.get_rect())
                            # Движение и активация бонусов Multiball
                            for bonus_ball in bonus_balls:
                                bonus_ball.y += balls_speed // 2
                                pygame.draw.circle(screen, bonus_ball.color, (bonus_ball.x, int(bonus_ball.y)), bonus_ball.r)
                                if stick.x <= bonus_ball.x <= stick.x + stick.size and (
                                        -1 * bonus_ball.r) <= stick.y - bonus_ball.y <= bonus_ball.r:
                                    balls.append(Ball((bonus_ball.x, int(bonus_ball.y) - 15)))
                                    balls[-1].x_move = False
                                    balls[-1].y_move = False
                                    balls[-1].ang = 45
                                    balls.append(Ball((bonus_ball.x, int(bonus_ball.y) - 15)))
                                    balls[-1].x_move = False
                                    balls[-1].y_move = False
                                    balls[-1].ang = 90
                                    balls.append(Ball((bonus_ball.x, int(bonus_ball.y) - 15)))
                                    balls[-1].x_move = True
                                    balls[-1].y_move = False
                                    balls[-1].ang = 45
                                    bonus_ball.on_field = False
                                    player_points += 10
                                elif bonus_ball.y >= height:
                                    bonus_ball.on_field = False
                            # Движение и активация бонусов Long_stick
                            for long_stick in bonus_long_stick:
                                long_stick.y += balls_speed // 2
                                pygame.draw.circle(screen, long_stick.color, (long_stick.x, int(long_stick.y)), long_stick.r)
                                if stick.x <= long_stick.x <= stick.x + stick.size and 0 <= stick.y - long_stick.y <= long_stick.r:
                                    long_stick.on_field = False
                                    if long_stick_time <= 0:
                                        stick.size += 50
                                    long_stick_time = 10
                                    player_points += 10
                                if long_stick.y >= height:
                                    long_stick.on_field = False

                            for ball in balls:
                                ball.move()
                            for brick in bricks:
                                if not brick.broken:
                                    brick.check()
                                if brick.y + brick_height >= stick.y:
                                    stage2 = False
                            # Обновление всех списков, удаление всех элементов, вышедших из игры
                            bricks = [i for i in bricks if not i.broken]
                            balls = [i for i in balls if i.on_field]
                            bonus_balls = [i for i in bonus_balls if i.on_field]
                            bonus_long_stick = [i for i in bonus_long_stick if i.on_field]
                            if len(balls) == 0:
                                stage2 = False
                            if len(bricks) == 0:
                                player_points += 10
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                            if event.type == pygame.MOUSEBUTTONUP:
                                stop = False
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                stop = True
                            if event.type == pygame.MOUSEMOTION:
                                x = event.pos[0]
                                if x > width:
                                    x = width
                                else:
                                    x -= stick.size // 2
                                stick.x = x
                                pygame.draw.rect(screen, (255, 255, 255), stick.get_rect())

                        pygame.display.flip()
                        clock.tick(fps)
                    # Экран, отображаемый после окончания игры
                    player_points = player_points * 10 + sec * 100
                    font = pygame.font.Font(None, 100)
                    text = font.render("Final score: {}".format(player_points), True, (100, 255, 100))
                    text_x = width // 2 - text.get_width() // 2
                    text_y = height // 2 - text.get_height() // 2
                    text_w = text.get_width()
                    text_h = text.get_height()
                    screen.blit(text, (text_x, text_y))
                    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                                           text_w + 20, text_h + 20), 1)

                    font = pygame.font.Font(None, 75)
                    text = font.render("Далее".format(player_points), True, (100, 255, 100))
                    text_x = width // 2 - text.get_width() // 2
                    text_y = height - text.get_height() * 2
                    text_w = text.get_width()
                    text_h = text.get_height()
                    screen.blit(text, (text_x, text_y))
                    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                                           text_w + 20, text_h + 20), 1)
                    button_x = text_x
                    button_y = text_y
                    button_x1 = text_x + text_w
                    button_y1 = text_y + text_h
                    in_game = False
                    running = True
                    pygame.display.flip()
                    stage2 = False

                    # Стадия игры, когда игрок может начать новую игру
                    while running:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                            if event.type == pygame.MOUSEBUTTONUP:
                                x, y = event.pos
                                if button_x <= x <= button_x1 and button_y <= y <= button_y1:
                                    save(id, player_name, player_points)
                                    in_game = True
                                    start_screen = True
                                    score_screen = False
                                    stage0 = False
                                    stage1 = False
                                    stage2 = False
                                    running = False
    con.close()
    pygame.quit()
