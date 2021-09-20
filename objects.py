import pygame

# A storage for images, so that they aren't loaded each time
# another object uses the same image is
imagestore = {}

def load_image(path):
    """
    Load an image, if not already loaded. Otherwise, return the
    already loaded image.
    """
    if not path in imagestore:
        imagestore[path] = pygame.image.load(path).convert_alpha()
    return imagestore[path]

class MovingObject:
    "This class represents any moving object in the game."

    def __init__(self, object_type, path, start, end, speed,
                 origin = (0,0), repeat=False,
                 adjust_start = (0,0), adjust_end = (0,0)):
        """
        Create a new moving object.

        Mandatory Arguments:
          object_type:   the name of this type of object
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
        self.image_path = path  # for serialization
        self.image = load_image(path)

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

        self.object_type = object_type

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
        self.image = load_image(self.image_path)

    def update(self, time):
        """
        Move the object.

        Arguments:
          time: The time passed in seconds.
        """
        if self.active:
            self.dist += self.speed * time
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

class Animation:
    """
    This class represents an animation
    """
    
    def __init__(self, object_type, path_scheme, frame_count, fps,
                 position, origin = (0.5,0.5)):
        """
        Create a new animation

        Mandatory Arguments:
          object_type: the name of this type of object
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
        self.images = [load_image(path_scheme.format(frame = n))
                       for n in range(frame_count)]

        width = self.images[0].get_width()
        height = self.images[0].get_height()

        self.position = (int(position[0] - width * origin[0]),
                         int(position[1] - height * origin[1]))

        self.frame_count = frame_count
        self.fps = fps
        self.time = 0
        self.current_frame = 0

        self.object_type = object_type

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("images")
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.images = [load_image(self.path_scheme.format(frame = n))
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
