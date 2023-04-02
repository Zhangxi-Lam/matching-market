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
    pass


# PAGES
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
        controller.generate_preferences(
            player.group.round_number, player.id_in_group)
        return {"group_size": group_size,
                "preference": controller.get_player_preference(player.id_in_group)}

    def live_method(player: Player, data):
        controller.set_player_preference(
            player.id_in_group, data['preference'])


class RoundResults(Page):
    def is_displayed(player):
        return config.has_round_config(player.group.round_number)

    def vars_for_template(player: Player):
        c = config.get_round_config(player.round_number)
        matching_system = MatchingSystem(controller)
        result = matching_system.get_matching_result(c["matching"], c["r"])


page_sequence = [WelcomePage, InstructionPage, MatchingPage, RoundResults]
