from awpy import DemoParser
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
import logging
# import warnings
# warnings.filterwarnings("ignore")
os.environ['NUMEXPR_MAX_THREADS'] = '12'


class GameEtl:
    def __init__(self, directory, demo_file, match_name, db_con_str, parse_rate=32, trade_time=5, buy_style="hltv"):
        self.directory = directory
        self.demo_file = demo_file
        self.match_name = match_name
        self.db_con_str = db_con_str
        self.parse_rate = parse_rate
        self.trade_time = trade_time
        self.buy_style = buy_style
        self.log = logging.getLogger(__name__)

    def etl(self):
        self.log.info(f"Openning connection to database: \"{self.db_con_str}\"")
        self.db_con = create_engine(self.db_con_str)
        self.parse()
        self.make_tables()
        self.save_to_db()
        self.db_con.dispose()
        return int(self.match_id)

    def parse(self):
        self.log.info(f"Parsing demo: \"{self.demo_file}\"")
        demo_parser = DemoParser(
            demofile=os.path.join(self.directory, self.demo_file),
            demo_id=self.demo_file[:-4],
            parse_rate=self.parse_rate,
            trade_time=self.trade_time,
            buy_style=self.buy_style,
        )
        self.df_demo = demo_parser.parse(return_type="df")
        self.parsed_demo = demo_parser.json
        self.log.debug(f"Removing demo json file: \"{self.demo_file[:-4]}\".json")
        os.remove(self.demo_file[:-4] + ".json")

    def make_tables(self):
        self.log.info("Creating all tables")
        self.match_info = self.get_match_info()
        self.match_id = self.get_match_id()
        self.players_df = self.get_player_data()
        self.player_id_mapping = self.get_player_mapping()
        self.match_df = self.get_match_data()
        self.player_name_mapping = self.get_player_name_mapping()
        self.kills = self.get_kills(self.df_demo["kills"],
                                    ["attacker", "victim", "assister", "flashThrower", "playerTraded"])
        self.damages = self.get_damages(self.df_demo["damages"], ["attacker", "victim"])
        self.grenades = self.get_dataframe(self.df_demo["grenades"].rename(columns={"throwTick": "tick"}), ["thrower"]
                                           ).rename(columns={"tick": "throwTick"})
        self.flashes = self.get_dataframe(self.df_demo["flashes"], ["attacker", "player"]).drop("matchId", axis=1)
        self.weaponFires = self.get_dataframe(self.df_demo["weaponFires"], ["player"])
        self.bombEvents = self.get_dataframe(self.df_demo["bombEvents"], ["player"]).drop("ID", axis=1)
        self.rounds = self.get_rounds(self.df_demo["rounds"])

    def save_to_db(self):
        self.log.info("Saving all tables to database")
        self.save_to_db_table(self.rounds, "round")
        self.save_to_db_frame()
        self.save_to_db_table(self.kills, "elimination")
        self.save_to_db_table(self.damages, "damage")
        self.save_to_db_table(self.grenades, "grenade")
        self.save_to_db_table(self.flashes, "flash")
        self.save_to_db_table(self.weaponFires, "weaponfire")
        self.save_to_db_table(self.bombEvents, "bombevent")

    def save_to_db_frame(self):
        self.log.debug(f"Saving frame table to database")
        self.match_df.to_csv(os.path.join(self.directory, "frame.csv"), sep=";", encoding='utf-8',
                             index=False, header=False)
        with self.db_con.begin() as connection:
            connection.execute("SET FOREIGN_KEY_CHECKS = 0;")
            connection.execute(r"LOAD DATA LOCAL INFILE '" + self.directory.replace('\\', '/') +
                               r"/frame.csv' INTO TABLE frame "
                               r"CHARACTER SET utf8 FIELDS TERMINATED BY ';' ESCAPED BY '\\';")
        os.remove(os.path.join(self.directory, "frame.csv"))

    def save_to_db_table(self, df, name):
        self.log.debug(f"Saving {name} table to database")
        with self.db_con.connect() as connection:
            connection.execute("SET FOREIGN_KEY_CHECKS = 0;")
            df.to_sql(name=name, con=connection, if_exists="append", index=False)

    def get_team_data(self, frame, team, mapping):
        team_frame = frame[team]
        team_data = {}
        team_data[team + 'Name'] = team_frame['teamName']
        team_data[team + 'EqVal'] = team_frame['teamEqVal']
        team_data[team + 'AlivePlayers'] = team_frame['alivePlayers']
        team_data[team + 'TotalUtility'] = team_frame['totalUtility']

        for player in team_frame['players']:
            mapped_player = mapping[player['steamID']]
            team_data[f"{team}{mapped_player}_ID"] = self.player_id_mapping[str(player['steamID'])]
            for key_player in player:
                if key_player not in ['inventory', 'steamID', 'name', 'team', 'side', 'flashGrenades', 'smokeGrenades',
                                      'heGrenades', 'fireGrenades', 'totalUtility']:
                    team_data[f'{team}{mapped_player}_{key_player}'] = player[key_player]
                elif key_player == 'inventory':
                    team_data[f"{team}{mapped_player}_SmokeGrenade"] = 0
                    team_data[f"{team}{mapped_player}_Flashbang"] = 0
                    team_data[f"{team}{mapped_player}_DecoyGrenade"] = 0
                    team_data[f"{team}{mapped_player}_fireGrenades"] = 0
                    team_data[f"{team}{mapped_player}_HEGrenade"] = 0
                    if player[key_player] is None:
                        team_data[f'{team}{mapped_player}_mainWeapon'] = ''
                        team_data[f'{team}{mapped_player}_secondaryWeapon'] = ''
                    else:
                        for weapon in player[key_player]:
                            if weapon['weaponClass'] == 'Pistols':
                                team_data[f'{team}{mapped_player}_secondaryWeapon'] = weapon['weaponName']
                            elif weapon['weaponClass'] == 'Grenade':
                                if weapon['weaponName'] in {"Molotov", "Incendiary Grenade"}:
                                    team_data[f"{team}{mapped_player}_fireGrenades"] = weapon['ammoInMagazine'] + \
                                                                                       weapon['ammoInReserve']
                                else:
                                    team_data[f"{team}{mapped_player}_{weapon['weaponName'].replace(' ', '')}"] = \
                                        weapon['ammoInMagazine'] + weapon['ammoInReserve']
                            else:
                                team_data[f'{team}{mapped_player}_mainWeapon'] = weapon['weaponName']
                        if f'{team}{mapped_player}_mainWeapon' not in team_data and \
                                f'{team}{mapped_player}_secondaryWeapon' not in team_data:
                            team_data[f'{team}{mapped_player}_mainWeapon'] = ''
                        elif f'{team}{mapped_player}_mainWeapon' not in team_data:
                            team_data[f'{team}{mapped_player}_mainWeapon'] = \
                                team_data[f'{team}{mapped_player}_secondaryWeapon']
        return team_data

    def get_frame_data(self, frame, mapping):
        frame_data = {**self.get_team_data(frame, 'ct', mapping),
                      **self.get_team_data(frame, 't', mapping)}
        frame_data['bombPlanted'] = frame['bombPlanted']
        frame_data['bombsite'] = frame['bombsite']
        frame_data['tick'] = frame['tick']
        frame_data['seconds'] = frame['seconds']
        frame_data['clockTime'] = frame['clockTime']
        bomb_data = frame['bomb']
        for key in bomb_data:
            frame_data[f"bomb_{key}"] = bomb_data[key]
        return frame_data

    def create_mapping(self, round_):
        ct_players = round_['ctSide']
        map_steam_id = {}
        for i, player in enumerate(ct_players['players']):
            map_steam_id[player['steamID']] = f'Player_{i + 1}'

        t_players = round_['tSide']
        for i, player in enumerate(t_players['players']):
            map_steam_id[player['steamID']] = f'Player_{i + 1}'

        return map_steam_id

    def get_match_data(self):
        self.log.debug("Creating frame table")
        data = self.parsed_demo
        data_list = []
        mapping = self.create_mapping(data['gameRounds'][0])
        for round_ in data['gameRounds']:
            for frame in round_['frames']:
                converted_vector = self.get_frame_data(frame, mapping)
                converted_vector['roundNum'] = round_['roundNum']
                data_list.append(converted_vector)
            last_tick = round_['endTick']

        frame_columns = []
        with open('frame_columns', 'r') as f:
            for line in f.readlines():
                frame_columns.append(line[:-1])
        res = pd.DataFrame(data_list, columns=frame_columns)
        res.fillna(method='ffill', inplace=True)
        for col in res.columns:
            if type(res[col][0]) == list:
                res[col] = res[col].astype('str')
        res["matchID"] = self.match_id
        res = res.sort_index(axis=1)
        for col in res.columns:
            if res[col].dtypes == "bool":
                res[col] = res[col].replace({False: "", True: "1"})
        return res

    def get_player_data(self):
        self.log.debug("Creating player table")
        players_df = self.df_demo["playerFrames"][["steamID", "name", "teamName"]]
        return players_df.drop_duplicates()

    def get_player_id_from_db(self, row):
        return pd.read_sql(sql=f'SELECT ID FROM player '
                               f'WHERE steamID = \"{row["steamID"]}\" AND '
                               f'name = \"{row["name"]}\" AND '
                               f'teamName = \"{row["teamName"]}\"', con=self.db_con)

    def get_player_id(self, row):
        self.log.debug(f'Getting player id for player: {row["name"]}')
        player_id = self.get_player_id_from_db(row)
        if player_id.empty:
            row.to_frame().T.to_sql(name="player", con=self.db_con, if_exists="append", index=False)
            player_id = self.get_player_id_from_db(row)
        self.log.debug(f'Player: \"{row["name"]}\" id is: {player_id.iloc[0, 0]}')
        return player_id.iloc[0, 0]

    def get_player_mapping(self):
        mapping = dict(zip(self.players_df["steamID"].astype('str'),
                           self.players_df.apply(lambda x: self.get_player_id(x), axis=1)))
        mapping["None"] = np.nan
        mapping["<NA>"] = np.nan
        mapping[""] = np.nan
        return mapping

    def get_player_name_mapping(self):
        return dict(zip(self.players_df["name"], self.players_df["steamID"].astype("str")))

    def get_match_info(self):
        self.log.debug("Creating game table")
        df_demo = self.df_demo
        return pd.DataFrame(dict(zip(['demoName', 'matchName', 'clientName', 'mapName', 'tickRate', 'playbackTicks',
                                      'parseRate'],
                                     [df_demo['matchID'], self.match_name, df_demo['clientName'], df_demo['mapName'],
                                      df_demo['tickRate'], df_demo['playbackTicks'], self.parse_rate])), index=[0])

    def get_match_id_from_db(self):
        match_info = self.match_info
        return pd.read_sql(sql=f'SELECT ID FROM game WHERE demoName = \"{match_info["demoName"][0]}\" AND '
                               f'matchName = \"{match_info["matchName"][0]}\" AND '
                               f'clientName = \"{match_info["clientName"][0]}\" AND '
                               f'parseRate = \"{match_info["parseRate"][0]}\"', con=self.db_con)

    def get_match_id(self):
        self.log.debug("Getting game id")
        match_id = self.get_match_id_from_db()
        if match_id.empty:
            self.match_info.to_sql(name="game", con=self.db_con, if_exists="append", index=False)
            match_id = self.get_match_id_from_db()
        self.log.debug(f"Game id is {match_id.iloc[0, 0]}")
        return match_id.iloc[0, 0]

    def get_dataframe(self, df, player_types):
        self.log.debug("Creating basic table")
        ticks = self.match_df["tick"]
        df = df.drop("mapName", axis=1)
        columns = ["Name", "Team"]
        to_drop = [player + col for player in player_types for col in columns]
        df = df.drop(to_drop, axis=1)
        for player in player_types:
            df[player + "SteamID"] = df[player + "SteamID"].astype("str")
            df = df.replace({player + "SteamID": self.player_id_mapping}) \
                .rename(columns={player + "SteamID": player + "ID"})
            df[player + "ID"] = df[player + "ID"].astype("Int64")
        df["tick_parsed"] = df["tick"].apply(lambda x: ticks[np.argmin(np.abs(ticks - x))])
        df["matchID"] = self.match_id
        df["ID"] = range(1, df.shape[0] + 1)
        return df

    def get_kills(self, df, player_types):
        self.log.debug("Creating elimination table")
        for player in ["attacker", "assister", "flashThrower", "playerTraded"]:
            df = df.replace({player + "Name": self.player_name_mapping})
            df[player + "SteamID"] = df[player + "Name"]
        return self.get_dataframe(df, player_types)

    def get_damages(self, df, player_types):
        self.log.debug("Creating damage table")
        df = df.replace({"attackerName": self.player_name_mapping})
        df["attackerSteamID"] = df["attackerName"]
        df["zoomLevel"] = df["zoomLevel"].fillna(0).astype("Int64")
        return self.get_dataframe(df, player_types)

    def get_rounds(self, df):
        self.log.debug("Creating round table")
        df["matchID"] = self.match_id
        df.loc[df['startTick'] < 0, 'startTick'] = 0
        end_t = self.parsed_demo['matchPhases']['roundEnded']
        if len(end_t) != df.shape[0]:
            ind = [None] * len(end_t)
            for i, tick in enumerate(end_t):
                ind[i] = (df['endTick'] - tick).abs().min()
            ind = pd.Series(ind)
            ind = list(ind.nlargest(abs(len(end_t) - df.shape[0])).index.sort_values(ascending=False))
            for i in ind:
                del end_t[i]
        df['endTickCorrect'] = end_t
        return df.drop("mapName", axis=1)
