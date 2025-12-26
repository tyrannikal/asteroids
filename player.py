import pygame
from constants import PLAYER_RADIUS, LINE_WIDTH
from circleshape import CircleShape

class Player(CircleShape):
    def __init__(self, x, y):
        if(not (type(x) == float and type(y) == float)):
            print(f"{self.__init__.__name__}: x and y must be integers")
        if(not (type(PLAYER_RADIUS) == int and PLAYER_RADIUS > 0)):
            print(f"{self.__init__.__name__}: PLAYER_RADIUS must be an int > 0")

        player = super().__init__(x, y, PLAYER_RADIUS)
        if(not (type(player) == type(None))):
            print(f"{self.__init__.__name__}: super().__init__ must return None")

        self.rotation = 0


    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        if(not (type(forward) == pygame.Vector2)):
            print(f"{self.triangle.__name__}: forward: pygame.Vector2.rotate must return a Vector2")

        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        if(not (type(right) == pygame.Vector2)):
            print(f"{self.triangle.__name__}: right: pygame.Vector2.rotate must return a Vector2")

        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]


    def draw(self, screen):
        if(not (type(screen) == pygame.surface.Surface)):
            print(f"{self.draw.__name__}: screen must be of type pygame.surface.Surface")

        get_player_triangle = self.triangle()
        if(not (type(get_player_triangle) == list and len(get_player_triangle) == 3
                and type(get_player_triangle[0]) == pygame.math.Vector2
                and type(get_player_triangle[1]) == pygame.math.Vector2
                and type(get_player_triangle[2]) == pygame.math.Vector2)):
            print(f"{self.draw.__name__}: self.triangle must return a list of 3 integers")

        if(not (type(LINE_WIDTH) == int and LINE_WIDTH > 0)):
            print(f"{self.draw.__name__}: LINE_WIDTH must be an int > 0")
        draw_player = pygame.draw.polygon(screen, "white", get_player_triangle, LINE_WIDTH)

