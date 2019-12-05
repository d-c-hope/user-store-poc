# /profile/<profileid>/optouts
# /profile/45a6b18d/optouts
# /profile/me/optouts
# /profile/45a6b18d/persona/2/skykids
# /profile/me/persona/2/skykids
"""
Thoughts:
Most data is just docs like
/profile/45a6b18d/optouts
/profile/45a6b18d/core

We also have personas under profiles
# /profile/45a6b18d/personas/12/optouts
# /profile/45a6b18d/personas/12/skykids/kid
# /profile/<prid>/personas/<pid>/devices/<dname>/accessibility
# /profile/45a6b18d/personas/12/devices/iphone/accessibility

Definition of rules
Note that the fields in sky kids are specific so we don'thave # /profile/45a6b18d/personas/12/<proposion>/kid
We'd want a POST to create the Persona but a PUT to create the device. We wouldn't want the PUT to work if the
persona wasn't already defined. We'd definitely need to be able to get all personas and devices name. What about say all
skykids docs. Would be convenient to get the core doc with this. Could extend later to allow
    personas/all/skykids/kid, i.e. "all" has special meaning (can't be used at the top level)

The idea of this is that we have 2 sets of route config dependent on whether it's a profile or household at the root.
Note this could be more generic with the token type being specified as a field but for now i've separated them.
(Authentication for now is only at the root level of profile or hh, any ids below don't correspond to a token though scopes may limit access)
Under either type we have a set of allowed paths. Any method to a path that isn't in here won't work. So, trying
sub paths between 2 items here won't work like if there is core and core/a/b and you try core/a

An item that is followed by children can't have data at that point. e.g. <profileid>/persona. "persona" here
serves to provide GET access to those items below and for POSTing to

GET rules:
    A GET to an item that has an <id> after it returns all the docs under the ID of the default type

POST rules:
    Can only POST to an item with "portAllowed:True". This is because POST creates an ID for the object being
    If there are any <ids> in the path preceding the path the POST will initially do a GET to check these are present
    A POST should include data for the default type under it, e.g. persona core

POST rules 2:
    Can POST to /optouts - error if already there
    Can POST to /personas - generates new ID
    Can POST to /personas/<id>/optouts if persona exists
    Can't POST to /personas/<id>
    If there are any <ids> in the path preceding the path the POST will initially do a GET to check these are present
    So Can't POST to /personas/<id>/core as previous must exist already and is created by POSTing to /personas
    A POST should include data for the default type under it, e.g. persona core


PUT rules
    What if a user wanted to do PUT /profile/22/persona/4543/skykids. Fails because of the rule that a PUT, like a
    POST always validates the path up to the end of the path
    A PUT to device/<id>/accessibility would fail if the device hadn't been created PUTing to device/id
    Could also PUT to device/core or whatever the default is
"""


routesConfig = {
   "profile": {
       "schema": "validateCore",
       "postAllowed": True,
       "defaultType": "coreprofile",
   },
    "profile/<id>": {
        "schema": "validateCore",
        "defaultType": "coreprofile"
    },
    "profile/<id>/coreprofile" : {
        "schema" : "validateCore",
        "isDefault": True
    },
    "profile/<id>/optouts" : {
        "schema" : "validateOptouts"
    },
    "profile/<id>/device" : {
        "defaultType" : "core",
        "schema" : "validateDeviceCore"
    },
    "profile/<id>/device/<id>" : {
        "schema": "validateDeviceCore",
        "defaultType" : "core"
    },
    "profile/<id>/device/<id>/core": {
        "schema": "validateDeviceCore",
        "isDefault": True
    },
    "profile/<id>/device/<id>/settings" : {
        "schema": "validateDeviceSettings",
    },
    "profile/<id>/device/<id>/settings/video" : {
        "schema": "validateDeviceVideoSettings",
    },
    "profile/<id>/persona" : {
        "schema" : "validatePersonaCore",
        "postAllowed" : True,
        "defaultType" : "core",
    },
    "profile/<id>/persona/<id>" : {
        "schema" : "validatePersonaCore",
        "defaultType" : "core",
        "putCreation" : False
    },
    "profile/<id>/persona/<id>/core" : {
        "schema" : "validatePersonaCore",
        "isDefault": True
    },
    "profile/<id>/persona/<id>/skykids" : {
        "schema" : "validateSkykids"
    },
    "profile/<id>/persona/<id>/sports" : {
        "schema" : "validateSports"
    },
    "profile/<id>/persona/<id>/sports/type/<id>/team": {
        "schema": "validateSports"
    },
    "household": {
        "schema": "validateCore",
        "postAllowed": True,
        "defaultType": "corehh",
    },
    "household/<id>/corehh": {
        "schema": "validateCore",
        "isDefault": True
    },
    "household/<id>/persona/<id>/skykids": {
        "schema": "validateSkykids"
    },
    "household/<id>/device/<id>/accessibility": {
        "schema": "validatePersonaCore",
        "postAllowed": True
    }
}



routesConfigNowTV = {
   "profile": {
       "schema": "validateCore",
       "postAllowed": True,
       "defaultType": "coreprofile",
   },
    "profile/<id>": {
        "schema": "validateCore",
        "defaultType": "coreprofile"
    },
    "profile/<id>/coreprofile" : {
        "schema" : "validateCore",
        "isDefault": True
    },
    "profile/<id>/optouts" : {
        "schema" : "validateOptouts"
    },
    "profile/<id>/persona" : {
        "schema" : "validatePersonaCore",
        "postAllowed" : True,
        "defaultType" : "core",
    },
    "profile/<id>/persona/<id>" : {
        "schema" : "validatePersonaCore",
        "defaultType" : "core",
        "putCreation" : False
    },
    "profile/<id>/persona/<id>/core" : {
        "schema" : "validatePersonaCore",
        "isDefault": True
    }

}

routesConfigs = {
    "sky" : routesConfig,
    "nowtv" : routesConfigNowTV
}





