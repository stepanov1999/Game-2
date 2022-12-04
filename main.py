from random import randint

name = input('Мы рады приветствовать вас в нашей игре, как к вам стоит обращаться:')

class Color:
    blue = '\033[94m'
    purple = '\033[35m'
    green = '\033[92m'
    yell = '\033[93m'
    red = '\033[91m'

    shapes = {
    0: blue + '·' +  purple,
    1: green + '►' + purple,
    2: blue + '·' +  purple,
    10: red + '•' +  purple,
    11: yell + '■' + purple,
    21: red + '■' +  purple
}


# Исключения
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __init__(self, text):
        self.txt = text

class BoardUsedException(BoardException):
    def __init__(self, text):
        self.txt = text


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f'({self.x},{self.y})'


class Ship:
    def __init__(self, dt, ln, dt_):
        self.dot = dt  # стартовая точка корабля
        self.length = ln  # длина коробля
        self.direction = dt_
        self.life = ln

    def dots(self):
        if self.direction:
            return [Dot(x, self.dot.y) for x in range(self.dot.x, self.dot.x + self.length)]
        else:
            return [Dot(self.dot.x, y) for y in range(self.dot.y, self.dot.y + self.length)]


class Board:
    def __init__(self, h):
        self.ships = []
        self.x_ships = 0
        self.hide = h
        self.f = [[0] * 6 for _ in range(0, 6)]

    @staticmethod
    def contour(c_ship):
        set_ = set()

        def add_dot(x1, y1):
            try:
                set_.add(Dot(x1, y1))
            except IndexError:
                pass

        for dt in c_ship.dots():
            add_dot(dt.x + 1, dt.y)
            add_dot(dt.x + 1, dt.y + 1)
            add_dot(dt.x, dt.y + 1)
            add_dot(dt.x - 1, dt.y + 1)
            add_dot(dt.x - 1, dt.y)
            add_dot(dt.x - 1, dt.y - 1)
            add_dot(dt.x, dt.y - 1)
            add_dot(dt.x + 1, dt.y - 1)
        return set_.difference(c_ship.dots())

    @staticmethod
    def out(dt):
        return (dt.x < 0) or (dt.x >= 6) or (dt.y < 0) or (dt.y >= 6)

    def add_ship(self, add_s):
        try:
            for dt in add_s.dots():
                if self.out(dt):
                    raise BoardOutException('')
                if self.f[dt.x][dt.y] != 0:
                    raise BoardUsedException('')
                for i in self.ships:
                    if dt in self.contour(i):
                        raise BoardUsedException('')
        except (BoardOutException, BoardUsedException):
            return False
        else:
            for dt in add_s.dots():
                self.f[dt.x][dt.y] = 1
            self.ships.append(add_s)
            self.x_ships += 1
            return True

    def shot(self, dt):  # выстрел в точку
        if self.out(dt):
            raise BoardOutException(f'{dt.x + 1} {dt.y + 1} - {Color.blue}Данные координаты вне зоны видимости орудий')
        if self.f[dt.x][dt.y] >= 10:
            raise BoardUsedException(f'{dt.x + 1} {dt.y + 1} - {Color.blue} Данные координатыы уже были ранее поражены')

        self.f[dt.x][dt.y] += 10
        if self.f[dt.x][dt.y] == 11:
            for s in self.ships:
                if dt in s.dots():
                    s.life -= 1
                    if not s.life:
                        for dt_ in s.dots():
                            self.f[dt_.x][dt_.y] += 10
                        for dt_ in self.contour(s):
                            if not self.out(dt_):
                                if self.f[dt_.x][dt_.y] < 10:
                                    self.f[dt_.x][dt_.y] += 10
                        self.x_ships -= 1
        return self.f[dt.x][dt.y]  # возвращаем значение выстрела

    def random_board(self):
        size_bord = 6
        count = 0
        for q in [3, 2, 2, 1, 1, 1, 1]:
            while True:
                x = randint(0, size_bord - 1)
                y = randint(0, size_bord - 1)
                dt = randint(0, 1)
                if self.add_ship(Ship(Dot(x, y), q, dt)):
                    break
                else:
                    count += 1
                if count > 2000:  # ограничение попыток
                    return False
        return True


class Player:
    def __init__(self, bd_):
        self.board = bd_
        self.last_shot_dot = []
        self.last_shot_value = 0

    def ask(self):
        x, y = 0, 0
        return Dot(x, y)

    def move(self, other):
        try:
            Game.check = 0
            dt_ = self.ask()
            shot_value = other.board.shot(dt_)
            if shot_value > 10:
                self.last_shot_dot.append(dt_)
                self.last_shot_value = shot_value
                if shot_value > 20:
                    print(f'{dt_.x + 1} {dt_.y + 1} - {Color.red}Убил!{Color.red}')
                    self.last_shot_dot.clear()
                    Game.check += 1
                else:
                    print(f'{dt_.x + 1} {dt_.y + 1} - {Color.yell}Ранил!{Color.yell}')
                    Game.check += 1
                if other.board.x_ships:
                    return True
                else:
                    self.board.hide = False
                    return False
            else:
                print(f'{dt_.x + 1} {dt_.y + 1} - {Color.green}Мимо!{Color.green}')
                return False
        except (BoardOutException, BoardUsedException) as e:
            if type(self) is User:
                print(e.txt)
            return True


