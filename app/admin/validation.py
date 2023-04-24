from jsonschema import validate, ValidationError


def validate_user_data(data):
    user_schema = {
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
            # TODO: Add validation for id > 3, 1 - scheduler, 2 - doctor, 3 - admin
            "level_id": {
                "type": "number",
                "error_msg": "level_id must be number"
            },
            # TODO: Add validation for .com
            "email": {
                "type": "string",
                "error_msg": "email must be text"
            },
            "fullName": {
                "type": "string",
                "error_msg": "fullName must be text"
            },
            "status": {
                "type": "boolean",
                "error_msg": "status must be boolean"
            },
        },
        "required": ["username", "password", "level_id", "email", "full_name"],
    }

    try:
        validate(instance=data, schema=user_schema)
    except ValidationError as err:
        return err.schema["error_msg"] if "error_msg" in err.schema else err.message

    return

