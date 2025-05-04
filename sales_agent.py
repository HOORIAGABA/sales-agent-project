import csv
import random
import time
from datetime import datetime, timedelta
import threading
import os
from google.generativeai import GenerativeModel, configure

# --- Configuration ---
LEADS_CSV_FILE = 'leads.csv'
FOLLOW_UP_DELAY_SECONDS = 10  # Simulate 24-hour delay for testing
AI_STUDIO_API_KEY = "AIzaSyB4jmT2-GJkA9HSkGtXZXBQXSPz7IC0k1g"  # Replace with your actual API key
MODEL_NAME = "gemini-pro"

# --- Initialize Google AI Studio ---
configure(api_key=AI_STUDIO_API_KEY)
model = GenerativeModel(MODEL_NAME)

# --- Lead Data Structure ---
class Lead:
    def __init__(self, lead_id, name):
        self.lead_id = lead_id
        self.name = name
        self.age = None
        self.country = None
        self.interest = None
        self.status = "initiated"
        self.last_interaction = datetime.now()
        self.conversation_history = []

    def to_dict(self):
        return {
            'lead_id': self.lead_id,
            'name': self.name,
            'age': self.age,
            'country': self.country,
            'interest': self.interest,
            'status': self.status
        }

# --- Lead Management ---
leads = {}

