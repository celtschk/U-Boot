import pygame
from copy import deepcopy

import settings
import resources
from gamedisplay import GameDisplay
from objects import MovingObject, Animation


# Currently there's only one game level. Nevertheless, it makes sense to
# separate out the class
class Level(GameDisplay):
    "A game level"
    # Level specific exit values
    LEVEL_CLEARED = GameDisplay.Status()
    LEVEL_FAILED  = GameDisplay.Status()
    LEVEL_SAVE = GameDisplay.Status()

    @staticmethod
    def initial_state(old_state = {}):
        """
        Generates the initial state of a level.

        The optional argument old_state is the state the previous
        level ended with. If omitted or empty, the oinitial state of
        the first level is generated.
        """
        level_number = old_state.get("level_number", 0) + 1

        object_settings = deepcopy(settings.objects)
        if level_number in settings.level_updates:
            resources.recursive_update(
                object_settings,
                settings.level_updates[level_number])

        return {
            "level_number": level_number,
            "object_settings": object_settings,
            "objects": {},
            "spawnables": set(),
            "score": old_state.get("score", 0)
            }


    def __init__(self, game, old_state):
        """
        Initializes a level based on the passed state
        """
        super().__init__(game)

        self.width = game.screen.get_width()
        self.height = game.screen.get_height()

        self.waterline = int(settings.sky_fraction * self.height)

        self.score = old_state["score"]
        self.level_number = old_state["level_number"]
        self.object_settings = old_state["object_settings"]
        self.game_objects = old_state["objects"]
        self.spawnables = old_state["spawnables"]

        self.score_frame_countdown = self.score_frames = settings.score_frames
        self.level_display_frames = settings.level_display_frames
        self.final_display_frames = 0

        if self.game_objects:
            self.ship = self.game_objects["ship"]["list"][0]
        else:
            # get limits and probabilities for objects
            for obj_type, obj in self.object_settings.items():
                # record object info in objects dictionary
                object_info = self.game_objects[obj_type] = { "list": [] }

                if "max_count" in obj:
                    # initially, none of those objects exis
                    object_info["max_count"] = obj["max_count"]

                if "spawn_rate" in obj:
                    object_info["spawn_rate"] = obj["spawn_rate"]
                    self.spawnables.add(obj_type)

                if "total_count" in obj:
                    object_info["remaining"] = obj["total_count"]

                if "to_destroy" in obj:
                    object_info["to_destroy"] = obj["to_destroy"]

            # create the ship
            self.ship = self.create_moving_object("ship")
            self.game_objects["ship"] = { "list": [self.ship] }

            # setup storage for animations
            for animation_type in settings.animations:
                self.game_objects[animation_type] = { "list": [] }

        # set displayed score to game score
        # (separate to allow score animation)
        self.displayed_score = self.score
        
        # background (sky) colour
        self.c_background = resources.get_colour("sky")

        # water colour
        self.c_water = resources.get_colour("water")

        # colours of the game state display
        self.c_text = resources.get_colour("text")
        self.c_no_bombs = resources.get_colour("no bombs")
        self.c_no_destroy = resources.get_colour("no more subs to destroy")
        self.c_not_enough_subs = resources.get_colour("not enough subs")

        # colour of the pause text display
        self.c_pause = resources.get_colour("pause")

        # colour of the level cleared text display
        self.c_cleared = resources.get_colour("cleared")

        # colour of the level failed text display
        self.c_failed = resources.get_colour("failed")

        # The game is initially not paused
        self.paused = False

        def bomb_text_colour(data):
            if data["available_bombs"] > 0:
                return self.c_text
            else:
                return self.c_no_bombs

        def submarine_text_colour(data):
            if data["to_destroy"] == 0:
                return self.c_no_destroy
            elif data["to_destroy"] > data["remaining_subs"]:
                return self.c_not_enough_subs
            else:
                return self.c_text

        self.game_state_display = [
            resources.MessageData(
                message = "Bombs: {remaining_bombs} ({available_bombs} available)",
                position = pygame.Vector2(20, 20),
                colour = bomb_text_colour,
                font = self.game.font
                ),

            resources.MessageData(
                message = "Bomb cost: {bomb_cost} ",
                position = pygame.Vector2(20, 50),
                colour = self.c_text,
                font = self.game.font
                ),

            resources.MessageData(
                message = "Level: {level},  Score: {score}",
                position = pygame.Vector2(20+self.width//2, 20),
                colour = self.c_text,
                font = self.game.font
                ),

            resources.MessageData(
                message = "Remaining submarines: {to_destroy}/{remaining_subs}",
                position = pygame.Vector2(20+self.width//2, 50),
                colour = submarine_text_colour,
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

        # message for cleared level
        self.cleared_msg = resources.MessageData(
            message = "*** LEVEL CLEARED ***",
            position = pygame.Vector2(self.width//2, self.height//2 - 32),
            colour = self.c_cleared,
            font = self.game.font,
            origin = pygame.Vector2(0.5,0.5))

        # message for failed level
        self.failed_msg = resources.MessageData(
            message = "*** LEVEL FAILED ***",
            position = pygame.Vector2(self.width//2, self.height//2 - 32),
            colour = self.c_failed,
            font = self.game.font,
            origin = pygame.Vector2(0.5,0.5))


    def get_state(self):
        """
        Get the current state of the level. The data is used in the
        save file, as well as to pass on data to the next level.
        """
        return {
            "level_number": self.level_number,
            "object_settings": self.object_settings,
            "objects": self.game_objects,
            "spawnables": self.spawnables,
            "score": self.score
            }


    def create_moving_object(self, object_type):
        """
        Create a moving object of type object_type
        """
        data = self.object_settings[object_type]
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
            "remaining_bombs": self.game_objects["bomb"]["remaining"],
            "available_bombs": self.get_available_bombs(),
            "bomb_cost": self.get_bomb_cost(),
            "remaining_subs": self.objects_remaining("submarine"),
            "to_destroy": self.game_objects["submarine"]["to_destroy"],
            "level": self.level_number,
            "score": self.displayed_score
            }

        for message in self.game_state_display:
            message.write(screen, displaydata)

        # show message if game is paused:
        if self.paused:
            self.paused_msg.write(screen)

        # show final message as appropriate:
        if not self.running:
            if self.status == self.LEVEL_CLEARED:
                self.cleared_msg.write(screen)
            elif self.status == self.LEVEL_FAILED:
                self.failed_msg.write(screen)

        pygame.display.flip()


    def get_bomb_cost(self, count=1):
        "Returns the score cost of dropping another count bombs"
        l = len(self.game_objects["bomb"]["list"])
        return sum((l+k)**2 for k in range(count))


    def get_available_bombs(self):
        "Returns the maximum number of extra bombs that can be thrown"

        bomb_info = self.game_objects["bomb"]
        max_bombs = min(bomb_info["max_count"], bomb_info["remaining"])
        existing_bombs = len(bomb_info["list"])

        available_bombs = max_bombs - existing_bombs

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
                self.game_objects["bomb"]["list"].append(newbomb)
                self.game_objects["bomb"]["remaining"] -= 1


    def spawn_objects(self):
        "Possibly spawn new spawnable objects"
        for obj_type in self.spawnables:
            obj_data = self.game_objects[obj_type]
            limited = ("remaining" in obj_data)

            max_objects = obj_data["max_count"]
            if limited and obj_data["remaining"] < max_objects:
                max_objects = obj_data["remaining"]

            existing_objects = len(obj_data["list"])
            rate = obj_data["spawn_rate"]

            if existing_objects < max_objects:
                if resources.randomly_true(rate/self.game.fps):
                    newobj = self.create_moving_object(obj_type)
                    self.game_objects[obj_type]["list"].append(newobj)
                    if limited:
                        obj_data["remaining"] -= 1


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
        Check if any projectile hit any target, and if so, remove both
        and update score
        """
        for obj_pair, info in settings.hit_info.items():
            target_name, projectile_name = obj_pair
            for target in self.game_objects[target_name]["list"]:
                for projectile in self.game_objects[projectile_name]["list"]:
                    bb1 = target.get_bounding_box()
                    bb2 = projectile.get_bounding_box()
                    if bb1.colliderect(bb2):
                        targetpos = target.get_position()
                        if target.is_active() and info["score"]:
                            self.score += int((targetpos[1] - self.waterline) /
                                              self.height * 20 + 0.5)
                        self.play(info["sound"])
                        self.create_animation(info["animation"],
                                              projectile.get_position())
                        target.deactivate()
                        projectile.deactivate()
                        if self.game_objects[target_name]["to_destroy"] > 0:
                            self.game_objects[target_name]["to_destroy"] -= 1;


    def handle_event(self, event):
        """
        Handle an event
        """
        if super().handle_event(event):
            return True

        if event.type == pygame.KEYDOWN:
            # Game actions are only processed if the game is running
            # and not paused
            if self.running and not self.paused:
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

            # Q quits the game and returns to the menu
            elif event.key == pygame.K_q:
                self.quit()

            # S shelves this level
            elif event.key == pygame.K_s:
                self.quit(self.LEVEL_SAVE)


    def objects_remaining(self, obj_type):
        """
        Return True if all objects of the given type have already beem
        generated.
        """
        obj_info = self.game_objects[obj_type];
        return obj_info.get("remaining", 1) + len(obj_info["list"])


    def update_state(self):
        """
        Update the state of the game
        """
        # if the game is paused, do nothing
        if self.paused:
            return

        # move the displayed score towards the actual score
        if self.displayed_score != self.score:
            if self.score_frame_countdown == 0:
                self.score_frame_countdown = self.score_frames
                if self.displayed_score < self.score:
                    self.displayed_score += 1
                elif self.displayed_score > self.score:
                    self.displayed_score -= 1
            else:
                self.score_frame_countdown -= 1

        # if the game is no longer running, decrease the final frame
        # counter if appropriate, advance any remaining animations,
        # and then return immediately (so that game objects no longer
        # move, and score is no longer collected)
        if not self.running:
            if self.final_display_frames > 0:
                self.final_display_frames -=1
            for animation_type in settings.animations:
                for obj in self.game_objects[animation_type]["list"]:
                    obj.update(self.game.clock.get_time()/1000)
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

        # determine whether to quit the level
        submarines_remaining = self.objects_remaining("submarine")
        submarines_to_destroy = self.game_objects["submarine"]["to_destroy"]
        if submarines_remaining == 0:
            self.final_display_frames = self.level_display_frames
            pygame.mixer.music.pause()
            if submarines_to_destroy > 0:
                self.quit(self.LEVEL_FAILED)
                self.play("losing")
            else:
                self.quit(self.LEVEL_CLEARED)
                self.play("winning")

        # spawn new spawnable objects at random
        self.spawn_objects()


    def ready_to_quit(self):
        return self.final_display_frames == 0


    def play(self, sound_name):
        """
        Play a sound only if sounds are enabled
        """
        sound = resources.get_sound(sound_name)
        if self.game.options["sound"]:
            sound.play()
