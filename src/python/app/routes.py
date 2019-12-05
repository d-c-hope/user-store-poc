from controller import httpMethods
from sanic import Sanic
from sanic import response
from sanic.exceptions import ServerError, Forbidden, NotFound, InvalidUsage, abort
from sanic.response import json
from controller.httpMethods import InvalidRequestException, ForbiddenException, NotFoundException, SchemaException
from persistance.datastore import AlreadyExistsException, IndexDocsException
import logging
logger = logging.getLogger("applogger")
import prometheus_client as prometheus
from prometheus_client import Counter, Histogram, Gauge
import time


app = Sanic()
global metrics



def getToken(request):
    token = None
    if "x-token" in request.headers:
        token = request.headers["x-token"]
    return token

def getBasicAuth(request):
    return request.token

# maybe put in a decorator
async def wrapCall(c):
    """
    Does the error handling, interpreting the various custom exceptions
    """

    doAbort = -1

    try:
        r = await c()
        if r["status"] == 200:
            body = r["body"]
            return response.json(body)
        else:
            logger.info("Server error decoding json response")
            doAbort = 500
            # raise ServerError("Something bad happened", status_code=500)
    except InvalidRequestException as e:
        logger.info("Invalid request failure")
        raise InvalidUsage() from None
    except SchemaException:
        logger.info("Schema failure")
        raise InvalidUsage() from None
    except ForbiddenException as e:
        logger.info("Forbidden")
        raise Forbidden("Forbidden") from None
    except NotFoundException as e:
        logger.info("Not found")
        raise NotFound() from None
    except AlreadyExistsException:
        logger.info("Already exists")
        doAbort = 409
    except IndexDocsException:
        logger.info("Index docs exception")
        doAbort = 500
    except Exception:
        logger.info("Server error")
        doAbort = 500

    if doAbort != -1:
        abort(doAbort)



@app.route("/")
async def test(request):
    return json({"test": "endpoint"})


@app.middleware('request')
async def before_request(request):
    if request.path != "/metrics" and request.method != "OPTIONS":
        request['__START_TIME__'] = time.time()

@app.middleware('response')
async def before_response(request, response):
    if request.path != "/metrics" and request.method != "OPTIONS":
        # metrics.after_request_handler(request, response, get_endpoint)

        lat = time.time() - request['__START_TIME__']
        print("lat was: {}".format(lat))
        endpoint = request.path

        # Note, that some handlers can ignore response logic,
        # for example, websocket handler
        response_status = response.status if response else 200
        metrics['RQS_LATENCY'].labels(request.method, endpoint,
                                      response_status).observe(lat)
        metrics['RQS_COUNT'].labels(request.method, endpoint,
                                    response_status).inc()


# Expose the metrics for prometheus
@app.get("/metrics")
async def metrics(request):
    output = prometheus.exposition.generate_latest().decode("utf-8")
    content_type = prometheus.exposition.CONTENT_TYPE_LATEST
    return response.text(body=output,
                         content_type=content_type)


@app.route("/graphql", methods=['POST'])
async def graphqlQuery(request):
    token = getToken(request)
    basicAuth = getBasicAuth(request)
    body = str(request.body, 'utf-8')
    r = await httpMethods.graphql(body, token, basicAuth, request.headers, app.loop)
    return response.json(r)

@app.route("/revokelist", methods=['PUT'])
async def revokelist(request):
    basicAuth = getBasicAuth(request)
    r = await httpMethods.revokelist(request.json, basicAuth, request.headers)
    return response.json(r)

@app.route('<urlpath:path>', methods=['GET'])
async def docGet(request, urlpath):
    token = getToken(request)
    basicAuth = getBasicAuth(request)
    c = lambda: httpMethods.dataGet(urlpath, token, basicAuth, request.headers)
    return await wrapCall(c)


@app.route('<urlpath:path>', methods=['POST'])
async def docPost(request, urlpath):

    token = getToken(request)
    basicAuth = getBasicAuth(request)
    c = lambda: httpMethods.dataPost(urlpath, request.json, token, basicAuth, request.headers)
    return await wrapCall(c)


@app.route('<urlpath:path>', methods=['PUT'])
async def docPut(request, urlpath):

    token = getToken(request)
    basicAuth = getBasicAuth(request)
    c = lambda: httpMethods.dataPut(urlpath, request.json, token, basicAuth, request.headers)
    return await wrapCall(c)


@app.route('<urlpath:path>', methods=['DELETE'])
async def docDelete(request, urlpath):

    token = getToken(request)
    basicAuth = getBasicAuth(request)
    c = lambda: httpMethods.dataDelete(urlpath, token, basicAuth, request.headers)
    return await wrapCall(c)


def initialise():
    global metrics
    metrics = {}
    metrics['RQS_COUNT'] = Counter(
        'sanic_request_count',
        'Sanic Request Count',
        ['method', 'endpoint', 'http_status']
    )
    metrics['RQS_LATENCY'] = Histogram(
        'sanic_request_latency_sec',
        'Sanic Request Latency Histogram',
        ['method', 'endpoint', 'http_status'],
    )