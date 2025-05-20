import pygame
import random

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PHEROMONE_A = (255, 0, 0, 100)  # red, semi-transparent
PHEROMONE_B = (0, 0, 255, 100)  # blue, semi-transparent
ANT_COLORS = {1: (200, 0, 0), 2: (0, 0, 200)}
CELL_SIZE = 6  # pixels
FPS = 60


class Cell:
    def __init__(self):
        self.color = 0  # 0 = white, 1 = black
        self.pheromone_owner = None
        self.pheromone_age = 0

class Grid:
    def __init__(self, width, height, pheromone_lifetime=5):
        self.width = width
        self.height = height
        self.pheromone_lifetime = pheromone_lifetime
        self.cells = [[Cell() for _ in range(height)] for _ in range(width)]

    def get_cell(self, x, y):
        return self.cells[x % self.width][y % self.height]

    def update_pheromones(self):
        for row in self.cells:
            for cell in row:
                if cell.pheromone_owner is not None:
                    cell.pheromone_age += 1
                    if cell.pheromone_age > self.pheromone_lifetime:
                        cell.pheromone_owner = None
                        cell.pheromone_age = 0

# Ant definition
class Ant:
    def __init__(self, id, x, y, direction, P_self=0.8, P_other=0.2):
        self.id = id
        self.x = x
        self.y = y
        self.dir = direction
        self.P_self = P_self
        self.P_other = P_other

    def turn_right(self):
        self.dir = (self.dir + 1) % 4

    def turn_left(self):
        self.dir = (self.dir - 1) % 4

    def move_forward(self, grid):
        if self.dir == 0:
            self.y -= 1
        elif self.dir == 1:
            self.x += 1
        elif self.dir == 2:
            self.y += 1
        else:
            self.x -= 1
        self.x %= grid.width
        self.y %= grid.height

    def step(self, grid, other_ant):
        cell = grid.get_cell(self.x, self.y)
        # Determine base probability
        if cell.pheromone_owner == self.id:
            base_prob = self.P_self
        elif cell.pheromone_owner == other_ant.id:
            base_prob = self.P_other
        else:
            base_prob = None
        # Compute action
        if base_prob is not None:
            decay = max(1 - (cell.pheromone_age / grid.pheromone_lifetime), 0)
            prob_straight = base_prob * decay
            go_straight = (random.random() < prob_straight)
        else:
            go_straight = False
        # Turn or not
        if not go_straight:
            if cell.color == 0:
                self.turn_right()
            else:
                self.turn_left()
        # Flip color
        cell.color = 1 - cell.color
        # Drop pheromone
        cell.pheromone_owner = self.id
        cell.pheromone_age = 0
        # Move
        self.move_forward(grid)

# Simulation with Pygame
class Simulation:
    def __init__(self, width, height):
        pygame.init()
        self.grid = Grid(width, height)
        self.ants = [
            Ant(1, width // 4, height // 2, 1),
            Ant(2, 3 * width // 4, height // 2, 3)
        ]
        self.screen = pygame.display.set_mode((width * CELL_SIZE, height * CELL_SIZE))
        pygame.display.set_caption("Two-Ant Langton's Ant Simulation")
        self.clock = pygame.time.Clock()
        self.running = True

    def draw(self):
        # Draw grid cells
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell = self.grid.cells[x][y]
                color = WHITE if cell.color == 0 else BLACK
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                # Pheromone overlay
                if cell.pheromone_owner:
                    overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    if cell.pheromone_owner == 1:
                        overlay.fill(PHEROMONE_A)
                    else:
                        overlay.fill(PHEROMONE_B)
                    self.screen.blit(overlay, rect.topleft)
        # Draw ants
        for ant in self.ants:
            ant_rect = pygame.Rect(ant.x * CELL_SIZE, ant.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, ANT_COLORS[ant.id], ant_rect)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            # Simulation step
            self.ants[0].step(self.grid, self.ants[1])
            self.ants[1].step(self.grid, self.ants[0])
            self.grid.update_pheromones()
            # Drawing
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    sim = Simulation(width=100, height=100)
    sim.run()
