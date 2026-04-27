import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

ZENDESK_SUBDOMAIN = os.getenv("ZENDESK_SUBDOMAIN")
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_TOKEN = os.getenv("ZENDESK_API_TOKEN")  

print(f"Loaded ENV → subdomain: {ZENDESK_SUBDOMAIN}, email: {ZENDESK_EMAIL}, token: {'✅' if ZENDESK_TOKEN else '❌'}")

BASE_URL = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2"

def test_connection():
    """Check if credentials are valid by listing recent tickets."""
    url = f"{BASE_URL}/tickets.json?page[size]=5"
    print(f"🔗 Testing Zendesk connection: {url}")

    try:
        response = requests.get(
            url,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_TOKEN),
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            tickets = data.get("tickets", [])
            print(f"✅ Connection successful! Found {len(tickets)} tickets.\n")
            for t in tickets:
                print(f"🎟️  Ticket #{t['id']}: {t['subject']} (Status: {t['status']})")
            return True
        elif response.status_code == 401:
            print("❌ Unauthorized. Check your email/token or token access settings.")
        elif response.status_code == 403:
            print("🚫 Forbidden. Your account may not have the correct permissions.")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(response.text)
        return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def post_test_comment(ticket_id: int):
    """Optionally add a test internal note to a ticket."""
    url = f"{BASE_URL}/tickets/{ticket_id}.json"
    payload = {
        "ticket": {
            "comment": {
                "body": "✅ This is a test internal note from API.",
                "public": False
            }
        }
    }
    try:
        response = requests.put(
            url,
            json=payload,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_TOKEN),
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if response.status_code == 200:
            print(f"📝 Successfully added test comment to Ticket #{ticket_id}")
        else:
            print(f"⚠️ Failed to post comment: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Error posting test comment: {e}")

if __name__ == "__main__":
    print("🚀 Starting Zendesk API Test...\n")
    if not (ZENDESK_SUBDOMAIN and ZENDESK_EMAIL and ZENDESK_TOKEN):
        print("❌ Missing environment variables. Please check your .env file.")
        exit(1)

    ok = test_connection()
    if ok:
        # Optional: comment on the first ticket
        choice = input("\nWould you like to add a test comment to the first ticket? (y/n): ").strip().lower()
        if choice == "y":
            ticket_id = int(input("Enter ticket ID (or press Enter to use the first one): ") or "0")
            if ticket_id == 0:
                # Automatically grab first ticket if available
                response = requests.get(
                    f"{BASE_URL}/tickets.json?page[size]=1",
                    auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_TOKEN)
                )
                first_ticket = response.json()["tickets"][0]["id"]
                ticket_id = first_ticket
            post_test_comment(ticket_id)
    else:
        print("❌ Could not verify Zendesk API connection.")
