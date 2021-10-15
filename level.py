import pygame
import shelve

import settings
import resources
from gamedisplay import GameDisplay
from objects import MovingObject, Animation


# Currently there's only one game level. Nevertheless, it makes sense to
# separate out the class
class Level(GameDisplay):
    "A game level"

    def __init__(self, game, old_state = None):
        super().__init__(game)

        self.width = game.screen.get_width()
        self.height = game.screen.get_height()

        self.waterline = int(settings.sky_fraction * self.height)

        if old_state:
            self.game_objects = old_state["objects"]
            self.ship = self.game_objects["ship"]["list"][0]
            self.spawnables = old_state["spawnables"]
        else:
            # objects dictonary
            self.game_objects = {}

            # set of spawnable object types
            self.spawnables = set()

            # get limits and probabilities for objects
            for obj_type, obj in settings.objects.items():
                # record object info in objects dictionary
                object_info = self.game_objects[obj_type] = { "list": [] }

                if "max_count" in obj:
                    # initially, none of those objects exis
                    object_info["max_count"] = obj["max_count"]

                if "spawn_rate" in obj:
                    object_info["spawn_rate"] = obj["spawn_rate"]
                    self.spawnables.add(obj_type)

            # create the ship
            self.ship = self.create_moving_object("ship")
            self.game_objects["ship"] = { "list": [self.ship] }

            # setup storage for animations
            for animation_type in settings.animations:
                self.game_objects[animation_type] = { "list": [] }

        # background (sky) colour
        self.c_background = resources.get_colour("sky")

        # water colour
        self.c_water = resources.get_colour("water")

        # colour of the game state display
        self.c_text = resources.get_colour("text")

        # colour of the pause text display
        self.c_pause = resources.get_colour("pause")

        # The game is initially not paused
        self.paused = False

        self.game_state_display = [
            resources.MessageData(
                message = "Bombs available: {available_bombs}",
                position = pygame.Vector2(20, 20),
                colour = self.c_text,
                font = self.game.font
                ),

            resources.MessageData(
                message = "Bomb cost: {bomb_cost} ",
                position = pygame.Vector2(20, 50),
                colour = self.c_text,
                font = self.game.font
                ),

            resources.MessageData(
                message = "Score: {score}",
                position = pygame.Vector2(20+self.width//2, 20),
                colour = self.c_text,
                font = self.game.font
                )
            ]

        # message for pause
        self.paused_msg = resources.MessageData(
            message = "--- PAUSED ---",
            position = pygame.Vector2(self.width//2, self.height//2),
            colour = self.c_pause,
            font = self.game.font,
            origin = pygame.Vector2(0.5,0.5))

        # sound effects
        self.explosion_sound = resources.get_sound("explosion")


    def create_moving_object(self, object_type):
        """
        Create a moving object of type object_type
        """
        data = settings.objects[object_type]
        filename = data["filename"]
        origin = pygame.Vector2(data["origin"])

        movement = data["movement"]

        start = movement["start"]
        if start[0] == "left":
            start_x = 0
            start_adjustment = pygame.Vector2(origin[0] - 1, 0)
        elif start[0] == "right":
            start_x = self.width
            start_adjustment = pygame.Vector2(origin[0], 0)
        else:
            if start[0] == "ship":
                start_x = self.ship.get_position()[0]
            elif isinstance(start[0],str):
                start_x = resources.get_value(data[start[0]])
            else:
                start_x = start[0]
            start_adjustment = pygame.Vector2(0, 0)

        if isinstance(start[1], str):
            if start[1] == "ship":
                start_depth = 0
            else:
                start_depth = resources.get_value(data[start[1]])
        else:
            start_depth = start[1]

        def y_from_depth(depth):
            return depth*(self.height - self.waterline) + self.waterline

        start = pygame.Vector2(start_x, y_from_depth(start_depth))

        speed = resources.get_value(movement["speed"])
        direction = movement["direction"]

        return MovingObject(
            filename,
            start = start,
            adjust_start = start_adjustment,
            movement_region = self.game.screen.get_rect(),
            velocity = pygame.Vector2(speed * direction[0] * self.width,
                                      speed * direction[1] * self.height),
            origin = origin,
            repeat = movement["repeat"])


    def draw(self):
        """
        Draw the game graphics
        """
        screen = self.game.screen
        screen.fill(self.c_background)
        pygame.draw.rect(screen, self.c_water,
                         (0,
                          self.waterline,
                          self.width,
                          self.height - self.waterline))

        for obj_data in self.game_objects.values():
            for obj in obj_data["list"]:
                obj.draw_on(screen)

        displaydata = {
            "available_bombs": self.get_available_bombs(),
            "bomb_cost": self.get_bomb_cost(),
            "score": self.game.score
            }

        for message in self.game_state_display:
            message.write(screen, displaydata)

        # show message if game is paused:
        if self.paused:
            self.paused_msg.write(screen)

        pygame.display.flip()


    def get_bomb_cost(self, count=1):
        "Returns the score cost of dropping another count bombs"
        l = len(self.game_objects["bomb"]["list"])
        return sum((l+k)**2 for k in range(count))


    def get_available_bombs(self):
        "Returns the maximum number of extra bombs that can be thrown"

        max_bombs = self.game_objects["bomb"]["max_count"]
        existing_bombs = len(self.game_objects["bomb"]["list"])

        available_bombs = max_bombs - existing_bombs

        while self.get_bomb_cost(available_bombs) > self.game.score:
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
                self.game.score -= self.get_bomb_cost();

                newbomb = self.create_moving_object("bomb")
                self.game_objects["bomb"]["list"].append(newbomb)


    def spawn_objects(self):
        "Possibly spawn new spawnable objects"
        for obj_type in self.spawnables:
            max_objects = self.game_objects[obj_type]["max_count"]
            existing_objects = len(self.game_objects[obj_type]["list"])
            rate = self.game_objects[obj_type]["spawn_rate"]

            if existing_objects < max_objects:
                if resources.randomly_true(rate/self.game.fps):
                    newsub = self.create_moving_object(obj_type)
                    self.game_objects[obj_type]["list"].append(newsub)


    def create_animation(self, animation_type, position):
        """
        Create an animation of given type at a specific position.
        """
        animation = settings.animations[animation_type]
        self.game_objects[animation_type]["list"].append(
            Animation(path_scheme = animation["images"],
                      frame_count = animation["frame_count"],
                      fps = animation["fps"],
                      position = position))


    def handle_hits(self):
        """
        Check if any bomb hit any submarine, and if so, remove both
        and update score
        """
        for sub in self.game_objects["submarine"]["list"]:
            for bomb in self.game_objects["bomb"]["list"]:
                bb_sub = sub.get_bounding_box()
                bb_bomb = bomb.get_bounding_box()
                if bb_sub.colliderect(bb_bomb):
                    subpos = sub.get_position()
                    self.game.score += int((subpos[1] - self.waterline) /
                                           self.height * 20 + 0.5)
                    self.explosion_sound.play()
                    self.create_animation("explosion", bomb.get_position())
                    sub.deactivate()
                    bomb.deactivate()


    def handle_event(self, event):
        """
        Handle an event
        """
        if super().handle_event(event):
            return True

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
                self.game.toggle_fullscreen()

            # Q quits the game and returns to the menu
            elif event.key == pygame.K_q:
                self.quit()

            # S shelves this level
            elif event.key == pygame.K_s:
                save_file = resources.get_save_file()
                save_state = {
                    "objects": self.game_objects,
                    "spawnables": self.spawnables,
                    "score": self.game.score
                    }
                with shelve.open(str(save_file), "c") as savefile:
                    savefile["game"] = save_state
                    self.quit()


    def update_state(self):
        """
        Update the state of the game
        """
        # if the game is paused, do nothing
        if self.paused:
            return

        # move all objects and advance all animations
        for obj_data in self.game_objects.values():
            for obj in obj_data["list"]:
                obj.update(self.game.clock.get_time()/1000)

        # handle bombs hitting submarines
        self.handle_hits()

        # remove inactive objects and animations
        for object in self.game_objects.values():
            object["list"] = [obj for obj in object["list"] if obj.is_active()]

        # spawn new spawnable objects at random
        self.spawn_objects()
