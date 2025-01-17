# Automated Task Management Framework

This project is an automated task management framework utilizing Python and OpenAI's API, designed to seamlessly integrate intelligent task planning and execution. It is structured to facilitate dynamic workflows by autonomously managing task sequences and interacting with a machine learning model for intelligent task resolution.

## Core Components

1. **agents.py**: Defines the `Planner`, `Worker`, and `Orchestrator` classes that work collaboratively to automate tasks.

2. **tools.py**: Provides various tools and utilities used by agents, implementing basic functionalities like file operations, state updates, and script execution.

3. **connector.py**: Manages the connection to OpenAI's API through the `OpenAIConnector` class, enabling intelligent responses.

4. **cli.py**: Provides a command-line interface that allows users to easily execute and manage tasks.

5. **main.py**: Implements core functionality, managing coordination between agents and task execution.

6. **constants.py**: Defines constants and configuration values used throughout the framework.

7. **dataholder.py**: Handles data retention and management, enabling data sharing between agents.

## Directory Structure

```
gpt_worker/
├── gpt_worker/          # Main source code
│   ├── agents.py
│   ├── cli.py
│   ├── connector.py
│   ├── constants.py
│   ├── dataholder.py
│   ├── main.py
│   └── tools.py
├── tests/               # Test files
│   ├── test_agents.py
│   ├── test_agents_integration.py
│   └── test_tools.py
└── logs/                # Execution logs
```

## Setup and Testing

Ensure your environment has the necessary API key:

```bash
echo $OPENAI_API_KEY
```

To verify functionality, execute:

```bash
pytest tests/
```

This executes all available unit tests and integration tests in the `tests` directory to confirm components work together reliably.

## API Integration

The framework interfaces with OpenAI's API, using the `OpenAIConnector` to interpret task-related queries and responses. Ensure your API key is set as an environment variable named `OPENAI_API_KEY`.

## Installation

To install this package, clone this repository and run the following command:

```bash
pip install .
```

After installation, the `gptw` command will be available.

## Usage

### Basic Commands

```bash
# Initialize a new workspace
gptw init [directory]

# Execute tasks
gptw run [instruction] [options]

# Display current task list
gptw list

# Show current state summary
gptw status
```

### Command Options

#### Global Options
- `--verbose`: Enable detailed output

#### Options for `run` command
- `--model, -m`: Specify the LLM model to use (default: gpt-4-1106-preview)
- `--directory, -d`: Specify working directory

#### Options for `init`, `list`, and `status` commands
- `--directory, -d`: Specify working directory

### Usage Examples

```bash
# Create a new workspace
gptw init myproject

# Execute a task (using GPT-4)
gptw run "Improve the website design" --model gpt-4

# Run with verbose output
gptw run --verbose

# Show task list in specific directory
gptw list --directory myproject

# Check current status
gptw status
```

## Contribution and Workflow

Contribute by extending the functionality or adding new tests. Verify changes with the provided testing suite to maintain the integrity of the framework. When adding new features, ensure to create appropriate tests and follow the existing code style.
