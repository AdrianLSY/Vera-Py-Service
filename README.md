# Vera-Py-Service

A Python microservice framework for building WebSocket-based services that integrate with the Vera Plugboard. This service provides a robust foundation for creating distributed, event-driven applications with automatic action discovery and registration.

## Overview

Vera-Py-Service is designed to be a pluggable microservice that connects to a central Plugboard system via WebSocket. It functions as an RPC (Remote Procedure Call) API, automatically discovering and registering actions (procedures), making it easy to build scalable, distributed systems where services can communicate and execute actions remotely.

### Key Features

- **RPC API**: Functions as a Remote Procedure Call API, allowing remote execution of actions
- **Authentication System**: Complete JWT-based authentication with user registration, login, and logout
- **User Management**: Full user lifecycle management with username, email, and phone number support
- **Password Security**: Bcrypt-based password hashing for secure credential storage
- **Token Revocation**: JWT token revocation system for secure logout and session management
- **High Availability**: Multiple consumer instances can be deployed for redundancy and fault tolerance
- **Horizontal Scaling**: Easy horizontal scaling by deploying additional consumer instances to meet demand
- **WebSocket Communication**: Real-time bidirectional communication with the Plugboard system
- **Automatic Action Discovery**: Dynamic discovery and registration of actions
- **Type-Safe Models**: Built on Pydantic for robust data validation and serialization
- **Event-Driven Architecture**: Support for various event types (service updates, token management, etc.)
- **Docker Support**: Containerized deployment with Alpine Linux and PostgreSQL

## Architecture

### Core Components

#### 1. **ActionSchema** (`core/action_schema.py`)
Base class for all action schemas providing:
- JSON schema generation
- Model serialization/deserialization
- Type validation through Pydantic
- Discriminator-based identification

#### 2. **ActionRunner** (`core/action_runner.py`)
Abstract base class for executable actions that:
- Inherits from ActionSchema
- Defines the interface for action execution
- Returns standardized ActionResponse objects

#### 3. **ActionRegistry** (`core/action_registry.py`)
Dynamic discovery system that:
- Automatically finds ActionRunner classes in specified directories
- Registers actions and events at runtime
- Provides JSON schema generation for all registered actions

#### 4. **PlugboardClient** (`core/plugboard_client.py`)
Main client for WebSocket communication that:
- Manages connection to the Plugboard system
- Handles event routing and processing
- Maintains service and token state
- Executes actions based on incoming requests

#### 5. **ActionResponse** (`core/action_response.py`)
Standardized response format containing:
- HTTP status codes
- Optional messages
- Response data fields

### Data Models

#### **Service** (`schemas/service.py`)
Represents a service instance with:
- Unique identifier
- Service name
- Creation and update timestamps

#### **Token** (`schemas/token.py`)
Authentication token with:
- Unique identifier
- Context and value
- Service association
- Expiration timestamps

#### **User** (`models/user.py`)
User account model with:
- Unique username, email, and phone number
- Full name and password digest
- Soft deletion support
- Comprehensive indexing for performance

#### **Revocation** (`models/revocation.py`)
JWT token revocation tracking with:
- JWT ID (JTI) for unique token identification
- Expiration timestamp for cleanup
- Audit trail with creation timestamps

### Event System

The service handles various predefined event types from the Plugboard system:

- **RequestEvent**: Handles incoming action requests
- **PhxJoinEvent**: Phoenix framework join events
- **PhxReplyEvent**: Phoenix framework reply events
- **ServiceUpdatedEvent**: Service configuration updates
- **ServiceDeletedEvent**: Service removal notifications
- **TokenCreatedEvent**: Token creation notifications
- **TokenDeletedEvent**: Token removal notifications
- **ConsumerConnectedEvent**: Consumer connection events

*Note: Events are predefined by the Plugboard system and typically don't need to be created by developers.*

## Authentication System

The service includes a complete JWT-based authentication system with three main actions:

### Authentication Actions

#### **Register** (`actions/register.py`)
Creates a new user account and returns a JWT token:

**Input Parameters:**
- `username` (str): Unique username (configurable length limits)
- `name` (str): User's full name (1-255 characters)
- `email` (str): Valid email address (must be unique)
- `phone_number` (str): Phone number in any format (converted to E.164)
- `password` (str): User password (configurable length limits)
- `not_before` (int, optional): JWT not-before timestamp
- `expires_at` (int, optional): JWT expiration timestamp

**Features:**
- Automatic phone number validation and E.164 formatting
- Bcrypt password hashing
- Duplicate prevention (username, email, phone number uniqueness)
- JWT token generation with configurable claims
- Comprehensive error handling for constraint violations

