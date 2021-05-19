# -*- coding: utf-8 -*-
import os


from nanny.gym import GymState


def test_state():
    gym_state = GymState()
    name = 'xxx'
    gym_state.save({'name': name})
    state = gym_state.load()
    assert state['name'] == name
    # clean up
    os.remove(gym_state.filename)
