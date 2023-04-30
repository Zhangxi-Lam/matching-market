import json
import os
from .preference_controller import PreferenceController


class Logger:
    def __init__(self, id_in_subsession):
        self.file_path = ("matching_market/data/data_"
                          + str(id_in_subsession)
                          + ".json"
                          )
        self.data = []

    def add_round_result(self, round_num, controller: PreferenceController, result):
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

    def write(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as outfile:
            json.dump(self.data, outfile)
