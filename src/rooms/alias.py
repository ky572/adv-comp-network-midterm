import urllib
from src.error.exceptions import MatrixError

AliasLookupPath = '/_matrix/client/r0/directory/room'

def lookupRoomAlias(alias, loginSession):
  if alias in loginSession.roomAliasMappings:
    return loginSession.roomAliasMappings[alias]

  path = f'{AliasLookupPath}/{urllib.parse.quote_plus("#" + loginSession.getFQEntityName(alias))}'

  result = loginSession.requestSession.get(loginSession.getResourceURL(path))
  
  if result.status_code == 200:
    resp = result.json()
    roomId = resp['room_id']
    loginSession.roomAliasMappings[alias] = roomId
    return roomId
  elif result.status_code == 404:
    return None
  else:
    raise Exception('Unknown error occurred')

def extractLocalPart(fqAlias):
  return fqAlias.split(':')[0][1:]
