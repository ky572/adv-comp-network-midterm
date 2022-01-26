from src.error.exceptions import MatrixError

CreateRoomPath = '/_matrix/client/r0/createRoom'

def create200(r):
  resp = r.json()
  return resp['room_id']

def create400(r):
  resp = r.json()
  raise MatrixError(resp['errcode'], resp['error'])

createRoomHandlers = {
  200: create200,
  400: create400
}

def createRoom(alias, loginSession):
  payload = {
    'room_alias_name': alias
  }
  result = loginSession.requestSession.post(loginSession.getResourceURL(CreateRoomPath), json=payload)

  if result.status_code in createRoomHandlers:
    roomId = createRoomHandlers[result.status_code](result)
  else:
    raise Exception('An unknown error event has occurred')
