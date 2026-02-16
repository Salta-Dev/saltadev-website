import pytest

from django.contrib.auth import password_validation
from django.test import override_settings

from users.models import User
from password_reset.forms import PasswordResetConfirmForm


@pytest.fixture(autouse=True)
def _recaptcha_and_cache(settings):
    settings.RECAPTCHA_PUBLIC_KEY = 'test'
    settings.RECAPTCHA_PRIVATE_KEY = 'test'
    password_validation.get_default_password_validators.cache_clear()
    yield
    password_validation.get_default_password_validators.cache_clear()


@pytest.mark.django_db
def test_reset_password_too_short():
    user = User.objects.create_user(
        email='user@example.com',
        first_name='Juan',
        last_name='Perez',
        birth_date='2000-01-01',
        password='Password123$'
    )
    form = PasswordResetConfirmForm(
        data={
            'new_password': 'abc',
            'confirm_password': 'abc',
            'g-recaptcha-response': 'test',
        },
        user=user,
    )
    assert not form.is_valid()
    errors = form.errors or {}
    assert (
        errors.get('new_password', [None])[0]
        == 'La contraseña es demasiado corta. Debe contener por lo menos 8 caracteres.'
    )


@pytest.mark.django_db
def test_reset_password_common():
    user = User.objects.create_user(
        email='user@example.com',
        first_name='Juan',
        last_name='Perez',
        birth_date='2000-01-01',
        password='Password123$'
    )
    form = PasswordResetConfirmForm(
        data={
            'new_password': 'password',
            'confirm_password': 'password',
            'g-recaptcha-response': 'test',
        },
        user=user,
    )
    assert not form.is_valid()
    errors = form.errors or {}
    assert (
        errors.get('new_password', [None])[0] == 'La contraseña tiene un valor demasiado común.'
    )


@pytest.mark.django_db
def test_reset_password_numeric():
    user = User.objects.create_user(
        email='user@example.com',
        first_name='Juan',
        last_name='Perez',
        birth_date='2000-01-01',
        password='Password123$'
    )
    with override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
        ]
    ):
        password_validation.get_default_password_validators.cache_clear()
        form = PasswordResetConfirmForm(
            data={
                'new_password': '9876543210',
                'confirm_password': '9876543210',
                'g-recaptcha-response': 'test',
            },
            user=user,
        )
        assert not form.is_valid()
        errors = form.errors or {}
        assert (
            errors.get('new_password', [None])[0]
            == 'La contraseña está formada completamente por dígitos.'
        )


@pytest.mark.django_db
def test_reset_password_similar_to_email():
    user = User.objects.create_user(
        email='juan@example.com',
        first_name='Juan',
        last_name='Perez',
        birth_date='2000-01-01',
        password='Password123$'
    )
    form = PasswordResetConfirmForm(
        data={
            'new_password': 'juan@example.com',
            'confirm_password': 'juan@example.com',
            'g-recaptcha-response': 'test',
        },
        user=user,
    )
    assert not form.is_valid()
    errors = form.errors or {}
    assert errors.get('new_password', [None])[0] == 'La contraseña es muy similar a email.'


@pytest.mark.django_db
def test_reset_password_mismatch():
    user = User.objects.create_user(
        email='user@example.com',
        first_name='Juan',
        last_name='Perez',
        birth_date='2000-01-01',
        password='Password123$'
    )
    form = PasswordResetConfirmForm(
        data={
            'new_password': 'Password123$',
            'confirm_password': 'Password124$',
            'g-recaptcha-response': 'test',
        },
        user=user,
    )
    assert not form.is_valid()
    errors = form.errors or {}
    assert errors.get('confirm_password', [None])[0] == 'Las contraseñas no coinciden.'


@pytest.mark.django_db
def test_reset_password_valid():
    user = User.objects.create_user(
        email='user@example.com',
        first_name='Juan',
        last_name='Perez',
        birth_date='2000-01-01',
        password='Password123$'
    )
    form = PasswordResetConfirmForm(
        data={
            'new_password': 'Password123$',
            'confirm_password': 'Password123$',
            'g-recaptcha-response': 'test',
        },
        user=user,
    )
    assert form.is_valid()
