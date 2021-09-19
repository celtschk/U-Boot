import pygame
import random

# python files from this game
import settings
import resources
from objects import MovingObject, Animation

def get_value(value_or_range):
    if type(value_or_range) is dict:
        return random.uniform(value_or_range["min"],
                              value_or_range["max"])
    else:
        return value_or_range

class Game:
    "The game"

    # screen dimensions
    width = settings.width
    height = settings.height

    # get limits and probabilities for objects
    max_objects = {}
    spawn_rates = {}
    for obj_type, obj in settings.objects.items():
        if "max_count" in obj:
            max_objects[obj_type] = obj["max_count"]
        if "spawn_rate" in obj:
            spawn_rates[obj_type] = obj["spawn_rate"]

    # minimal submarime depth
    min_depth_fraction = settings.objects["submarine"]["depth"]["min"]

    # maximal submarine depth
    max_depth_fraction = settings.objects["submarine"]["depth"]["max"]

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
        self.ship = self.create_moving_object("ship")

        # a list of all objects, initially there's only a ship
        self.objects = [self.ship]

        self.score = 0

        self.font = pygame.font.SysFont(settings.font["name"],
                                        settings.font["size"])

        # music
        resources.load_music("background")

        # sound effects
        self.explosion_sound = resources.get_sound("explosion")

        # game state display
        self.game_state_display = [
            resources.MessageData(
                message = "Bombs available: {available_bombs}",
                position = (20, 20),
                colour = self.c_text,
                font = self.font
                ),

            resources.MessageData(
                message = "Bomb cost: {bomb_cost} ",
                position = (20, 50),
                colour = self.c_text,
                font = self.font
                ),

            resources.MessageData(
                message = "Score: {score}",
                position = (20+self.width//2, 20),
                colour = self.c_text,
                font = self.font
                )
            ]

        # message for pause
        self.paused_msg = resources.MessageData(
            message = "--- PAUSED ---",
            position = (self.width//2, self.height//2),
            colour = self.c_pause,
            font = self.font,
            origin = (0.5,0.5))
            
         # The game is initially not paused
        self.paused = False

    def create_moving_object(self, object_type):
        """
        Create a moving object of type object_type
        """
        data = settings.objects[object_type]
        filename = data["filename"]
        origin = data["origin"]

        # y coordinates (1) are actually depths
        cache = {
            (0, "left"): { "pos": 0, "adjustment": origin[0] - 1 },
            (0, "right"): { "pos": self.width, "adjustment": origin[0] },
            (1, "bottom"): { "pos": 1, "adjustment": 0 }
            }

        # the ship might not yet exist, therefore only use
        # ship coordinates when actually requested
        def get_boundary_data(coordinate, name_or_value):
            if type(name_or_value) == str:
                if not (coordinate, name_or_value) in cache:
                    if name_or_value == "ship":
                        shippos = self.ship.get_position()
                        cache[0,"ship"] = {
                            "pos": shippos[0],
                            "adjustment": 0
                            }
                        cache[1,"ship"] = {
                            "pos": 0,
                            "adjustment": 0
                            }
                    else:
                        cache[coordinate, name_or_value] = {
                            "pos": get_value(data[name_or_value]),
                            "adjustment": 0
                            }
            else:
                return { "pos": name_or_value, "adjustment": 0 }

            return cache[coordinate, name_or_value]

        movement = data["movement"]

        def y_from_depth(depth):
            return depth*(self.height - self.waterline) + self.waterline

        start_x = get_boundary_data(0, movement["start"][0])
        start_depth = get_boundary_data(1, movement["start"][1])

        start = (start_x["pos"], y_from_depth(start_depth["pos"]))
        start_adjustment = (start_x["adjustment"], start_depth["adjustment"])

        end_x = get_boundary_data(0, movement["end"][0])
        end_depth = get_boundary_data(1, movement["end"][1])

        end = (end_x["pos"], y_from_depth(end_depth["pos"]))
        end_adjustment = (end_x["adjustment"], end_depth["adjustment"])

        return MovingObject(
            object_type,
            filename,
            start = start,
            adjust_start = start_adjustment,
            end = end,
            adjust_end = end_adjustment,
            speed = get_value(movement["speed"]),
            origin = origin,
            repeat = movement["repeat"])

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

        for obj in self.get_objects(Animation, inverse=True):
            obj.draw_on(self.screen)

        # animations are always on top
        for anim in self.get_objects(Animation):
            anim.draw_on(self.screen)

        displaydata = {
            "available_bombs": self.get_available_bombs(),
            "bomb_cost": self.get_bomb_cost(),
            "score": self.score
            }

        for message in self.game_state_display:
            message.write(self.screen, displaydata)

        # show message if game is paused:
        if self.paused:
            self.paused_msg.write(self.screen)

        pygame.display.flip()

    def get_objects(self, object_type, inverse = False):
        if type(object_type) is str:
            condition = lambda obj: (obj.object_type == object_type) != inverse
        elif type(object_type) is type:
            condition = lambda obj: (type(obj) is object_type) != inverse
        return [obj for obj in self.objects if condition(obj)]

    def get_bomb_cost(self, count=1):
        "Returns the score cost of dropping another count bombs"
        l = len(self.get_objects("bomb"))
        return sum((l+k)**2 for k in range(count))

    def get_available_bombs(self):
        "Returns the maximum number of extra bombs that can be thrown"
        available_bombs = self.max_objects["bomb"] - len(self.get_objects("bomb"))
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

                newbomb = self.create_moving_object("bomb")
                self.objects.append(newbomb)

    def spawn_objects(self):
        "Possibly spawn new spawnable objects"
        for obj_type, rate in self.spawn_rates.items():
            if len(self.get_objects(obj_type)) < Game.max_objects[obj_type]:
                if random.uniform(0,1) < rate/self.fps:
                    newsub = self.create_moving_object(obj_type)
                    self.objects.append(newsub)

    def handle_hits(self):
        """
        Check if any bomb hit any submarine, and if so, remove both
        and update score
        """
        for sub in self.get_objects("submarine"):
            for bomb in self.get_objects("bomb"):
                bb_sub = sub.get_bounding_box()
                bb_bomb = bomb.get_bounding_box()
                if bb_sub.colliderect(bb_bomb):
                    subpos = sub.get_position()
                    self.score += int((subpos[1] - self.waterline) /
                                      self.height * 20 + 0.5)
                    self.explosion_sound.play()
                    explode = settings.animations["explosion"]
                    self.objects.append(
                        Animation(object_type = "explosion",
                                  path_scheme = explode["images"],
                                  frame_count = explode["frame_count"],
                                  fps = explode["fps"],
                                  position = bomb.get_position()))
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

        # move all objects and advance all animations
        for obj in self.objects:
            obj.update(1/self.fps)

        # handle bombs hitting submarines
        self.handle_hits()

        # remove inactive objects and animations
        self.objects = [obj for obj in self.objects if obj.is_active()]

        # spawn new spawnable objects at random
        self.spawn_objects()

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
