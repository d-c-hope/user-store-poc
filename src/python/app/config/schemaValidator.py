import fastjsonschema

# schema = {
# ...     "type" : "array",
# ...     "items" : {"enum" : [1, 2, 3]},
# ...     "maxItems" : 2,
# ... }

coreSchema = {
    "type": "object",
    "properties": {
        "name":      { "type": "string" },
        "email":     { "type": "string" },
        "address":   { "type": "string" },
        "telephone": { "type": "string" }
    },
    "required": ["email"],
    "additionalProperties": False
}

optoutsSchema = {
    "type": "object",
    "properties": {
        "marketing": {"type": "boolean"},
        "pushNotifications": {"type": "boolean"},
    },
    "additionalProperties": False
}

personaSchema = {
    "type": "object",
    "properties": {
        "displayName": {"type": "string"},
    },
    "additionalProperties": False
}

skykidsPersonaSchema = {
    "type": "object",
    "properties": {
        "age" : {"type": "string", "format": "date"},
        "avatar" : {"type": "string"}
    },
    "additionalProperties": False
}

sportsPersonaSchema = {
    "type": "object",
    "properties": {
        "team": {"type": "string"}
    },
    "additionalProperties": False
}

sportsPersonaSchema = {
    "type": "object",
    "properties": {
        "team": {"type": "string"}
    },
    "additionalProperties": False
}

deviceCoreSchema = {
    "type": "object",
    "properties": {
        "deviceName": {"type": "string"}
    },
    "additionalProperties": False
}

deviceSettingsSchema = {
    "type": "object",
    "properties": {
        "volume": {"type": "integer"}
    },
    "additionalProperties": False
}

deviceVideoSettingsSchema = {
    "type": "object",
    "properties": {
        "ratio": {"type": "string"}
    },
    "additionalProperties": False
}

validateCore = fastjsonschema.compile(coreSchema)
validateOptouts = fastjsonschema.compile(optoutsSchema)
validatePersonaCore = fastjsonschema.compile(personaSchema)
validateSkykids = fastjsonschema.compile(skykidsPersonaSchema)
validateSports = fastjsonschema.compile(sportsPersonaSchema)
validateDeviceCore = fastjsonschema.compile(deviceCoreSchema)
validateDeviceSettings = fastjsonschema.compile(deviceSettingsSchema)
validateDeviceVideoSettings = fastjsonschema.compile(deviceVideoSettingsSchema)

validatorMap = {
    "validateCore" : validateCore,
    "validateOptouts" : validateOptouts,
    "validateSkykids" : validateSkykids,
    "validatePersonaCore" : validatePersonaCore,
    "validateSports" : validateSports,
    "validateDeviceCore" : validateDeviceCore,
    "validateDeviceSettings" : validateDeviceSettings,
    "validateDeviceVideoSettings" : validateDeviceVideoSettings
}


if __name__ == "__main__":

    validateCore({'name':'david', "email" : "david.hope@sky.uk", "address": "sky"})
    validateOptouts({"marketing":True, "pushNotifications":True})
    # r = validateOptouts({"test": "object"})
    validateSkykids({'age': "2016-04-22", "avatar": "spongebob"})
    validateSports({'team': 'liverpool'})
