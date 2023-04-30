from otree.api import *
from .preference_controller import PreferenceController
from .matching_system import MatchingSystem
from .config_parser import ConfigParser
from .logger import Logger
import numpy as np

pref_controllers = {}
loggers = {}
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
                payoff -= 50
        self.payoff = payoff


class WelcomePage(Page):
    def is_displayed(player):
        return player.group.round_number == 1


class InstructionPage(Page):
    def is_displayed(player):
        return player.group.round_number == 1


class MatchingPage(Page):
    def is_displayed(player):
        return config.has_round_config(player.group.round_number)

    def vars_for_template(player: Player):
        group = player.group
        round_num = group.round_number
        group_size = len(group.get_players())
        if round_num not in pref_controllers:
            pref_controllers[round_num] = {}
        if group.id_in_subsession not in pref_controllers[round_num]:
            pref_controllers[round_num][group.id_in_subsession] = PreferenceController(
                group_size)
        c = config.get_round_config(round_num)
        controller = pref_controllers[round_num][group.id_in_subsession]
        controller.generate_original_preference_for_id(
            round_num, player.id_in_group, c["r"])
        return {"group_size": group_size,
                "preference": controller.get_player_original_preference(player.id_in_group)}

    def live_method(player: Player, data):
        controller = pref_controllers[player.group.round_number][player.group.id_in_subsession]
        controller.set_player_custom_preference(
            player.id_in_group, data['preference'])


class WaitResult(WaitPage):
    body_text = "Waiting for other players to submit their preferences"
    wait_for_all_groups = False


class RoundResults(Page):
    def is_displayed(player):
        return config.has_round_config(player.group.round_number)

    def vars_for_template(player: Player):
        group = player.group
        round_num = group.round_number
        c = config.get_round_config(round_num)
        controller = pref_controllers[round_num][group.id_in_subsession]
        matching_system = MatchingSystem(controller)
        result = matching_system.get_matching_result(c["matching"], c["r"])
        player.compute_payoff(
            result, controller.get_player_original_preference(
                player.id_in_group),
            c["penalty"],
            c["r"]
        )
        print(player.id_in_group, result, player.payoff)
        id_in_subsession = group.id_in_subsession
        if id_in_subsession not in loggers:
            loggers[id_in_subsession] = Logger(id_in_subsession)
        loggers[id_in_subsession].add_round_result(
            round_num, controller, result)
        return {"result": result,
                "preference": controller.get_player_custom_preference(player.id_in_group)}


class FinalResults(Page):
    def is_displayed(player):
        return player.group.round_number == config.get_num_round()

    def vars_for_template(player: Player):
        for logger in loggers.values():
            logger.write()


page_sequence = [WelcomePage, InstructionPage,
                 MatchingPage, WaitResult, RoundResults,
                 FinalResults]
