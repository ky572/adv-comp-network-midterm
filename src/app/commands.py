import src.rooms.admin as RoomAdmin
import src.rooms.membership as RoomMembership
import src.messages.room as RoomMessage
from src.error.exceptions import MatrixError

def logoutSession(args, loginSession):
  return True

def createRoom(args, loginSession):
  if len(args) < 1:
    print('Missing args: createroom <room-alias>')
    return False
  try:
    alias = args[0]
    roomId = RoomAdmin.createRoom(alias, loginSession)
    loginSession.roomAliasMappings[alias] = roomId
    print(f'Room {alias} created successfully')
  except Exception as e:
    print('Room creation failed')
  return False

def joinRoom(args, loginSession):
  if len(args) < 1:
    print('Missing args: joinroom <room-alias>')
    return False

  try:
    alias = args[0]
    ok = RoomMembership.joinRoom(alias, loginSession)
    print(f'Joined room {alias}')
  except Exception as e:
    print('Could not join room')

  return False

def sendToRoom(args, loginSession):
  if len(args) < 2:
    print('Missing args: send <room-alias> <message>')
    return False

  try:
    alias = args[0]
    msg = ' '.join(args[1:])
    ok = RoomMessage.send(alias, msg, loginSession)
    if not ok:
      print('Could not send message')
    else:
      print('Sent')
  except Exception as e:
    print('Could not send message')

  return False

handlers = {
  'logout': logoutSession,
  'createroom': createRoom,
  'joinroom': joinRoom,
  'send': sendToRoom
}

def parse_command(line):
  terms = line.split()
  cmd = terms[0].lower()
  args = terms[1:]
  return (handlers[cmd] if cmd in handlers else None, args)

def run_command(line, loginSession):
  handler, args = parse_command(line)
  if handler is not None:
    return handler(args, loginSession)
  else:
    print('Command not recognized')
    return False
