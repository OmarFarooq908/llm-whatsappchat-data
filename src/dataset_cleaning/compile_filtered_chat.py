import os
import json

def compile_json_files(input_directory, output_file):
    compiled_data = []

    # Iterate over each file in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)

            # Load the JSON data from the file
            with open(file_path, 'r', encoding='utf-8') as infile:
                data = json.load(infile)
                compiled_data.extend(data)

    # Save the compiled data to the output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(compiled_data, outfile, indent=4)

    print(f"Compiled data saved to {output_file}")

if __name__ == "__main__":
    input_directory = '/media/omar/Horse/OmarFarooq/Projects/LLM/Project-1/Dataset/formatted_data'
    output_directory = '/media/omar/Horse/OmarFarooq/Projects/LLM/Project-1/Dataset/compiled_dataset'
    os.makedirs(output_directory, exist_ok=True)
    output_file = output_directory+'/compiled_dataset.json'

    compile_json_files(input_directory, output_file)
