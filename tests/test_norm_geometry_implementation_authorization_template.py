"""Tests for core/norm_geometry_implementation_authorization_template.py (HARDENING)"""

from core.norm_geometry_implementation_authorization_template import (
    NormGeometryImplementationAuthorizationTemplateValidationError,
    ALLOWED_TEMPLATE_STATUS,
)


def test_allowed_status_exists():
    assert isinstance(ALLOWED_TEMPLATE_STATUS, (list, tuple, set)) or ALLOWED_TEMPLATE_STATUS is not None


def test_error_class_exists():
    assert NormGeometryImplementationAuthorizationTemplateValidationError is not None
    assert issubclass(NormGeometryImplementationAuthorizationTemplateValidationError, Exception)
