import argparse

from aiohttp import web
import aiohttp_cors

from .app import create_app
from .handlers import APIHandler

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Time-series service")
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default='8000')

    args = parser.parse_args()

    app = create_app()

    handler = APIHandler()
    app.router.add_get("/chart/contribution/{username}", handler.chart_user_contribution)
    app.router.add_get("/get_top_contributors", handler.get_top_contributors)

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    # Configure CORS on all routes.
    for route in list(app.router.routes()):
        cors.add(route)

    web.run_app(app, host=args.host, port=args.port)
