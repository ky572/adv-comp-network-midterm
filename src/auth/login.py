from src.auth.interactive import supportedAuthTypes
from src.error.exceptions import MatrixError
import requests

class LoginException(Exception):
  def __init__(self, message):
    self.message = message

class LoginSession():
  def __init__(self, userId, accessToken, deviceId, endpoint, homeserver):
    self.userId = userId
    self.accessToken = accessToken
    self.deviceId = deviceId
    self.endpoint = endpoint
    self.requestSession = requests.Session()
    self.requestSession.headers = {'Authorization': f'Bearer {self.accessToken}'}
    self.roomAliasMappings = {}
    self.homeserver = homeserver
    self.roomMessages = {}
    self.nextSync = None

  def getResourceURL(self, path):
    return f'http://{self.endpoint}{path}'

  def getFQEntityName(self, name):
    return f'{name}:{self.homeserver}'

  def close(self):
    self.requestSession.close()

UserLoginPath = '/_matrix/client/r0/login'

def handle200(r):
  resp = r.json()
  user_id = resp['user_id']
  access_token = resp['access_token']
  device_id = resp['device_id']
  homeserver = resp['home_server']
  return (user_id, access_token, device_id, homeserver)

def handle400(r):
  resp = r.json()
  raise MatrixError(resp['errcode'], resp['error'])

def handle403(r):
  resp = r.json()
  messages = {
    'M_FORBIDDEN': 'Invalid credentials',
    'M_USER_DEACTIVATED': 'The user has been deactivated'
  }
  errcode = resp['errcode']
  if errcode in messages:
    m = messages[errcode]
  else:
    m = 'Login attempt failed'

  raise MatrixError(errcode, m)

def handleOther(r):
  raise LoginException('An unknown error event has occurred')

handlers = {
  200: handle200,
  400: handle400,
  403: handle403
}

def login(homeserver, username, password):
  url = f'http://{homeserver}{UserLoginPath}'
  result = requests.get(url)
  resp = result.json()
  available_flows = resp['flows']
  if not any(f['type'] == 'm.login.password' for f in available_flows):
    raise LoginException('Server does not support password authentication')
    
  payload = {
    'type': 'm.login.password',
    'identifier': {
      'type': 'm.id.user',
      'user': username
    },
    'password': password
  }

  result = requests.post(url, json=payload)
  if result.status_code in handlers:
    loginSession = handlers[result.status_code](result)
  else:
    loginSession = handleOther(result)

  return LoginSession(loginSession[0], loginSession[1], loginSession[2], homeserver, loginSession[3])
