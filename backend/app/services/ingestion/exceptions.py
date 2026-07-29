class PaperFetchError(Exception):
    """Exception raised when failing to fetch a paper."""
    pass

class PaperParseError(Exception):
    """Exception raised when failing to parse a paper."""
    pass

class SourceUnavailableError(Exception):
    """Exception raised when a paper source is unavailable."""
    pass
