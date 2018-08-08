from colorama import Fore, Style, init


init()


__all__ = [
  "red",
  "green",
  "blue",
  "yellow",
  "result"
]


def red(text):
  return Fore.RED + str(text) + Style.RESET_ALL


def green(text):
  return Fore.GREEN + str(text) + Style.RESET_ALL


def blue(text):
  return Fore.BLUE + str(text) + Style.RESET_ALL


def yellow(text):
  return Fore.YELLOW + str(text) + Style.RESET_ALL


def result(value):
  return (green if value else red)(value)
