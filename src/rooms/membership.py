import urllib
from src.error.exceptions import MatrixError
from src.rooms.alias import lookupRoomAlias

RoomsPath = '/_matrix/client/r0/rooms'

def join200(r, loginSession):
  return True

def join403(r, loginSession):
  resp = r.json()
  raise MatrixError(resp['errcode'], resp['error'])

joinHandlers = {
  200: join200,
  403: join403
}

def joinRoom(alias, loginSession):
  if alias in loginSession.roomAliasMappings:
    roomId = loginSession.roomAliasMappings[alias]
  else:
    roomId = lookupRoomAlias(alias, loginSession)
 
  path = f'{RoomsPath}/{urllib.parse.quote_plus(roomId)}/join'
  result = loginSession.requestSession.post(loginSession.getResourceURL(path))

  if result.status_code in joinHandlers:
    return joinHandlers[result.status_code](result, loginSession)
  else:
    return False
