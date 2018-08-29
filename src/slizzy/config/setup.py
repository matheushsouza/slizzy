import errno
import os
import stat
from configparser import ConfigParser

from ..util import os as util_os


__all__ = [
  "config_file",
  "default_cfg",
  "setup",
  "load",
  "update"
]


xdg_config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expandvars("$HOME/.config"))
config_dir  = xdg_config_home + "/slizzy"
config_file = config_dir + "/slizzy.cfg"
config_file_mode = stat.S_IRUSR | stat.S_IWUSR

default_cfg = r"""[slizzy]
duration-tolerance = 5
bitrate-min = 315

[google]
key = <key>

[beatport]
cx = <cx>
fuzz-threshold = 50

[slider]
fuzz-threshold = 10

[zippyshare]
cx = <cx>
fuzz-threshold = 40
blacklist =
  DANCEDJ\.CLUB
  \[ClapCrate\.me\]
  \[RIP\]
  Bass *Boosted
"""


def setup():
  try:
    os.makedirs(config_dir, mode=0o755)
  except:
    if not os.path.isdir(xdg_config_home):
      raise util_os.oserror(errno.ENOTDIR, xdg_config_home)
    
    if not os.path.isdir(config_dir):
      raise util_os.oserror(errno.ENOTDIR, config_dir)
    
    if os.path.exists(config_file) and not os.path.isfile(config_file):
      raise util_os.oserror(errno.EISDIR, config_file)
  
  if not os.path.exists(config_file):
    # Prevents always downgrading umask to 0:
    with util_os.Umask(0o777 ^ config_file_mode), \
         open(config_file, "w", config_file_mode) as file:
      file.write(default_cfg)


def load():
  cfg = ConfigParser(inline_comment_prefixes = ("#", ";"))

  try:
    with open(config_file, "r") as file:
      cfg.read_file(file)
  except Exception as e:
    raise util_os.oserror(errno.EACCES, config_file) from e
  
  return cfg


def update(cfg):
  try:
    # Prevents always downgrading umask to 0:
    with util_os.Umask(0o777 ^ config_file_mode), \
         open(config_file, "w", config_file_mode) as file:
      cfg.write(file)
  except Exception as e:
    raise util_os.oserror(errno.EACCES, config_file) from e
