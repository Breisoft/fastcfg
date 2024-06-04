from pydantic import BaseModel

from fastcfg.exceptions import ConfigItemValidationError
from fastcfg.sources.files import from_yaml
from fastcfg.validation.policies import PydanticValidator, URLValidator


# Define a Pydantic model for validating stage configurations
class StageModel(BaseModel):
    stage: str
    url: str


# Load configurations from a YAML file
stages = from_yaml("./examples/files/staging_invalid_url.yml")
# staging.yml:
# dev:
#   stage: dev
#   url: https://dev.example.com
# prod:
#   stage: prod
#   url: invalid-url

# Add validators to the dev stage configuration
stages.dev.add_validator(PydanticValidator(StageModel))
stages.dev.url.add_validator(URLValidator())

# Add validators to the prod stage configuration
stages.prod.add_validator(PydanticValidator(StageModel))

# Attempt to add a URL validator to the prod stage URL and handle potential validation errors
try:
    stages.prod.url.add_validator(URLValidator())
except ConfigItemValidationError as exc:
    pass
    # Output: ConfigItemValidationError: Validation failed: Value must be a
    # valid URL.

# Set the current environment to 'dev'
stages.set_environment("dev")

# Print the URL for the current environment, which should be the dev environment's URL
print(stages.url)  # Outputs https://dev.example.com
