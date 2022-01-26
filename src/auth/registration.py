import requests
from src.error.exceptions import MatrixError
from src.auth.login import LoginSession
from src.auth.interactive import AuthSession, selectFlow, TooManyAttemptsException

UserRegisterPath = '/_matrix/client/r0/register?kind=user'

class RegistrationException(Exception):
  def __init__(self, message):
    self.message = message

def handle400(r, authSession):
  resp = r.json()
  raise MatrixError(resp['errcode'], resp['error'])

def handle401(r, authSession):
  resp = r.json()
  sessionKey = resp['session']
  flows = resp['flows']
  if authSession is None:
    f = selectFlow(flows)
    if f is None:
      raise RegistrationException('No authentication flows supported by this client') 
    authSession = AuthSession(f, sessionKey)
    return (None, authSession)
  else:
    if 'errcode' in resp:
      print(f'{resp["errcode"]}: {resp["error"]}')
    if 'completed' in resp:
      authSession.completed = resp['completed']
    return (None, authSession)
 
def handle403(r, authSession):
  resp = r.json()
  raise MatrixError('M_FORBIDDEN', 'Registration is disabled on this homeserver')

def handle200(r, authSession):
  resp = r.json()
  user_id = resp['user_id']
  access_token = resp['access_token']
  device_id = resp['device_id']
  homeserver = resp['home_server']
  return ((user_id, access_token, device_id, homeserver), None) 

def handleOther(r, authSession):
  raise MatrixError('M_UNKNOWN', 'An unknown error event has occurred')

handlers = {
  400: handle400,
  401: handle401,
  403: handle403,
  200: handle200
}

def interactive_register(homeserver, username, password, authSession):
  url = f'http://{homeserver}{UserRegisterPath}'
  payload = {
    "username": username,
    "password": password
  }

  if authSession is not None:
    auth = authSession.getAuth()
    payload['auth'] = auth
#  print(payload)
  result = requests.post(url, json=payload)
#  print(result.status_code)
#  print(result.text)
  if result.status_code in handlers:
    loginSession, authSession = handlers[result.status_code](result, authSession)
  else:
    loginSession, authSession = handleOther(result, authSession)

  if loginSession is not None:
    return LoginSession(loginSession[0], loginSession[1], loginSession[2], homeserver, loginSession[3])
  
  return interactive_register(homeserver, username, password, authSession) 

def register(homeserver, username, password):
  try:
    return interactive_register(homeserver, username, password, None) 
  except TooManyAttemptsException:
    raise RegistrationException('Too many authentication attempts were made')
