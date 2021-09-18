import pygame
import random
from dataclasses import dataclass, asdict

# python files from this game
import settings
import resources
from objects import MovingObject

@dataclass
class DisplayData:
    available_bombs: int
    bomb_cost: int
    score: int

@dataclass
class MessageData:
    message: str
    position: tuple
    colour: tuple
    font: pygame.font.SysFont
    origin: tuple = (0, 0)

    def write(self, screen, data = None):
        """
        Write the message at a given position on screen
        """
        if data is None:
            string = self.message
        else:
            string = self.message.format(**asdict(data))

        text = self.font.render(string, True, self.colour)
        textsize = (text.get_width(), text.get_height())
        position = tuple(int(pos - size * orig)
                         for pos, size, orig
                         in zip(self.position,
                                textsize,
                                self.origin))

        screen.blit(text, position)

class Game:
    "The game"

    # screen dimensions
    width = settings.width
    height = settings.height

    # maximal number of simultaneous submarines
    max_subs = settings.limits["submarine"]

    # maximal number of simultaneous bombs
    max_bombs = settings.limits["bomb"]

    # background (sky) colour
    c_background = resources.get_colour("sky")

    # water colour
    c_water = resources.get_colour("water")

    # colour of the game state display
    c_text = resources.get_colour("text")

    # colour of the pause text display
    c_pause = resources.get_colour("pause")

    # the game's frames per second
    fps = settings.fps

    def __init__(self):
        """
        Initialize the game with screen dimensions width x height
        """
        self.waterline = int(settings.sky_fraction * self.height)

        self.running = False

        pygame.init()
        self.screen = pygame.display.set_mode((self.width,self.height))
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
        self.p_spawn = settings.spawn_rates["submarine"]/self.fps

        self.score = 0

        self.font = pygame.font.SysFont(settings.font["name"],
                                        settings.font["size"])

        # music
        resources.load_music("background")

        # sound effects
        self.explosion_sound = resources.get_sound("explosion")

        # game state display
        self.game_state_display = [
            MessageData(
                message = "Bombs available: {available_bombs}",
                position = (20, 20),
                colour = self.c_text,
                font = self.font
                ),

            MessageData(
                message = "Bomb cost: {bomb_cost} ",
                position = (20, 50),
                colour = self.c_text,
                font = self.font
                ),

            MessageData(
                message = "Score: {score}",
                position = (20+self.width//2, 20),
                colour = self.c_text,
                font = self.font
                )
            ]

        # message for pause
        self.paused_msg = MessageData(
            message = "--- PAUSED ---",
            position = (self.width//2, self.height//2),
            colour = self.c_pause,
            font = self.font,
            origin = (0.5,0.5))
            
         # The game is initially not paused
        self.paused = False

    def moving_objects(self):
        """
        A generator to iterate over all moving objects
        """
        yield self.ship

        for sub in self.submarines:
            yield sub

        for bomb in self.bombs:
            yield bomb

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

        for obj in self.moving_objects():
            obj.draw_on(self.screen)

        displaydata = DisplayData(
            available_bombs = self.get_available_bombs(),
            bomb_cost = self.get_bomb_cost(),
            score = self.score
            )

        for message in self.game_state_display:
            message.write(self.screen, displaydata)

        # show message if game is paused:
        if self.paused:
            self.paused_msg.write(self.screen)

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
                    self.explosion_sound.play()

    def handle_events(self):
        """
        Handle all events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # Game actions are only processed if the game is not paused
                if not self.paused:
                    # Down arrow drops a bomb
                    if event.key == pygame.K_DOWN:
                        self.drop_bomb()

                # Other keys are always processed

                # P or Pause pauses the game
                if event.key in {pygame.K_p, pygame.K_PAUSE}:
                    if self.paused:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                    self.paused = not self.paused
                # F toggles fullscreen display
                elif event.key == pygame.K_f:
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
        # if the game is paused, do nothing
        if self.paused:
            return

        # move all objects
        for sub in self.moving_objects():
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
        # start the backkground music in infinte loop
        pygame.mixer.music.play(-1)
        
        self.running = True
        while self.running:
            self.draw()
            self.clock.tick(60)
            self.handle_events()
            self.update_state()

        # stop the background music
        pygame.mixer.music.stop()

if __name__=='__main__':
    Game().run()
