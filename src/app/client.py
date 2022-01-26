import argparse
import sys
from src.auth.registration import register, RegistrationException
from src.auth.login import LoginSession, login
from src.auth.logout import logout
from src.error.exceptions import MatrixError
from src.auth.password import prompt_pass
from src.app.commands import run_command
from src.sync.device import sync

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--register', help='Begin a session by registering a new user', action='store_true')
  parser.add_argument('homeserver', help='Homeserver address or name')
  args = parser.parse_args()
  if args.register:
    print('Registering new user')
    username, pw = prompt_pass()
 
    try:
      loginSession = register(args.homeserver, username, pw) 
    except MatrixError as e:
      print(f'{e.errCode}: {e.error}')
      sys.exit() 
    except RegistrationException as e:
      print(f'Registration error: {e.message}')
      sys.exit()
  else:
    username, pw = prompt_pass()

    try:
      loginSession = login(args.homeserver, username, pw)
    except MatrixError as e:
      print(f'{e.errCode}: {e.error}')
      sys.exit()
    except LoginException as e:
      print(f'Login error: {e.message}')
      sys.exit()

  print(f'Logged in as: {loginSession.userId}')
  sync(loginSession)
  print(f'You have joined the following rooms:')
  roomAliases = loginSession.roomAliasMappings.keys()
  if len(roomAliases) == 0:
    print('You have not joined any rooms')
  else:
    for r in loginSession.roomAliasMappings.keys():
      print(r)

  while True:
    try:
      end = run_command(next(sys.stdin).strip(), loginSession)
      if end:
        break
    except KeyboardInterrupt:
      break
    except MatrixError as e:
      print(f'{e.errCode}: {e.error}')
    except Exception as e:
      print(e)

  logout(loginSession)
  print('Logged out')
