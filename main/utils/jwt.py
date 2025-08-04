from graphql_jwt.settings import jwt_settings
from graphql_jwt.utils import get_operation_name


def allow_any(info, **kwargs):
    try:
        operation_name = get_operation_name(info.operation.operation).title()
        operation_type = info.schema.get_type(operation_name)

        if not hasattr(operation_type, 'fields'):
            return False

        field = operation_type.fields.get(info.field_name)
        if field is None:
            return False

        graphene_type = getattr(field.type, 'graphene_type', None)

        return graphene_type is not None and issubclass(
            graphene_type, tuple(jwt_settings.JWT_ALLOW_ANY_CLASSES)
        )
    except Exception:
        return False
