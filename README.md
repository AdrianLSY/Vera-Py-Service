# Vera-Py-Service

A Python microservice framework for building WebSocket-based services that integrate with the Vera Plugboard. This service provides a robust foundation for creating distributed, event-driven applications with automatic action discovery and registration.

## Overview

Vera-Py-Service is designed to be a pluggable microservice that connects to a central Plugboard system via WebSocket. It functions as an RPC (Remote Procedure Call) API, automatically discovering and registering actions (procedures), making it easy to build scalable, distributed systems where services can communicate and execute actions remotely.

### Key Features

- **RPC API**: Functions as a Remote Procedure Call API, allowing remote execution of actions
- **High Availability**: Multiple consumer instances can be deployed for redundancy and fault tolerance
- **Horizontal Scaling**: Easy horizontal scaling by deploying additional consumer instances to meet demand
- **WebSocket Communication**: Real-time bidirectional communication with the Plugboard system
- **Automatic Action Discovery**: Dynamic discovery and registration of actions
- **Type-Safe Models**: Built on Pydantic for robust data validation and serialization
- **Event-Driven Architecture**: Support for various event types (service updates, token management, etc.)
- **Docker Support**: Containerized deployment with Alpine Linux

## Architecture

### Core Components

#### 1. **ActionModel** (`core/action_model.py`)
Base class for all action models providing:
- JSON schema generation
- Model serialization/deserialization
- Type validation through Pydantic
- Discriminator-based identification

#### 2. **ActionRunner** (`core/action_runner.py`)
Abstract base class for executable actions that:
- Inherits from ActionModel
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

#### **Service** (`models/service.py`)
Represents a service instance with:
- Unique identifier
- Service name
- Creation and update timestamps

#### **Token** (`models/token.py`)
Authentication token with:
- Unique identifier
- Context and value
- Service association
- Expiration timestamps

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

## Installation

### Prerequisites

- Python 3.13+
- pip package manager

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Py-Service
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   export WEBSOCKET_URL="ws://localhost:4000/websocket"
   export TOKEN="your_plugboard_token"
   ```

4. **Run the service**:
   ```bash
   python entrypoint.py
   ```

### Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t vera-py-service .
   ```

2. **Run a single container**:
   ```bash
   docker run -e WEBSOCKET_URL="ws://your-plugboard:4000/websocket" \
              -e TOKEN="your_plugboard_token" \
              vera-py-service
   ```

3. **Scale horizontally with multiple containers**:
   ```bash
   # Deploy multiple instances for high availability and load distribution
   docker run -d --name consumer-1 -e WEBSOCKET_URL="ws://your-plugboard:4000/websocket" -e TOKEN="your_plugboard_token" vera-py-service
   docker run -d --name consumer-2 -e WEBSOCKET_URL="ws://your-plugboard:4000/websocket" -e TOKEN="your_plugboard_token" vera-py-service
   docker run -d --name consumer-3 -e WEBSOCKET_URL="ws://your-plugboard:4000/websocket" -e TOKEN="your_plugboard_token" vera-py-service
   ```

4. **Using Docker Compose for orchestration**:
   ```yaml
   py_services:
     consumer:
       build: .
       environment:
         - WEBSOCKET_URL=ws://your-plugboard:4000/websocket
         - TOKEN=your_plugboard_token
       deploy:
         replicas: 3  # Scale to 3 instances
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
├── models/            # Data models
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
python -m tests.core.action_model_test
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

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `WEBSOCKET_URL` | WebSocket URL for Plugboard connection | Yes | - |
| `TOKEN` | Authentication token for Plugboard | Yes | - |

### Example Configuration

```bash
# Development
export WEBSOCKET_URL="ws://localhost:4000/websocket"
export TOKEN="dev_token_123"

# Production
export WEBSOCKET_URL="wss://plugboard.yourdomain.com/websocket"
export TOKEN="prod_token_456"
```

## Dependencies

- **pydantic**: Data validation and serialization
- **websockets**: WebSocket client implementation
- **typing-extensions**: Enhanced type hints
- **annotated-types**: Type annotation utilities

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

1. Follow the established code style and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for any API changes
4. Ensure all tests pass before submitting changes

## Support

For questions, issues, or contributions, please refer to the project repository or contact the development team.
