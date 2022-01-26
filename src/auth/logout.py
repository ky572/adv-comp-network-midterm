from src.auth.login import LoginSession

UserLogoutPath = '/_matrix/client/r0/logout'

def logout(loginSession):
  result = loginSession.requestSession.post(loginSession.getResourceURL(UserLogoutPath))
  if result.status_code != 200:
    print('Logout attempt failed')
