# Logging System Documentation

This FastAPI application includes a comprehensive logging system built with `structlog` and Python's standard logging library. The system provides structured logging, multiple output formats, file rotation, and performance monitoring.

## Features

### 🚀 **Core Features**
- **Structured Logging**: JSON, text, and structured key-value formats
- **File Rotation**: Daily, weekly, or size-based rotation
- **Multiple Handlers**: Console, file, and separate error file handlers
- **Performance Monitoring**: Request timing and slow query detection
- **Security Event Logging**: Dedicated security event tracking
- **Request/Response Logging**: Comprehensive HTTP request logging
- **Exception Handling**: Structured exception logging with context

### 📊 **Log Formats**

The system supports different formats for console and file output:

#### Pretty Console Format (Default for Console)
```
10:54:01 | INFO     | app | User logged in successfully | user_id=123 | email=user@example.com
10:54:01 | WARNING  | demo | Database query slow | query_time=2.5 | table=users
10:54:01 | ERROR    | auth | Authentication failed | attempts=3 | locked=false
```
*Colored, clean format ideal for development*

#### JSON Format (Default for Files)
```json
{
  "timestamp": "2025-06-24T10:44:40.013889",
  "level": "INFO",
  "logger": "app",
  "message": "User logged in successfully",
  "module": "auth",
  "function": "login",
  "line": 31,
  "extra": {
    "user_id": 123,
    "email": "user@example.com"
  }
}
```
*Machine-readable format for log aggregation*

#### Text Format
```
2025-06-24 10:44:40 | INFO     | app | User logged in successfully
```
*Simple text format*

#### Structured Format
```
2025-06-24T10:44:40.013889 | INFO     | app | User logged in successfully | user_id=123 | email=user@example.com
```
*Key-value format with timestamp*

## Configuration

Configure logging through environment variables or the `Settings` class in `app/core/config.py`:

```python
# Logging Configuration
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json                   # json, text, structured (for files)
CONSOLE_LOG_FORMAT=pretty         # pretty, json, text, structured (for console)
LOG_FILE=logs/app.log            # Path to log file (optional)
LOG_MAX_SIZE=10                  # MB - for size-based rotation
LOG_RETENTION=7                  # Days - number of backup files
LOG_ROTATION=daily               # daily, weekly, size
ENABLE_REQUEST_LOGGING=true      # Enable HTTP request logging
ENABLE_SQL_LOGGING=false         # Enable SQLAlchemy logging
LOG_SQL_QUERIES=false           # Log individual SQL queries
LOG_SLOW_QUERIES_THRESHOLD=1.0   # Seconds - threshold for slow query alerts
```

## Usage Examples

### Basic Logging

```python
from app.core.logging import get_logger

# Get a logger for your module
logger = get_logger("my_module")

# Basic logging
logger.info("User logged in")
logger.warning("Database connection slow")
logger.error("Authentication failed")

# Logging with extra context
logger.info(
    "User action completed", 
    extra={
        "user_id": 123,
        "action": "profile_update",
        "duration": 0.5
    }
)
```

### Pre-configured Loggers

```python
from app.core.logging import (
    app_logger,      # General application logging
    api_logger,      # API endpoint logging
    database_logger, # Database operations
    security_logger  # Security events
)

# Use pre-configured loggers
app_logger.info("Application started")
api_logger.debug("Processing request", extra={"endpoint": "/users"})
database_logger.warning("Connection pool exhausted")
security_logger.error("Failed login attempt", extra={"ip": "1.2.3.4"})
```

### Exception Logging

```python
from app.core.logging import log_exception, get_logger

logger = get_logger("my_module")

try:
    # Some operation that might fail
    risky_operation()
except Exception as e:
    log_exception(
        logger, 
        e, 
        context={
            "user_id": 123,
            "operation": "data_processing"
        }
    )
```

### Security Event Logging

```python
from app.core.logging import log_security_event

# Log security events
log_security_event("FAILED_LOGIN", {
    "username": "john_doe",
    "ip_address": "192.168.1.100",
    "attempts": 3,
    "timestamp": datetime.utcnow()
})

log_security_event("SUSPICIOUS_ACTIVITY", {
    "user_id": 456,
    "activity_type": "unusual_access_pattern",
    "details": "Multiple rapid requests"
})
```

### Performance Logging

