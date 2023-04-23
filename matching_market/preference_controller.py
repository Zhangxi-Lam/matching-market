import random
import numpy as np


class PreferenceController:

    def __init__(self):
        self.n = None
        self.player_original_preferences = None
        self.player_custom_preferences = None
        self.space_original_preferences = None

    def set_group_size(self, n):
        self.n = n
        self.player_original_preferences = [[] for _ in range(n)]
        self.player_custom_preferences = [[] for _ in range(n)]
        self.space_original_preferences = [[] for _ in range(n)]

    def get_group_size(self):
        return self.n

    # Generate the preferences for the id_in_group and its corresponding space_id
    def generate_original_preference_for_id(self, round_number, id_in_group, r):
        player_preference = []
        pref = list(range(0, self.n * 2))
        random.seed(round_number * 1e6 + id_in_group)
        random.shuffle(pref)
        payoff = len(pref)
        for p in pref:
            player_preference.append([int(p / 2) + 1, p % 2, payoff])
            payoff -= 1
        self.player_original_preferences[id_in_group - 1] = player_preference

        space_id = id_in_group
        space_preference = []
        pref = list(range(0, self.n * 2))
        random.seed(round_number * 1e6 + space_id * 1e3)
        random.shuffle(pref)
        for p in pref:
            if id_in_group <= r and int(p / 2) == id_in_group - 1:
                space_preference.insert(0, [int(p / 2) + 1, p % 2])
            else:
                space_preference.append([int(p / 2) + 1, p % 2])
        self.space_original_preferences[space_id - 1] = space_preference

    def get_player_original_preference(self, id_in_group):
        return self.player_original_preferences[id_in_group - 1]

    def set_player_custom_preference(self, id_in_group, preference):
        self.player_custom_preferences[id_in_group - 1] = preference

    def player_pref_to_numpy_array(self, player_pref):
        res = []
        for i in range(self.n):
            tmp = []
            for space_id, term in player_pref[i]:
                tmp.append([i + 1, space_id, term])
            res.append(np.array(tmp))
        return res

    def space_pref_to_numpy_array(self, space_pref):
        res = []
        for i in range(self.n):
            tmp = []
            for player_id, term in space_pref[i]:
                tmp.append([player_id, i + 1, term])
            res.append(np.array(tmp))
        return res
