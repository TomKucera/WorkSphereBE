from .provider_settings import ProviderSettings


DEFAULT_MAX_MESSAGE_LENGTH: int = 1000

PROVIDER_SETTINGS: dict[str, ProviderSettings] = {
    "JobsCZ": ProviderSettings(
        max_message_length=DEFAULT_MAX_MESSAGE_LENGTH,
        auto_apply_enabled=True,
    ),
    "StartupJobs": ProviderSettings(
        max_message_length=DEFAULT_MAX_MESSAGE_LENGTH,
        auto_apply_enabled=True,
    ),
    "CoolJobs": ProviderSettings(
        max_message_length=DEFAULT_MAX_MESSAGE_LENGTH,
        auto_apply_enabled=True,
    ),
    "Titans": ProviderSettings(
        max_message_length=DEFAULT_MAX_MESSAGE_LENGTH,
        auto_apply_enabled=True,
    ),
    "JobStackIT": ProviderSettings(
        max_message_length=500,
        auto_apply_enabled=False,
    ),
}
