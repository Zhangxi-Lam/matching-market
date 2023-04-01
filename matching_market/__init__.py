from otree.api import *
from .preference_controller import PreferenceController
from .matching_system import MatchingSystem
import numpy as np

doc = """
Your app description
"""

controller = PreferenceController()


class C(BaseConstants):
    NAME_IN_URL = 'matching_market'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 100


class Subsession(BaseSubsession):
    pass


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
        pass

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
    def vars_for_template(player: Player):
        matching_system = MatchingSystem()
        print(matching_system.algo_da(controller.to_numpy_array(controller.player_preferences),
                                      controller.to_numpy_array(
                                          controller.space_preferences), controller.get_group_size()
                                      ))


page_sequence = [WelcomePage, InstructionPage, MatchingPage, RoundResults]
