import random
import sys
import pygame
from pygame.locals import *


def heuristic_cost_estimate(start, goal):
    return abs(goal[0] - start[0]) + abs(goal[1] - start[1])


def reconstruct_path(came_from, current_node):
    if current_node in came_from:
        p = reconstruct_path(came_from, came_from[current_node])
        return p + [current_node]
    return [current_node]


def neighbours_of(node):
    for y in range(grid['y']):
        for x in range(grid['x']):
            if abs(x - node[0]) ** 2 + abs(y - node[1]) ** 2 != 1:
                continue
            if Point(x, y) in obstacles:
                continue
            yield (x, y)


def a_star(start, goal):
    closed_set = set()
    open_set = set([start])
    came_from = {}

    g_score = {start: 0}
    f_score = {start: g_score[start] + heuristic_cost_estimate(start, goal)}

    while open_set:
        current = [n for n in sorted(f_score, key=f_score.get) if n in open_set][0]
        if current == goal:
            return reconstruct_path(came_from, goal)

        open_set.remove(current)
        closed_set.add(current)

        for neighbour in neighbours_of(current):
            if neighbour in closed_set:
                continue
            tentative_g_score = g_score[current] + 1  # distance between cells

            if neighbour not in open_set or tentative_g_score < g_score.get(neighbour, sys.maxint):
                came_from[neighbour] = current
                g_score[neighbour] = tentative_g_score
                f_score[neighbour] = g_score[neighbour] + heuristic_cost_estimate(neighbour, goal)
                if neighbour not in open_set:
                    open_set.add(neighbour)

    return None


class Point(object):
    def __init__(self, *args):
        if len(args) == 1:
            self.x, self.y = args[0]
        if len(args) == 2:
            self.x, self.y = args[0], args[1]

    @property
    def tuple(self):
        return (self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return Point(self.x + other[0], self.y + other[1])

    def __str__(self):
        return str((self.x, self.y))


#
# Painting
#

colors = {
    'background': pygame.Color(30, 30, 30),
    'grid': pygame.Color(70, 70, 70),
    'obstacle': pygame.Color(150, 150, 150),
    'player': pygame.Color(0, 255, 0),
    'monster': pygame.Color(0, 0, 255)
}


def to_screen(point):
    return (
        surface.get_width() * point.x / grid['y'],
        surface.get_height() * point.y / grid['x']
    )


def to_screen_rect(point):
    return pygame.Rect(to_screen(point), to_screen(Point(1, 1)))


def paint():
    surface.fill(colors['background'])
    for y in range(1, grid['y']):
        for x in range(1, grid['x']):
            pygame.draw.circle(surface, colors['grid'], to_screen(Point(x, y)), 0)

    for y in range(0, grid['y']):
        for x in range(0, grid['x']):
            point = Point(x, y)
            if point in obstacles:
                pygame.draw.rect(surface, colors['obstacle'], to_screen_rect(point))
            if point == player:
                pygame.draw.rect(surface, colors['player'], to_screen_rect(point))
            if point == monster:
                pygame.draw.rect(surface, colors['monster'], to_screen_rect(point))

    pygame.display.update()


#
# Game logic
#

grid = {
    'x': 30,
    'y': 30
}


def new_game():
    global monster, obstacles, player

    cells = grid['x'] * grid['y']
    obstacles = []
    good = False

    def rand_pos():
        p = None
        while not p or Point(p) in obstacles:
            p = (random.randrange(grid['x']), random.randrange(grid['y']))
        return p

    good = False
    while not good:
        for i in range(random.randint(cells / 20, cells / 4)):
            p = rand_pos()
            obstacles.append(Point(p))

        player = Point(rand_pos())
        monster = Point(rand_pos())

        if heuristic_cost_estimate(monster.tuple, player.tuple) > 15 \
                and a_star(monster.tuple, player.tuple):
                    good = True


if __name__ == '__main__':

    pygame.init()
    pygame.display.set_caption('A*dventure Time')
    pygame.key.set_repeat(500, 10)

    surface = pygame.display.set_mode((640, 480))

    new_game()

    while True:

        monster_path = a_star(monster.tuple, player.tuple)
        if monster_path:
            if len(monster_path) > 1:
                monster = Point(*monster_path[1])

            if monster == player:
                new_game()

        paint()

        proceed = False
        while not proceed:

            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()

                if event.type == KEYDOWN:
                    shift = {
                        K_LEFT: (-1, 0),
                        K_RIGHT: (1, 0),
                        K_UP: (0, -1),
                        K_DOWN: (0, 1)
                    }.get(event.key, None)

                    if shift:
                        desired = player + shift
                        if desired not in obstacles \
                            and desired.x >= 0 and desired.y >= 0 \
                                and desired.x < grid['x'] and desired.y < grid['y']:
                            player += shift
                            proceed = True

                    else:
                        key = pygame.key.name(event.key)

                        if key == 'r':
                            new_game()
                            proceed = True
