# backend/app/core/exceptions.py
class RetellAPIError(Exception):
    """Raised when Retell AI API returns an error"""
    pass

class PostProcessingError(Exception):
    """Raised when post-processing fails"""
    pass

class AgentConfigError(Exception):
    """Raised when agent configuration is invalid"""
    pass

class GeminiAPIError(Exception):
    """Raised when Gemini API returns an error"""
    pass