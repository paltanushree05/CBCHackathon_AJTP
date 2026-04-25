# engine/claude.py
import anthropic
import json
import os

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# PROMPT 1: parse raw coordinator text → structured JSON
def parse_input(raw_text):
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are a coordinator assistant for Friendship Donations 
                          Network in Ithaca, NY. Parse this coordinator note into JSON 
                          with fields: donors, quantities, locations, time_windows, 
                          volunteer_windows. Return only valid JSON, no explanation.
                          Input: {raw_text}"""
        }]
    )
    return json.loads(message.content[0].text)


# PROMPT 2: route assignments → plain English briefing
def generate_briefing(assignments, unroutable, partners, day):
    # pull partner names for context
    partner_names = [p["name"] for p in partners]

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are a coordinator assistant for Friendship Donations 
                          Network in Ithaca, NY. Today is {day}.
                          
                          FDN currently serves these community partners: 
                          {", ".join(partner_names)}.
                          
                          Generate a concise plain-English daily briefing per driver 
                          based on these route assignments: 
                          {json.dumps(assignments, default=str)}.
                          
                          Also flag these unroutable donations and suggest which FDN 
                          partner organizations might be able to absorb them:
                          {json.dumps(unroutable)}.
                          
                          Be actionable and specific to Ithaca."""
        }]
    )
    return message.content[0].text