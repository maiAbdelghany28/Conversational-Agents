# <<<< Mai Waheed AbdelMaksoud >>>>
#       <<<< 202200556 >>>>

import os
import json
import requests
import csv
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
API_KEY = os.getenv("API_KEY", os.getenv('OPTOGPT_API_KEY'))
BASE_URL = os.getenv("BASE_URL", os.getenv('BASE_URL'))
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv('OPTOGPT_MODEL'))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Replace with your API key or set it as an environment variable
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# Implementing Basic Tool Calling
def get_current_weather(location):
    """Get the current weather for a location."""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}&aqi=no"
    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return f"Error: {data['error']['message']}"

        weather_info = data["current"]
        return json.dumps({
            "location": data["location"]["name"],
            "temperature_c": weather_info["temp_c"],
            "temperature_f": weather_info["temp_f"],
            "condition": weather_info["condition"]["text"],
            "humidity": weather_info["humidity"],
            "wind_kph": weather_info["wind_kph"]
        })
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def get_weather_forecast(location, days=3):
    """Get a weather forecast for a location for a specified number of days."""
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days={days}&aqi=no"
    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return f"Error: {data['error']['message']}"

        forecast_days = data["forecast"]["forecastday"]
        forecast_data = []

        for day in forecast_days:
            forecast_data.append({
                "date": day["date"],
                "max_temp_c": day["day"]["maxtemp_c"],
                "min_temp_c": day["day"]["mintemp_c"],
                "condition": day["day"]["condition"]["text"],
                "chance_of_rain": day["day"]["daily_chance_of_rain"]
            })

        return json.dumps({
            "location": data["location"]["name"],
            "forecast": forecast_data
        })
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA or country e.g., France",
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get the weather forecast for a location for a specific number of days",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA or country e.g., France",
                    },
                    "days": {
                        "type": "integer",
                        "description": "The number of days to forecast (1-10)",
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["location"],
            },
        },
    }
]

available_functions = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast
}

def process_messages(client, messages, tools=None, available_functions=None):
    """Process messages and invoke tools as needed."""
    tools = tools or []
    available_functions = available_functions or {}

    # Step 1: Send the messages to the model with the tool definitions
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=tools,
    )

    response_message = response.choices[0].message

    # Step 2: Append the model's response to the conversation
    messages.append({
        "Role": response_message.role,
        "Content": response_message.content,
        "ToolCalls": response_message.tool_calls,
    })

    # Step 3: Check if the model wanted to use a tool
    if response_message.tool_calls is not None:
        # Step 4: Extract tool invocation and make evaluation
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            # Step 5: Extend conversation with function response
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        # Step 6: Send the messages back to the model to get the last response
        last_response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
        )
        last_message = last_response.choices[0].message
        messages.append({
            "role": last_message.role,
            "content": last_message.content,
        })

    return messages

# Enhancing with Chain of Thought Reasoning
def calculator(expression):
    """Evaluate a mathematical expression and return the result as plain text."""
    try:
        result = eval(expression)
        return str(result)
    except (ValueError, SyntaxError) as e:
        return f"Error: {str(e)}"

calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g., '2 + 2' or '5 * (3 + 2)'",
                }
            },
            "required": ["expression"],
        },
    }
}

cot_tools = weather_tools + [calculator_tool]
available_functions["calculator"] = calculator

cot_system_message = """You are a helpful assistant that can answer questions about weather and perform calculations.

When responding to complex questions, please follow these steps:
1. Think step-by-step about what information you need.
2. Break down the problem into smaller parts.
3. Use the appropriate tools to gather information.
4. Explain your reasoning clearly using plain text (no LaTeX or special formatting).
5. Provide a clear final answer.

For example, if someone asks about temperature conversions or comparisons between cities, first get the weather data, then use the calculator if needed, showing your work.
"""


def web_search(query):
    """Simulate a web search for information."""
    search_results = {
        "weather forecast": "Weather forecasts predict atmospheric conditions for a specific location and time period. They typically include temperature, precipitation, wind, and other variables.",
        "temperature conversion": "To convert Celsius to Fahrenheit: multiply by 9/5 and add 32. To convert Fahrenheit to Celsius: subtract 32 and multiply by 5/9.",
        "climate change": "Climate change refers to significant changes in global temperature, precipitation, wind patterns, and other measures of climate that occur over several decades or longer.",
        "severe weather": "Severe weather includes thunderstorms, tornadoes, hurricanes, blizzards, floods, and high winds that can cause damage, disruption, and loss of life."
    }

    best_match = None
    best_match_score = 0

    for key in search_results:
        words_in_query = set(query.lower().split())
        words_in_key = set(key.lower().split())
        match_score = len(words_in_query.intersection(words_in_key))

        if match_score > best_match_score:
            best_match = key
            best_match_score = match_score

    if best_match_score > 0:
        return json.dumps({"query": query, "result": search_results[best_match]})
    else:
        return json.dumps({"query": query, "result": "No relevant information found."})

search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search for information on the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                }
            },
            "required": ["query"],
        },
    }
}

react_tools = cot_tools + [search_tool]
available_functions["web_search"] = web_search

