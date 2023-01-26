import tempfile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from ..models import *
from ..gameModelsDto import *
from ..gameSerializers import *
from ..roundModelsDto import *
from ..roundSerializers import *


class GameTests(APITestCase):
    player_dto = PlayerDto(name="test_player", kills=5, assists=4, deaths=3)

    team_dto = TeamDto(name="test_team")
    team_dto.players = [player_dto]

    teams_dto = TeamsDto()
    team_dto.lastTSide = team_dto
    teams_dto.lastCTSide = team_dto

    game_dto = GameDto(name="test_name", createdTimestamp="2023-01-15T15:16:17", map="test_map", roundsPlayed=30)
    game_dto.teams = teams_dto

    game_small_dto = GameDto(name="test_name", createdTimestamp="2023-01-15T15:16:17", map="test_map")

    @patch("csgoanalysis_app.models.Game.objects.filter")
    @patch("csgoanalysis_app.gameModelsDto.GameSmallDto.from_game")
    def test_get_games(self, mock_from_game, mock_games):
        mock_games.return_value = [Game()]
        mock_from_game.return_value = self.game_small_dto

        url = reverse("csgoanalysis_app:get_games")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, GameSmallDtoSerializer([self.game_small_dto], many=True).data)

    @patch("csgoanalysis_app.models.Game.objects.get")
    @patch("csgoanalysis_app.gameModelsDto.GameDto.from_game")
    def test_get_game_ok(self, mock_from_game, mock_game):
        mock_game.return_value = Game()
        mock_from_game.return_value = self.game_dto

        url = reverse("csgoanalysis_app:get_game", args=[1])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, GameDtoSerializer(self.game_dto).data)

    @patch("csgoanalysis_app.models.Game.objects.get")
    def test_get_game_not_found(self, mock_game):
        mock_game.side_effect = Game.DoesNotExist()

        url = reverse("csgoanalysis_app:get_game", args=[1])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, None)


class RoundTests(APITestCase):
    player_dto = PlayerDto(name="test_player", kills=5, assists=4, deaths=3)

    team_dto = TeamDto(name="test_team")
    team_dto.players = [player_dto]

    teams_dto = TeamsDto()
    teams_dto.lastTSide = team_dto
    teams_dto.lastCTSide = team_dto

    game_dto = GameDto(map="test_map", roundsPlayed=30)
    game_dto.teams = teams_dto

    round_player_dto = RoundPlayerDto(id=1, name="test_player", team="test_team")

    round_dto = RoundDto(roundNumber=5, tName="test_t_name", ctName="test_ct_name", tScore=3, ctScore=2, length=100)
    round_dto.players = [round_player_dto]

    @patch("csgoanalysis_app.models.Round.objects.get")
    @patch("csgoanalysis_app.roundModelsDto.RoundDto.from_round")
    def test_get_round_ok(self, mock_from_round, mock_round):
        mock_round.return_value = Round()
        mock_from_round.return_value = self.round_dto

        url = reverse("csgoanalysis_app:get_round", args=[1, 1])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, RoundDtoSerializer(self.round_dto).data)

    @patch("csgoanalysis_app.models.Round.objects.get")
    def test_get_round_not_found(self, mock_round):
        mock_round.side_effect = Round.DoesNotExist()

        url = reverse("csgoanalysis_app:get_round", args=[1, 1])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, None)


class UploadTests(APITestCase):
    @patch("django.core.files.storage.default_storage.save")
    @patch("csgoanalysis_app.GameEtl.GameEtl.etl")
    @patch("os.remove")
    def test_post_upload(self, mock_os_remove, mock_game_etl, mock_storage_save):
        mock_storage_save.return_value = "test_path"
        mock_game_etl.return_value = 1

        with tempfile.NamedTemporaryFile(suffix=".dem") as dem_file:
            dem_file.write(b"testtest")
            dem_file.seek(0)

            url = reverse("csgoanalysis_app:upload_file")
            response = self.client.post(url, data={"file": dem_file}, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data, "{game_id: 1}")

    def test_post_upload_no_file(self):
        url = reverse("csgoanalysis_app:upload_file")
        response = self.client.post(url, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Missing file in request.")

    def test_post_upload_bad_suffix(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as dem_file:
            dem_file.write(b"testtest")
            dem_file.seek(0)

            url = reverse("csgoanalysis_app:upload_file")
            response = self.client.post(url, data={"file": dem_file}, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            self.assertEqual(response.data, "Only .dem files accepted.")

    @patch("django.core.files.storage.default_storage.save")
    @patch("csgoanalysis_app.GameEtl.GameEtl.etl")
    @patch("os.remove")
    def test_post_upload_error_etl(self, mock_os_remove, mock_game_etl, mock_storage_save):
        mock_storage_save.return_value = "test_path"
        mock_game_etl.side_effect = Exception("Test exception.")

        with tempfile.NamedTemporaryFile(suffix=".dem") as dem_file:
            dem_file.write(b"testtest")
            dem_file.seek(0)

            url = reverse("csgoanalysis_app:upload_file")
            response = self.client.post(url, data={"file": dem_file}, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data, "Error parsing dem file.")

    @patch("django.core.files.storage.default_storage.save")
    @patch("csgoanalysis_app.GameEtl.GameEtl.etl")
    @patch("os.remove")
    def test_post_upload_name(self, mock_os_remove, mock_game_etl, mock_storage_save):
        mock_storage_save.return_value = "test_path"
        mock_game_etl.return_value = 1

        with tempfile.NamedTemporaryFile(suffix=".dem") as dem_file:
            dem_file.write(b"testtest")
            dem_file.seek(0)

            url = reverse("csgoanalysis_app:upload_file_name", args=["test_name"])
            response = self.client.post(url, data={"file": dem_file}, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data, "{game_id: 1}")
