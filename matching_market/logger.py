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
        self.data = []
        self.log_data = []
        self.payoffs = {}
        self.final_payoffs = {}
        self.selected_round = None

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

    def get_player_final_payoff(self, id_in_group, config: ConfigParser):
        if not self.selected_round:
            self.selected_round = self.select_round_for_final_payoff(config)
        self.final_payoffs[id_in_group] = {
            'player_id': id_in_group,
            'selected_round': self.selected_round,
            'payoff': self.payoffs[self.selected_round][id_in_group]
        }
        return self.payoffs[self.selected_round][id_in_group], self.selected_round

    def select_round_for_final_payoff(self, config: ConfigParser):
        non_practice_rounds = []
        for r in range(config.get_num_round()):
            if not config.get_round_config(r + 1)["practice"]:
                non_practice_rounds.append(r + 1)
        selected_round_index = random.randint(0, len(non_practice_rounds) - 1)
        selected_round = non_practice_rounds[selected_round_index]
        return selected_round

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
            json.dump(self.final_payoffs, outfile)