react_system_message = """You are a helpful weather and information assistant that uses the ReAct (Reasoning and Acting) approach to solve problems.

When responding to questions, follow this pattern:
1. Thought: Think about what you need to know and what steps to take
2. Action: Use a tool to gather information (weather data, search, calculator)
3. Observation: Review what you learned from the tool
4. ... (repeat the Thought, Action, Observation steps as needed)
5. Final Answer: Provide your response based on all observations

For example:
User: What's the temperature difference between New York and London today?
Thought: I need to find the current temperatures in both New York and London, then calculate the difference.
Action: [Use get_current_weather for New York]
Observation: [Results from weather tool]
Thought: Now I need London's temperature.
Action: [Use get_current_weather for London]
Observation: [Results from weather tool]
Thought: Now I can calculate the difference.
Action: [Use calculator to subtract]
Observation: [Result of calculation]
Final Answer: The temperature difference between New York and London today is X degrees.

Always make your reasoning explicit and show your work.
"""

def run_conversation(client, system_message="You are a helpful weather assistant."):
    """Run a conversation with the user, processing their messages and handling tool calls."""
    messages = [{"role": "system", "content": system_message}]
    print("Weather Assistant: Hello! I can help you with weather information. Ask me about the weather anywhere!")
    print("(Type 'exit' to end the conversation)\n")

    while True:
        # Request user input and append to messages
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nWeather Assistant: Goodbye! Have a great day!")
            break

        messages.append({"role": "user", "content": user_input})

        # Process the messages and get tool calls if any
        messages = process_messages(client, messages, weather_tools, available_functions)

        # Check the last message to see if it's from the assistant or a tool
        last_message = messages[-1]

        # If the message is from a tool, format and print the weather data
        if last_message.get("role") == "tool":
            tool_response = json.loads(last_message["content"])

            if "temperature_c" in tool_response:  # Current weather response
                print(f"\nWeather Assistant: The current weather in {tool_response['location']} is:")
                print(f"- Temperature: {tool_response['temperature_c']}°C ({tool_response['temperature_f']}°F)")
                print(f"- Condition: {tool_response['condition']}")
                print(f"- Humidity: {tool_response['humidity']}%")
                print(f"- Wind Speed: {tool_response['wind_kph']} kph\n")
            elif "forecast" in tool_response:  # Forecast response
                print(f"\nWeather Assistant: The weather forecast for {tool_response['location']} is:")
                for day in tool_response["forecast"]:
                    print(f"- Date: {day['date']}")
                    print(f"  Max Temp: {day['max_temp_c']}°C, Min Temp: {day['min_temp_c']}°C")
                    print(f"  Condition: {day['condition']}")
                    print(f"  Chance of Rain: {day['chance_of_rain']}%")
                print()

        # If the message is from the assistant and has content, print it
        elif last_message.get("role") == "assistant" and last_message.get("content"):
            # Clean up the response by removing LaTeX and unnecessary spaces
            response = last_message["content"]
            response = response.replace("\\[", "").replace("\\]", "")  # Remove LaTeX brackets
            response = re.sub(r"\\frac\{(\d+)\}\{(\d+)\}", r"(\1/\2)", response)  # Replace all LaTeX fractions
            response = response.replace("\\times", "*")  # Replace LaTeX multiplication
            response = response.replace("\\(", "").replace("\\)", "")  # Remove LaTeX inline math
            response = response.replace("\n\n", "\n")  # Remove extra line breaks

            print(f"\nWeather Assistant: {response}\n")

def evaluate_agents(client):
    """Run the comparative evaluation system, collect ratings, and save results."""
    print("=== Comparative Evaluation System ===")
    user_query = input("Enter your query: ").strip()

    # Define agent types and their system messages/tools
    agents = {
        "Basic": {"system_message": "You are a helpful weather assistant.", "tools": weather_tools},
        "Chain of Thought": {"system_message": cot_system_message, "tools": cot_tools},
        "ReAct": {"system_message": react_system_message, "tools": react_tools}
    }

    responses = {}

    # Run all agents
    for agent, config in agents.items():
        messages = [{"role": "system", "content": config["system_message"]}]
        messages.append({"role": "user", "content": user_query})
        response = process_messages(client, messages, config["tools"], available_functions)
        responses[agent] = response[-1]["content"]

    # Collect user ratings
    ratings = {}
    print("\nPlease rate each response on a scale of 1-5 (1 = Poor, 5 = Excellent):")
    for agent in agents:
        ratings[agent] = int(input(f"Rate the {agent} Agent's response: "))

    # Save results to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = "agent_evaluation.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "User Query", "Agent Type", "Response", "Rating"])
        for agent, response in responses.items():
            writer.writerow([timestamp, user_query, agent, response, ratings[agent]])

    print(f"\nResults saved to {filename}.")


# Main function to run the comparative evaluation
if __name__ == "__main__":
    choice = input("\n1: Single Agent\n2: Comparative Evaluation\nChoose an option: ").strip()
    if choice == "1":
        agent_choice = input("\n1: Basic\n2: Chain of Thought\n3: ReAct\nChoose an agent type: ").strip()
        if agent_choice == "1":
            system_message = "You are a helpful weather assistant."
            tools = weather_tools
        elif agent_choice == "2":
            system_message = cot_system_message
            tools = cot_tools
        elif agent_choice == "3":
            system_message = react_system_message
            tools = react_tools
        else:
            print("Invalid choice. Defaulting to Basic agent.")
            system_message = "You are a helpful weather assistant."
            tools = weather_tools

        run_conversation(client, system_message)
    elif choice == "2":
        evaluate_agents(client)
    else:
        print("Invalid choice. Exiting.")