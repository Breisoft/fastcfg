from fastcfg import Config, config

# By default, there's a `Config` instance already created for you.
# You can access it via the `config` global object by importing:
# from fastcfg import config

# Example of a practical use case: setting up database configuration.
config.db_name = "my_database"
config.db_credentials = {"user": "admin", "password": "securepassword123"}

# You can access them with the dot operator:

# Outputs: {'user': 'admin', 'password': 'securepassword123'}
print(config.db_credentials)

print(config.db_name)  # Outputs: my_database
print(config.db_credentials["user"])  # Outputs: admin

# Since dictionaries are automatically converted to `Config` objects,
# you can access dictionary keys as attributes:
print(config.db_credentials.user)  # Outputs: admin

# You can also create your own `Config` instance if you'd like.
# This config is completely separate from the global config instance.
# Here's an example of how to do that:
custom_config = Config()

# Setting up a custom configuration for another part of the application, e.g., email server
custom_config.email_server = "smtp.example.com"
custom_config.email_port = 587
custom_config.email_credentials = {
    "username": "email_user",
    "password": "email_password",
}

# Accessing custom configuration values
print(custom_config.email_server)  # Outputs: smtp.example.com
print(custom_config.email_port)  # Outputs: 587
print(custom_config.email_credentials.username)  # Outputs: email_user
