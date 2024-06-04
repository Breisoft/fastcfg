from fastcfg import config

# Define environments
dev_stage = {"stage": "dev"}
prod_stage = {"stage": "prod"}

# Assign environments to the config
config.dev = dev_stage
config.prod = prod_stage

# Automatically detects environments based on top level attributes of `Config`
# instance. Only `Config` instances and `dict` subclasses are supported.
print(config.environments)  # Output: ['dev', 'prod']

# Set and print the 'dev' environment
config.set_environment("dev")
print(config.stage)  # Output: dev

# Set and print the 'prod' environment
config.set_environment("prod")
print(config.stage)  # Output: prod

# Remove the current environment setting
config.remove_environment()  # Equivalent to `config.set_environment(None)`
print(config)  # Output: displays both dev and prod configurations

# Attempt to access an attribute that may not exist
try:
    print(config.stage)
except AttributeError:
    print("AttributeError: 'stage' not found")
