from src.auth.password import prompt_pass

supportedAuthTypes = ['m.login.password', 'm.login.dummy']

class NoFlowSupportedException(Exception):
  pass

class TooManyAttemptsException(Exception):
  pass

def handlePassword(authSession):
  username, pw = prompt_pass()

  return {
    'type': 'm.login.password',
    'identifier': {
      'type': 'm.id.user',
      'user': username
    },
    'password': pw,
    'session': authSession.sessionKey
  }

def handleDummy(authSession):
  return {
    "type": "m.login.dummy",
    "session": authSession.sessionKey
  }

authHandlers = {
  'm.login.password': handlePassword,
  'm.login.dummy': handleDummy
}

class AuthSession():
  def __init__(self, flow, sessionKey):
    self.flow = flow
    self.completed = []
    self.sessionKey = sessionKey
    self.attempts = 0
    self.lastStage = None
    

  def getNextStage(self):
    for s in self.flow['stages']:
      if s not in self.completed:
        return s
    return None

  def getAuth(self):
    nextStage = self.getNextStage()
    if nextStage != self.lastStage:
      self.lastStage = nextStage
      self.attempts = 0
    else:
      self.attempts += 1
      if self.attempts > 4:
        raise TooManyAttemptsException()
    return authHandlers[nextStage](self)

def selectFlow(flows):
  for f in flows:
    stages = f['stages']
    if all(s in supportedAuthTypes for s in stages):
      return f
    return None
