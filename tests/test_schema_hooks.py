"""Tests for schema hooks."""


class TestBaseSerializerExtension:
    """Tests for BaseSerializerExtension."""

    def test_extension_class_exists(self):
        """Test that extension class can be imported."""
        from ennam_django_apidog.schema_hooks import BaseSerializerExtension

        assert BaseSerializerExtension is not None
        assert BaseSerializerExtension.target_class == "rest_framework.serializers.BaseSerializer"
        assert BaseSerializerExtension.match_subclasses is True

    def test_map_serializer_returns_object_schema(self):
        """Test that map_serializer returns valid object schema."""
        from rest_framework import serializers

        from ennam_django_apidog.schema_hooks import BaseSerializerExtension

        class TestSerializer(serializers.BaseSerializer):
            def to_representation(self, instance):
                return {"id": instance.id}

        # Create an instance to test
        serializer = TestSerializer()

        # Create extension instance (mock the target)
        extension = BaseSerializerExtension.__new__(BaseSerializerExtension)
        extension.target = serializer

        # Call map_serializer
        result = extension.map_serializer(None, "response")

        assert result["type"] == "object"
        assert "description" in result
        assert result["additionalProperties"] is True


class TestPreprocessHook:
    """Tests for preprocess hook."""

    def test_preprocess_returns_endpoints(self):
        """Test that preprocess hook returns endpoints unchanged."""
        from ennam_django_apidog.schema_hooks import preprocess_exclude_problematic_views

        endpoints = [
            ("/api/v1/users/", None, "GET", None),
            ("/api/v1/posts/", None, "POST", None),
        ]

        result = preprocess_exclude_problematic_views(endpoints)

        assert result == endpoints
        assert len(result) == 2

    def test_preprocess_with_empty_list(self):
        """Test preprocess with empty endpoints list."""
        from ennam_django_apidog.schema_hooks import preprocess_exclude_problematic_views

        result = preprocess_exclude_problematic_views([])
        assert result == []
