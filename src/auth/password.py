import getpass
import sys

def prompt_pass():
  print('Enter username: ', end='', flush=True)
  username = next(sys.stdin).strip()
  pw = getpass.getpass('Password: ').strip()
  return (username, pw)
