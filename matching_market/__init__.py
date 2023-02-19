from otree.api import *

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'matching_market'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class WelcomePage(Page):
    pass


class InstructionPage(Page):
    pass


class MatchingPage(Page):
    # def get_timeout_seconds(self):
    # return 1800

    @staticmethod
    def vars_for_template(self):
        print(len(self.group.get_players()))
        group_size = len(self.group.get_players())
        return {"group_size": group_size,
                "contracts": MatchingPage.generate_contracts(group_size)}

    @staticmethod
    def generate_contracts(group_size):
        contracts = []
        for i in range(1, group_size + 1):
            contracts.append((i, '+'))
            contracts.append((i, '-'))
        return contracts


class RoundResults(Page):
    pass


page_sequence = [WelcomePage, InstructionPage, MatchingPage, RoundResults]
