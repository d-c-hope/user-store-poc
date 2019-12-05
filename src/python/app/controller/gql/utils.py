from accessRights import authenticator


def makeObjectMap(data, pairItems):
    """
    Input like  {'coreprofile': {'email': 'david'}, 'optouts': {'marketing': True}},
    (["coreprofile", CoreProfile],["optouts", Optouts]))
    """
    objectMap = {}
    for pair in pairItems:
        if pair[0] in data:
            obj = pair[1](**data[pair[0]])
            objectMap[pair[0]] = obj
    return objectMap


def checkAccess(resource, resourceType, context):
    basicAuthUser = context["basicAuthUser"]
    tokenClaims = context["tokenClaims"]
