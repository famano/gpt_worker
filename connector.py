from abc import abstractmethod
import json
import openai
from openai import OpenAI
from dataholder import DataHolder

class Connector:
    @abstractmethod
    def CreateResponse(messages, tools):
        pass

class OpenAIConnector(Connector):

    def CreateResponse(messages: list[str], tools: list[type], dataholder: DataHolder, model: str="gpt-4o") -> list[str]:
        llm = OpenAI()

        response = llm.chat.completions.create(
            model=model,
            messages=messages,
            tools=[openai.pydantic_function_tool(tool) for tool in tools]
        )
        # TODO: edge case
        
        print("choice:")
        print(response.choices[0])

        if response.choices[0].message.content != None:
            messages.append({
                "role": response.choices[0].message.role,
                "content": response.choices[0].message.content
            })

        if response.choices[0].finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            messages.append({
                "role": response.choices[0].message.role,
                "tool_calls": [vars(tool_call) for tool_call in tool_calls]
            })
        
            for tool_call in tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                arguments.update({"dataholder": dataholder})
                tool = next(filter(lambda tool: tool.__name__ == tool_call.function.name, tools), None)
                content = tool.run(arguments)
                messages.append({
                    "role": "tool",
                    "content": json.dumps(content),
                    "tool_call_id": tool_call.id
                })
            OpenAIConnector.CreateResponse(messages=messages, tools=tools, dataholder=dataholder, model=model)
        
        return messages