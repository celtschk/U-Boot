import pygame

import resources

class MovingObject:
    "This class represents any moving object in the game."

    def __init__(self, path, start, end, speed,
                 movement_region,# =
                     #pygame.Rect(0,0,settings.width,settings.height),
                 origin = (0,0), repeat=False,
                 adjust_start = (0,0)):
        """
        Create a new moving object.

        Mandatory Arguments:
          path:             the file path to the image to display
          start:            the pixel at which the movement starts
          end:              the pixel at which the movement ends
          speed:            the fraction of the distance to move per second
          movement_region:  The region in which the object may move.

        Optional arguments:
          origin:           which point of the image to use for placement
          repeat:           whether to repeat the movement
          adjust_start:     adjustment of the start position

        All coordinates in the optional arguments are in units of
        image width or image height, as opposed to pixel coordinates
        as used in the mandatory arguments. For example, if the image
        has width of 5 pixels and height of 4 pixels, the arguments

           start = (5,5), adjust_start = (-1,0.5)

        will result in an actual starting point of (0,7).

        If the object completely leaves the movement region (that is,
        its bounding box no longer intersects the movement region),
        its current movement ends and it is either deactivated or
        set back to the start position, depending on the value of
        repeat.
        """
        self.image_path = path  # for serialization
        self.image = resources.load_image(path)

        width = self.image.get_width()

        self.start = tuple(s + width * a for s,a in zip(start,adjust_start))

        self.repeat = repeat

        self.pos = self.start

        self.speed = speed
        self.velocity = (speed * (end[0] - self.start[0]),
                         speed * (end[1] - self.start[1]))

        self.disp = (-self.image.get_width()*origin[0],
                     -self.image.get_height()*origin[1])

        self.movement_region = movement_region
        self.active = True


    def __getstate__(self):
        """
        Serialize the object for pickle
        """
        # omit image from saved state
        state = self.__dict__.copy()
        state.pop("image")
        return state


    def __setstate__(self, state):
        """
        Deserialize the object for pickle
        """
        self.__dict__.update(state)
        self.image = resources.load_image(self.image_path)


    def update(self, time):
        """
        Move the object.

        Arguments:
          time: The time passed in seconds.
        """

        # test if the object is inside the movement region before the
        # movement occurs
        def inside():
            return self.movement_region.colliderect(self.get_bounding_box())

        if self.active:
            inside_before = inside()

            self.pos = (self.pos[0] + self.velocity[0] * time,
                        self.pos[1] + self.velocity[1] * time)
            if inside_before and not inside():
                if self.repeat:
                    self.pos = self.start
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
        if displace:
            return (self.pos[0] + self.disp[0],
                    self.pos[1] + self.disp[1])
        else:
            return self.pos


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
        pos = self.get_position(True)
        return pygame.Rect(pos,
                           (self.image.get_width(),
                            self.image.get_height()))



class Animation:
    """
    This class represents an animation
    """

    def __init__(self, path_scheme, frame_count, fps,
                 position, origin = (0.5,0.5)):
        """
        Create a new animation

        Mandatory Arguments:
          path_scheme: format string for the file names of the
                       images of the animation. The frame number
                       must be given as \"{frame}\". Frame numbering
                       starts at 0.

          frame_count: number of frames.

          fps:         frames per second of the animation.

          position:    the coordinates where the animation is to be played

        Optional arguments:
          origin:      The point of the image which is places at position.

        All images are assumed to have the same size. The origin is
        relative to the upper left corner of the image and is given in
        units of image width resp. image height.
        """
        # store path scheme for serialization
        self.path_scheme = path_scheme
        self.images = [resources.load_image(path_scheme.format(frame = n))
                       for n in range(frame_count)]

        width = self.images[0].get_width()
        height = self.images[0].get_height()

        self.position = (int(position[0] - width * origin[0]),
                         int(position[1] - height * origin[1]))

        self.frame_count = frame_count
        self.fps = fps
        self.time = 0
        self.current_frame = 0


    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("images")
        return state


    def __setstate__(self, state):
        self.__dict__.update(state)
        self.images = [resources.load_image(self.path_scheme.format(frame = n))
                       for n in range(self.frame_count)]


    def is_active(self):
        """
        Returns if the animation is currently active.
        """
        return not self.current_frame is None


    def deactivate(self):
        """
        Deactivates the animation.
        """
        self.current_frame = None


    def draw_on(self, surface):
        """
        Draws the animation
        """
        if (self.is_active()):
            surface.blit(self.images[self.current_frame], self.position)


    def update(self, time):
        """
        Updates the animation
        """
        if self.is_active():
            self.time += time
            frame = int(self.time * self.fps)
            if frame >= self.frame_count:
                self.deactivate()
            else:
                self.current_frame = frame
