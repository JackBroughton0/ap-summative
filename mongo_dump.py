import json
import mongodb_interaction

# Define the output file name
output_file = "MongoDB_dump.json"

collection = mongodb_interaction.connect_to_mongodb()

cursor = collection.find()

# Create an empty list to hold the documents
documents_list = []

# Iterate over the cursor and add each document to the list
for document in cursor:
    documents_list.append(document)

# Open the output file in write mode
with open(output_file, "w") as file:
    # Write the entire list as a JSON array to the file
    json.dump(documents_list, file, default=str)
