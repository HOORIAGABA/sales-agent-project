# Sales Agent with Google AI Studio

## Overview

This Python-based sales agent simulates interactions with multiple leads concurrently. It collects information through a step-by-step conversational flow and follows up with leads who do not respond within a specified timeframe. This implementation utilizes the Google AI Studio API (Gemini Pro model) for generating conversational responses and stores lead data in a CSV file.

## Setup Instructions

1.  **Prerequisites:**
    * Python 3.6 or higher.
    * pip (Python package installer).

2.  **Install Dependencies:**
    Open your terminal and run the following command to install the necessary library:
    ```bash
    pip install google-generativeai
    ```

3.  **Google AI Studio API Key:**
    * Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) and create an API key.
    * Replace the placeholder `"YOUR_API_KEY"` in the `AI_STUDIO_API_KEY` variable in the `sales_agent.py` file with your actual API key.


## Usage Guide

1.  **Running the Agent:**
    Save the provided Python code as `sales_agent.py`. Open your terminal, navigate to the directory where you saved the file, and run the script using:
    ```bash
    python sales_agent.py
    ```

2.  **Simulating Lead Interactions:**
    The `simulate_concurrent_conversations()` function within the script simulates multiple leads interacting with the agent. This function defines a list of leads with predefined names and a sequence of responses they will provide.

3.  **Observing the Output:**
    The script will print the agent's initial messages to each simulated lead and the subsequent agent responses based on the simulated lead responses. You will also see messages indicating when a follow-up message is sent to an unresponsive lead.

4.  **Checking the `leads.csv` File:**
    After the simulation runs, a file named `leads.csv` will be created (or updated) in the same directory. This file will contain the collected information for each lead, including their ID, name, age, country, interest, and status.

5.  **Follow-Up Mechanism:**
    The agent checks for unresponsive leads every 5 seconds (simulating a 24-hour delay using the `FOLLOW_UP_DELAY_SECONDS` variable). If a lead hasn't responded (their `last_interaction` timestamp is older than the delay and their status is not "secured" or "no_response"), a follow-up message will be printed to the console.

## Design Decisions

1.  **Lead Management (`Lead` class and `leads` dictionary):**
    * The `Lead` class is used to represent each individual lead and store their relevant information (ID, name, collected data, status, interaction history).
    * The `leads` dictionary acts as an in-memory store for all active leads, using the `lead_id` as the key for efficient access and management.

2.  **Data Persistence (`leads.csv`):**
    * A CSV file (`leads.csv`) is used to persist the lead data as required. The `load_leads()` function reads existing data from the CSV on startup, and the `save_leads()` function writes updated lead information to the CSV after each interaction or status change.

3.  **Concurrency (`threading`):**
    * The `threading` module is used to simulate concurrent conversations. Each simulated lead interaction is run in a separate thread, allowing for the demonstration of the agent handling multiple conversations independently.
    * A separate thread is also used for the `check_for_follow_ups()` function, ensuring that the follow-up mechanism runs in the background without blocking the main simulation.

4.  **Conversation Flow:**
    * The conversation follows a predefined sequential flow: initial greeting, consent, and then questions about age, country, and interest. The `status` attribute of the `Lead` object tracks the current stage of the conversation.

5.  **Simulation:**
    * The `simulate_concurrent_conversations()` function provides a controlled environment to test the agent's functionalities without requiring real external triggers or manual interactions. Predefined lead data and responses are used to automate the simulation.
    * The `FOLLOW_UP_DELAY_SECONDS` variable allows for easy adjustment of the simulated follow-up delay.

## Assumptions

* The simulated user responses are always valid and follow the expected format. In a real-world scenario, more robust error handling and natural language understanding would be necessary.
* The focus of this implementation is on demonstrating the core conversational flow, concurrency, and follow-up mechanisms. More advanced features like context retention across multiple turns or handling ambiguous responses are not included.
* The `conversation_history` is stored in memory for each `Lead` object but is not persisted to the `leads.csv`

## Test Cases

For detailed test cases and expected outcomes, please refer to the `test_cases.md` file.
