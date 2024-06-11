import os
import pandas as pd
from datetime import datetime, timedelta

# Function to filter out lines containing "<Media omitted>"
def filter_media_omitted(input_file):
    filtered_lines = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
        for line in lines:
            if '<Media omitted>' not in line:
                filtered_lines.append(line)
    return filtered_lines

# Function to split conversations based on a time threshold
def split_conversations(lines, time_threshold=30):
    conversations = []
    current_conversation = []
    last_timestamp = None

    for line in lines:
        try:
            timestamp_str, message = line.split(' - ', 1)
            timestamp = datetime.strptime(timestamp_str, '%m/%d/%y, %I:%M %p')
        except ValueError:
            # Skip lines that do not match the expected format
            continue

        if last_timestamp and (timestamp - last_timestamp > timedelta(minutes=time_threshold)):
            if current_conversation:
                conversations.append(current_conversation)
                current_conversation = []

        current_conversation.append(line)
        last_timestamp = timestamp

    if current_conversation:
        conversations.append(current_conversation)

    return conversations

# Define directories
raw_data_dir = '../../Dataset/raw_data'
filtered_data_dir = '../../Dataset/filtered_data'

# Ensure the filtered_data directory exists
os.makedirs(filtered_data_dir, exist_ok=True)

# Process each file in the raw_data directory
for filename in os.listdir(raw_data_dir):
    if filename.endswith('.txt'):
        input_file = os.path.join(raw_data_dir, filename)
        
        # Filter out media omitted lines
        filtered_lines = filter_media_omitted(input_file)
        
        # Split the lines into conversations
        conversations = split_conversations(filtered_lines)
        
        # Save each conversation into a separate file
        for i, conversation in enumerate(conversations):
            output_file = os.path.join(filtered_data_dir, f"{os.path.splitext(filename)[0]}_conv{i+1}.txt")
            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.writelines(conversation)
        
        print(f"Filtered conversations saved for {filename}")
