from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .gameSerializers import *
from .roundSerializers import *
from .GameEtl import GameEtl
import os
import logging

log = logging.getLogger(__name__)


def hello(request):
    return HttpResponse("Hello, world.")


@api_view(['GET'])
def get_games(request):
    log.info("Getting all games")
    games = Game.objects.filter(valid=True)
    games = [GameSmallDto.from_game(game) for game in games]
    return Response(GameSmallDtoSerializer(games, many=True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_game(request, game_id):
    log.info(f"Getting game with id: {game_id}")
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    game = GameDto.from_game(game)
    return Response(GameDtoSerializer(game).data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_rounds(request, game_id):
    log.info(f"Getting all rounds for game with id: {game_id}")
    try:
        Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    rounds = [RoundDto.from_round(round_) for round_ in Round.objects.filter(matchid=game_id)]
    return Response(RoundDtoSerializer(rounds, many=True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_round(request, game_id, round_id):
    log.info(f"Getting round with id: {round_id} for game with id: {game_id}")
    try:
        round_ = Round.objects.get(matchid=game_id, roundnum=round_id)
    except Round.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    round_ = RoundDto.from_round(round_)
    return Response(RoundDtoSerializer(round_).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_file(request, name="standard"):
    if "file" not in request.FILES.keys():
        return Response("Missing file in request.", status=status.HTTP_400_BAD_REQUEST)
    file_obj = request.FILES["file"]
    if not file_obj.name.endswith(".dem"):
        return Response("Only .dem files accepted.", status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    log.info(f"Uploading dem file: \"{file_obj.name}\" with given name: \"{name}\"")
    db_con_str = r"mysql+mysqlconnector://" + settings.DATABASES['default']['USER'] + r":" + \
                 settings.DATABASES['default']['PASSWORD'] + r"@" + settings.DATABASES['default']['HOST'] + r"/" + \
                 settings.DATABASES['default']['NAME'] + r"?allow_local_infile=1"
    path = default_storage.save(file_obj.name, ContentFile(file_obj.read()))
    game_etl = GameEtl(directory=settings.MEDIA_ROOT, demo_file=path, match_name=name, db_con_str=db_con_str)
    try:
        game_id = game_etl.etl()
    except Exception as e:
        log.warning(f"Exception occurred while parsing dem file: \"{file_obj.name}\". Exception: {e}")
        os.remove(os.path.join(settings.MEDIA_ROOT, path))
        return Response("Error parsing dem file.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    os.remove(os.path.join(settings.MEDIA_ROOT, path))
    log.info(f"Created new game with id: {game_id}")
    return Response("{game_id: " + str(game_id) + "}", status=status.HTTP_201_CREATED)
