from otree.api import *
from .preference_controller import PreferenceController
from .matching_system import MatchingSystem
from .config_parser import ConfigParser
import numpy as np

controller = PreferenceController()
config = ConfigParser("matching_market/config/config.csv")


class C(BaseConstants):
    NAME_IN_URL = 'matching_market'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 20


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    # Read switch_group and switch_type settings from the first row. switch_type
    # only works when switch_group=True
    c = config.get_round_config(1)
    fixed_id_in_group = not c["switch_type"]
    if c["switch_group"]:
        subsession.group_randomly(fixed_id_in_group=fixed_id_in_group)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    def compute_payoff(self, result, original_pref, has_penalty, r):
        res = result[result["player"] == self.id_in_group]
        space, term = list(res["space"])[0], list(res["term"])[0]
        payoff = None
        for p in original_pref:
            if p[0] == space and p[1] == term:
                payoff = p[2]
        if has_penalty:
            if space != self.id_in_group and term == 0 and list(result[result["space"] == self.id_in_group]["term"])[0] == 1:
                payoff -= 50
        self.payoff = payoff


class WelcomePage(Page):
    def is_displayed(player):
        return player.group.round_number == 1

    def vars_for_template(player: Player):
        group_size = len(player.group.get_players())
        controller.set_group_size(group_size)


class InstructionPage(Page):
    def is_displayed(player):
        return player.group.round_number == 1


class MatchingPage(Page):
    def is_displayed(player):
        return config.has_round_config(player.group.round_number)

    def vars_for_template(player: Player):
        group_size = len(player.group.get_players())
        c = config.get_round_config(player.group.round_number)
        controller.generate_original_preference_for_id(
            player.group.round_number, player.id_in_group, c["r"])
        return {"group_size": group_size,
                "preference": controller.get_player_original_preference(player.id_in_group)}

    def live_method(player: Player, data):
        controller.set_player_custom_preference(
            player.id_in_group, data['preference'])


class WaitResult(WaitPage):
    body_text = "Waiting for other players to submit their preferences"
    wait_for_all_groups = False


class RoundResults(Page):
    def is_displayed(player):
        return config.has_round_config(player.group.round_number)

    def vars_for_template(player: Player):
        c = config.get_round_config(player.round_number)
        matching_system = MatchingSystem(controller)
        result = matching_system.get_matching_result(c["matching"], c["r"])
        player.compute_payoff(
            result, controller.get_player_original_preference(
                player.id_in_group),
            c["penalty"],
            c["r"]
        )
        print(player.id_in_group, result, player.payoff)


page_sequence = [WelcomePage, InstructionPage,
                 MatchingPage, WaitResult, RoundResults]
