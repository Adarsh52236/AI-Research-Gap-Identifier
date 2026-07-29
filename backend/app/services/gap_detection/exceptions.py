class GapDetectionError(Exception):
    """Exception raised for general gap detection failures."""
    pass

class ConfidenceCalculationError(GapDetectionError):
    """Exception raised when confidence calculation fails."""
    pass
