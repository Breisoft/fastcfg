import os

from fastcfg import config
from fastcfg.sources.memory import from_os_environ

os.environ["MY_ENVIRONMENT_VARIABLE"] = "Hello, World!"

# from_os_environ uses a `LiveConfigItem` which, on access, returns the current state
config.my_env_var = from_os_environ("MY_ENVIRONMENT_VARIABLE")

print(config.my_env_var)  # Outputs: Hello, World!

os.environ["MY_ENVIRONMENT_VARIABLE"] = "Different value!"

print(config.my_env_var)  # Outputs: Different value!
