# Read cleaned data
with open("titles_with_timestamp.txt", "r") as file:
    lines = file.readlines()

# 🔥 Define broader suspicious keywords (expanded list)
keywords = [
    "hack", "hacker", "attack", "exploit", "malware", "virus",
    "crypto", "bitcoin", "torrent", "piracy", "crack",
    "dark web", "leak", "breach", "password", "phishing",
    "anonymous", "ddos", "spoof"
]

# 🔹 Extract suspicious entries
suspicious = [line for line in lines if any(k in line.lower() for k in keywords)]

# 🔹 Fallback if no suspicious entries found
if len(suspicious) == 0:
    print("⚠️ No suspicious activity found. Using general browsing data instead.\n")
    selected = lines[:1000]
else:
    print(f"✅ Suspicious entries found: {len(suspicious)}\n")
    selected = suspicious[:1000]  # limit if too many

# 🔹 Format for LLM
formatted_data = "User Browser Activity Analysis:\n\n"

for line in selected:
    formatted_data += f"- {line.strip()}\n"

# Preview
print(formatted_data[:1000])