**Response:**
- Status 201: User created successfully with JWT token
- Status 409: Username, email, or phone number already exists
- Status 500: Server error

#### **Login** (`actions/login.py`)
Authenticates an existing user and returns a JWT token:

**Input Parameters:**
- `username` (str, optional): Username for authentication
- `email` (str, optional): Email for authentication
- `phone_number` (str, optional): Phone number for authentication
- `password` (str): User password
- `not_before` (int, optional): JWT not-before timestamp
- `expires_at` (int, optional): JWT expiration timestamp

**Features:**
- Flexible authentication (username, email, or phone number)
- Exactly one identifier required
- Phone number validation and E.164 formatting
- Secure password verification with bcrypt
- JWT token generation with user ID

**Response:**
- Status 200: Authentication successful with JWT token
- Status 400: Invalid input (multiple/no identifiers)
- Status 401: Invalid password
- Status 404: User not found
- Status 500: Server error

#### **Logout** (`actions/logout.py`)
Revokes a JWT token by adding it to the revocation list:

**Input Parameters:**
- `jwt` (str): JWT token to revoke

**Features:**
- JWT validation and decoding
- Token revocation tracking
- Duplicate revocation prevention
- Automatic cleanup support via expiration timestamps

**Response:**
- Status 200: Token successfully revoked
- Status 401: Invalid or malformed token
- Status 409: Token already revoked
- Status 500: Server error

### Security Features

- **Password Hashing**: Uses bcrypt with automatic salt generation
- **JWT Security**: Configurable algorithm, issuer, and audience validation
- **Token Revocation**: Complete token lifecycle management
- **Input Validation**: Comprehensive validation using Pydantic
- **Phone Number Validation**: International phone number support with E.164 formatting
- **Soft Deletion**: User accounts support soft deletion for data integrity
- **Database Transactions**: All operations wrapped in transactions for consistency

### JWT Configuration

The authentication system requires several environment variables:

- `JWT_SECRET`: Secret key for JWT signing
- `JWT_ISSUER`: JWT issuer claim
- `JWT_AUDIENCE`: JWT audience claim
- `MIN_USERNAME_LENGTH`: Minimum username length
- `MAX_USERNAME_LENGTH`: Maximum username length
- `MIN_PASSWORD_LENGTH`: Minimum password length
- `MAX_PASSWORD_LENGTH`: Maximum password length

## Installation

### Prerequisites

- Python 3.12+
- pip package manager
- PostgreSQL 17+ (for authentication features)
- Docker and Docker Compose (for containerized deployment)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Vera-Py-Service
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**:
   ```bash
   # Start PostgreSQL with Docker Compose
   docker compose up -d postgres

   # Or set up a local PostgreSQL instance
   # Create database and user as needed
   ```

4. **Set environment variables**:
   ```bash
   # Core service configuration
   export WEBSOCKET_URL="ws://localhost:4000/websocket"
   export TOKEN="your_plugboard_token"

   # Database configuration
   export POSTGRES_USER="auth"
   export POSTGRES_PASSWORD="your_secure_password"
   export POSTGRES_DB="auth"
   export POSTGRES_PORT="5432"

   # JWT configuration
   export JWT_SECRET="your_jwt_secret_key"
   export JWT_ISSUER="vera-py-service"
   export JWT_AUDIENCE="vera-clients"

   # Password policy
   export MIN_USERNAME_LENGTH="3"
   export MAX_USERNAME_LENGTH="50"
   export MIN_PASSWORD_LENGTH="8"
   export MAX_PASSWORD_LENGTH="128"
   ```

5. **Run database migrations**:
   ```bash
   # Initialize database tables
   alembic upgrade head
   ```

6. **Run the service**:
   ```bash
   python entrypoint.py
   ```

### Docker Deployment

#### Using Docker Compose (Recommended)

1. **Create environment file** (`.env`):
   ```bash
   # Core service configuration
   WEBSOCKET_URL=ws://your-plugboard:4000/websocket
   TOKEN=your_plugboard_token

   # Database configuration
   POSTGRES_USER=auth
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=auth
   POSTGRES_PORT=5432

   # JWT configuration
   JWT_SECRET=your_jwt_secret_key
   JWT_ALGORITHM=HS256
   JWT_ISSUER=vera-py-service
   JWT_AUDIENCE=vera-clients

   # Password policy
   MIN_USERNAME_LENGTH=3
   MAX_USERNAME_LENGTH=50
   MIN_PASSWORD_LENGTH=8
   MAX_PASSWORD_LENGTH=128
   ```

2. **Start the complete stack**:
   ```bash
   # Start PostgreSQL and authentication service
   docker compose up -d

   # View logs
   docker compose logs -f auth
   ```

