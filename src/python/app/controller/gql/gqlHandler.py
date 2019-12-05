import graphene
import json
import asyncio
from graphql.execution.executors.asyncio import AsyncioExecutor

from persistance import datastore
from controller.gql.gqlProfileSchema import Profile, CoreProfile, Optouts
from accessRights import authenticator
from controller.gql.utils import checkAccess, makeObjectMap

class Query(graphene.ObjectType):

    profile = graphene.Field(graphene.List(Profile), ids=graphene.List(graphene.String))

    async def resolve_profile(parent, info, ids):
        ptp = info.context["ptp"]
        id = ids[0]
        checkAccess("profile.{}".format(id), "profile.<id>", info.context)

        pData = await datastore.getAllSubDocs("profile.{}".format(id), ptp)
        objectMap = makeObjectMap(pData,(["coreprofile", CoreProfile],["optouts", Optouts]))
        p = Profile(**objectMap)
        p.profileId = ids[0]
        return [p]


schema = graphene.Schema(query=Query)

async def executeQuery(queryString, token, basicAuth, ptp, loop):
    user, tokenClaims = await authenticator.authenticateGQL(token, basicAuth, ptp)
    result = await schema.execute(queryString, context_value={"tokenClaims": token,
                                                        "basicAuthUser": user,
                                                        "ptp": ptp},
                            executor=AsyncioExecutor(loop=loop), return_promise=True)
    return result.data


if __name__ == "__main__":

    queryString = '''
            query profiles {
                profile(ids: ["23"]) {
                    coreprofile {
                        email
                    }
                    optouts {
                        marketing
                    }
                    personas {
                        core {
                            displayName
                        }
                    }
                }
            }
        '''

    from persistance import couchbaseWrapper

    async def initialise():
        await couchbaseWrapper.initialise()

    def executeQuery():
        from config.tenancies import Proposition, Provider, Territory
        ptp = (Provider.SKY, Territory.GB, Proposition.SKYGO)
        result = schema.execute(queryString, context_value={"token": None,
                                                            "basicAuth": None,
                                                            "ptp": ptp}, executor=AsyncioExecutor())
        # result = schema.execute('{ person {first_name} }')
        print(json.dumps(result.data))

    # executeQuery()
    loop = asyncio.get_event_loop()
    rv = loop.run_until_complete(initialise())
    executeQuery()

