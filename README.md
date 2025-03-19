###############################################################
## CSAI 422: Laboratory Assignment 4 - Conversational Agents ##
###############################################################

## Overview

This repository includes the implementation of a conversational agent that can apply reasoning techniques such as the Chain of Thought (CoT) and ReAct paradigms, as well as use external tools The agent can answer weather-related queries, perform calculations, and search for information.

## Learning Objectives

• Implement tool definitions and function calling with the OpenAI API.
• Build a conversational agent capable of using external tools.
• Apply Chain of Thought and ReAct reasoning paradigms to improve agent performance.
• Integrate external APIs into your conversational agent.

## Prerequisites

 • Basic understanding of APIs and async programming
 • Access to API key

## Features

- Current Weather: Get the current weather for any location.

- Weather Forecast: Get a weather forecast for a specified number of days.

- Calculator: Evaluate mathematical expressions.

- Web Search: Simulate a web search for weather-related information.

- Comparative Evaluation: Compare the performance of different agent types (Basic, Chain of Thought, and ReAct) based on user ratings.

## Installation

1. Clone the repository:
      git clone <repository_url>
      cd <repository_folder>
2. Install the required Python packages:
      pip install -r requirements.txt
3. Create a .env file in the root directory and add your API keys:
      OPENAI_API_KEY=your_openai_api_key
      WEATHER_API_KEY=your_weatherapi_key
4. Run the conversational agent:
      python conversational_agent.py


## Example Queries

+ Current Weather: "What's the weather in New York?"
+ Weather Forecast: "What's the weather forecast for Paris for the next 5 days?"
+ Calculator: "What is 2 + 2?"
+ Web Search: "What is climate change?"

## Documentation

1. Agent Types
   The project implements three types of conversational agents:
      1. Basic Agent: Uses weather tools to answer queries.
      2. Chain of Thought (CoT) Agent: Breaks down complex queries into smaller steps and uses a calculator tool for mathematical operations.
      3. ReAct Agent: Uses the ReAct (Reasoning and Acting) paradigm to solve problems by iteratively thinking, acting, and observing.

2. Tools
   The following tools are implemented:
      • Weather Tools:
         get_current_weather: Retrieves the current weather for a given location.
         get_weather_forecast: Retrieves a weather forecast for a given location and number of days.
      • Calculator Tool: Evaluates mathematical expressions.
      • Search Tool: Simulates a web search for information.
      
3. Comparative Evaluation
   A comparative evaluation system is implemented to:
      • Run a single query through each of the three kinds of agents.
      • Show the answers next to each other.
      • Permit the user to assign a number between 1 and 5 to each response.
      • For analysis, save the outcomes to a CSV file.


## Analysis of Reasoning Strategies

1. Basic Agent
   • Strengths: Simple and straightforward. Works well for direct queries like current weather or forecasts.
   • Weaknesses: Has trouble answering complicated questions that call for calculations or multi-step reasoning.

2. Chain of Thought Agent
   • Strengths: Breaks down complex queries into smaller steps, making it easier to handle calculations and comparisons.
   • Weaknesses: The reasoning process is not always explicit, and the agent may not always choose the most efficient steps.

3. ReAct Agent
   • Strengths: Explicitly shows the reasoning process (Thought, Action, Observation), making it highly transparent and effective for complex queries.
   • Weaknesses: The response can be verbose, and the agent may take unnecessary steps for simple queries.


## Challenges and Solutions

1. Handling API Errors
   • Challenge: The WeatherAPI sometimes returns errors for invalid locations or API key issues.
   • Solution: Added error handling in the get_current_weather and get_weather_forecast functions to return user-friendly error messages.

2. Managing Tool Calls
   • Challenge: The OpenAI API requires precise JSON schema definitions for tool calls.
   • Solution: Defined the tool schemas and ensured the process_messages function correctly handles tool invocations.

3. Comparative Evaluation
   • Challenge: Displaying responses from all three agents side by side and collecting user ratings.
   • Solution: Implemented the compare_agents function to streamline the process and save results to a CSV file.


## References
- Chapter 8: Conversational Agency from the textbook
- OpenAIAPIDocumentation: https://platform.openai.com/docs/guides/functioncalling
- WeatherAPI Documentation: https://www.weatherapi.com/docs/