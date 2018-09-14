import errno
import os
import stat
from configparser import ConfigParser

from . import default
from ..util import os as util_os


__all__ = [
  "config_file",
  "setup",
  "update"
]


xdg_config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expandvars("$HOME/.config"))
config_dir  = xdg_config_home + "/slizzy"
config_file = config_dir + "/slizzy.cfg"
config_file_mode = stat.S_IRUSR | stat.S_IWUSR


def setup():
  cfg = ConfigParser(inline_comment_prefixes = ("#", ";"))
  cfg.read_dict(default.cfg)
  
  try:
    os.makedirs(config_dir, mode=0o755)
  except OSError as e:
    if not os.path.isdir(xdg_config_home):
      raise util_os.oserror(errno.ENOTDIR, xdg_config_home) from e
    
    if not os.path.isdir(config_dir):
      raise util_os.oserror(errno.ENOTDIR, config_dir) from e
    
    if os.path.exists(config_file) and not os.path.isfile(config_file):
      raise util_os.oserror(errno.EISDIR, config_file) from e

  try:
    # Prevents always downgrading umask to 0:
    with util_os.Umask(0o777 ^ config_file_mode):
      if os.path.exists(config_file): # Read the config if it exists:
        with open(config_file, "r", config_file_mode) as file:
          cfg.read_file(file)
          
      with open(config_file, "w", config_file_mode) as file: # Update the config:
        cfg.write(file)
  except OSError as e:
    raise util_os.oserror(errno.EACCES, config_file) from e

  return cfg


def update(cfg):
  try:
    # Prevents always downgrading umask to 0:
    with util_os.Umask(0o777 ^ config_file_mode), \
         open(config_file, "w", config_file_mode) as file:
      cfg.write(file)
  except OSError as e:
    raise util_os.oserror(errno.EACCES, config_file) from e
