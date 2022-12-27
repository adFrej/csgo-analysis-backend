from django.test import TestCase
from unittest.mock import patch
from django_mock_queries.query import MockSet

from ..models import *
from ..gameModelsDto import *
from ..gameSerializers import *
from ..roundModelsDto import *
from ..roundSerializers import *


class ModelsTests(TestCase):
    game = Game(id=1, mapname="test_map")

    player_1 = Player(id=1, name="test_player1")
    player_2 = Player(id=2, name="test_player2")
    player_3 = Player(id=3, name="test_player3")
    player_4 = Player(id=4, name="test_player4")
    player_5 = Player(id=5, name="test_player5")
    player_6 = Player(id=6, name="test_player6")
    player_7 = Player(id=7, name="test_player7")
    player_8 = Player(id=8, name="test_player8")
    player_9 = Player(id=9, name="test_player9")
    player_10 = Player(id=10, name="test_player10")

    frame = Frame(matchid_id=game.id, ctplayer_1=player_1, ctplayer_2=player_2, ctplayer_3=player_3,
                  ctplayer_4=player_4, ctplayer_5=player_5, tplayer_1=player_6,
                  tplayer_2=player_7, tplayer_3=player_8, tplayer_4=player_9,
                  tplayer_5=player_10, clocktime="01:50", roundnum=1, tick=64,
                  **{f"ctplayer_{i}_equipmentvaluefreezetimeend": i * 1000 for i in range(1, 6)},
                  **{f"tplayer_{i}_equipmentvaluefreezetimeend": i * 1000 for i in range(1, 6)},
                  **{f"ctplayer_{i}_armor": (i % 2) * 100 for i in range(1, 6)},
                  **{f"tplayer_{i}_armor": (i % 2) * 100 for i in range(1, 6)},
                  **{f"ctplayer_{i}_hasdefuse": True for i in range(1, 6)},
                  **{f"tplayer_{i}_hasdefuse": False for i in range(1, 6)},
                  **{f"ctplayer_{i}_hashelmet": False for i in range(1, 6)},
                  **{f"tplayer_{i}_hashelmet": True for i in range(1, 6)},
                  **{f"ctplayer_{i}_hp": 100 for i in range(1, 6)},
                  **{f"tplayer_{i}_hp": 90 for i in range(1, 6)},
                  **{f"ctplayer_{i}_isblinded": False for i in range(1, 6)},
                  **{f"tplayer_{i}_isblinded": True for i in range(1, 6)},
                  **{f"ctplayer_{i}_mainweapon": "test_weapon" for i in range(1, 6)},
                  **{f"tplayer_{i}_mainweapon": "test_weapon" for i in range(1, 6)},
                  **{f"ctplayer_{i}_viewx": 50 for i in range(1, 6)},
                  **{f"tplayer_{i}_viewx": 60 for i in range(1, 6)},
                  **{f"ctplayer_{i}_x": 1000 for i in range(1, 6)},
                  **{f"tplayer_{i}_x": 900 for i in range(1, 6)},
                  **{f"ctplayer_{i}_y": 800 for i in range(1, 6)},
                  **{f"tplayer_{i}_y": 700 for i in range(1, 6)})

    mock_eliminations = MockSet(
        Elimination(matchid_id=frame.matchid_id, attackerid=1, assisterid=2, victimid=6),
        Elimination(matchid_id=frame.matchid_id, attackerid=1, assisterid=3, victimid=7),
        Elimination(matchid_id=frame.matchid_id, attackerid=2, assisterid=1, victimid=10),
        Elimination(matchid_id=frame.matchid_id, attackerid=8, assisterid=9, victimid=1))
    patch_eliminations = patch("csgoanalysis_app.models.Elimination.objects", mock_eliminations)

    round = Round(matchid_id=game.id, roundnum=frame.roundnum, tteam="test_tteam", ctteam="test_ctteam", tscore=0, ctscore=0)

    mock_rounds = MockSet(
        round,
        Round(matchid_id=game.id, roundnum=2, tteam="test_tteam", ctteam="test_ctteam"),
        Round(matchid_id=game.id, roundnum=3, tteam="test_tteam", ctteam="test_ctteam"),
        Round(matchid_id=game.id, roundnum=4, tteam="test_tteam", ctteam="test_ctteam"),
        Round(matchid_id=game.id, roundnum=5, tteam="test_tteam", ctteam="test_ctteam"))
    patch_rounds = patch("csgoanalysis_app.models.Round.objects", mock_rounds)

    mock_frame = MockSet(frame,
                         Frame(matchid_id=game.id, ctplayer_1=player_1, ctplayer_2=player_2, ctplayer_3=player_3,
                               ctplayer_4=player_4, ctplayer_5=player_5, tplayer_1=player_6,
                               tplayer_2=player_7, tplayer_3=player_8, tplayer_4=player_9,
                               tplayer_5=player_10, clocktime="01:50", roundnum=1, tick=96,
                               **{f"ctplayer_{i}_equipmentvaluefreezetimeend": i * 1000 for i in range(1, 6)},
                               **{f"tplayer_{i}_equipmentvaluefreezetimeend": i * 1000 for i in range(1, 6)},
                               **{f"ctplayer_{i}_armor": (i % 2) * 100 for i in range(1, 6)},
                               **{f"tplayer_{i}_armor": (i % 2) * 100 for i in range(1, 6)},
                               **{f"ctplayer_{i}_hasdefuse": True for i in range(1, 6)},
                               **{f"tplayer_{i}_hasdefuse": False for i in range(1, 6)},
                               **{f"ctplayer_{i}_hashelmet": False for i in range(1, 6)},
                               **{f"tplayer_{i}_hashelmet": True for i in range(1, 6)},
                               **{f"ctplayer_{i}_hp": 100 for i in range(1, 6)},
                               **{f"tplayer_{i}_hp": 90 for i in range(1, 6)},
                               **{f"ctplayer_{i}_isblinded": False for i in range(1, 6)},
                               **{f"tplayer_{i}_isblinded": True for i in range(1, 6)},
                               **{f"ctplayer_{i}_mainweapon": "test_weapon" for i in range(1, 6)},
                               **{f"tplayer_{i}_mainweapon": "test_weapon" for i in range(1, 6)},
                               **{f"ctplayer_{i}_viewx": 50 for i in range(1, 6)},
                               **{f"tplayer_{i}_viewx": 60 for i in range(1, 6)},
                               **{f"ctplayer_{i}_x": 1000 for i in range(1, 6)},
                               **{f"tplayer_{i}_x": 900 for i in range(1, 6)},
                               **{f"ctplayer_{i}_y": 800 for i in range(1, 6)},
                               **{f"tplayer_{i}_y": 700 for i in range(1, 6)}))
    patch_frame = patch("csgoanalysis_app.models.Frame.objects", mock_frame)

    mock_weaponfire = MockSet(
        Weaponfire(matchid_id=game.id, roundnum=round.roundnum, playerid=player_6.id, tick_parsed_id=frame.tick))
    patch_weaponfire = patch("csgoanalysis_app.models.Weaponfire.objects", mock_weaponfire)

    @patch_eliminations
    def test_player_dto_create(self):
        result = PlayerDto.create(self.player_1, self.frame.matchid_id)

        self.assertEqual(result.name, self.player_1.name)
        self.assertEqual(result.kills, 2)
        self.assertEqual(result.assists, 1)
        self.assertEqual(result.deaths, 1)

    @patch_rounds
    @patch_frame
    @patch_eliminations
    def test_game_dto_from_game(self):
        result = GameDto.from_game(self.game)

        self.assertEqual(result.map, self.game.mapname)
        self.assertEqual(result.roundsPlayed, 5)
        self.assertEqual(result.teams.lastTSide.name, "test_ctteam")
        self.assertEqual(result.teams.lastCTSide.name, "test_tteam")
        self.assertEqual(result.teams.lastTSide.players[0].name, self.player_1.name)
        self.assertEqual(result.teams.lastCTSide.players[0].name, self.player_6.name)
        self.assertEqual(result.teams.lastTSide.players[1].name, self.player_2.name)
        self.assertEqual(result.teams.lastCTSide.players[1].name, self.player_7.name)

    @patch_frame
    @patch_weaponfire
    def test_round_dto_from_round(self):
        result = RoundDto.from_round(self.round)

        self.assertEqual(result.roundNumber, self.round.roundnum)
        self.assertEqual(result.tName, self.round.tteam)
        self.assertEqual(result.ctName, self.round.ctteam)
        self.assertEqual(result.tScore, self.round.tscore)
        self.assertEqual(result.ctScore, self.round.ctscore)
        self.assertEqual(result.length, 2)
        self.assertEqual(result.clockTime, ["01:50"]*2)
        self.assertEqual(result.CTpredictions, [0, 1])
        self.assertEqual(result.players[0].id, 0)
        self.assertEqual(result.players[0].name, "test_player6")
        self.assertEqual(result.players[0].team, "T")
        self.assertEqual(result.players[0].equipmentValueFreezetimeEnd, 1000)
        self.assertEqual(result.players[0].fires, [True, False])
        self.assertEqual(result.players[0].hasArmor, True)
        self.assertEqual(result.players[0].hasDef, [False] * 2)
        self.assertEqual(result.players[0].hasHelmet, True)
        self.assertEqual(result.players[0].hp, [90]*2)
        self.assertEqual(result.players[0].isBlinded, [True] * 2)
        self.assertEqual(result.players[0].mainWeapon, ["test_weapon"] * 2)
        self.assertEqual(result.players[0].viewx, [60]*2)
        self.assertEqual(result.players[0].x, [900]*2)
        self.assertEqual(result.players[0].y, [700]*2)
