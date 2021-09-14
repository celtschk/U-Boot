import pygame
import random

import settings

# get the colour names from X11's rgb.txt
rgbvalues = {}
with open("rgb.txt", "r") as rgbfile:
    for line in rgbfile:
        if line == "" or line[0] == '!':
            continue
        rgb, name = line.split('\t\t')
        rgbvalues[name.strip()] = tuple(int(value) for value in rgb.split())

class MovingObject:
    "This class represents any moving object in the game."

    # A storage for images, so that they aren't loaded each time
    # another object uses the same image is
    imagestore = {}

    def __init__(self, path, start, end, speed,
                 origin = (0,0), repeat=False,
                 adjust_start = (0,0), adjust_end = (0,0)):
        """
        Create a new moving object.

        Mandatory Arguments:
          path:          the file path to the image to display
          start:         the pixel at which the movement starts
          end:           the pixel at which the movement ends
          speed:         the fraction of the distance to move per second

        Optional arguments:
          origin:        which point of the image to use for placement
          repeat:        whether to repeat the movement
          adjust_start:  adjustment of the start position
          adjust_end:    adjustment of the end position

        All coordinates in the optional arguments are in units of
        image width or image height, as opposed to pixel coordinates
        as used in the mandatory arguments. For example, if the image
        has width of 5 pixels and height of 4 pixels, the arguments

           start = (5,5), adjust_start = (-1,0.5)

        will result in an actual starting point of (0,7).
        """
        if not path in MovingObject.imagestore:
            MovingObject.imagestore[path] =\
                 pygame.image.load(path).convert_alpha()
        self.image = MovingObject.imagestore[path]

        width = self.image.get_width()

        self.start = tuple(s + width * a for s,a in zip(start,adjust_start))
        self.end = tuple(e + width * a for e,a in zip(end,adjust_end))

        self.repeat = repeat

        self.pos = self.start

        self.speed = speed
        self.dist = 0

        self.disp = (-self.image.get_width()*origin[0],
                     -self.image.get_height()*origin[1])

        self.active = True

    def move(self, seconds):
        """
        Move the object.

        Arguments:
          seconds: The number of seconds passed.
        """
        if self.active:
            self.dist += self.speed * seconds
            if self.dist > 1:
                if self.repeat:
                    self.dist = 0
                else:
                    self.active = False

    def get_position(self, displace = False):
        """
        Return the current position of the object.

        Arguments:
          displace: If True, give the position of the upper left corner.
                    If False (default), give the position of the origin.

        Return value: The pixel coordinates of the object.
        """
        return tuple(int(s + self.dist*(e-s) + (d if displace else 0))
                     for e, s, d in zip(self.end, self.start, self.disp))

    def draw_on(self, surface):
        """
        Draw the object on a pygame surface, if active
        """
        if self.is_active():
            surface.blit(self.image, self.get_position(True))

    def is_active(self):
        """
        Returns true if the object is active, False otherwise
        """
        return self.active

    def deactivate(self):
        """
        Set the object's state to not active.
        """
        self.active = False

    def get_bounding_box(self):
        """
        Get the bounding box of the objects representation on screen
        """
        pos = self.get_position()
        return pygame.Rect(pos,
                           (self.image.get_width(),
                            self.image.get_height()))

class Game:
    "The game"

    # maximal number of simultaneous submarines
    max_subs = settings.limits["submarine"]

    #maximal number of simultaneous bombs
    max_bombs = settings.limits["bomb"]

    # background (sky) colour
    c_background = rgbvalues[settings.colours["sky"]]

    # water colour
    c_water = rgbvalues[settings.colours["water"]]

    # colour of the score display
    c_score = rgbvalues[settings.colours["text"]]

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
        self.fps = settings.fps

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
        text = self.font.render(string, True, self.c_score)
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
                if event.key == pygame.K_q:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if event.key == pygame.K_DOWN:
                    self.drop_bomb()

    def update_state(self):
        """
        Update the state of the game
        """
        # move all objects
        self.ship.move(1/self.fps)

        for sub in self.submarines:
            sub.move(1/self.fps)

        for bomb in self.bombs:
            bomb.move(1/self.fps)

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

def main():
    game = Game(settings.width, settings.height)
    game.run()

if __name__=='__main__':
    main()
