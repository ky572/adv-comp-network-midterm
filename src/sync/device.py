from src.error.exceptions import MatrixError
from src.auth.login import LoginSession
from src.rooms.alias import extractLocalPart

SyncPath = '/_matrix/client/r0/sync'

def syncRooms(result, loginSession):
  resp = result.json()
  nextSync = resp['next_batch']
  loginSession.nextSync = nextSync
  if 'rooms' not in resp:
    return
  rooms = resp['rooms']

  if 'join' not in rooms:
    return

  join = rooms['join']
  for roomId, roomEvents in join.items():
    if roomId not in loginSession.roomMessages:
      loginSession.roomMessages[roomId] = []
    timelineEvents = roomEvents['timeline']['events']
    for e in timelineEvents:
      et = e['type']
      if et == 'm.room.canonical_alias':
        alias = e['content']['alias']
        alias = extractLocalPart(alias)
        if alias not in loginSession.roomAliasMappings:
          loginSession.roomAliasMappings[alias] = roomId
      elif et == 'm.room.message':
        sender = e['sender']
        msg = e['content']['body']
        loginSession.roomMessages[roomId].append((sender, msg))

def sync(loginSession):
  if loginSession.nextSync is not None:
    path = f'{SyncPath}?sync={loginSession.nextSync}'
  else:
    path = SyncPath

  result = loginSession.requestSession.get(loginSession.getResourceURL(path))
  
  if result.status_code != 200:
    return False

  syncRooms(result, loginSession)
  return True