```python
from app.core.logging import performance_logger

# Log slow database queries
performance_logger.log_slow_query(
    query="SELECT * FROM users WHERE created_at > %s",
    duration=2.5,
    params={"created_at": "2024-01-01"}
)

# Log request timing
performance_logger.log_request_timing(
    method="POST",
    path="/api/v1/users",
    duration=1.2,
    status_code=201
)
```

## Middleware Integration

The logging system includes middleware for automatic request logging:

```python
from app.core.middleware import RequestLoggingMiddleware

# Already integrated in main.py
app.add_middleware(RequestLoggingMiddleware)
```

This middleware automatically logs:
- Request start with full details (method, URL, headers, IP)
- Request completion with timing and response status
- Request failures with exception details
- Request IDs for correlation

## File Structure

```
logs/
├── app.log        # Main application log (all levels)
└── app_error.log  # Error and critical logs only
```

## Log Rotation

### Daily Rotation (Default)
- New log file created each day
- Old files kept for configured retention period
- Format: `app.log.2024-06-24`

### Size-based Rotation
- New log file when size limit reached
- Numbered backup files: `app.log.1`, `app.log.2`, etc.

### Weekly Rotation
- New log file each week (Monday)
- Format: `app.log.2024-W25`

## Environment-specific Configuration

### Development
```bash
LOG_LEVEL=DEBUG
CONSOLE_LOG_FORMAT=pretty         # Colored, clean output
LOG_FORMAT=structured             # For file logging
ENABLE_SQL_LOGGING=true
LOG_SQL_QUERIES=true
```

### Production
```bash
LOG_LEVEL=INFO
CONSOLE_LOG_FORMAT=json           # If using container logging
LOG_FORMAT=json                   # Structured for log aggregation
LOG_FILE=logs/app.log
LOG_ROTATION=daily
LOG_RETENTION=30
ENABLE_REQUEST_LOGGING=true
```

## 🔇 Noise Reduction

The logging system automatically reduces noise from development tools:

- **File Watchers**: `watchfiles` (FastAPI dev server) set to WARNING level
- **Third-party Libraries**: HTTP clients, database drivers set to WARNING level  
- **Development Tools**: Starlette, multipart parsers set to WARNING level

This eliminates the continuous "change detected" messages and other development noise while preserving important error information.

## Testing

Run the included test scripts to verify logging functionality:

```bash
# Test all logging features
python test_logging.py

# Demo different formats
python demo_logging.py
```

## Monitoring and Alerting

The JSON format is designed for easy integration with log aggregation systems:

- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Prometheus + Grafana**: For metrics and alerting
- **Sentry**: For error tracking and alerting
- **DataDog**: For comprehensive monitoring

## Best Practices

1. **Use appropriate log levels**:
   - `DEBUG`: Detailed diagnostic information
   - `INFO`: General operational messages
   - `WARNING`: Something unexpected but not an error
   - `ERROR`: Error conditions that don't stop the application
   - `CRITICAL`: Serious errors that might stop the application

2. **Include context**:
   ```python
   logger.info("User operation", extra={
       "user_id": user.id,
       "operation": "profile_update",
       "request_id": request.state.request_id
   })
   ```

3. **Use structured data**:
   - Prefer structured extra data over string formatting
   - Makes logs searchable and analyzable

4. **Log security events**:
   ```python
   log_security_event("ACCESS_DENIED", {
       "resource": "/admin/users",
       "user_id": user.id,
       "reason": "insufficient_permissions"
   })
   ```

5. **Monitor performance**:
   - Log slow operations
   - Track request timing
   - Monitor database query performance

## Troubleshooting

### Common Issues

1. **Logs not appearing**: Check `LOG_LEVEL` setting
2. **File permission errors**: Ensure write permissions to log directory
3. **Disk space**: Monitor log file sizes and retention settings
4. **Performance impact**: Use appropriate log levels in production

### Debug Mode

Enable debug logging:
```bash
LOG_LEVEL=DEBUG
```

This will show:
- All application debug messages
- Request/response details
- SQL queries (if enabled)
- Performance metrics

## Integration with External Systems

### Sentry Integration
```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR
)

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[sentry_logging]
)
```

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

The logging system provides a solid foundation for monitoring, debugging, and maintaining your FastAPI application in both development and production environments.
