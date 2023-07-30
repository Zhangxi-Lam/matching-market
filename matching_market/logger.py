import json
import os
from .preference_controller import PreferenceController
from .config_parser import ConfigParser
import random


class Logger:
    def __init__(self, id_in_subsession):
        self.file_path = ("matching_market/data/data_"
                          + str(id_in_subsession)
                          + ".json"
                          )
        # Record the original data for each round for each player_id. Preference data is stored in Pandas Dataframe (can not be written into log directly).
        # self.data = [{round_num, id_in_group, player_original_preference, player_custom_preference, space_original_preference, final_allocation}]
        self.data = []
        # Record the data for each round for each player_id. Preference data is stored in Python List (can be written into log directly).
        # self.log_data = [{round_num, id_in_group, player_original_preference, player_custom_preference, space_original_preference, final_allocation}]
        self.log_data = []
        # Record the payoff of each player_id for each round.
        # self.payoffs = {round_num: {id_in_group: payoff}}
        self.payoffs = {}

    def add_round_result(self, id_in_group, round_num, controller: PreferenceController, results, payoff):
        # Check if we have added result for this player
        if round_num in self.payoffs and id_in_group in self.payoffs[round_num]:
            return
        if round_num not in self.payoffs:
            self.payoffs[round_num] = {}
        self.payoffs[round_num][id_in_group] = payoff
        final_allocation = None
        for r in results:
            if r[0] == id_in_group:
                # results is a list of the final allocations [player_id, space_id, term]
                final_allocation = [r[0], r[1], r[2]]
        self.data.append(
            {
                "round_num": round_num,
                "id_in_group": id_in_group,
                "player_original_preference": controller.get_player_original_preference(id_in_group),
                "player_custom_preference": controller.get_player_custom_preference(id_in_group),
                "space_original_preference": controller.get_space_original_preference(id_in_group),
                "final_allocation": final_allocation,
            }
        )
        self.log_data.append(
            {
                "round_num": round_num,
                "id_in_group": id_in_group,
                "player_original_preference": controller.player_preference_to_log(controller.get_player_original_preference(id_in_group)),
                "player_custom_preference": controller.player_preference_to_log(controller.get_player_custom_preference(id_in_group)),
                "space_original_preference": controller.space_preference_to_log(controller.get_space_original_preference(id_in_group)),
                "final_allocation": {
                    "player_id": final_allocation[0],
                    "space_id": final_allocation[1],
                    "term": final_allocation[2],
                }
            })

    def debug_message(self, round_num, n):
        player_orig_prefs = []
        player_cus_prefs = []
        space_orig_prefs = []
        final_allocations = []
        for d in self.data:
            for id_in_group in range(1, n + 1):
                if d["round_num"] == round_num and d["id_in_group"] == id_in_group:
                    for pref in d["player_original_preference"]:
                        p = pref[:]
                        p.append(id_in_group)
                        player_orig_prefs.append(p[:])
                    for pref in d["player_custom_preference"]:
                        p = pref[:]
                        p.append(id_in_group)
                        player_cus_prefs.append(p[:])
                    for pref in d["space_original_preference"]:
                        p = pref[:]
                        p.append(id_in_group)
                        space_orig_prefs.append(p[:])
                    final_allocations.append(d["final_allocation"])
        return {
            "player_original_preferences": player_orig_prefs,
            "player_custom_preferences": player_cus_prefs,
            "space_original_preferences": space_orig_prefs,
            "final_allocations": final_allocations
        }

    def write(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as outfile:
            json.dump(self.log_data, outfile)
