import pytest
from django.contrib.auth import password_validation
from django.test import override_settings
from users.forms import RegisterForm


@pytest.fixture(autouse=True)
def _recaptcha_and_cache(settings):
    settings.RECAPTCHA_PUBLIC_KEY = "test"
    settings.RECAPTCHA_PRIVATE_KEY = "test"
    password_validation.get_default_password_validators.cache_clear()
    yield
    password_validation.get_default_password_validators.cache_clear()


@pytest.mark.django_db
def test_register_password_too_short():
    form = RegisterForm(
        data={
            "email": "user@example.com",
            "first_name": "Juan",
            "last_name": "Perez",
            "birth_date": "2000-01-01",
            "country": "AR",
            "province": "1",
            "password1": "abc",
            "password2": "abc",
            "terms": True,
            "g-recaptcha-response": "test",
        }
    )
    assert not form.is_valid()
    errors = form.errors or {}
    assert (
        errors.get("password2", [None])[0]
        == "La contraseña es demasiado corta. Debe contener por lo menos 8 caracteres."
    )


@pytest.mark.django_db
def test_register_password_common():
    form = RegisterForm(
        data={
            "email": "user@example.com",
            "first_name": "Juan",
            "last_name": "Perez",
            "birth_date": "2000-01-01",
            "country": "AR",
            "province": "1",
            "password1": "password",
            "password2": "password",
            "terms": True,
            "g-recaptcha-response": "test",
        }
    )
    assert not form.is_valid()
    errors = form.errors or {}
    assert (
        errors.get("password2", [None])[0]
        == "La contraseña tiene un valor demasiado común."
    )


@pytest.mark.django_db
def test_register_password_numeric():
    with override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
            },
        ]
    ):
        password_validation.get_default_password_validators.cache_clear()
        form = RegisterForm(
            data={
                "email": "user@example.com",
                "first_name": "Juan",
                "last_name": "Perez",
                "birth_date": "2000-01-01",
                "country": "Argentina",
                "province": "Salta",
                "password1": "9876543210",
                "password2": "9876543210",
                "terms": True,
                "g-recaptcha-response": "test",
            }
        )
        assert not form.is_valid()
        errors = form.errors or {}
        assert (
            errors.get("password2", [None])[0]
            == "La contraseña está formada completamente por dígitos."
        )


@pytest.mark.django_db
def test_register_password_similar_to_email():
    form = RegisterForm(
        data={
            "email": "juan@example.com",
            "first_name": "Juan",
            "last_name": "Perez",
            "birth_date": "2000-01-01",
            "country": "AR",
            "province": "1",
            "password1": "juan@example.com",
            "password2": "juan@example.com",
            "terms": True,
            "g-recaptcha-response": "test",
        }
    )
    assert not form.is_valid()
    errors = form.errors or {}
    assert errors.get("password2", [None])[0] == "La contraseña es muy similar a email."


@pytest.mark.django_db
def test_register_password_mismatch():
    form = RegisterForm(
        data={
            "email": "user@example.com",
            "first_name": "Juan",
            "last_name": "Perez",
            "birth_date": "2000-01-01",
            "country": "AR",
            "province": "1",
            "password1": "Password123",
            "password2": "Password124",
            "terms": True,
            "g-recaptcha-response": "test",
        }
    )
    assert not form.is_valid()
    errors = form.errors or {}
    assert (
        errors.get("password2", [None])[0]
        == "Los dos campos de contraseñas no coinciden entre si."
    )


@pytest.mark.django_db
def test_register_password_valid():
    form = RegisterForm(
        data={
            "email": "user@example.com",
            "first_name": "Juan",
            "last_name": "Perez",
            "birth_date": "2000-01-01",
            "country": "AR",
            "province": "1",
            "password1": "Password123$",
            "password2": "Password123$",
            "terms": True,
            "g-recaptcha-response": "test",
        }
    )
    assert form.is_valid()
