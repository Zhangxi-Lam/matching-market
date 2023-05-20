import numpy as np
import pandas as pd
from .preference_controller import PreferenceController
import random


class MatchingSystem:
    def __init__(self, controller: PreferenceController):
        self.controller = controller

    def get_matching_result(self, matching, r):
        pref_player = self.controller.player_pref_to_numpy_array(
            self.controller.player_custom_preferences)
        pref_space = self.controller.space_pref_to_numpy_array(
            self.controller.space_original_preferences)
        n = self.controller.get_group_size()

        result = None
        if matching == 'DA':
            result = self.algo_da(pref_player, pref_space, n)
        elif matching == 'BE':
            result = self.algo_be(pref_player, pref_space, n, r)
        elif matching == 'CO':
            result = self.algo_co(pref_player, pref_space, n, r)
        elif matching == 'SM':
            result = self.algo_sm(pref_player, pref_space, n, r)
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
            pref_player[i] = pref_player[i][((pref_player[i][:, 0] == pref_player[i][:, 1]) |
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

    def algo_co(self, pref_player, pref_space, n, r):
        # get the initial empty accumulate set for each space
        space_acum = pref_space.copy()
        player_acum = pref_player.copy()

        for i in range(n):
            # add a 4th column to store whether the contract is in the accumulate set
            space_acum[i] = np.column_stack(
                (space_acum[i], np.zeros(space_acum[i].shape[0])))
            space_acum[i] = space_acum[i].astype(int)

        # get the initial empty choice set for each space
        space_choi = np.zeros((n, 4))
        space_choi = pd.DataFrame(
            space_choi, columns=['player', 'space', 'term', 'status'])
        space_choi = space_choi.astype(int)

        # loop for Benchmark mechanism
        for i in range(1000):
            # collect the players without contract
            reject_player = []
            for j in range(1, n + 1):
                if j in space_choi['player'].values:
                    continue
                else:
                    reject_player.append(j)
            # break out of the loop if there is no rejected player
            if len(reject_player) == 0:
                break
            # randomly select a rejected player to propose the choice
            elif len(reject_player) == 1:
                p = reject_player[0]
            else:
                p = random.choice(reject_player)
            # get that player's most preferred contract and remove it from the preference
            contract = player_acum[p - 1][0, :]
            player_acum[p - 1] = np.delete(player_acum[p - 1], 0, axis=0)
            # locate the corresponding space and add the contract to space' accumulate set
            # =1 means the contract is in the accumulate set
            # =2 means the contract is blocked by a claim contract
            s = contract[1]
            for k in range(space_acum[s - 1].shape[0]):
                if all(space_acum[s - 1][k][0:3] == contract) and space_acum[s - 1][k][3] != 2:
                    space_acum[s - 1][k][3] = 1
                    break
            # for the space selected update the corresponding choice set
            accept_contract = space_acum[s - 1][space_acum[s - 1][:, 3] == 1, :]
            if accept_contract.shape[0] >= 1:
                accept_contract = accept_contract[0]
                space_choi.iloc[s - 1, :] = accept_contract.reshape((4,))
            else:
                continue

            # if the player is resident lock the resident's space with t- contract
            if (p <= r) and (accept_contract[0] == p) and (accept_contract[1] != p) and (accept_contract[2] == 0):
                # send back a claim contract to block the t+ term of the resident's space
                for k in range(space_acum[p - 1].shape[0]):
                    if space_acum[p - 1][k, 0] != p and space_acum[p - 1][k, 2] == 1:
                        # mark the claim contract status = 2
                        space_acum[p - 1][k, 3] = 2
                # the resident's space rerun its choice function
                rerun_contract = space_acum[p - 1][space_acum[p - 1][:, 3] == 1, :]
                if rerun_contract.shape[0] >= 1:
                    rerun_contract = rerun_contract[0]
                    space_choi.iloc[p - 1, :] = rerun_contract.reshape((4,))

                    # check if the new contract also belongs to a residents
                    p2 = rerun_contract[0]
                    if (p2 <= r) and (rerun_contract[1] != p2) and (rerun_contract[2] == 0):
                        for k in range(space_acum[p2 - 1].shape[0]):
                            if space_acum[p2 - 1][k, 0] != p2 and space_acum[p2 - 1][k, 2] == 1:
                                space_acum[p2 - 1][k, 3] = 2
                        rerun_contract2 = space_acum[p2 - 1][space_acum[p2 - 1][:, 3] == 1, :]
                        if rerun_contract2.shape[0] >= 1:
                            rerun_contract2 = rerun_contract2[0]
                            space_choi.iloc[p2 - 1, :] = rerun_contract2.reshape((4,))
                        else:
                            space_choi.iloc[p2 - 1, :] = np.array([0, 0, 0, 0])
                else:
                    space_choi.iloc[p - 1, :] = np.array([0, 0, 0, 0])
            # anyone who hold two contracts, she keeps the preferred one.
            # loop over players in space choices to find the player with two choices
            for k in range(1, n+1):
                player_hold = space_choi[space_choi['player'] == k]
                nrow = player_hold.shape[0]
                if nrow >= 2:
                    # extract the two contracts
                    contract1 = player_hold.iloc[0, :]
                    contract2 = player_hold.iloc[1, :]
                    # loop over players preference to compare the two contracts
                    for m in range(pref_player[k - 1].shape[0]):
                        # if player prefers contract1, remove contract2 from space choice
                        if np.array_equal(contract1[0:3], pref_player[k - 1][m, :]):
                            sp = contract2[1]

                            for l in range(space_choi.shape[0]):
                                if np.array_equal(contract2[0:3], space_choi.iloc[l, 0:3]):
                                    space_choi.iloc[l, :] = np.zeros(4)
                                    break
                            # remove contract2 from space accumulate set
                            for l in range(len(space_acum[sp - 1])):
                                if np.array_equal(contract2[0:3], space_acum[sp - 1][l, 0:3]):
                                    space_acum[sp - 1][l, 3] = 0
                                    break
                            break
                        # if player prefers contract2, remove contract1 from space choice
                        elif np.array_equal(contract2[0:3], pref_player[k - 1][m, :]):
                            sp = contract1[1]
                            for l in range(space_choi.shape[0]):
                                if np.array_equal(contract1[0:3], space_choi.iloc[l, 0:3]):
                                    space_choi.iloc[l, :] = np.zeros(4)
                                    break
                            for l in range(len(space_acum[sp - 1])):
                                if np.array_equal(contract1[0:3], space_acum[sp - 1][l, 0:3]):
                                    space_acum[sp - 1][l, 3] = 0
                                    break
                            break
        return space_choi

    # similar to CO but the players are matched within their own type
    def algo_sm(self, pref_player, pref_space, n, r):
        # get the initial empty accumulate set for each space
        space_acum = pref_space.copy()
        player_acum = pref_player.copy()

        # rebuild the player' preference to separate the markets
        # for residents
        for i in range(r):
            player_acum[i] = player_acum[i][(player_acum[i][:, 1] <= r), :]
        # for visitors
        for i in range(r, n):
            player_acum[i] = player_acum[i][player_acum[i][:, 1] > r, :]
        for i in range(n):
            # add a 4th column to store whether the contract is in the accumulate set
            space_acum[i] = np.column_stack(
                (space_acum[i], np.zeros(space_acum[i].shape[0])))
            space_acum[i] = space_acum[i].astype(int)

        # get the initial empty choice set for each space
        space_choi = np.zeros((n, 4))
        space_choi = pd.DataFrame(
            space_choi, columns=['player', 'space', 'term', 'status'])
        space_choi = space_choi.astype(int)

        # loop for Benchmark mechanism
        for i in range(1000):
            # collect the players without contract
            reject_player = []
            for j in range(1, n + 1):
                if j in space_choi['player'].values:
                    continue
                else:
                    reject_player.append(j)
            # break out of the loop if there is no rejected player
            if len(reject_player) == 0:
                break
            # randomly select a rejected player to propose the choice
            elif len(reject_player) == 1:
                p = reject_player[0]
            else:
                p = random.choice(reject_player)

            # get that player's most preferred contract and remove it from the preference
            contract = player_acum[p - 1][0, :]
            player_acum[p - 1] = np.delete(player_acum[p - 1], 0, axis=0)

            # locate the corresponding space and add the contract to space' accumulate set
            # =1 means the contract is in the accumulate set
            # =2 means the contract is blocked by a claim contract
            s = contract[1]
            for k in range(space_acum[s - 1].shape[0]):
                if all(space_acum[s - 1][k][0:3] == contract) and space_acum[s - 1][k][3] != 2:
                    space_acum[s - 1][k][3] = 1
                    break

            # for the space selected update the corresponding choice set
            accept_contract = space_acum[s - 1][space_acum[s - 1][:, 3] == 1, :]
            if accept_contract.shape[0] >= 1:
                accept_contract = accept_contract[0]
                space_choi.iloc[s - 1, :] = accept_contract.reshape((4,))
            else:
                continue

            # if the player is resident lock the resident's space with t- contract
            if (p <= r) and (accept_contract[0] == p) and (accept_contract[1] != p) and (accept_contract[2] == 0):
                # send back a claim contract to block the t+ term of the resident's space
                for k in range(space_acum[p - 1].shape[0]):
                    if space_acum[p - 1][k, 0] != p and space_acum[p - 1][k, 2] == 1:
                        # mark the claim contract status = 2
                        space_acum[p - 1][k, 3] = 2
                # the resident's space rerun its choice function
                rerun_contract = space_acum[p - 1][space_acum[p - 1][:, 3] == 1, :]
                if rerun_contract.shape[0] >= 1:
                    rerun_contract = rerun_contract[0]
                    space_choi.iloc[p - 1, :] = rerun_contract.reshape((4,))
                else:
                    space_choi.iloc[p - 1, :] = np.array([0, 0, 0, 0])

            # anyone who hold two contracts, she keeps the preferred one.
            # loop over players in space choices to find the player with two choices
            for k in range(1, n+1):
                player_hold = space_choi[space_choi['player'] == k]
                nrow = player_hold.shape[0]
                if nrow >= 2:
                    # extract the two contracts
                    contract1 = player_hold.iloc[0, :]
                    contract2 = player_hold.iloc[1, :]
                    # loop over players preference to compare the two contracts
                    for m in range(pref_player[k - 1].shape[0]):
                        # if player prefers contract1, remove contract2 from space choice
                        if np.array_equal(contract1[0:3], pref_player[k - 1][m, :]):
                            sp = contract2[1]
                            for l in range(space_choi.shape[0]):
                                if np.array_equal(contract2[0:3], space_choi.iloc[l, 0:3]):
                                    space_choi.iloc[l, :] = np.zeros(4)
                                    break
                            # remove contract2 from space accumulate set
                            for l in range(len(space_acum[sp - 1])):
                                if np.array_equal(contract2[0:3], space_acum[sp - 1][l, 0:3]):
                                    space_acum[sp - 1][l, 3] = 0
                                    break
                            break
                        # if player prefers contract2, remove contract1 from space choice
                        elif np.array_equal(contract2[0:3], pref_player[k - 1][m, :]):
                            sp = contract1[1]
                            for l in range(space_choi.shape[0]):
                                if np.array_equal(contract1[0:3], space_choi.iloc[l, 0:3]):
                                    space_choi.iloc[l, :] = np.zeros(4)
                                    break
                            for l in range(len(space_acum[sp - 1])):
                                if np.array_equal(contract1[0:3], space_acum[sp - 1][l, 0:3]):
                                    space_acum[sp - 1][l, 3] = 0
                                    break
                            break
        return space_choi