3. **Scale the authentication service**:
   ```bash
   # Scale to multiple instances
   docker compose up -d --scale auth=3
   ```

#### Manual Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t vera-py-service .
   ```

2. **Run with external PostgreSQL**:
   ```bash
   docker run -e WEBSOCKET_URL="ws://your-plugboard:4000/websocket" \
              -e TOKEN="your_plugboard_token" \
              -e POSTGRES_USER="auth" \
              -e POSTGRES_PASSWORD="your_password" \
              -e POSTGRES_DB="auth" \
              -e POSTGRES_HOST="your-postgres-host" \
              -e JWT_SECRET="your_jwt_secret" \
              vera-py-service
   ```

3. **Scale horizontally with multiple containers**:
   ```bash
   # Deploy multiple instances for high availability and load distribution
   docker run -d --name auth-1 -e WEBSOCKET_URL="ws://your-plugboard:4000/websocket" -e TOKEN="your_plugboard_token" -e POSTGRES_HOST="your-postgres-host" -e JWT_SECRET="your_jwt_secret" vera-py-service
   docker run -d --name auth-2 -e WEBSOCKET_URL="ws://your-plugboard:4000/websocket" -e TOKEN="your_plugboard_token" -e POSTGRES_HOST="your-postgres-host" -e JWT_SECRET="your_jwt_secret" vera-py-service
   docker run -d --name auth-3 -e WEBSOCKET_URL="ws://your-plugboard:4000/websocket" -e TOKEN="your_plugboard_token" -e POSTGRES_HOST="your-postgres-host" -e JWT_SECRET="your_jwt_secret" vera-py-service
   ```

## Usage

### RPC API Functionality

The service acts as an RPC API where:

1. **Action Registration**: All `ActionRunner` classes in the `actions/` directory are automatically discovered and registered
2. **Remote Execution**: Actions can be called remotely through the Plugboard system
3. **Request/Response Pattern**: Uses a standardized request/response pattern with `RequestEvent` and `ActionResponse`
4. **Type Safety**: Full type validation and serialization for both requests and responses
5. **Error Handling**: Graceful handling of unknown actions and execution errors

### High Availability & Scaling

Since this service acts as a **consumer** in the Plugboard system:

- **Multiple Instances**: Deploy multiple consumer instances for redundancy and load distribution
- **Load Balancing**: The Plugboard system can distribute requests across available consumer instances
- **Fault Tolerance**: If one consumer instance fails, others continue processing requests
- **Easy Scaling**: Simply deploy additional consumer instances to handle increased load
- **Stateless Design**: Each consumer instance is stateless, making horizontal scaling straightforward

### Authentication Usage Examples

#### User Registration
```python
# Register a new user
register_action = {
    "action": "Register",
    "data": {
        "username": "johndoe",
        "name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+1-555-123-4567",
        "password": "securepassword123",
        "expires_at": 1735689600  # Optional: JWT expiration timestamp
    }
}

# Response: {"status_code": 201, "fields": {"jwt": "...", "expires_at": 1735689600}}
```

#### User Login
```python
# Login with username
login_action = {
    "action": "Login",
    "data": {
        "username": "johndoe",
        "password": "securepassword123"
    }
}

# Login with email
login_action = {
    "action": "Login",
    "data": {
        "email": "john@example.com",
        "password": "securepassword123"
    }
}

# Login with phone number
login_action = {
    "action": "Login",
    "data": {
        "phone_number": "+15551234567",
        "password": "securepassword123"
    }
}

