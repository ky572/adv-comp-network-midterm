class MatrixError(Exception):
  def __init__(self, errCode, error):
    self.errCode = errCode
    self.error = error

class RateLimitError(Exception):
  def __init__(self, retry_after):
    self.retry_after = retry_after
