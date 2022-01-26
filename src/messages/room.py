import urllib
import random
import string
from src.error.exceptions import MatrixError
from src.rooms.membership import RoomsPath
from src.rooms.alias import lookupRoomAlias

def send(alias, message, loginSession):
  roomId = lookupRoomAlias(alias, loginSession)
  txnId = ''.join(random.choices(string.ascii_lowercase, k=20))
  path = f'{RoomsPath}/{urllib.parse.quote_plus(roomId)}/send/m.room.message/{txnId}'

  payload = {
    'msgtype': 'm.text',
    'body': message
  }

  result = loginSession.requestSession.put(loginSession.getResourceURL(path), json=payload)
  if result.status_code == 200:
    return True
  
  return False
