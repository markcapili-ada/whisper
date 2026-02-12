from datetime import date, datetime
from typing import Any, Optional, Union, get_args, get_origin, get_type_hints

from annotated_types import MaxLen, MinLen
from flask_restx import fields
from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.fields import FieldInfo, PydanticUndefined, _Unset

from app.extensions.api import api


class BaseRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer('*')
    def serialize_fields(self, v, _info):
        if isinstance(v, str):
            return v.strip()
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(v, date):
            return v.strftime("%Y-%m-%d")
        if isinstance(v, BaseModel):
            return v.model_dump()
        return v

    @classmethod
    def to_restx_model(cls):
        """Convert Pydantic model to Flask-RestX model"""

        def process_field_type(field_name: str, field: Optional[FieldInfo]):
            """Process field type and return RestX field"""
            required = True
            field_type: type = get_type_hints(cls)[field_name]

            if get_origin(field_type) is Union:
                field_type = get_args(field_type)[0]
                required = False

            if field and field.default_factory is _Unset and field.default is PydanticUndefined:
                required = False

            if get_origin(field_type) is list:
                field_type = get_args(field_type)[0]
                return handle_list_type(field_type, field, required)

            if issubclass(field_type, BaseRequest):
                return fields.Nested(field_type.to_restx_model(), required=required)

            return get_field_for_type(field_type, field, required)

        def get_field_for_type(field_type: Any | type, field: Optional[FieldInfo], required: bool):
            """Return RestX field for type"""
            type_to_field = {
                str: fields.String(required=required),
                int: fields.Integer(required=required),
                float: fields.Float(required=required),
                bool: fields.Boolean(required=required),
                date: fields.String(example=date.today().strftime("%Y-%m-%d"), required=required),
                datetime: fields.String(example=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), required=required),
            }

            if not isinstance(field_type, type):
                return fields.String(required=required)

            restx_field: fields.Raw = type_to_field.get(field_type, fields.String(required=required))

            if field and field.description is not _Unset:
                restx_field.description = field.description

            if field and field.examples is not _Unset and field.examples is not None and len(field.examples) > 0:
                restx_field.example = field.examples

            if field and field.metadata:
                for constraint in field.metadata:
                    if isinstance(constraint, MinLen):
                        restx_field.min_items = constraint.min_length
                    if isinstance(constraint, MaxLen):
                        restx_field.max_items = constraint.max_length

            return restx_field

        def handle_list_type(field_type: Any | type, field: Optional[FieldInfo], required: bool):
            """Handle list type and return RestX List field"""
            return fields.List(get_field_for_type(field_type, field, required), required=required)

        restx_fields = {}
        for field_name, field in cls.model_fields.items():
            restx_fields[field_name] = process_field_type(field_name, field)

        return api.model(cls.__name__, restx_fields)
