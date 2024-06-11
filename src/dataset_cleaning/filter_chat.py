import os
import json
from datetime import datetime, timedelta

# Function to filter out lines containing "<Media omitted>" and non-conversational messages
def filter_lines(input_file):
    filtered_lines = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
        for line in lines:
            if '<Media omitted>' not in line and 'Messages and calls are end-to-end encrypted' not in line:
                filtered_lines.append(line)
    return filtered_lines

# Function to split conversations based on a time threshold
def split_conversations(lines, time_threshold=30):
    conversations = []
    current_conversation = []
    last_timestamp = None
    found_participant = False

    for line in lines:
        try:
            timestamp_str, message = line.split(' - ', 1)
            timestamp = datetime.strptime(timestamp_str, '%m/%d/%y, %I:%M %p')
        except ValueError:
            # Skip lines that do not match the expected format
            continue

        if not found_participant and "Muhammad Omar Farooq" in message:
            found_participant = True

        if found_participant:
            if last_timestamp and (timestamp - last_timestamp > timedelta(minutes=time_threshold)):
                if current_conversation:
                    conversations.append(current_conversation)
                    current_conversation = []

            current_conversation.append((timestamp,message))
            last_timestamp = timestamp

    if current_conversation:
        conversations.append(current_conversation)

    return conversations

# Function to format conversations into JSON structure for LLM training
def format_for_llm_training(conversations, participant_name="Muhammad Omar Farooq"):
    formatted_data = []
    omar_started = False
    consecutive_participant = False
    first_run = True
    for conversation in conversations:
        input_prompt = ""
        output_response = ""
        collecting_response = False
        prev_sender = None
        
        for timestamp, message in conversation:
            if ": " not in message:
                continue

            sender, message_text = message.split(": ", 1)
            prev_sender = sender
            if sender != participant_name:
                first_run = False
            if (sender == participant_name) and first_run:
                omar_started = True
            if omar_started and first_run:
                continue
            """
            if prev_sender is not None and prev_sender != sender:
                if collecting_response:
                    formatted_data.append({
                        "input_prompt": input_prompt.strip(),
                        "output_response": output_response.strip()
                    })
                    input_prompt = ""
                    output_response = ""
                collecting_response = False
            """
            if participant_name in sender:
                output_response += message_text.strip() + " "
                collecting_response = True
            else:
                input_prompt += message_text.strip() + " "
                collecting_response = True
                first_run = False

            if prev_sender == sender and sender == participant_name:
                output_response += output_response
            if prev_sender == sender and sender != participant_name:
                input_prompt += input_prompt
            if input_prompt != "" and output_response != "":
                formatted_data.append({
                    "input_prompt": input_prompt.strip(),
                    "output_response": output_response.strip()
                    })

    return formatted_data

# Define directories
raw_data_dir = '../../Dataset/raw_data'
filtered_data_dir = '../../Dataset/filtered_data'
formatted_data_dir = '../../Dataset/formatted_data'

# Ensure the filtered_data and formatted_data directories exist
os.makedirs(filtered_data_dir, exist_ok=True)
os.makedirs(formatted_data_dir, exist_ok=True)

# Process each file in the raw_data directory
for filename in os.listdir(raw_data_dir):
    if filename.endswith('.txt'):
        input_file = os.path.join(raw_data_dir, filename)
        
        # Filter out media omitted lines and non-conversational messages
        filtered_lines = filter_lines(input_file)
        
        # Split the lines into conversations
        conversations = split_conversations(filtered_lines)
        # Save each conversation into a separate file
        '''
        for i, conversation in enumerate(conversations):
            output_file = os.path.join(filtered_data_dir, f"{os.path.splitext(filename)[0]}_conv{i+1}.txt")
            with open(output_file, 'w', encoding='utf-8') as outfile:
                messages = [message for timestamp, message in conversation]
                for msg in messages:
                    outfile.writelines(msg)
        
        print(f"Filtered conversations saved for {filename}")
        '''
        # Format the conversations for LLM fine-tuning
        formatted_conversations = format_for_llm_training(conversations)
        
        # Save the formatted conversations
        formatted_output_file = os.path.join(formatted_data_dir, f"{os.path.splitext(filename)[0]}_formatted.json")
        with open(formatted_output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(formatted_conversations, jsonfile, indent=4)
        
        print(f"Filtered and formatted conversations saved for {filename}")

