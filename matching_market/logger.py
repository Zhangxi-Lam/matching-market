import json
import os
from .preference_controller import PreferenceController
from .config_parser import ConfigParser
import random


class Logger:
    def __init__(self):
        self.round_data_file_path = ("matching_market/data/round_data.json")
        self.final_payoff_file_path = (
            "matching_market/data/final_payoff.json")
        # Record the original data for each round for each player_id. Preference data is stored in numpy array (can not be written into log directly).
        # self.data = [{round_num, id_in_group, player_original_preference, player_custom_preference, space_original_preference, final_allocation}]
        self.data = []
        # Record the data for each round for each player_id. Preference data is stored in Python List (can be written into log directly).
        # self.round_result_log_data = [{round_num, id_in_group, player_original_preference, player_custom_preference, space_original_preference, final_allocation}]
        self.round_result_log_data = []
        # Record the payoff of each player_id for each round.
        # self.payoffs = {id_in_subsession: {round_num: {id_in_group: payoff}}}
        self.payoffs = {}
        # Record the final_payoff of each player_id in the group.
        self.final_payoffs_log_data = []

    def add_round_result(self, session_code, participant_label, id_in_subsession, id_in_group, round_num, controller: PreferenceController, results, payoff, config):
        # Check if we have added result for this player
        if id_in_subsession in self.payoffs and round_num in self.payoffs[id_in_subsession] and id_in_group in self.payoffs[id_in_subsession][round_num]:
            return
        if id_in_subsession not in self.payoffs:
            self.payoffs[id_in_subsession] = {}
        if round_num not in self.payoffs[id_in_subsession]:
            self.payoffs[id_in_subsession][round_num] = {}
        self.payoffs[id_in_subsession][round_num][id_in_group] = payoff
        final_allocation = None
        for r in results:
            if r[0] == id_in_group:
                # results is a list of the final allocations [player_id, space_id, term]
                final_allocation = [r[0], r[1], r[2]]
        self.data.append(
            {
                "session_code": session_code,
                "participant_label": participant_label,
                "round_num": round_num,
                "id_in_subsession": id_in_subsession,
                "id_in_group": id_in_group,
                "player_original_preference": controller.get_player_original_preference(id_in_group),
                "player_custom_preference": controller.get_player_custom_preference(id_in_group),
                "space_original_preference": controller.get_space_original_preference(id_in_group),
                "final_allocation": final_allocation,
            }
        )
        self.round_result_log_data.append(
            {
                "session_code": session_code,
                "participant_label": participant_label,
                "round_num": round_num,
                "id_in_subsession": id_in_subsession,
                "id_in_group": id_in_group,
                "player_original_preference": controller.player_preference_to_log(controller.get_player_original_preference(id_in_group)),
                "player_custom_preference": controller.player_preference_to_log(controller.get_player_custom_preference(id_in_group)),
                "space_original_preference": controller.space_preference_to_log(controller.get_space_original_preference(id_in_group)),
                "final_allocation": {
                    "player_id": final_allocation[0],
                    "space_id": final_allocation[1],
                    "term": final_allocation[2],
                },
                "payoff": payoff,
                "switch_group": config["switch_group"],
                "switch_type": config["switch_type"],
                "r": config["r"],
                "matching": config["matching"],
                "penalty": config["penalty"],
                "practice": config["practice"],
                "payoff_multiplier": config["payoff_multiplier"],
            })

    def add_final_payoff(self, session_code, participant_label, id_in_subsession, id_in_group, final_payoff):
        # Check if we have added the final_payoff for this player
        for record in self.final_payoffs_log_data:
            if record['id_in_subsession'] == id_in_subsession and record['id_in_group'] == id_in_group:
                return
        self.final_payoffs_log_data.append({
            "session_code": session_code,
            "participant_label": participant_label,
            "id_in_subsession": id_in_subsession,
            "id_in_group": id_in_group,
            "final_payoff": final_payoff
        })

    def debug_message(self, id_in_subsession, round_num, n):
        player_orig_prefs = []
        player_cus_prefs = []
        space_orig_prefs = []
        final_allocations = []
        for d in self.data:
            for id_in_group in range(1, n + 1):
                if d["id_in_subsession"] == id_in_subsession and d["round_num"] == round_num and d["id_in_group"] == id_in_group:
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
        os.makedirs(os.path.dirname(self.round_data_file_path), exist_ok=True)
        with open(self.round_data_file_path, "w") as outfile:
            json.dump(self.round_result_log_data, outfile)

        os.makedirs(os.path.dirname(
            self.final_payoff_file_path), exist_ok=True)
        with open(self.final_payoff_file_path, "w") as outfile:
            json.dump(self.final_payoffs_log_data, outfile)
