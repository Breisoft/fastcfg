from fastcfg import config
from fastcfg.validation.policies import RangeValidator, TypeValidator

# Set some configuration values
config.age = 25
config.name = "John Doe"

# Add a RangeValidator to ensure 'age' is between 18 and 65
config.age.add_validator(RangeValidator(min_value=18, max_value=65))

# Add a TypeValidator to ensure 'name' is a string
config.name.add_validator(TypeValidator(str))

# The configuration system automatically triggers validation in three cases:
# 1. When a value is assigned to a configuration attribute (e.g., setting config.age = 25).
# 2. When a new validator is attached to a configuration attribute (e.g.,
#    adding `RangeValidator` to config.age).
# 3. When a `LiveConfigItem`'s state is changed (See `Advanced Validation`
#    examplef for more info)

# This ensures that all configuration values always adhere to the specified
# constraints without constantly validating them on access.
