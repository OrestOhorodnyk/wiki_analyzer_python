from pathlib import Path
from datetime import datetime

config_path = Path(__file__).parent.parent.parent.absolute().joinpath("logs").joinpath(
    "_{:D%Y%m%d_T%H%M%S}.log".format(datetime.now()))

config = {
    "logger": {
        "path": config_path,
        "filename": "access.log",
        "level": "info",
        "rotation": "20 days",
        "retention": "1 months",
        "format": "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> request id: {extra[request_id]} - <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    }
}