class User(Player):
    def ask(self):
        while True:
            ent_list = input(f"\n{name}, введите координаты: {Color.blue}").split()
            if len(ent_list) != 2:
                print(f"{Color.blue}Введите две координаты{Color.blue}")
                continue
            x, y = ent_list
            if not (x.isdigit()) or not (y.isdigit()):
                print(f"{Color.blue}Введите числа{Color.blue}")
                continue
            x = int(ent_list[0]) - 1
            y = int(ent_list[1]) - 1
            return Dot(x, y)


class AI(Player):
    def ask(self):
        if self.last_shot_value == 11:
            if len(self.last_shot_dot) == 1:
                dt_ = self.last_shot_dot[0]
                t = randint(1, 4)
                if t == 1:
                    return Dot(dt_.x, dt_.y - 1)
                elif t == 2:
                    return Dot(dt_.x + 1, dt_.y)
                elif t == 3:
                    return Dot(dt_.x, dt_.y + 1)
                elif t == 4:
                    return Dot(dt_.x - 1, dt_.y)
            else:
                t = randint(0, 1)
                if self.last_shot_dot[0].x == self.last_shot_dot[1].x:
                    miny = self.last_shot_dot[0].y
                    maxy = miny
                    for dt_ in self.last_shot_dot:
                        if miny > dt_.y:
                            miny = dt_.y
                        if maxy < dt_.y:
                            maxy = dt_.y
                    if t:
                        return Dot(self.last_shot_dot[0].x, miny - 1)
                    else:
                        return Dot(self.last_shot_dot[0].x, maxy + 1)
                else:
                    minx = self.last_shot_dot[0].x
                    maxx = minx
                    for dt_ in self.last_shot_dot:
                        if minx > dt_.x:
                            minx = dt_.x
                        if maxx < dt_.x:
                            maxx = dt_.x
                    if t:
                        return Dot(minx - 1, self.last_shot_dot[0].y)
                    else:
                        return Dot(maxx + 1, self.last_shot_dot[0].y)
        else:
            x = randint(0, 5)
            y = randint(0, 5)
            return Dot(x, y)


class Game(Color):
    check = 0

    def __init__(self):
        bd_us = Board(False)
        bd_ai = Board(True)
        while not bd_us.random_board():
            bd_us = Board(False)
        while not bd_ai.random_board():
            bd_ai = Board(True)
        self.board_us = bd_us
        self.board_ai = bd_ai
        self.us = User(bd_us)
        self.ai = AI(bd_ai)

    def print_board(self):
        size = 6

        def get_row(bd):
            if bd.hide:
                return '   '.join(self.shapes[bd.f[i][j] if bd.f[i][j] >= 10 else 2] for j in range(0, size))
            else:
                return '   '.join(self.shapes[bd.f[i][j]] for j in range(0, size))

        print(f'\n{self.red}Поле игрока {name} :{"":15}Поле компьютера:')
        print(f'{self.purple}{"_" * 29}{"":10}{"_" * 29}')
        coord_numbers = '│ '.join(f'{str(s + 1):2}' for s in range(0, size))
        print(f'│ {self.purple} {self.purple} │ {coord_numbers}│{"":10}│ {self.purple} {self.purple} │ {coord_numbers}│')
        print(f'│{"–––│" * 7}{"":10}│{"–––│" * 7}')
        for i in range(0, size):
            print(f'│ {str(i + 1):2}│ {get_row(self.board_us)} │{"":10}│ {str(i + 1):2}│ {get_row(self.board_ai)} │')
        print(f'|___|{"_" * 23}|{"":10}|___|{"_" * 23}|')

    def loop(self, user_move):
        if user_move:
            while True:
                self.print_board()
                if self.us.move(self.ai):
                    continue
                else:
                    self.print_board()
                    break
        else:
            print('\nХод компьютера: ')
            while True:
                if Game.check == 1:
                    self.print_board()
                    print('\nХод компьютера: ')
                if self.ai.move(self.us):
                    continue
                else:
                    break

    def start(self):
        user_move = True
        print(f'{self.blue}{"-" * 77}{self.blue}')
        while True:
            self.loop(user_move)
            user_move = not user_move
            if not self.board_us.x_ships:
                self.print_board()
                print(f'{self.blue}\n Победу одержал компьютер!\n{self.blue}')
                break
            if not self.board_ai.x_ships:
                self.print_board()
                print(f'{self.yell}\n Победу одержал {name}!\n{self.yell}')
                break
        return False


class Greet:
    @staticmethod
    def greet():
        print(f'{Game.blue}')
        print(f'{Game.blue}{"-" * 77}\n')
        print(f'{Game.blue} НАПУТСТВИЕ ПЕРЕД БОЕМ:')
        print(f' {Game.blue} Приветствуем вас в игре "Морской бой"')
        print(f' {Game.blue} Формат ввода x y')
        print(f' {Game.blue} x - номер строки')
        print(f' {Game.blue} y - номер столбца')
        print(f'{Game.blue}{"-" * 77}')


Greet.greet()
while True:
    g = Game()
    if g.start():
        break
