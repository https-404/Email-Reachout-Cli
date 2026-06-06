class JobReachError(Exception):
    """Base exception for clean CLI errors."""


class ConfigError(JobReachError):
    pass


class AIProviderError(JobReachError):
    pass


class GmailAuthError(JobReachError):
    pass


class SendBlockedError(JobReachError):
    pass


class LeadLoadError(JobReachError):
    pass


class CVParseError(JobReachError):
    pass