# Response: {"status_code": 200, "fields": {"jwt": "...", "expires_at": 1735689600}}
```

#### User Logout
```python
# Revoke a JWT token
logout_action = {
    "action": "Logout",
    "data": {
        "jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}

# Response: {"status_code": 200, "message": "Token successfully revoked"}
```

### Creating Custom Actions

To create a new action, inherit from `ActionRunner`:

```python
from typing import TYPE_CHECKING, override
from pydantic import Field
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class MyCustomAction(ActionRunner):
    """
    A custom action that demonstrates the framework.
    """
    input_data: str = Field(description="Input data for processing")
    multiplier: int = Field(description="Multiplier value", default=2)

    @classmethod
    @override
    def description(cls) -> str:
        return "Processes input data with a multiplier"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        result = self.input_data * self.multiplier
        return ActionResponse(
            status_code=200,
            message="Processing completed",
            fields={"result": result}
        )
```

### Working with Events

Events are predefined by the Plugboard system and automatically handled by the framework. The service will receive and process events like service updates, token changes, and consumer connections without requiring custom event handlers.

If you need to handle specific event logic, you can extend the existing event classes in the `events/` directory, but this is rarely necessary as the framework handles most event processing automatically.

### Directory Structure

Place your custom actions in the `actions/` directory. The ActionRegistry will automatically discover and register them.

```
Py-Service/
├── actions/           # Custom action implementations
├── events/            # Predefined event handlers (rarely modified)
├── core/              # Core framework components
├── schemas/            # Data schemas
├── tests/             # Test suite
└── entrypoint.py      # Application entry point
```

## Development

### Running Tests

The project includes comprehensive tests using Python's unittest framework:

```bash
# Run all tests
python -m tests

# Run specific test module
python -m tests.core.action_schema_test
```

### Code Style

This project follows strict Python coding standards:

- **Type Hints**: All functions and methods must have complete type annotations
- **Docstrings**: Comprehensive documentation for all public methods and classes
- **Naming**: Descriptive variable names (no single-letter variables)
- **Formatting**: Spaces around operators, proper line breaks for multi-parameter functions
- **Imports**: Sorted by character length, specific imports only

### Error Handling

The framework includes robust error handling:

- **Connection Management**: Automatic reconnection and error recovery
- **Validation**: Pydantic-based input validation
- **Action Execution**: Graceful handling of unknown actions and execution errors
- **WebSocket Errors**: Proper handling of connection issues and malformed messages

## Configuration

### Environment Variables

#### Core Service Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `WEBSOCKET_URL` | WebSocket URL for Plugboard connection | Yes | - |
| `TOKEN` | Authentication token for Plugboard | Yes | - |

#### Database Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POSTGRES_USER` | PostgreSQL username | Yes | - |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes | - |
| `POSTGRES_DB` | PostgreSQL database name | Yes | - |
| `POSTGRES_HOST` | PostgreSQL host | No | localhost |
| `POSTGRES_PORT` | PostgreSQL port | No | 5432 |

#### JWT Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `JWT_SECRET` | Secret key for JWT signing | Yes | - |
| `JWT_ALGORITHM` | JWT signing algorithm | No | HS256 |
| `JWT_ISSUER` | JWT issuer claim | Yes | - |
| `JWT_AUDIENCE` | JWT audience claim | Yes | - |

#### Password Policy Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MIN_USERNAME_LENGTH` | Minimum username length | Yes | - |
| `MAX_USERNAME_LENGTH` | Maximum username length | Yes | - |
| `MIN_PASSWORD_LENGTH` | Minimum password length | Yes | - |
| `MAX_PASSWORD_LENGTH` | Maximum password length | Yes | - |

### Example Configuration

```bash
# Development
export WEBSOCKET_URL="ws://localhost:4000/websocket"
export TOKEN="dev_token_123"
export POSTGRES_USER="auth"
export POSTGRES_PASSWORD="dev_password"
export POSTGRES_DB="auth"
export JWT_SECRET="dev_jwt_secret_key"
export JWT_ISSUER="vera-py-service"
export JWT_AUDIENCE="vera-clients"
export MIN_USERNAME_LENGTH="3"
export MAX_USERNAME_LENGTH="50"
export MIN_PASSWORD_LENGTH="8"
export MAX_PASSWORD_LENGTH="128"

# Production
export WEBSOCKET_URL="wss://plugboard.yourdomain.com/websocket"
export TOKEN="prod_token_456"
export POSTGRES_USER="auth"
export POSTGRES_PASSWORD="secure_production_password"
export POSTGRES_DB="auth"
export POSTGRES_HOST="postgres.yourdomain.com"
export JWT_SECRET="secure_production_jwt_secret"
export JWT_ISSUER="vera-py-service"
export JWT_AUDIENCE="vera-clients"
export MIN_USERNAME_LENGTH="3"
export MAX_USERNAME_LENGTH="50"
export MIN_PASSWORD_LENGTH="12"
export MAX_PASSWORD_LENGTH="128"
```

## Dependencies

### Core Framework
- **pydantic**: Data validation and serialization
- **websockets**: WebSocket client implementation
- **typing-extensions**: Enhanced type hints
- **annotated-types**: Type annotation utilities

### Authentication & Security
- **bcrypt**: Password hashing and verification
- **PyJWT**: JWT token creation and validation
- **email-validator**: Email address validation
- **phonenumbers**: International phone number validation and formatting

### Database & ORM
- **SQLAlchemy**: Database ORM and connection management
- **alembic**: Database migration management
- **greenlet**: SQLAlchemy async support

### Additional Utilities
- **dnspython**: DNS resolution for email validation
- **idna**: Internationalized domain name support

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

1. Follow the established code style and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for any API changes
4. Ensure all tests pass before submitting changes

## Support

For questions, issues, or contributions, please refer to the project repository or contact the development team.
