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
        self.payoffs = {}

    def add_round_result(self, id_in_group, round_num, controller: PreferenceController, result, payoff):
        if round_num not in self.payoffs:
            self.payoffs[round_num] = {}
        self.payoffs[round_num][id_in_group] = payoff
        for i in range(controller.get_group_size()):
            id_in_group = i + 1
            self.data.append(
                {
                    "round_num": round_num,
                    "id_in_group": id_in_group,
                    "player_original_preference": controller.get_player_original_preference(id_in_group),
                    "player_custom_preference": controller.get_player_custom_preference(id_in_group),
                    "space_original_preference": controller.get_space_original_preference(id_in_group),
                    "final_allocation": result[i]
                })

    def get_player_final_payoff(self, id_in_group, seed, config: ConfigParser):
        non_practice_rounds = []
        for r in range(config.get_num_round()):
            if not config.get_round_config(r + 1)["practice"]:
                non_practice_rounds.append(r + 1)
        random.seed(seed)
        selected_round_index = random.randint(0, len(non_practice_rounds) - 1)
        seleced_round = non_practice_rounds[selected_round_index]
        return self.payoffs[seleced_round][id_in_group]

    def write(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as outfile:
            json.dump(self.data, outfile)
