from jsonschema import validate, ValidationError


def validate_user_data(data):
    schema = {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "error_msg": "username must be text"
            },
            "password": {
                "type": "string",
                "error_msg": "password must be text"
            },
        },
        "required": ["username", "password"],
    }

    try:
        validate(instance=data, schema=schema)
    except ValidationError as err:
        return err.schema["error_msg"] if "error_msg" in err.schema else err.message

    return
