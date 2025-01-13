# Automated Task Management Framework

This project is an automated task management framework utilizing Python and OpenAI's API, designed to seamlessly integrate intelligent task planning and execution. It is structured to facilitate dynamic workflows by autonomously managing task sequences and interacting with a machine learning model for intelligent task resolution.

## Core Components

1. **tools.py**: Contains foundational classes for file operations, state updates, script execution, and plan management.

2. **main.py**: Central script that initiates task orchestration and execution, reading the current plan and state summaries.

3. **agents.py**: Defines the `Planner`, `Worker`, and `Orchestrator` classes, which automate tasks using the utilities from `tools.py`.

4. **connector.py**: Maintains the connection to OpenAI's API, enabling intelligent responses through the `OpenAIConnector` class.

5. **tests directory**: Includes unit tests for various components to ensure they are functioning as expected.

## Setup and Testing

Ensure your environment has the necessary API key:

```bash
echo $OPENAI_API_KEY
```

To verify functionality, execute:

```bash
pytest tests/
```

This executes all available unit tests in the `tests` directory to confirm components work together reliably.

## API Integration

The framework interfaces with OpenAI's API, using the `OpenAIConnector` to interpret task-related queries and responses. Ensure your API key is set as an environment variable named `OPENAI_API_KEY`.

## Usage

To run the task automation, execute `main.py` like so:

```bash
python main.py
```

The script will load tasks from `plan.json` and update from `state_summery.md`, running the automation as prescribed in the task list.

## Contribution and Workflow

Contribute by extending the functionality or adding new tests. Verify changes with the provided testing suite to maintain the integrity of the framework.

