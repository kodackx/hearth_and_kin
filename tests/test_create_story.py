from src.models.story import Story


# Test to create a story
def test_create_story(story: Story):
    assert story is not None, 'Story should be created successfully via the fixture in conftest.py'

# TODO: add more tests 