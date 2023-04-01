import random
import numpy as np


class PreferenceController:

    def __init__(self):
        self.n = 0
        self.player_preferences = None
        self.space_preferences = None

    def set_group_size(self, n):
        self.n = n
        self.player_preferences = [[] for _ in range(n)]
        self.space_preferences = [[] for _ in range(n)]

    def get_group_size(self):
        return self.n

    # Generate the preferences for the id_in_group and its corresponding space_id
    def generate_preferences(self, round_number, id_in_group):
        player_preference = []
        pref = list(range(0, self.n * 2))
        random.seed(round_number * 1e6 + id_in_group)
        random.shuffle(pref)
        for p in pref:
            player_preference.append([int(p / 2), p % 2])
        self.player_preferences[id_in_group - 1] = player_preference

        space_id = id_in_group
        space_preference = []
        pref = list(range(0, self.n * 2))
        random.seed(round_number * 1e6 + space_id * 1e3)
        random.shuffle(pref)
        for p in pref:
            space_preference.append([int(p / 2), p % 2])
        self.space_preferences[space_id - 1] = space_preference

    def get_player_preference(self, id_in_group):
        return self.player_preferences[id_in_group - 1]

    def set_player_preference(self, id_in_group, preference):
        self.player_preferences[id_in_group - 1] = preference

    def to_numpy_array(self, preferences):
        res = []
        for i in range(self.n):
            for contract in preferences[i]:
                tmp = [i] + contract
                res.append([i] + contract)
        return np.array(res)
