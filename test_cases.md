# Test Cases for Sales Agent

This document outlines several test cases to demonstrate the behavior of the sales agent under different scenarios.

## Test Case 1: Successful Lead Acquisition

* **Scenario:** A lead (Alice) provides consent and answers all the questions (age: 30, country: USA, interest: AI Development Kit) within the follow-up time.
* **Steps (Simulated):**
    1.  Run the `sales_agent.py` script.
    2.  Observe the console output for the interaction with Alice. You should see the initial greeting, Alice's positive response to consent, the age question, Alice's age, the country question, Alice's country, the interest question, and Alice's interest.
    3.  Check the `leads.csv` file after the simulation completes.
* **Expected Outcome:** The `leads.csv` should contain a record for Alice with the following data:
    ```csv
    lead_id,name,age,country,interest,status
    1,Alice,30,USA,AI Development Kit,secured
    ```
    No follow-up message should be printed for Alice in the console.

## Test Case 2: Lead Declines Consent

* **Scenario:** A lead (Bob initially) responds negatively to the initial consent question ("No, not interested right now.").
* **Steps (Simulated):**
    1.  Run the `sales_agent.py` script.
    2.  Observe the console output for the interaction with Bob. You should see the initial greeting and Bob's negative response, followed by the agent's "Alright, no problem. Have a great day!" message.
    3.  Check the `leads.csv` file after the simulation.
* **Expected Outcome:** The `leads.csv` should contain a record for Bob with the `status` as "no_response":
    ```csv
    lead_id,name,age,country,interest,status
    2,Bob,,,,"no_response"
    ```
    No further questions should be asked to Bob initially.

## Test Case 3: Unresponsive Lead (Follow-up Triggered)

* **Scenario:** A lead (Charlie) provides consent ("Sure, go ahead.") but does not respond to the first question ("What is your age?") within the simulated follow-up delay (10 seconds).
* **Steps (Simulated):**
    1.  Run the `sales_agent.py` script.
    2.  Observe the console output for Charlie's consent and the age question.
    3.  Wait for approximately 10-15 seconds (to account for the follow-up check interval).
    4.  Observe the console output for a follow-up message initiated by the `check_for_follow_ups()` thread for Charlie: "(Follow-up for lead 3 - Charlie): Just checking in to see if you're still interested. Let me know when you're ready to continue."
    5.  Check the `leads.csv` file. The `last_interaction` timestamp for Charlie should be updated to reflect the follow-up. The `status` should still be "waiting_for_age".

## Test Case 4: Late Response After Declining

* **Scenario:** A lead (Bob) initially declines consent ("No, not interested right now.") resulting in a "no\_response" status. Later in the simulation, Bob sends another message ("Actually, maybe I do have a question.").
* **Steps (Simulated):**
    1.  Run the `sales_agent.py` script. Observe Bob's initial decline and the "no\_response" status.
    2.  Observe the subsequent simulated response from Bob ("Actually, maybe I do have a question.").
    3.  Check the console output for the agent's response to Bob's later message. The agent should ideally restart the conversation flow (ask for consent again or proceed based on the "question"). *Note: The current code restarts the flow by going back to the consent handling.*
    4.  Check the `leads.csv` file. Bob's `status` should have been reset to "initiated".
* **Expected Outcome:** The console should show the agent's initial greeting again after Bob's second message. Bob's record in `leads.csv` should have its `status` updated to "initiated".

## Test Case 5: Concurrent Interactions

* **Scenario:** Observe the overall output of the `simulate_concurrent_conversations()` function with all the defined leads (Alice, Bob, Charlie, David, Eve) interacting (or not) simultaneously.
* **Steps (Simulated):**
    1.  Run the `sales_agent.py` script.
    2.  Observe the interleaved messages in the console from the agent and the simulated users for each lead. Note how different leads are at different stages of the conversation at the same time.
    3.  Check the `leads.csv` file at the end of the simulation to see the final status and collected information for all leads.
* **Expected Outcome:** The console output should demonstrate that the agent handles each lead independently. The `leads.csv` should contain records for all five leads with their respective final statuses and collected data (if any).

## Test Case 6: Loading Existing Leads

* **Scenario:** Run the script once, which will create or update `leads.csv`. Then, run the script a second time.
* **Steps (Simulated):**
    1.  Run `python sales_agent.py`. This will create or modify `leads.csv`.
    2.  Run `python sales_agent.py` again without deleting `leads.csv`.
    3.  Observe the initial console output of the second run. The `load_leads()` function should print messages indicating that it's loading existing leads. The simulation will then proceed with these loaded leads.
    4.  Observe if the agent attempts to continue the conversation with the loaded leads based on their previous `status`.
* **Expected Outcome:** The console should show "[load\_leads] Loaded row: ..." messages for each lead from the `leads.csv` file. The simulation should proceed, potentially re-initiating conversations or continuing from the last known status of the loaded leads.

These test cases cover the core functionalities of the sales agent. You can expand on these with more edge cases if needed. Remember to describe these test cases in your `test_cases.md` file for your submission.