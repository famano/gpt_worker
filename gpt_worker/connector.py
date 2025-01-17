from abc import abstractmethod
import json
import logging
from typing import List, Dict, Type, Optional
import openai
from openai import OpenAI
from openai import APIError, RateLimitError
from gpt_worker.dataholder import DataHolder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log format configuration
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler('connector.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Custom exceptions for Connector errors
class ConnectorError(Exception):
    """Base exception class for Connector errors"""
    pass

class APIConnectionError(ConnectorError):
    """Raised when API connection fails"""
    pass

class ToolExecutionError(ConnectorError):
    """Raised when tool execution fails"""
    pass

# Abstract Connector class
class Connector:
    @abstractmethod
    def CreateResponse(messages: List[Dict], tools: List[Type]) -> List[Dict]:
        """
        Abstract method to create a response by interacting with external API using provided messages and tools.
        """
        pass

# Process responses with OpenAI's API and handle errors
class OpenAIConnector(Connector):
    MAX_RETRIES = 3
    RETRY_DELAY = 20  # seconds

    @classmethod
    def CreateResponse(cls, messages: List[Dict], tools: List[Type], dataholder: DataHolder, model: str):
        """
        Communicates with the OpenAI API to generate a response based on input messages.
        Handles retries on rate limits and manages tool execution for enhanced task processing.
        """
        llm = OpenAI()
        retry_count = 0

        while retry_count < cls.MAX_RETRIES:
            try:
                response = llm.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=[openai.pydantic_function_tool(tool) for tool in tools]
                )

                logger.debug(f"API Response: {response.choices[0]}")

                if not response.choices:
                    raise APIConnectionError("No response choices returned from API")

                if response.choices[0].message.content is not None:
                    message = {
                        "role": response.choices[0].message.role,
                        "content": response.choices[0].message.content
                    }
                    messages.append(message)
                    yield message

                if response.choices[0].finish_reason == "tool_calls":
                    tool_calls = response.choices[0].message.tool_calls
                    message = {
                        "role": response.choices[0].message.role,
                        "tool_calls": [vars(tool_call) for tool_call in tool_calls]
                    }
                    messages.append(message)
                    yield message

                    for tool_call in tool_calls:
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                            arguments.update({"dataholder": dataholder})

                            tool = next((t for t in tools if t.__name__ == tool_call.function.name), None)
                            if not tool:
                                raise ToolExecutionError(f"Tool not found: {tool_call.function.name}")

                            content = tool.run(arguments)
                            if not content.get("success", False):
                                logger.error(f"Tool execution failed: {content.get('content', 'Unknown error')}")

                            message = {
                                "role": "tool",
                                "content": json.dumps(content),
                                "tool_call_id": tool_call.id
                            }
                            messages.append(message)
                            yield message
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid tool arguments: {e}")
                            raise ToolExecutionError(f"Invalid tool arguments: {e}")
                        except Exception as e:
                            logger.error(f"Tool execution error: {e}")
                            raise ToolExecutionError(f"Tool execution failed: {e}")

                    for message in cls.CreateResponse(messages=messages, tools=tools, dataholder=dataholder, model=model):
                        yield message
                    return  # ツール実行後は再帰呼び出しの結果を返して終了

                return  # 正常終了時はループを抜ける

            except RateLimitError as e:
                retry_count += 1
                if retry_count < cls.MAX_RETRIES:
                    logger.warning(f"Rate limit reached. Retrying in {cls.RETRY_DELAY} seconds...")
                    import time
                    time.sleep(cls.RETRY_DELAY)
                else:
                    logger.error("Max retries reached for rate limit")
                    raise APIConnectionError(f"Rate limit exceeded after {cls.MAX_RETRIES} retries")

            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise APIConnectionError(f"OpenAI API error: {e}")

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise ConnectorError(f"Unexpected error: {e}")