def load_leads():
    if os.path.exists(LEADS_CSV_FILE):
        try:
            with open(LEADS_CSV_FILE, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                if reader.fieldnames is None or 'lead_id' not in reader.fieldnames:
                    print("Warning: 'leads.csv' might be missing the header or the 'lead_id' column. Starting with an empty lead list.")
                    leads.clear()
                    return
                for row in reader:
                    lead = Lead(row['lead_id'], row['name'])
                    lead.age = row['age']
                    lead.country = row['country']
                    lead.interest = row['interest']
                    lead.status = row['status']
                    leads[lead.lead_id] = lead
        except Exception as e:
            print(f"Error loading leads from CSV: {e}. Starting with an empty lead list.")
            leads.clear()
    else:
        print("Leads CSV file not found. Will be created on the first save.")

def save_leads():
    fieldnames = ['lead_id', 'name', 'age', 'country', 'interest', 'status']
    with open(LEADS_CSV_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads.values():
            lead_data = lead.to_dict()
            writer.writerow(lead_data)

def create_new_lead(lead_id, name):
    if lead_id not in leads:
        lead = Lead(lead_id, name)
        leads[lead_id] = lead
        save_leads()
        return lead
    return leads[lead_id]

def get_lead(lead_id):
    return leads.get(lead_id)

def update_lead_info(lead_id, key, value):
    lead = get_lead(lead_id)
    if lead:
        setattr(lead, key, value)
        lead.last_interaction = datetime.now()
        save_leads()

def get_lead_status(lead_id):
    lead = get_lead(lead_id)
    return lead.status if lead else None

def set_lead_status(lead_id, status):
    lead = get_lead(lead_id)
    if lead:
        lead.status = status
        lead.last_interaction = datetime.now()
        save_leads()

def record_interaction(lead_id, message, is_user=True):
    lead = get_lead(lead_id)
    if lead:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        role = "user" if is_user else "agent"
        lead.conversation_history.append(f"[{timestamp}] {role}: {message}")

def get_conversation_history(lead_id):
    lead = get_lead(lead_id)
    return lead.conversation_history if lead else []

def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I encountered an issue."

# --- Agent Conversation Logic ---
def initiate_conversation(lead):
    initial_message = f"Hey {lead.name}, thank you for filling out the form. I'd like to gather some information from you. Is that okay?"
    record_interaction(lead.lead_id, initial_message, is_user=False)
    return initial_message

def handle_consent(lead, response):
    record_interaction(lead.lead_id, response)
    if "yes" in response.lower() or "okay" in response.lower() or "sure" in response.lower():
        lead.status = "waiting_for_age"
        lead.last_interaction = datetime.now()
        save_leads()
        return ask_question(lead, "age")
    else:
        set_lead_status(lead.lead_id, "no_response")
        response_message = "Alright, no problem. Have a great day!"
        record_interaction(lead.lead_id, response_message, is_user=False)
        return response_message

def handle_response(lead, response):
    record_interaction(lead.lead_id, response)
    if lead.status == "waiting_for_age":
        update_lead_info(lead.lead_id, "age", response)
        lead.status = "waiting_for_country"
        save_leads()
        return ask_question(lead, "country")
    elif lead.status == "waiting_for_country":
        update_lead_info(lead.lead_id, "country", response)
        lead.status = "waiting_for_interest"
        save_leads()
        return ask_question(lead, "interest")
    elif lead.status == "waiting_for_interest":
        update_lead_info(lead.lead_id, "interest", response)
        lead.status = "secured"
        save_leads()
        final_message = "Thank you for your responses! We’ve noted your interest and will get back to you soon."
        record_interaction(lead.lead_id, final_message, is_user=False)
        return final_message
    else:
        return "Thank you! If you have any more questions, feel free to ask."

def ask_question(lead, field):
    if field == "age":
        return "What is your age?"
    elif field == "country":
        return "Which country are you from?"
    elif field == "interest":
        return "What product or service are you interested in?"
    return None

def follow_up(lead):
    follow_up_message = "Just checking in to see if you're still interested. Let me know when you're ready to continue."
    record_interaction(lead.lead_id, follow_up_message, is_user=False)
    return follow_up_message

def check_for_follow_ups():
    while True:
        time.sleep(5)  # Check every 5 seconds in the simulation
        for lead_id, lead in list(leads.items()):
            if lead.status != "secured" and lead.status != "no_response" and (datetime.now() - lead.last_interaction).total_seconds() > FOLLOW_UP_DELAY_SECONDS:
                print(f"(Follow-up for lead {lead.lead_id} - {lead.name}): {follow_up(lead)}")
                leads[lead_id].last_interaction = datetime.now()
                save_leads()

def handle_lead_interaction(lead_id, name, responses):
    """Handles the entire interaction flow for a single lead."""
    lead = simulate_lead_submission(lead_id, name)
    if lead:
        for response in responses:
            time.sleep(random.uniform(1, 3)) # Simulate some delay between responses
            simulate_lead_response(lead_id, response)

def simulate_lead_submission(lead_id, name):
    lead = get_lead(lead_id)
    if not lead:
        lead = create_new_lead(lead_id, name)
        initial_message = initiate_conversation(lead)
        print(f"(Agent for lead {lead_id} - {lead.name}): {initial_message}")
        return lead
    else:
        initial_message = initiate_conversation(lead)
        print(f"(Agent for existing lead {lead_id} - {lead.name}): {initial_message}")
        return lead

def simulate_lead_response(lead_id, response):
    if lead_id in leads:
        lead = leads[lead_id]
        if lead.status == "no_response":
            lead.status = "initiated"
            lead.last_interaction = datetime.now()
            save_leads()
        if lead.status == "initiated":
            agent_response = handle_consent(lead, response)
            print(f"(Agent for lead {lead_id}): {agent_response}")
        elif lead.status.startswith("waiting_for_"):
            agent_response = handle_response(lead, response)
            print(f"(Agent for lead {lead_id}): {agent_response}")
        elif lead.status != "secured" and lead.status != "no_response":
            agent_response = handle_response(lead, response)
            print(f"(Agent for lead {lead_id}): {agent_response}")
        save_leads()

def simulate_concurrent_conversations():
    load_leads() # Load any existing leads

    # Define multiple leads and their simulated responses
    lead_data = [
        {"id": "1", "name": "Alice", "responses": ["Yes, that's fine.", "30", "USA", "AI Development Kit"]},
        {"id": "2", "name": "Bob", "responses": ["No, not interested right now.", "Actually, maybe I do have a question."]},
        {"id": "3", "name": "Charlie", "responses": ["Sure, go ahead.", "25", "Canada", "Cloud Computing Services"]},
        {"id": "4", "name": "David", "responses": ["Okay.", "45", "UK", "Data Analytics Platform"]},
        {"id": "5", "name": "Eve", "responses": ["Not right now."]},
    ]

    threads = []
    for data in lead_data:
        thread = threading.Thread(target=handle_lead_interaction, args=(data["id"], data["name"], data["responses"]))
        threads.append(thread)
        thread.start()
        time.sleep(random.uniform(0.5, 1.5)) # Simulate staggered lead submissions

    # Wait for all conversation threads to complete
    for thread in threads:
        thread.join()

    # Keep the follow-up thread running for a bit longer to observe
    time.sleep(FOLLOW_UP_DELAY_SECONDS * 2)

    print("\n--- Final Lead Data ---")
    for lead_id in sorted(leads.keys(), key=lambda x: int(x)):
        lead = leads[lead_id]
        print(f"Lead ID: {lead.lead_id}, Name: {lead.name}, Age: {lead.age}, Country: {lead.country}, Interest: {lead.interest}, Status: {lead.status}")
        print("Conversation History:")
        for message in lead.conversation_history:
            print(f"- {message}")
        print("-" * 20)

if __name__ == "__main__":
    follow_up_thread = threading.Thread(target=check_for_follow_ups, daemon=True)
    follow_up_thread.start()
    simulate_concurrent_conversations()













# # --- Lead Data Structure ---
# class Lead:
#     def __init__(self, lead_id, name):
#         self.lead_id = lead_id
#         self.name = name
#         self.age = None
#         self.country = None
#         self.interest = None
#         self.status = "initiated"
#         self.last_interaction = datetime.now()
#         self.conversation_history = []

#     def to_dict(self):
#         return {
#             'lead_id': self.lead_id,
#             'name': self.name,
#             'age': self.age,
#             'country': self.country,
#             'interest': self.interest,
#             'status': self.status
#         }

# # --- Lead Management ---
# leads = {}

# def load_leads():
#     if os.path.exists(LEADS_CSV_FILE):
#         try:
#             with open(LEADS_CSV_FILE, 'r', newline='') as csvfile:
#                 reader = csv.DictReader(csvfile)
#                 if reader.fieldnames is None or 'lead_id' not in reader.fieldnames:
#                     print("Warning: 'leads.csv' might be missing the header or the 'lead_id' column. Starting with an empty lead list.")
#                     leads.clear()
#                     return
#                 for row in reader:
#                     print(f"[load_leads] Loaded row: {row}")
#                     lead = Lead(row['lead_id'], row['name'])
#                     lead.age = row['age']
#                     lead.country = row['country']
#                     lead.interest = row['interest']
#                     lead.status = row['status']
#                     leads[lead.lead_id] = lead
#                     print(f"[load_leads] Leads dictionary after load: {leads}")
#         except Exception as e:
#             print(f"Error loading leads from CSV: {e}. Starting with an empty lead list.")
#             leads.clear()
#     else:
#         print("Leads CSV file not found. Will be created on the first save.")

# def save_leads():
#     fieldnames = ['lead_id', 'name', 'age', 'country', 'interest', 'status']
#     with open(LEADS_CSV_FILE, 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for lead in leads.values():
#             lead_data = lead.to_dict()
#             print(f"[save_leads] Saving: {lead_data}")
#             writer.writerow(lead_data)


# def create_new_lead(lead_id, name):
#     if lead_id not in leads:
#         lead = Lead(lead_id, name)
#         leads[lead_id] = lead
#         save_leads()
#         print(f"  [create_new_lead] Lead {lead_id} created with status (after save): {lead.status}")
#         return lead
#     return leads[lead_id]

# def get_lead(lead_id):
#     return leads.get(lead_id)

# def update_lead_info(lead_id, key, value):
#     lead = get_lead(lead_id)
#     if lead:
#         setattr(lead, key, value)
#         lead.last_interaction = datetime.now()
#         save_leads()

# def get_lead_status(lead_id):
#     lead = get_lead(lead_id)
#     return lead.status if lead else None

# def set_lead_status(lead_id, status):
#     lead = get_lead(lead_id)
#     if lead:
#         lead.status = status
#         lead.last_interaction = datetime.now()
#         save_leads()

# def record_interaction(lead_id, message, is_user=True):
#     lead = get_lead(lead_id)
#     if lead:
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         role = "user" if is_user else "agent"
#         lead.conversation_history.append(f"[{timestamp}] {role}: {message}")
#         # Note: conversation_history is not persisted in this basic CSV storage.

# def get_conversation_history(lead_id):
#     lead = get_lead(lead_id)
#     return lead.conversation_history if lead else []

# def generate_response(prompt):
#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         print(f"Error generating response: {e}")
#         return "Sorry, I encountered an issue."

# # --- Agent Conversation Logic ---
# def initiate_conversation(lead):
#     initial_message = f"Hey {lead.name}, thank you for filling out the form. I'd like to gather some information from you. Is that okay?"
#     record_interaction(lead.lead_id, initial_message, is_user=False)
#     return initial_message

# def handle_consent(lead, response):
#     record_interaction(lead.lead_id, response)
#     print(f"  [handle_consent] Lead {lead.lead_id} response: {response}")
#     if "yes" in response.lower() or "okay" in response.lower() or "sure" in response.lower():
#         print(f"  [handle_consent] Lead {lead.lead_id} - Consent given")
#         lead.status = "waiting_for_age"
#         lead.last_interaction = datetime.now()
#         save_leads()  # ✅ Save status change
#         print(f"  [handle_consent] Lead {lead.lead_id} status set to: {lead.status}")
#         next_question = ask_question(lead, "age")
#         print(f"  [handle_consent] Lead {lead.lead_id} asking: {next_question}")
#         return next_question
#     else:
#         print(f"  [handle_consent] Lead {lead.lead_id} - Consent denied")
#         set_lead_status(lead.lead_id, "no_response")
#         response_message = "Alright, no problem. Have a great day!"
#         record_interaction(lead.lead_id, response_message, is_user=False)
#         print(f"  [handle_consent] Lead {lead.lead_id} no consent: {response_message}")
#         return response_message

# def handle_response(lead, response):
#     record_interaction(lead.lead_id, response)
#     print(f"  [handle_response] Lead {lead.lead_id} response: {response}")

#     if lead.status == "waiting_for_age":
#         print(f"  [handle_response] Lead {lead.lead_id} - Processing age")
#         update_lead_info(lead.lead_id, "age", response)
#         lead.status = "waiting_for_country"
#         save_leads()
#         return ask_question(lead, "country")

#     elif lead.status == "waiting_for_country":
#         print(f"  [handle_response] Lead {lead.lead_id} - Processing country")
#         update_lead_info(lead.lead_id, "country", response)
#         lead.status = "waiting_for_interest"
#         save_leads()
#         return ask_question(lead, "interest")

#     elif lead.status == "waiting_for_interest":
#         print(f"  [handle_response] Lead {lead.lead_id} - Processing interest")
#         update_lead_info(lead.lead_id, "interest", response)
#         lead.status = "secured"
#         save_leads()
#         final_message = "Thank you for your responses! We’ve noted your interest and will get back to you soon."
#         record_interaction(lead.lead_id, final_message, is_user=False)
#         return final_message

#     else:
#         return "Thank you! If you have any more questions, feel free to ask."


# def ask_question(lead, field):
#     if field == "age":
#         return "What is your age?"
#     elif field == "country":
#         return "Which country are you from?"
#     elif field == "interest":
#         return "What product or service are you interested in?"
#     return None

# def follow_up(lead):
#     follow_up_message = "Just checking in to see if you're still interested. Let me know when you're ready to continue."
#     record_interaction(lead.lead_id, follow_up_message, is_user=False)
#     return follow_up_message

# def check_for_follow_ups():
#     while True:
#         time.sleep(5)  # Check every 5 seconds in the simulation
#         for lead_id, lead in list(leads.items()): # Iterate over a copy to allow modifications
#             if lead.status != "secured" and lead.status != "no_response" and (datetime.now() - lead.last_interaction).total_seconds() > FOLLOW_UP_DELAY_SECONDS:
#                 print(f"(Follow-up for lead {lead.lead_id} - {lead.name}): {follow_up(lead)}")
#                 leads[lead_id].last_interaction = datetime.now() # Update last interaction time
#                 save_leads()

# def simulate_lead_submission(lead_id, name):
#     print(f"New lead submitted: ID - {lead_id}, Name - {name}")
#     lead = get_lead(lead_id)  # Check if the lead already exists
#     if not lead:
#         lead = create_new_lead(lead_id, name)
#         print(f"  [simulate_lead_submission] Created new lead {lead_id}. Leads dictionary: {leads}")
#     else:
#         print(f"  [simulate_lead_submission] Found existing lead {lead_id}. Leads dictionary: {leads}")

#     initial_message = initiate_conversation(lead)
#     print(f"(Agent for lead {lead_id} - {lead.name}): {initial_message}")
#     return lead

# def simulate_lead_response(lead_id, response):
#     print(f"(User for lead {lead_id}): {response}")
#     if lead_id in leads:
#         lead = leads[lead_id]
#         print(f"  [simulate_lead_response] Lead {lead_id} status: {lead.status}")

#         # Reset no_response if lead talks again
#         if lead.status == "no_response":
#             print(f"  [simulate_lead_response] Resetting no_response status for Lead {lead_id}")
#             lead.status = "initiated"
#             lead.last_interaction = datetime.now()
#             save_leads()

#         if lead.status == "initiated":
#             print(f"  [simulate_lead_response] Lead {lead_id} in 'initiated' block")
#             agent_response = handle_consent(lead, response)
#             print(f"(Agent for lead {lead_id}): {agent_response}")
#         elif lead.status.startswith("waiting_for_"):
#             print(f"  [simulate_lead_response] Lead {lead_id} in 'waiting_for_' block")
#             agent_response = handle_response(lead, response)
#             print(f"(Agent for lead {lead_id}): {agent_response}")
#         elif lead.status != "secured" and lead.status != "no_response":
#             # Handle responses when not in a waiting state (could be a follow-up response)
#             print(f"  [simulate_lead_response] Lead {lead_id} in generic response block, status: {lead.status}")
#             agent_response = handle_response(lead, response)
#             print(f"(Agent for lead {lead_id}): {agent_response}")

#         save_leads()
#     else:
#         print(f"Lead ID {lead_id} not found.")



# def handle_lead_interaction(lead_id, name, responses):
#     """Handles the entire interaction flow for a single lead."""
#     lead = simulate_lead_submission(lead_id, name)
#     if lead:
#         for response in responses:
#             time.sleep(random.uniform(1, 3)) # Simulate some delay between responses
#             simulate_lead_response(lead_id, response)

# def simulate_concurrent_conversations():
#     load_leads() # Load any existing leads

#     # Define multiple leads and their simulated responses
#     lead_data = [
#         {"id": "1", "name": "Alice", "responses": ["Yes, that's fine.", "30", "USA", "AI Development Kit"]},
#         {"id": "2", "name": "Bob", "responses": ["No, not interested right now.", "Actually, maybe I do have a question."]},
#         {"id": "3", "name": "Charlie", "responses": ["Sure, go ahead.", "25", "Canada", "Cloud Computing Services"]},
#         {"id": "4", "name": "David", "responses": ["Okay.", "45", "UK", "Data Analytics Platform"]},
#         {"id": "5", "name": "Eve", "responses": ["Not right now."]},
#     ]

#     threads = []
#     for data in lead_data:
#         thread = threading.Thread(target=handle_lead_interaction, args=(data["id"], data["name"], data["responses"]))
#         threads.append(thread)
#         thread.start()
#         time.sleep(random.uniform(0.5, 1.5)) # Simulate staggered lead submissions

#     # Wait for all conversation threads to complete
#     for thread in threads:
#         thread.join()

#     # Keep the follow-up thread running for a bit longer to observe
#     time.sleep(FOLLOW_UP_DELAY_SECONDS * 2)

#     print("\n--- Final Lead Data ---")
#     for lead_id in sorted(leads.keys(), key=lambda x: int(x)):
#         lead = leads[lead_id]
#         print(f"Lead ID: {lead.lead_id}, Name: {lead.name}, Age: {lead.age}, Country: {lead.country}, Interest: {lead.interest}, Status: {lead.status}")
#         print("Conversation History:")
#         for message in lead.conversation_history:
#             print(f"- {message}")
#         print("-" * 20)

# if __name__ == "__main__":
#     follow_up_thread = threading.Thread(target=check_for_follow_ups, daemon=True)
#     follow_up_thread.start()
#     simulate_concurrent_conversations()

