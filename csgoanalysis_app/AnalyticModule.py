import json
import logging
import pickle
import numpy as np
import pandas as pd
from awpy.analytics.nav import find_closest_area
from awpy.data import PLACE_DIST_MATRIX, NAV
from sklearn.preprocessing import OneHotEncoder
from lightgbm import LGBMClassifier


class AnalyticModule:
    __slots__ = ["input_data", "model", "db_con", "log", "map_encoder", "bomb_encoder"]

    def __init__(self, model_path):
        with open(model_path, "rb") as handle:
            self.model = pickle.load(handle)
        self.log = logging.getLogger(__name__)
        self.map_encoder = OneHotEncoder(
            categories=[['de_ancient', 'de_dust2', 'de_inferno', 'de_mirage', 'de_nuke', 'de_overpass', 'de_vertigo']],
            sparse=False,
            handle_unknown='ignore')
        self.bomb_encoder = OneHotEncoder(categories=[['A', 'B', 'not_planted']], sparse=False, handle_unknown='ignore')

    def transform_data(self, input_data):
        self.log.info(f"Transforming data")
        sum_cols = self._get_summed_columns(input_data,
                                            ["hp", "armor", "hasHelmet", "DecoyGrenade", "Flashbang", "HEGrenade",
                                             "SmokeGrenade", "fireGrenades", "isBlinded"],
                                            [("ct", "hasDefuse"), ("t", "hasBomb"), ("ct", "isDefusing"),
                                             ("t", "isPlanting")]).reset_index(drop=True)
        dist_cols = self._get_distance_to_bombsites(input_data).reset_index(drop=True)
        spotters_cols = self._get_spotters(input_data).reset_index(drop=True)
        active_weap_cols = self._convert_weapons(input_data, 'activeWeapon').reset_index(drop=True)
        main_weap_cols = self._convert_weapons(input_data, 'mainWeapon').reset_index(drop=True)
        sec_weap_cols = self._convert_sec_weapons(input_data, 'secondaryWeapon').reset_index(drop=True)
        bombsite_col = np.where(input_data['bombsite'] == '', 'not_planted', input_data['bombsite'])
        map_cols = pd.DataFrame(self.map_encoder.fit_transform(input_data[['mapName']]),
                                columns=['de_ancient', 'de_dust2', 'de_inferno', 'de_mirage',
                                         'de_nuke', 'de_overpass', 'de_vertigo']).reset_index(drop=True)
        other_cols = input_data[["seconds", "ctEqVal", "tEqVal", "ctAlivePlayers", "tAlivePlayers"]].reset_index(drop=True)
        bombsite_cols = pd.DataFrame(self.bomb_encoder.fit_transform(bombsite_col.reshape(-1, 1)),
                                     columns=['bombsite_A', 'bombsite_B', 'bombsite_not_planted']).reset_index(drop=True)
        return pd.concat([sum_cols, dist_cols, spotters_cols, active_weap_cols,
                          main_weap_cols, sec_weap_cols, map_cols, bombsite_cols, other_cols], axis=1)

    def get_predictions(self, input_data):
        self.log.info(f"Creating predictions")
        transformed_data = self.transform_data(input_data)
        predictions = self.model.predict_proba(transformed_data)[:, 1]
        return predictions

    @staticmethod
    def _get_summed_columns(input_data, sum_columns: list, team_specific: list) -> pd.DataFrame:
        sum_cols = {}
        for team in ["ct", "t"]:
            for column in sum_columns:
                summed_cols = [f"{team}Player_1_{column}", f"{team}Player_2_{column}", f"{team}Player_3_{column}",
                               f"{team}Player_4_{column}", f"{team}Player_5_{column}"]
                sum_cols[f"{team}_{column}"] = input_data[summed_cols].sum(axis=1)

        for team, column in team_specific:
            summed_cols = [f"{team}Player_1_{column}", f"{team}Player_2_{column}", f"{team}Player_3_{column}",
                           f"{team}Player_4_{column}", f"{team}Player_5_{column}"]
            sum_cols[f"{team}_{column}"] = input_data[summed_cols].sum(axis=1)

        return pd.DataFrame.from_dict(sum_cols)

    @staticmethod
    def _get_distance_to_bombsites(input_data):
        def _get_dist(is_alive, map_name, last_place, position):
            if is_alive:
                if last_place in PLACE_DIST_MATRIX[map_name]:
                    new_place = last_place
                else:
                    area_id = find_closest_area(map_name, position)['areaId']
                    new_place = NAV[map_name][area_id]["areaName"]
                dist_to_a = PLACE_DIST_MATRIX[map_name][new_place]['BombsiteA']['geodesic']['median_dist']
                dist_to_b = PLACE_DIST_MATRIX[map_name][new_place]['BombsiteB']['geodesic']['median_dist']
            else:
                dist_to_a = None
                dist_to_b = None
            return dist_to_a, dist_to_b

        all_parts = []
        for team in ['ct', 't']:
            for i in range(1, 6):
                data = [
                    _get_dist(isAlive, mapName, lastPlace, [x, y, z])
                    for isAlive, mapName, lastPlace, x, y, z in
                    zip(input_data[f'{team}Player_{i}_isAlive'],
                        input_data[f'mapName'],
                        input_data[f'{team}Player_{i}_lastPlaceName'],
                        input_data[f'{team}Player_{i}_x'],
                        input_data[f'{team}Player_{i}_y'],
                        input_data[f'{team}Player_{i}_z'])
                ]
                part = pd.DataFrame.from_records(data,
                                                 columns=[f'{team}Player_{i}_distToA', f'{team}Player_{i}_distToB'])
                all_parts.append(part)

        dist_df = pd.concat(all_parts, axis=1)

        ct_dist_to_a = ["ctPlayer_1_distToA", "ctPlayer_2_distToA", "ctPlayer_3_distToA", "ctPlayer_4_distToA",
                        "ctPlayer_5_distToA"]
        ct_dist_to_b = ["ctPlayer_1_distToB", "ctPlayer_2_distToB", "ctPlayer_3_distToB", "ctPlayer_4_distToB",
                        "ctPlayer_5_distToB"]
        t_dist_to_a = ["tPlayer_1_distToA", "tPlayer_2_distToA", "tPlayer_3_distToA", "tPlayer_4_distToA",
                       "tPlayer_5_distToA"]
        t_dist_to_b = ["tPlayer_1_distToB", "tPlayer_2_distToB", "tPlayer_3_distToB", "tPlayer_4_distToB",
                       "tPlayer_5_distToB"]
        dist_df['ctMinDistToA'] = dist_df[ct_dist_to_a].min(axis=1)
        dist_df['ctMinDistToB'] = dist_df[ct_dist_to_a].min(axis=1)
        dist_df['tMinDistToA'] = dist_df[t_dist_to_a].min(axis=1)
        dist_df['tMinDistToB'] = dist_df[t_dist_to_b].min(axis=1)
        dist_df['ctMeanDistToA'] = dist_df[ct_dist_to_a].mean(axis=1)
        dist_df['ctMeanDistToB'] = dist_df[ct_dist_to_b].mean(axis=1)
        dist_df['tMeanDistToA'] = dist_df[t_dist_to_a].mean(axis=1)
        dist_df['tMeanDistToB'] = dist_df[t_dist_to_b].mean(axis=1)
        res_df = dist_df[
            ['ctMinDistToA', 'ctMinDistToB', 'tMinDistToA', 'tMinDistToB', 'ctMeanDistToA', 'ctMeanDistToB',
             'tMeanDistToA', 'tMeanDistToB']].copy()
        res_df = res_df.fillna(9000)
        return res_df

    @staticmethod
    def _get_spotters(input_data):
        def get_spotted_players(*args):
            spotted = set()
            for arg in args:
                spotted.update(json.loads(arg))
            return len(spotted)

        spotters_parts = []
        for team in ['ct', 't']:
            data = [
                get_spotted_players(spot1, spot2, spot3, spot4, spot5)
                for spot1, spot2, spot3, spot4, spot5 in
                zip(input_data[f'{team}Player_1_spotters'],
                    input_data[f'{team}Player_2_spotters'],
                    input_data[f'{team}Player_3_spotters'],
                    input_data[f'{team}Player_4_spotters'],
                    input_data[f'{team}Player_5_spotters'])
            ]
            part = pd.DataFrame(data, columns=[f'{team}_spottedPlayers'])
            spotters_parts.append(part)
        return pd.concat(spotters_parts, axis=1)

    @staticmethod
    def _convert_weapons(input_data, col):
        pistols = {'Glock-18', 'USP-S', 'P2000', 'P250', 'Dual Berettas'}
        enhanced_pistols = {'CZ75 Auto', 'Five-SeveN', 'Tec-9', 'R8 Revolver'}
        deagle = 'Desert Eagle'
        shotguns = {'MAG-7', 'XM1014', 'Nova', 'Sawed-Off'}
        machine_guns = {'M249', 'Negev'}
        smgs = {'MP9', 'MP7', 'MP5-SD', 'MAC-10', 'UMP-45', 'PP-Bizon', 'P90'}
        weaker_rifles = {'Galil AR', 'SSG 08', 'FAMAS'}
        lunet_rifles = {'SG 553', 'AUG'}
        sniper_rifle = {'G3SG1', 'SCAR-20', 'AWP'}
        assault_rifle = {'M4A1', 'M4A4', 'AK-47'}
        others = {'Zeus x27', 'Knife', 'C4', 'Molotov', 'Incendiary Grenade',
                  'Smoke Grenade', 'Flashbang', 'Decoy Grenade', 'HE Grenade', ''}
        others.update(shotguns, machine_guns)
        weapon_dict = {}
        for team in ['ct', 't']:
            weapon_dict[f"{team}_{col}_Pistol"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_EnhancedPistols"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_Deagle"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_SMG"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_WeakAssaultRifle"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_LunetRifle"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_SniperRifle"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_AssaultRifle"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_Others"] = np.zeros(len(input_data.index))
            for i in range(1, 6):
                weapon_dict[f"{team}_{col}_Pistol"] += input_data[f"{team}Player_{i}_{col}"].isin(pistols).astype(
                    int)
                weapon_dict[f"{team}_{col}_EnhancedPistols"] = input_data[f"{team}Player_{i}_{col}"].isin(
                    enhanced_pistols).astype(int)
                weapon_dict[f"{team}_{col}_Deagle"] += (input_data[f"{team}Player_{i}_{col}"] == deagle).astype(
                    int)
                weapon_dict[f"{team}_{col}_SMG"] += input_data[f"{team}Player_{i}_{col}"].isin(smgs).astype(int)
                weapon_dict[f"{team}_{col}_WeakAssaultRifle"] += input_data[f"{team}Player_{i}_{col}"].isin(
                    weaker_rifles).astype(int)
                weapon_dict[f"{team}_{col}_LunetRifle"] += input_data[f"{team}Player_{i}_{col}"].isin(
                    lunet_rifles).astype(int)
                weapon_dict[f"{team}_{col}_SniperRifle"] += input_data[f"{team}Player_{i}_{col}"].isin(
                    sniper_rifle).astype(int)
                weapon_dict[f"{team}_{col}_AssaultRifle"] += input_data[f"{team}Player_{i}_{col}"].isin(
                    assault_rifle).astype(int)
                weapon_dict[f"{team}_{col}_Others"] += input_data[f"{team}Player_{i}_{col}"].isin(others).astype(
                    int)
        return pd.DataFrame.from_dict(weapon_dict)

    @staticmethod
    def _convert_sec_weapons(input_data, col):
        pistols = {'Glock-18', 'USP-S', 'P2000', 'P250', 'Dual Berettas'}
        enhanced_pistols = {'CZ75 Auto', 'Five-SeveN', 'Tec-9', 'R8 Revolver'}
        deagle = 'Desert Eagle'
        weapon_dict = {}
        for team in ['ct', 't']:
            weapon_dict[f"{team}_{col}_Pistol"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_EnhancedPistols"] = np.zeros(len(input_data.index))
            weapon_dict[f"{team}_{col}_Deagle"] = np.zeros(len(input_data.index))
            for i in range(1, 6):
                weapon_dict[f"{team}_{col}_Pistol"] += input_data[f"{team}Player_{i}_{col}"].isin(pistols).astype(int)
                weapon_dict[f"{team}_{col}_EnhancedPistols"] = input_data[f"{team}Player_{i}_{col}"].isin(
                    enhanced_pistols).astype(int)
                weapon_dict[f"{team}_{col}_Deagle"] += (input_data[f"{team}Player_{i}_{col}"] == deagle).astype(int)
        return pd.DataFrame.from_dict(weapon_dict)
