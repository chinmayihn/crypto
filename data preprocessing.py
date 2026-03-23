import json
from datetime import datetime

input_file = "History (1).json"
output_file = "titles_with_timestamp.txt"

def convert_time_usec_to_readable(time_usec):
    time_seconds = time_usec / 1000000
    dt_object = datetime.fromtimestamp(time_seconds)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")

# Load JSON
with open(input_file, "r") as file:
    data = json.load(file)

# Extract title + timestamp
entries = [
    (entry["title"], entry["time_usec"])
    for entry in data.get("Browser History", [])
    if entry["title"].strip() != ""
]

# ✅ Remove duplicates (important)
unique_entries = list(set(entries))

# Write to file
with open(output_file, "w") as file:
    for title, time_usec in unique_entries:
        readable_timestamp = convert_time_usec_to_readable(time_usec)
        file.write(f"{readable_timestamp}: {title}\n")

print(f"Extracted {len(unique_entries)} cleaned entries")
