import pygame
import random

# python files from this game
import settings
from colours import get_colour
from objects import MovingObject

class Game:
    "The game"

    # maximal number of simultaneous submarines
    max_subs = settings.limits["submarine"]

    #maximal number of simultaneous bombs
    max_bombs = settings.limits["bomb"]

    # background (sky) colour
    c_background = get_colour("sky")

    # water colour
    c_water = get_colour("water")

    # colour of the score display
    c_text = get_colour("text")

    # the game's frames per second
    fps = settings.fps

    def __init__(self, width, height):
        """
        Initialize the game with screen dimensions width x height
        """
        self.width = width
        self.height = height
        self.waterline = int(settings.sky_fraction * height)

        self.running = False

        pygame.init()
        self.screen = pygame.display.set_mode((width,height))
        pygame.display.set_caption(settings.game_name)
        pygame.mouse.set_visible(False)
        pygame.key.set_repeat(0)

        self.clock = pygame.time.Clock()

        # create the ship
        self.ship = MovingObject(settings.image_files["ship"],
                                 start = (0, self.waterline),
                                 adjust_start = (-0.5,0),
                                 end = (self.width, self.waterline),
                                 adjust_end = (0.5,0),
                                 speed = settings.speeds["ship"],
                                 origin = (0.5,1),
                                 repeat = True)

        # initially there are no submarines nor bombs
        self.submarines = []
        self.bombs = []

        # spawn a submarine on average every 3 seconds
        self.p_spawn = 1/(3*self.fps)

        self.score = 0

        self.font = pygame.font.SysFont(settings.font["name"],
                                        settings.font["size"])

    def write_string(self, string, position):
        """
        Write a string at a given position on screen
        """
        text = self.font.render(string, True, self.c_text)
        self.screen.blit(text, position)

    def draw(self):
        """
        Draw the game graphics
        """
        self.screen.fill(Game.c_background)
        pygame.draw.rect(self.screen, Game.c_water,
                         (0,
                          self.waterline,
                          self.width,
                          self.height - self.waterline))

        self.ship.draw_on(self.screen)

        for sub in self.submarines:
            sub.draw_on(self.screen)

        for bomb in self.bombs:
            bomb.draw_on(self.screen)

        self.write_string("Bombs available: "
                          + str(self.get_available_bombs()),
                          (20, 20))

        self.write_string("Bomb cost: " + str(self.get_bomb_cost()),
                          (20,50))

        self.write_string("Score: " + str(self.score),
                          (20+self.width//2, 20))
        
        pygame.display.flip()

    def get_bomb_cost(self, count=1):
        "Returns the score cost of dropping another count bombs"
        l = len(self.bombs)
        return sum((l+k)**2 for k in range(count))

    def get_available_bombs(self):
        "Returns the maximum number of extra bombs that can be thrown"
        available_bombs = self.max_bombs - len(self.bombs)
        while self.get_bomb_cost(available_bombs) > self.score:
               available_bombs -= 1
        return available_bombs

    def drop_bomb(self):
        "Drop a bomb, if possible"

        # don't drop a new bomb if there already exist a naximal
        # number of them, or the score would go negative
        if self.get_available_bombs() > 0:
            ship_pos = self.ship.get_position();

            # don't drop a bomb off-screen
            if ship_pos[0] > 0 and ship_pos[0] < self.width:
                # the score must be updated before adding the new bomb
                # because adding the bomb changes the cost
                self.score -= self.get_bomb_cost();

                newbomb = MovingObject(settings.image_files["bomb"],
                                       start = ship_pos,
                                       end = (ship_pos[0], self.height),
                                       speed = settings.speeds["bomb"],
                                       origin = (0.5, 0))
                self.bombs.append(newbomb)

    def spawn_submarine(self):
        "Possibly spawn a new submarine"
        if random.uniform(0,1) < self.p_spawn:
            ship_speed = self.ship.speed

            total_depth = self.height - self.waterline
            min_depth = 0.1*total_depth + self.waterline
            max_depth = self.height - 20
            sub_depth = random.uniform(min_depth, max_depth)
            sub_speed = random.uniform(settings.speeds["submarine_min"],
                                       settings.speeds["submarine_max"])

            newsub = MovingObject(settings.image_files["submarine"],
                                  start = (self.width, sub_depth),
                                  end = (0, sub_depth),
                                  adjust_end = (-1,0),
                                  speed = sub_speed)
            
            self.submarines.append(newsub)                  

    def handle_hits(self):
        """
        Check if any bomb hit any submarine, and if so, remove both
        and update score
        """
        for sub in self.submarines:
            for bomb in self.bombs:
                bb_sub = sub.get_bounding_box()
                bb_bomb = bomb.get_bounding_box()
                if bb_sub.colliderect(bb_bomb):
                    subpos = sub.get_position()
                    self.score += int((subpos[1] - self.waterline) /
                                      self.height * 20 + 0.5)
                    sub.deactivate()
                    bomb.deactivate()

    def handle_events(self):
        """
        Handle all events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # Down arrow drops a bomb
                if event.key == pygame.K_DOWN:
                    self.drop_bomb()

                # F toggles fullscreen display
                elif (event.key == pygame.K_f):
                    size = (self.width, self.height)
                    if self.screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode(size)
                    else:
                        pygame.display.set_mode(size, pygame.FULLSCREEN)

                # Q quits the game
                elif event.key == pygame.K_q:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        
    def update_state(self):
        """
        Update the state of the game
        """
        # move all objects
        for sub in [self.ship] + self.submarines + self.bombs:
            sub.move(1/self.fps)

        # handle bombs hitting submarines
        self.handle_hits()

        # remove inactive objects
        self.submarines = [sub for sub in self.submarines if sub.is_active()]
        self.bombs = [bomb for bomb in self.bombs if bomb.is_active()]

        # spawn new submarines at random
        if len(self.submarines) < Game.max_subs:
            self.spawn_submarine()

    def run(self):
        """
        Run the game
        """
        self.running = True
        while self.running:
            self.draw()
            self.clock.tick(60)
            self.handle_events()
            self.update_state()

if __name__=='__main__':
    Game(settings.width, settings.height).run()
