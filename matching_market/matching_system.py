import numpy as np
import pandas as pd
from .preference_controller import PreferenceController


class MatchingSystem:
    def __init__(self, controller: PreferenceController):
        self.controller = controller

    def get_matching_result(self, matching, r):
        pref_player = self.controller.player_pref_to_numpy_array(
            self.controller.player_custom_preferences)
        pref_space = self.controller.space_pref_to_numpy_array(
            self.controller.space_original_preferences)
        n = self.controller.get_group_size()

        if matching == 'DA':
            result = self.algo_da(pref_player, pref_space, n)
        elif matching == 'BE':
            result = self.algo_be(pref_player, pref_space, n, r)
        return result.values.tolist()

    def algo_da(self, pref_player, pref_space, n):
        # get the initial empty accumulate set for each space
        space_acum = pref_space.copy()
        for i in range(n):
            # add a 4th column to store whether the contract is in the accumulate set
            space_acum[i] = np.column_stack(
                (space_acum[i], np.zeros(len(space_acum[i]))))
            space_acum[i] = space_acum[i].astype(int)
        # get the initial empty choice set for each space
        space_choi = np.zeros((n, 4))
        space_choi = pd.DataFrame(
            space_choi, columns=['player', 'space', 'term', 'status'])
        space_choi = space_choi.astype(int)

        # loop for GS mechanism
        for i in range(10000):
            # set up the reject player list for all players in the first round
            if i == 0:
                reject_player = list(range(1, n + 1))
            # loop over players to submit their preference
            for j in reject_player:
                # get player's most preferred contract and remove it from the preference
                contract = pref_player[j - 1][0]
                pref_player[j - 1] = np.delete(pref_player[j - 1], 0, axis=0)
                # locate the corresponding space and add the contract to space's accumulate set
                s = contract[1]
                for k in range(len(space_acum[s - 1])):
                    if all(space_acum[s - 1][k][0:3] == contract):
                        space_acum[s - 1][k][3] = 1
                        break
            # initialize reject player for the next round
            reject_player = []
            # loop over spaces to reject the lowest player
            for j in range(n):
                # filter the accumulate set
                temp_acum = space_acum[j][space_acum[j][:, 3] == 1, :]
                row = temp_acum.shape[0]
                if row > 1:
                    # find the rejected contract
                    reject_contract = temp_acum[-1, :]
                    # add the reject player to the overall reject players set
                    reject_player.append(reject_contract[0])
                    # remove the contract from the accumulate set
                    for k in range(space_acum[j].shape[0]):
                        if np.array_equal(reject_contract, space_acum[j][k, :]):
                            space_acum[j][k, 3] = 0
                            break
            # break out of the loop if there is no rejected player
            if len(reject_player) == 0:
                break
        steps = i
        for i in range(n):
            accept_contract = space_acum[i][space_acum[i][:, 3] == 1, :]
            space_choi.iloc[i, :] = accept_contract[0, :]

        return space_choi

    # similar to DA but the visitors cannot apply t+ contract to residents' space
    def algo_be(self, pref_player, pref_space, n, r):
        # get the initial empty accumulate set for each space
        space_acum = pref_space.copy()
        for i in range(n):
            # add a 4th column to store whether the contract is in the accumulate set
            space_acum[i] = np.column_stack(
                (space_acum[i], np.zeros(len(space_acum[i]))))
            space_acum[i] = space_acum[i].astype(int)
        # get the initial empty choice set for each space
        space_choi = np.zeros((n, 4))
        space_choi = pd.DataFrame(
            space_choi, columns=['player', 'space', 'term', 'status'])
        space_choi = space_choi.astype(int)

        # remove t+ contract for visitors from resident's space
        for i in range(r):
            # mark all the deleted rows (visitors that occupy a resident t+ space)
            for j in range(space_acum[i].shape[0]):
                if (space_acum[i][j, 0] != space_acum[i][j, 1]) and (space_acum[i][j, 2] == 1):
                    space_acum[i][j, 3] = 2
            # remove those deleted rows
            space_acum[i] = space_acum[i][space_acum[i][:, 3] != 2, :]

        # similarly, remove these contracts from players' preference
        # for residents
        for i in range(r):
            pref_player[i] = pref_player[i][((pref_player[i][:, 0] != pref_player[i][:, 1]) |
                                            (pref_player[i][:, 1] > r) |
                                            (pref_player[i][:, 2] == 0))]

        # for visitors
        for i in range(r, n):
            pref_player[i] = pref_player[i][(
                (pref_player[i][:, 1] > r) | (pref_player[i][:, 2] == 0))]

        # loop for Benchmark mechanism
        for i in range(10000):
            # set up the reject player list for all players in the first round
            if i == 0:
                reject_player = list(range(1, n + 1))
            # loop over players to submit their preference
            for j in reject_player:
                # get player's most preferred contract and remove it from the preference
                contract = pref_player[j - 1][0]
                pref_player[j - 1] = np.delete(pref_player[j - 1], 0, axis=0)
                # locate the corresponding space and add the contract to space's accumulate set
                s = contract[1]
                for k in range(len(space_acum[s - 1])):
                    if all(space_acum[s - 1][k][0:3] == contract):
                        space_acum[s - 1][k][3] = 1
                        break
            # initialize reject player for the next round
            reject_player = []
            # loop over spaces to reject the lowest player
            for j in range(n):
                # filter the accumulate set
                temp_acum = space_acum[j][space_acum[j][:, 3] == 1, :]
                row = temp_acum.shape[0]
                if row > 1:
                    # find the rejected contract
                    reject_contract = temp_acum[-1, :]
                    # add the reject player to the overall reject players set
                    reject_player.append(int(reject_contract[0]))
                    # remove the contract from the accumulate set
                    for k in range(space_acum[j].shape[0]):
                        if np.array_equal(reject_contract, space_acum[j][k, :]):
                            space_acum[j][k, 3] = 0
                            break
            # break out of the loop if there is no rejected player
            if len(reject_player) == 0:
                break

        # return the allocation
        for i in range(n):
            accept_contract = space_acum[i][space_acum[i][:, 3] == 1, :]
            space_choi.iloc[i, :] = accept_contract[0, :]

        return space_choi
