# FastCFG ⚡️

**Serverless's missing nervous system** - Real-time, dynamic configuration
management that scales from localhost to billions of invocations. No more
restarting your container or server for configuration updates!

[![PyPI version](https://badge.fury.io/py/fastcfg.svg)](https://badge.fury.io/py/fastcfg)
[![Python Support](https://img.shields.io/pypi/pyversions/fastcfg.svg)](https://pypi.org/project/fastcfg/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

```python
from fastcfg import config

# This is all you need
config.api_key = "sk-..."
config.temperature = 0.8
config.max_retries = 3

# Your config reacts to changes in real-time
print(config.temperature)  # 0.8
```

## 🚀 Quick Start

### Installation

```bash
pip install fastcfg

# With AWS support
pip install "fastcfg[aws]"

# With all features
pip install "fastcfg[all]"
```

### Basic Usage

```python
from fastcfg import config, Config

# Simple assignment
config.app_name = "my-service"
config.debug = True
config.max_workers = 10

# Nested configuration
config.database = Config(host="localhost", port=5432)

# Dictionary-style access
config["api"]["key"] = "secret"

# It just works™
print(config.app_name)  # "my-service"
print(config.database.host)  # "localhost"
```

### 🌍 Global vs Instance Configs

```python
# Option 1: Use the global config (most common)
from fastcfg import config  # Same instance everywhere!

# In app.py
config.api_key = "secret"

# In database.py
from fastcfg import config
print(config.api_key)  # "secret" - it's the same config!

# Option 2: Create your own instances
from fastcfg import Config

# Create separate configs for different purposes
app_config = Config()
test_config = Config()
feature_flags = Config()

# They're completely independent
app_config.debug = True
test_config.debug = False  # Different config, different value
```

**Pro tip**: Use the global `config` for your main app configuration, and create separate `Config()` instances for isolated subsystems or testing.

## 🎓 The 3 Simple Rules

FastCFG's magic makes config values behave like regular Python values 99% of the time. For that 1%, here are the only rules you need:

```python
# Rule 1: Your code → Just use it normally ✨
if config.timeout > 30:
    config.retries = 5

# Rule 2: External libraries → Use .value 📦
import requests
requests.get(url, timeout=config.timeout.value)  # External code needs .value

# Rule 3: When in doubt → .value always works 🤷
value = config.setting.value  # Always safe
```

**That's it!** FastCFG handles the complexity so you don't have to.

## 🤔 Why FastCFG?

**Born from the frustration of managing serverless configuration at scale.** After a year of wrestling with environment variables, AWS Parameter Store, and hardcoded values across Lambda functions, we built the configuration system serverless deserves.

### The Serverless Configuration Problem

- **Cold starts are expensive** - Every millisecond counts
- **Environment variables hit size limits** - Lambda's 4KB limit is real
- **Configuration changes require redeployment** - 15-minute deploys for a feature flag?
- **No validation until runtime** - Your Lambda fails at 3 AM
- **AWS Parameter Store is slow without caching** - 50ms per parameter adds up

### FastCFG: Your Serverless Nervous System

Just like your nervous system instantly responds to stimuli, FastCFG gives your serverless applications instant access to configuration with real-time updates, automatic retries, and intelligent caching.

## ⚡ Performance That Matters

```python
# Benchmark results (1M operations)
FastCFG:           0.5μs per access  ⚡️
Pydantic Settings: 0.04μs per access (but static)
DynaConf:          17μs per access   (31.7x slower)
Raw AWS SDK:       50,000μs per access (100,000x slower!)
```

**In real terms**: FastCFG adds just 0.0005ms overhead while saving you 50ms+ on AWS API calls through intelligent caching.

## 🎯 Real-World Use Cases

### 1. Multi-Stage Serverless API

```python
from fastcfg import config
from fastcfg.sources.aws import from_appconfig

# Load configuration for your stage
config.update(from_appconfig("my-api", os.environ["STAGE"]))

@app.route("/api/v1/process")
def process_request():
    # Auto-refreshing rate limits
    if request_count > config.rate_limit:
        return {"error": "Rate limit exceeded"}, 429
    
    # Feature flags without redeploy
    if config.features.new_algorithm:
        return process_v2(request.data)
    
    return process_v1(request.data)
```

### 2. ML Model Configuration

```python
from fastcfg import config
from fastcfg.validation.policies import RangeValidator

# Type-safe model parameters
config.temperature = 0.8
config.temperature.add_validator(RangeValidator(0.0, 2.0))

config.max_tokens = 1000
config.model_name = "gpt-4"

# Dynamic model switching
@config.on_change("model_name")
def reload_model(event):
    global model
    model = load_model(event.new_value)
    logger.info(f"Switched to model: {event.new_value}")
```

### 3. Database Connection Management

```python
from fastcfg import config
from fastcfg.sources.aws import from_secrets_manager

# Load secrets securely
config.update(from_secrets_manager("prod/database"))

# Automatic connection recycling on config change
@config.on_change("database.connection_string")
def update_connection_pool(event):
    connection_pool.reconfigure(event.new_value)

# Use it naturally
db = create_connection(
    host=config.database.host,
    port=config.database.port,
    password=config.database.password
)
```

### 4. Feature Flags & A/B Testing

```python
from fastcfg import config
from fastcfg.sources.aws import from_appconfig
from fastcfg.cache import Cache
from fastcfg.cache.strategies import TTLCacheStrategy

# Poll for updates every 30 seconds
config.features = from_appconfig(
    "feature-flags",
    "production",
    cache=Cache(TTLCacheStrategy(seconds=30))
)

def should_show_new_ui(user_id: str) -> bool:
    # Real-time feature flag updates
    if not config.features.new_ui_enabled:
        return False
    
    # Percentage rollout
    if hash(user_id) % 100 < config.features.new_ui_percentage:
        return True
    
    return False
```

### 5. Microservice Configuration

```python
from fastcfg import config
from pydantic import BaseModel
from fastcfg.validation.policies import PydanticValidator

# Define your schema with Pydantic
class ServiceConfig(BaseModel):
    service_name: str
    port: int
    timeout_seconds: int = 30
    retry_attempts: int = 3

# Load from multiple sources
config.update(from_env())  # Environment variables
config.update(from_yaml("config/base.yml"))  # Base config
config.update(from_yaml(f"config/{ENVIRONMENT}.yml"))  # Environment overrides

# Add validation
config.service.add_validator(PydanticValidator(ServiceConfig))

# AWS native integration
if ENVIRONMENT == "production":
    config.update(from_appconfig("myservice", "prod"))
```

## 🌟 Key Features

### 🚄 **Blazing Fast**
- **31.7x faster** than DynaConf
- Sub-microsecond access times
- Intelligent caching strategies
- Optimized for serverless cold starts

### 🔄 **Live Configuration**
```python
# Configuration that updates without redeploy
config.api_endpoint = from_appconfig("endpoints", "prod")

# Automatic polling with caching
config.feature_flags = from_appconfig(
    "features", 
    "prod",
    poll_interval=30  # seconds
)
```

### 🛡️ **Built-in Validation**
```python
# Multiple validation strategies
config.port.add_validator(RangeValidator(1, 65535))
config.email.add_validator(RegexValidator(r".*@company\.com$"))
config.api_config.add_validator(PydanticValidator(MyModel))

# Validation on assignment
config.port = 70000  # Raises ConfigItemValidationError
```

### ☁️ **AWS Native**
```python
# First-class AWS support
from fastcfg.sources.aws import (
    from_appconfig,
    from_parameter_store,
    from_secrets_manager,
    from_lambda_environment
)

# Built-in retry and caching
config.update(
    from_parameter_store("/myapp/prod/"),
    retry=True,
    cache=TTLCache(minutes=5)
)
```

### 🔌 **Works with Pydantic**
```python
# Use your existing Pydantic models
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str
    port: int = 5432
    ssl_enabled: bool = True

config.database.add_validator(PydanticValidator(DatabaseConfig))
```

### 🎯 **Smart Defaults**
```python
from fastcfg import config

# Just works - no setup required
config.debug = False
config.timeout = 30
config.retries = 3

# Add sources as needed
if running_in_aws():
    config.update(from_lambda_environment())
```

## 🔧 Advanced Usage

### Environment Management

```python
from fastcfg import Config

# Create environment-specific configs
config = Config(
    dev={"api_url": "http://localhost:8000"},
    staging={"api_url": "https://staging.api.com"},
    prod={"api_url": "https://api.com"}
)

# Switch environments dynamically
config.set_environment("prod")
print(config.api_url)  # https://api.com
```

### Loading from Files

```python
from fastcfg import config
from fastcfg.sources.files import from_yaml, from_json

# Load configurations
config.update(from_yaml("config/base.yml"))
config.update(from_json("config/secrets.json"))

# Layer configurations
for env in ["base", "prod", "local"]:
    config.update(from_yaml(f"config/{env}.yml"))
```

### AWS Integration

```python
from fastcfg import config
from fastcfg.sources.aws import from_appconfig

# Load from AppConfig with automatic refresh
config.update(
    from_appconfig(
        application="my-app",
        environment="prod",
        profile="feature-flags"
    )
)

# Your config now auto-updates when AppConfig changes!
```

## 🔥 Coming Soon

### Event Listeners

```python
@config.on_change("database.connection_string")
def handle_connection_change(event):
    print(f"Connection changed from {event.old_value} to {event.new_value}")
    recreate_connection_pool()

@config.on_change("features.*")
def handle_feature_change(event):
    clear_feature_cache()
```

### State Tracking

```python
# Enable state tracking
config.enable_state_tracking()

# Get configuration history
history = config.api_key.get_history()
for change in history:
    print(f"{change.timestamp}: {change.old_value} -> {change.new_value}")

# Rollback to previous values
config.rollback_to(timestamp="2024-01-10T10:00:00")
```

## 🤝 Contributing

We love contributions! FastCFG is built by developers who needed better configuration management, for developers who need better configuration management.

```bash
# Clone the repo
git clone https://github.com/yourusername/fastcfg.git

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest
```

## 📊 Benchmarks

Run the benchmarks yourself:

```bash
cd benchmarks
python benchmark_comprehensive.py
```

## 🏢 Who's Using FastCFG?

- **Startups** love the simplicity and speed
- **Enterprises** trust the AWS integration and validation
- **Serverless teams** rely on the performance and real-time updates

## 📝 License

MIT - Build amazing things!

## 🙏 Acknowledgments

Built with frustration, maintained with love. Special thanks to the serverless community and everyone who's had to restart a Lambda function just to change a config value.

---

**FastCFG**: Because your serverless functions deserve a proper nervous system. 🧠⚡️

*Built with ❤️ by Josh Breininger - Making configuration management suck less, one Lambda at a time.*
