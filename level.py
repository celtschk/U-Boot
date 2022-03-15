#  Copyright 2022 Christopher Eltschka
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
This module implements the class Level, which contains the actual gameplay.
"""

from copy import deepcopy

import pygame

import settings
import resources
from gamedisplay import GameDisplay
from objects import MovingObject, Animation, TransientDisplay


# Currently there's only one game level. Nevertheless, it makes sense to
# separate out the class
class Level(GameDisplay):
    "A game level"
    # Level specific exit values
    LEVEL_CLEARED = GameDisplay.Status()
    LEVEL_FAILED  = GameDisplay.Status()
    LEVEL_SAVE = GameDisplay.Status()

    @staticmethod
    def initial_state(old_state):
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

        self.dimensions = {
            "width": game.screen.get_width(),
            "height": game.screen.get_height()
            }
        self.dimensions["waterline"] = int(settings.sky_fraction * self.dimensions["height"])

        center_x = self.dimensions["width"]//2
        center_y = self.dimensions["height"]//2

        self.state = old_state

        if not self.state["objects"]:
            # get limits and probabilities for objects
            for obj_type, obj in self.state["object_settings"].items():
                # record object info in objects dictionary
                object_info = self.state["objects"][obj_type] = { "list": [] }

                if "max_count" in obj:
                    # initially, none of those objects exis
                    object_info["max_count"] = obj["max_count"]

                if "spawn_rate" in obj:
                    object_info["spawn_rate"] = obj["spawn_rate"]
                    self.state["spawnables"].add(obj_type)

                if "total_count" in obj:
                    object_info["remaining"] = obj["total_count"]

                if "to_destroy" in obj:
                    object_info["to_destroy"] = obj["to_destroy"]

            # create the ship
            ship = self.create_moving_object("ship")
            self.state["objects"]["ship"] = { "list": [ship] }

            # setup storage for animations
            for animation_type in settings.animations:
                self.state["objects"][animation_type] = { "list": [] }

        # setup storage for transient displays
        self.state["objects"]["transients"] = { "list": [] }

        self.display = {
            # set displayed score to game score
            # (separate to allow score animation)
            "score": self.state["score"],

            # number of frames between displayed score steps
            "score_frames":    settings.score_frames,

            # remaining frames until next score step
            "score_countdown": settings.score_frames,

            # number of frames the finished level is still shown
            "final_display_frames": settings.level_display_frames,
            }

        self.colours = {
            # background (sky) colour
            "background": resources.get_colour("sky"),

            # water colour
            "water": resources.get_colour("water"),

            # colours of the game state display
            "text": resources.get_colour("text"),
            "no bombs": resources.get_colour("no bombs"),
            "no destroy": resources.get_colour("no more subs to destroy"),
            "not enough subs": resources.get_colour("not enough subs"),

            # colour of the pause text display
            "pause": resources.get_colour("pause"),

            # colour of the level cleared text display
            "cleared": resources.get_colour("cleared"),

            # colour of the level failed text display
            "failed": resources.get_colour("failed")
            }

        # The game is initially not paused
        self.paused = False

        def bomb_text_colour(data):
            if data["available_bombs"] > 0:
                return self.colours["text"]
            return self.colours["no bombs"]

        def submarine_text_colour(data):
            if data["to_destroy"] == 0:
                return self.colours["no destroy"]
            if data["to_destroy"] > data["remaining_subs"]:
                return self.colours["not enough subs"]
            return self.colours["text"]

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
                colour = self.colours["text"],
                font = self.game.font
                ),

            resources.MessageData(
                message = "Level: {level},  Score: {score}",
                position = pygame.Vector2(20+center_x, 20),
                colour = self.colours["text"],
                font = self.game.font
                ),

            resources.MessageData(
                message = "Remaining submarines: {to_destroy}/{remaining_subs}",
                position = pygame.Vector2(20+center_x, 50),
                colour = submarine_text_colour,
                font = self.game.font
                )

            ]

        self.messages = {
            # message for pause
            "paused": resources.MessageData(
                message = "--- PAUSED ---",
                position = pygame.Vector2(center_x, center_y),
                colour = self.colours["pause"],
                font = self.game.font,
                origin = pygame.Vector2(0.5,0.5)),

            # message for cleared level
            "cleared": resources.MessageData(
                message = "*** LEVEL CLEARED ***",
                position = pygame.Vector2(center_x, center_y - 32),
                colour = self.colours["cleared"],
                font = self.game.font,
                origin = pygame.Vector2(0.5,0.5)),

            # message for failed level
            "failed": resources.MessageData(
                message = "*** LEVEL FAILED ***",
                position = pygame.Vector2(center_x, center_y - 32),
                colour = self.colours["failed"],
                font = self.game.font,
                origin = pygame.Vector2(0.5,0.5))
            }

        self.key_bindings.update({
            pygame.K_p:          self.pause_game,
            pygame.K_PAUSE:      self.pause_game,
            pygame.K_s:          self.quit_for_save,
            pygame.K_q:          self.quit_game,
            pygame.K_ESCAPE:     self.quit_game
            })


    def get_state(self):
        """
        Get the current state of the level. The data is used in the
        save file, as well as to pass on data to the next level.
        """
        # transient displays cannot be shelved, but don't need to be
        # saved anyway, thus simply remove them from the state
        state = deepcopy(self.state)
        del state["objects"]["transients"]
        return state


    def create_moving_object(self, object_type):
        """
        Create a moving object of type object_type
        """
        data = self.state["object_settings"][object_type]
        origin = pygame.Vector2(data["origin"])

        height = self.dimensions["height"]
        width = self.dimensions["width"]
        waterline = self.dimensions["waterline"]

        movement = data["movement"]

        start = movement["start"]
        if start[0] == "left":
            start_x = 0
            start_adjustment = pygame.Vector2(origin[0] - 1, 0)
        elif start[0] == "right":
            start_x = width
            start_adjustment = pygame.Vector2(origin[0], 0)
        else:
            if start[0] == "ship":
                ship = self.state["objects"]["ship"]["list"][0]
                start_x = ship.get_position()[0]
            elif isinstance(start[0], str):
                start_x = resources.get_value(data[start[0]])
            else:
                start_x = start[0]
            start_adjustment = pygame.Vector2(0, 0)

        if isinstance(start[1], str):
            if start[1] == "ship":
                start_depth = 0
            else:
                start_depth = resources.get_value(data["constants"][start[1]])
        else:
            start_depth = start[1]

        def y_from_depth(depth):
            return depth*(height - waterline) + waterline

        def calc_velocity(speed, direction):
            return pygame.Vector2(speed * direction[0] * width,
                                  speed * direction[1] * height)

        return MovingObject(
            data["filename"],
            start = pygame.Vector2(start_x, y_from_depth(start_depth)),
            adjust_start = start_adjustment,
            movement_region = self.game.screen.get_rect(),
            velocity = calc_velocity(resources.get_value(movement["speed"]),
                                     movement["direction"]),
            origin = origin,
            repeat = movement["repeat"])


    def draw(self):
        """
        Draw the game graphics
        """
        screen = self.game.screen
        screen.fill(self.colours["background"])
        pygame.draw.rect(screen, self.colours["water"],
                         (0,
                          self.dimensions["waterline"],
                          self.dimensions["width"],
                          self.dimensions["height"] - self.dimensions["waterline"]))

        for obj_data in self.state["objects"].values():
            for obj in obj_data["list"]:
                obj.draw_on(screen)

        displaydata = {
            "remaining_bombs": self.state["objects"]["bomb"]["remaining"],
            "available_bombs": self.get_available_bombs(),
            "bomb_cost": self.get_bomb_cost(),
            "remaining_subs": self.objects_remaining("submarine"),
            "to_destroy": self.state["objects"]["submarine"]["to_destroy"],
            "level": self.state["level_number"],
            "score": self.display["score"]
            }

        for message in self.game_state_display:
            message.write(screen, displaydata)

        # show message if game is paused:
        if self.paused:
            self.messages["paused"].write(screen)

        # show final message as appropriate:
        if not self.running:
            if self.status == self.LEVEL_CLEARED:
                self.messages["cleared"].write(screen)
            elif self.status == self.LEVEL_FAILED:
                self.messages["failed"].write(screen)

        pygame.display.flip()


    def get_bomb_cost(self, count=1):
        "Returns the score cost of dropping another count bombs"
        num_of_bombs = len(self.state["objects"]["bomb"]["list"])
        return sum((num_of_bombs+k)**2 for k in range(count))


    def get_available_bombs(self):
        "Returns the maximum number of extra bombs that can be thrown"

        bomb_info = self.state["objects"]["bomb"]
        max_bombs = min(bomb_info["max_count"], bomb_info["remaining"])
        existing_bombs = len(bomb_info["list"])

        available_bombs = max_bombs - existing_bombs

        while self.get_bomb_cost(available_bombs) > self.state["score"]:
            available_bombs -= 1

        return available_bombs


    def drop_bomb(self):
        "Drop a bomb, if possible"

        # don't drop a new bomb if there already exist a naximal
        # number of them, or the score would go negative
        if self.get_available_bombs() > 0:
            ship = self.state["objects"]["ship"]["list"][0]
            ship_pos = ship.get_position()

            # don't drop a bomb off-screen
            if ship_pos[0] > 0 and ship_pos[0] < self.dimensions["width"]:
                # the score must be updated before adding the new bomb
                # because adding the bomb changes the cost
                bomb_cost = self.get_bomb_cost()
                if bomb_cost != 0:
                    scoredisplay = self.game.font.render(
                        f"{-bomb_cost}", True,
                        resources.get_colour("bomb score delta"))
                    self.state["objects"]["transients"]["list"].append(
                        TransientDisplay(scoredisplay,
                                         (ship_pos[0], ship_pos[1]-40),
                                         settings.transient_display_time))
                self.state["score"] -= bomb_cost

                newbomb = self.create_moving_object("bomb")
                self.state["objects"]["bomb"]["list"].append(newbomb)
                self.state["objects"]["bomb"]["remaining"] -= 1


    def spawn_objects(self):
        "Possibly spawn new spawnable objects"
        for obj_type in self.state["spawnables"]:
            obj_data = self.state["objects"][obj_type]
            limited = ("remaining" in obj_data)

            max_objects = obj_data["max_count"]
            if limited and obj_data["remaining"] < max_objects:
                max_objects = obj_data["remaining"]

            existing_objects = len(obj_data["list"])
            rate = obj_data["spawn_rate"]

            if existing_objects < max_objects:
                if resources.randomly_true(rate/self.game.fps):
                    newobj = self.create_moving_object(obj_type)
                    self.state["objects"][obj_type]["list"].append(newobj)
                    if limited:
                        obj_data["remaining"] -= 1


    def create_animation(self, animation_type, position):
        """
        Create an animation of given type at a specific position.
        """
        animation = settings.animations[animation_type]
        self.state["objects"][animation_type]["list"].append(
            Animation(path_scheme = animation["images"],
                      frame_count = animation["frame_count"],
                      fps = animation["fps"],
                      position = position))


    def handle_hits(self):
        """
        Check if any projectile hit any target, and if so, remove both
        and update score
        """
        waterline = self.dimensions["waterline"]
        height    = self.dimensions["height"]

        for obj_pair, info in settings.hit_info.items():
            target_name, projectile_name = obj_pair
            for target in self.state["objects"][target_name]["list"]:
                for projectile in self.state["objects"][projectile_name]["list"]:
                    bb1 = target.get_bounding_box()
                    bb2 = projectile.get_bounding_box()
                    if bb1.colliderect(bb2):
                        targetpos = target.get_position()
                        if target.is_active() and info["score"]:
                            delta = int(
                                (targetpos[1] - waterline) / height * 20 + 0.5)
                            self.state["score"] += delta
                            scoredisplay = self.game.font.render(
                                f"{delta:+}", True,
                                resources.get_colour("score delta"))
                            self.state["objects"]["transients"]["list"].append(
                                TransientDisplay(scoredisplay, targetpos,
                                                 settings.transient_display_time))
                        self.play(info["sound"])
                        self.create_animation(info["animation"],
                                              projectile.get_position())
                        target.deactivate()
                        projectile.deactivate()
                        if self.state["objects"][target_name]["to_destroy"] > 0:
                            self.state["objects"][target_name]["to_destroy"] -= 1


    def pause_game(self):
        """
        Pause the game
        """
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused


    def quit_game(self):
        """
        Quit the level immediately, without saving
        """
        self.display["final_display_frames"] = 0
        self.quit()


    def quit_for_save(self):
        """
        Quit the level and mark it for being saved
        """
        self.display["final_display_frames"] = 0
        self.quit(self.LEVEL_SAVE)


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
                    return True

        return False


    def objects_remaining(self, obj_type):
        """
        Return True if all objects of the given type have already beem
        generated.
        """
        obj_info = self.state["objects"][obj_type]
        return obj_info.get("remaining", 1) + len(obj_info["list"])


    def update_displayed_score(self):
        """
        Move the displayed score one step closer to the actual score
        """
        if self.display["score"] != self.state["score"]:
            if self.display["score_countdown"] == 0:
                self.display["score_countdown"] = self.display["score_frames"]
                if self.display["score"] < self.state["score"]:
                    self.display["score"] += 1
                elif self.display["score"] > self.state["score"]:
                    self.display["score"] -= 1
            else:
                self.display["score_countdown"] -= 1


    def update_state(self):
        """
        Update the state of the game
        """
        # if the game is paused, do nothing
        if self.paused:
            return

        # move the displayed score towards the actual score
        self.update_displayed_score()

        # if the game is no longer running, decrease the final frame
        # counter if appropriate, advance any remaining animations,
        # and then return immediately (so that game objects no longer
        # move, and score is no longer collected)
        if not self.running:
            if self.display["final_display_frames"] > 0:
                self.display["final_display_frames"] -=1
            for animation_type in settings.animations:
                for obj in self.state["objects"][animation_type]["list"]:
                    obj.update(self.game.clock.get_time()/1000)
            return

        # move all objects and advance all animations
        for obj_data in self.state["objects"].values():
            for obj in obj_data["list"]:
                obj.update(self.game.clock.get_time()/1000)

        # handle bombs hitting submarines
        self.handle_hits()

        # remove inactive objects and animations
        for thing in self.state["objects"].values():
            thing["list"] = [obj for obj in thing["list"] if obj.is_active()]

        # determine whether to quit the level
        submarines_remaining = self.objects_remaining("submarine")
        submarines_to_destroy = self.state["objects"]["submarine"]["to_destroy"]
        if submarines_remaining == 0:
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
        return self.display["final_display_frames"] == 0


    def play(self, sound_name):
        """
        Play a sound only if sounds are enabled
        """
        sound = resources.get_sound(sound_name)
        if self.game.options["sound"]:
            sound.play()
