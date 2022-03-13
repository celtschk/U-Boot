"""
Test resources.py
"""

import resources

def test_imagestore():
    """
    Test that theimagestore variable exists, is a dictionary, and
    starts out empty
    """
    assert isinstance(resources.imagestore, dict)
    assert not resources.imagestore


def test_loadimage_new_image(mocker):
    """
    Test that a new image is properly loaded and stored in the
    imagestore
    """
    # pylint: disable=too-few-public-methods
    class Dummy:
        """
        A dummy class to stand for the result of pygame.image.load
        """
        def __init__(self, string):
            self.string = string
        def convert_alpha(self):
            """
            This mocks pygame.Surface.convert_alpha
            """
            return self.string
    # pylint: enable=too-few-public-methods
    mocker.patch('resources.pygame.image.load',
                 return_value = Dummy("the image"))
    # make sure the imagestore is initially empty
    resources.imagestore = {}
    result = resources.load_image("test")
    assert result == "the image"
    assert resources.imagestore["test"] == "the image"


def test_loadimage_existing_image():
    """
    Test that an existing image is taken straight out of the image store
    """
    # set resources.imagestore to some fake image
    resources.imagestore = { "foo": "some image" }
    result = resources.load_image("foo")
    assert result == "some image"


def test_subset_or_none_with_subset():
    """
    Test resources.subset_or_none when the second directory is a
    subset
    """
    dict1 = { 1: 10, 2: 20, 3: 30 }
    dict2 = { 1: 11, 3: 31 }
    result = resources.subset_or_none(dict1, dict2)
    assert isinstance(result, dict)
    assert result ==  { 1: 11, 2: 20, 3: 31 }


def test_subset_or_none_with_not_subset():
    """
    Test resources.subset_or_none when the second directory is a
    subset
    """
    dict1 = { 1: 10, 2: 20, 3: 30 }
    dict2 = { 1: 11, 4: 31 }
    result = resources.subset_or_none(dict1, dict2)
    assert isinstance(result, dict)
    assert result ==  {}


class MyDict(dict):
    """
    Dictionary, but with user defined type
    """


class MyDict2(dict):
    """
    Dictionary, but with other user defined type
    """


def test_subset_or_none_with_mydict_and_subset():
    """
    Test resources.subset_or_none when the second directory is a
    subset
    """
    dict1 = MyDict({ 1: 10, 2: 20, 3: 30 })
    dict2 = MyDict2({ 1: 11, 3: 31 })
    result = resources.subset_or_none(dict1, dict2)
    assert isinstance(result, MyDict)
    assert result ==  { 1: 11, 2: 20, 3: 31 }


def test_subset_or_none_with_mydict_and_not_subset():
    """
    Test resources.subset_or_none when the second directory is a
    subset
    """
    dict1 = MyDict({ 1: 10, 2: 20, 3: 30 })
    dict2 = MyDict2({ 1: 11, 4: 31 })
    result = resources.subset_or_none(dict1, dict2)
    assert isinstance(result, MyDict)
    assert result ==  {}
