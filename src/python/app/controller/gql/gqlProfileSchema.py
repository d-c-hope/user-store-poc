import graphene
from persistance import datastore
from controller.gql.utils import *

class CoreProfile(graphene.ObjectType):
    name = graphene.String()
    email = graphene.String()

class Optouts(graphene.ObjectType):
    marketing = graphene.String()
    pushNotifications = graphene.String()

class PersonaCore(graphene.ObjectType):
    displayName = graphene.String()

class Persona(graphene.ObjectType):
    core = graphene.Field(PersonaCore)

class Profile(graphene.ObjectType):
    coreprofile = graphene.Field(CoreProfile)
    optouts = graphene.Field(Optouts)
    personas = graphene.Field(graphene.List(Persona),
                              ids=graphene.List(graphene.String, required=False))

    async def resolve_personas(parent, info, ids=None):

        ptp = info.context["ptp"]
        personaDicts = await datastore.getAllGQL("profile.{}.persona".format(parent.profileId),
                                             ["core", "skykids"], ptp)
        personas = []
        for key, personaDict in personaDicts.items():
            objectMap = makeObjectMap(personaDict, ((["core", PersonaCore]),))
            p = Persona(**objectMap)
            personas.append(p)

        return personas
