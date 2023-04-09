import logging
import requests

from celery import shared_task
from django.core.cache import cache

from . import app_settings, constants

TZ_STRING = "%Y-%m-%dT%H:%M:%SZ"

logger = logging.getLogger(__name__)

# Sync Losses


@shared_task
def sqb_sync_losses():
    _stats_request = requests.get(
        "https://zkillboard.com/api/stats/allianceID/" + str(app_settings.SQUATBOT_ALLIANCE) + "/")
    _stats_json = _stats_request.json()
    stats = _stats_json.get("months", {})
    cache.set(constants.LOSS_KEY, stats, 60*60*24*30)
    return stats
