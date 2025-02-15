import json
from telegram_interface import send_message
from time import sleep
import requests

def extract_bookable_spots(data):
    """
    Extracts information about bookable parking spots from the ParkWhiz API response.

    Args:
        data: The JSON response from the ParkWhiz API (as a Python dictionary).

    Returns:
        A list of dictionaries, where each dictionary represents a bookable
        parking location and its details.
    """

    bookable_locations = []

    for location_data in data.get("data", []):
        location = location_data["_embedded"]["pw:location"]
        location_name = location["name"]
        location_address = location["address1"]
        location_city = location["city"]
        location_state = location["state"]
        location_postal_code = location["postal_code"]
        distance_feet = location_data["distance"]["straight_line"]["feet"]

        purchase_options = location_data["purchase_options"]

        if purchase_options:
            purchase_option = purchase_options[0]
            if purchase_option["space_availability"]["status"] == "limited" or purchase_option["space_availability"]["status"] == "available":
                bookable_locations.append({
                    "name": location_name,
                    "address": location_address,
                    "city": location_city,
                    "state": location_state,
                    "postal_code": location_postal_code,
                    "distance_feet": distance_feet,
                    "price": purchase_option["price"]["USD"],
                    "purchase_url": purchase_option["_links"]["site:purchase"]["href"],
                    "spaces_remaining": purchase_option["space_availability"].get("spaces_remaining") # Add spaces_remaining
                })

    return bookable_locations



def search_parkwhiz():
    """
    Fetches parking data from ParkWhiz API and sends a Telegram message
    if bookable spots are found.
    """
    url = "https://api.parkwhiz.com/v4/quotes/?start_time=2025-03-01T08%3A00%3A00&end_time=2025-03-01T17%3A00%3A00&fields=quote%3A%3Adefault%2Cquote%3Ashuttle_times%2Clocation%3A%3Adefault%2Clocation%3Atimezone%2Clocation%3Asite_url%2Clocation%3Aaddress2%2Clocation%3Adescription%2Clocation%3Amsa%2Clocation%3Arating_summary&option_types=all&returns=curated%20offstreet_bookable_sold_out%20offstreet_bookable&q=anchor_coordinates%3A40.58012834865102%2C-111.65928840637208%20search_type%3Atransient%20bounds%3A40.587851449860125%2C-111.66773086099646%2C40.587851449860125%2C-111.65331382646357%2C40.57504989566016%2C-111.65331382646357%2C40.57504989566016%2C-111.66773086099646%20event_id%3A1531201&routing_style=parkwhiz&capabilities=capture_plate%3Aalways"
    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "Bearer cdbd6875c8ba14b73c1ff984e776528b28ef24ca1501a5fb07b5a503432ba6d5",
        "sec-ch-ua": "\"Chromium\";v=\"133\", \"Not(A:Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "x-language-locale": "en-us"
    }
    referrer = "https://www.parkwhiz.com/"

    try:
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        json_data = response.json()  # Parse the JSON response
        # Write the json to a file¸
        with open('parkwhiz_data.json', 'w') as file:
            json.dump(json_data, file, indent=4)
        bookable_spots = extract_bookable_spots(json_data)

        if bookable_spots:
            message = "**ParkWhiz Availability**\n\n"
            for spot in bookable_spots:
                message += f"**{spot['name']}**\n"
                message += f"Address: {spot['address']}, {spot['city']}, {spot['state']} {spot['postal_code']}\n"
                message += f"Distance: {spot['distance_feet']} feet\n"
                message += f"Price: ${spot['price']}\n"
                message += f"Purchase URL: {spot['purchase_url']}\n\n"
            send_message(message)
            print("Parking available, message sent!")
        else:
            print("No bookable parking spots found.")
            # send_message("No bookable parking spots found.") # Uncomment if you want a message even when no spots are available

    except requests.exceptions.RequestException as e:
        send_message(f"Error fetching URL: {e}")
        print(f"Error fetching URL: {e}")
    except json.JSONDecodeError as e:
        send_message(f"Error decoding JSON: {e}")
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        send_message(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    while True:
        search_parkwhiz()
        sleep(60)  # Wait for 60 seconds before running the search again
