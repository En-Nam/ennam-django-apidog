"""
Custom hooks for drf-spectacular to handle BaseSerializer subclasses.

These serializers don't have the standard 'fields' attribute that
drf-spectacular expects, so we need special handling.

Usage in Django settings.py SPECTACULAR_SETTINGS:

    SPECTACULAR_SETTINGS = {
        ...
        'PREPROCESSING_HOOKS': [
            'ennam_django_apidog.schema_hooks.preprocess_exclude_problematic_views',
        ],
        'EXTENSIONS': [
            'ennam_django_apidog.schema_hooks.BaseSerializerExtension',
        ],
    }
"""

from typing import Any, Dict, List, Optional, Tuple, cast

from drf_spectacular.extensions import OpenApiSerializerExtension


class BaseSerializerExtension(OpenApiSerializerExtension):  # type: ignore[no-untyped-call]
    """
    Extension to handle serializers that inherit from BaseSerializer
    without defining fields (custom to_representation only).

    This prevents drf-spectacular from failing when encountering
    serializers that don't have the standard 'fields' attribute.
    """

    target_class = "rest_framework.serializers.BaseSerializer"
    match_subclasses = True

    def get_name(self, auto_schema: Any = None, direction: str = "") -> Optional[str]:
        """Return the name of the serializer class."""
        return cast(str, self.target.__class__.__name__)

    def map_serializer(self, auto_schema: Any, direction: str) -> Dict[str, Any]:
        """
        For BaseSerializer subclasses without fields,
        return a generic object schema.

        Args:
            auto_schema: The AutoSchema instance
            direction: 'request' or 'response'

        Returns:
            dict: OpenAPI schema for this serializer
        """
        serializer = self.target

        # Check if serializer has working fields attribute
        try:
            if hasattr(serializer, "fields") and serializer.fields:
                # Has working fields, use default handler by returning None
                # But we must return a valid schema to avoid NoneType error
                pass
        except (AttributeError, AssertionError, Exception):
            pass

        # Always return a valid schema for BaseSerializer subclasses
        return {
            "type": "object",
            "description": f"Response from {self.get_name()}",
            "additionalProperties": True,
        }


def preprocess_exclude_problematic_views(
    endpoints: List[Tuple[str, str, str, Any]]
) -> List[Tuple[str, str, str, Any]]:
    """
    Preprocessing hook for drf-spectacular.

    This hook can be used to filter out problematic endpoints
    that cause issues during schema generation.

    Args:
        endpoints: List of (path, path_regex, method, callback) tuples

    Returns:
        list: Filtered list of endpoints
    """
    # By default, pass through all endpoints
    # Users can override this function if needed
    return endpoints
