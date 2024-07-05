from src.models.story import Story


# Test to create a story
def test_create_story(stories: list[Story]):
    story1 = stories[0]
    assert story1 is not None, 'Story should be created successfully via the fixture in conftest.py'

# TODO: add more tests 