from sanic import Sanic
import routes
from controller import httpMethods
import json_logging, logging, sys

json_logging.ENABLE_JSON_LOGGING = True
json_logging.init_sanic()
json_logging.init_request_instrument(routes.app)

logger = logging.getLogger("applogger")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

@routes.app.listener('before_server_start')
async def setup_db(app, loop):
    routes.initialise()
    app.db = await httpMethods.initialise()



if __name__ == "__main__":
    logger.info("App starting up")

    import cProfile, pstats, io

    cProfile.run('routes.app.run(host="0.0.0.0", port=8000)', 'restats3')
    # routes.app.run(host="0.0.0.0", port=8000)
