import pytest

from prompt_forge.examples import example_spec
from prompt_forge.models import Profile
from prompt_forge.profiles import PROFILES, get_profile


@pytest.mark.parametrize("profile", list(Profile))
def test_profile_has_both_languages(profile):
    spec = get_profile(profile)
    assert spec is not None
    for lang in ("ru", "en"):
        assert spec.label(lang)
        assert spec.role_text(lang)
        assert spec.default_output_format(lang)
        assert spec.default_requirements(lang)


@pytest.mark.parametrize("profile", list(Profile))
def test_example_spec_exists(profile):
    spec = example_spec(profile, "ru")
    assert spec.task
    assert spec.profile is profile


def test_get_profile_accepts_string_and_enum():
    assert get_profile("code").key is Profile.CODE
    assert get_profile("  BUGFIX  ").key is Profile.BUGFIX
    assert get_profile(Profile.TEST).key is Profile.TEST
    assert get_profile("unknown") is None


def test_role_includes_stack():
    spec = get_profile(Profile.CODE)
    assert "Python 3.11" in spec.role_text("ru", "Python 3.11 + pytest")


def test_profiles_registry_is_complete():
    assert set(PROFILES) == set(Profile)
