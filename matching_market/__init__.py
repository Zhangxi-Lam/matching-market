from otree.api import *
from .preference_controller import PreferenceController
from .matching_system import MatchingSystem
from .config_parser import ConfigParser
from .logger import Logger
import numpy as np
import random

# pref_controllers[round_num][id_in_subsession] = controller
pref_controllers = {}
logger = Logger()


class C(BaseConstants):
    NAME_IN_URL = 'matching_market'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 20


class Subsession(BaseSubsession):
    config_file_path = models.StringField()


def creating_session(subsession: Subsession):
    # Read switch_group and switch_type settings from the first row. switch_type
    # only works when switch_group=True
    subsession.config_file_path = 'matching_market/config/' + \
        subsession.session.config['config_file']
    config = ConfigParser(subsession.config_file_path)
    c = config.get_round_config(1)
    fixed_id_in_group = not c["switch_type"]
    if c["switch_group"]:
        subsession.group_randomly(fixed_id_in_group=fixed_id_in_group)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    def compute_round_payoff(self, result, original_pref, has_penalty, r):
        space, term = None, None
        for r in result:
            if r[0] == self.id_in_group:
                space, term = r[1], r[2]
        payoff = None
        for p in original_pref:
            if p[0] == space and p[1] == term:
                payoff = p[2]
        if has_penalty:
            resident_space_term = None
            for r in result:
                if r[1] == self.id_in_group:
                    resident_space_term = r[2]
            if space != self.id_in_group and term == 0 and resident_space_term == 1:
                # penalty number
                payoff -= 2
        return payoff

    # Final payoff = sum(non_pratice_round_payoff)
    def compute_final_payoff(self, round_payoffs, config: ConfigParser):
        player_id = self.id_in_group
        final_payoff = 0
        for round in range(config.get_num_round()):
            if not config.get_round_config(round + 1)["practice"]:
                final_payoff += round_payoffs[round][player_id]
        return final_payoff


class WelcomePage(Page):
    def is_displayed(player: Player):
        return player.group.round_number == 1


class InstructionPage(Page):
    def is_displayed(player: Player):
        return player.group.round_number == 1

    def vars_for_template(player: Player):
        group = player.group
        round_num = group.round_number
        config = ConfigParser(player.group.subsession.config_file_path)
        c = config.get_round_config(round_num)
        return {"matching": c["matching"]}


class MatchingPage(Page):
    timeout_seconds = 90

    def is_displayed(player: Player):
        config = ConfigParser(player.group.subsession.config_file_path)
        return config.has_round_config(player.group.round_number)

    def vars_for_template(player: Player):
        group = player.group
        round_num = group.round_number
        group_size = len(group.get_players())
        config = ConfigParser(player.group.subsession.config_file_path)
        c = config.get_round_config(round_num)
        if round_num not in pref_controllers:
            pref_controllers[round_num] = {}
        if group.id_in_subsession not in pref_controllers[round_num]:
            # If we haven't initialized this group, initialize all players' and spaces' preferences.
            pref_controllers[round_num][group.id_in_subsession] = PreferenceController(
                group_size)
            controller = pref_controllers[round_num][group.id_in_subsession]
            for i in range(1, group_size + 1):
                controller.generate_original_preference_for_id(
                    round_num, i, c["r"], c["payoff_multiplier"])
        else:
            controller = pref_controllers[round_num][group.id_in_subsession]
        player_pref = controller.get_player_original_preference(
            player.id_in_group)
        return {"group_size": group_size,
                "matching": c["matching"],
                "player_pref": MatchingPage.sort(player_pref),
                "decision_pref": MatchingPage.shuffle(player_pref),
                "space_pref": MatchingPage.get_all_space_pref(controller, group_size, player.id_in_group)}

    def live_method(player: Player, data):
        controller = pref_controllers[player.group.round_number][player.group.id_in_subsession]
        controller.set_player_custom_preference(
            player.id_in_group, data['player_pref'])

    @staticmethod
    def sort(preference):
        sorted_preference = sorted(
            preference, key=lambda pref: (pref[0], pref[1]))
        return sorted_preference

    @staticmethod
    def shuffle(preference):
        shuffled_preference = preference[:]
        random.shuffle(shuffled_preference)
        return shuffled_preference

    @staticmethod
    def get_all_space_pref(controller: PreferenceController, group_size, player_id):
        prefs = []
        for space_id in range(1, group_size + 1):
            space_pref = controller.get_space_original_preference(space_id)
            space_pref_for_player = []
            for ranking, p in enumerate(space_pref, 1):
                if p[0] == player_id:
                    space_pref_for_player.append([space_id, p[1], ranking])
            prefs.append(space_pref_for_player)
        return prefs


class WaitResult(WaitPage):
    body_text = "Waiting for other players to submit their preferences"
    wait_for_all_groups = False


class RoundResults(Page):
    timeout_seconds = 30

    def is_displayed(player: Player):
        config = ConfigParser(player.group.subsession.config_file_path)
        return config.has_round_config(player.group.round_number)

    def vars_for_template(player: Player):
        group = player.group
        round_num = group.round_number
        config = ConfigParser(player.group.subsession.config_file_path)
        c = config.get_round_config(round_num)
        controller = pref_controllers[round_num][group.id_in_subsession]
        matching_system = MatchingSystem(controller)
        result = matching_system.get_matching_result(c["matching"], c["r"])
        payoff = player.compute_round_payoff(
            result, controller.get_player_original_preference(
                player.id_in_group),
            c["penalty"],
            c["r"]
        )
        id_in_subsession = group.id_in_subsession
        logger.add_round_result(
            group.subsession.session.code,
            player.participant.label,
            group.id_in_subsession,
            player.id_in_group,
            round_num, controller, result, payoff, c)
        logger.write()
        return {"result": result,
                "matching": c["matching"],
                "payoff": payoff,
                "preference": controller.get_player_custom_preference(player.id_in_group)}


class DebugPage(Page):
    def vars_for_template(player: Player):
        return logger.debug_message(player.group.id_in_subsession, player.round_number, len(player.group.get_players()))


class FinalResults(Page):
    def is_displayed(player):
        config = ConfigParser(player.group.subsession.config_file_path)
        return player.group.round_number == config.get_num_round()

    def vars_for_template(player: Player):
        config = ConfigParser(player.group.subsession.config_file_path)
        final_payoff = player.compute_final_payoff(
            logger.payoffs[player.group.id_in_subsession], config)
        logger.add_final_payoff(player.group.subsession.session.code,
                                player.participant.label,
                                player.group.id_in_subsession,
                                player.id_in_group,
                                final_payoff)
        logger.write()
        return {"payoff": final_payoff}


page_sequence = [WelcomePage, InstructionPage,
                 MatchingPage, WaitResult, RoundResults,
                 # DebugPage,
                 FinalResults]
