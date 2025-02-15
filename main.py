import requests
from bs4 import BeautifulSoup
import json
from telegram_interface import send_message

def parse_parkwhiz_html(html_string):
    """
    Parses ParkWhiz HTML to extract parking availability information.

    Args:
        html_string: The HTML content as a string.

    Returns:
        A dictionary containing the venue availability and a list of
        location details with availability.
    """

    soup = BeautifulSoup(html_string, 'html.parser')

    # Extract initial state (where the data is)
    script_tag = soup.find('script', string=lambda t: "__INITIAL_STATE__" in t if t else False)
    if not script_tag:
        return {"error": "Could not find __INITIAL_STATE__ script tag"}

    # stupid ah linting error shut up
    script_content = script_tag.string
    if script_content is None:
        return {"error": "Script tag content is None"}

    start_index = script_content.find('{')
    end_index = script_content.rfind('}') + 1
    try:
        initial_state = json.loads(script_content[start_index:end_index])
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON from __INITIAL_STATE__"}

    # Extract venue availability
    venue_availability = initial_state.get('venue', {}).get('availability', {})

    # Extract location details and availability
    locations_data = []
    for location in initial_state.get('locations', []):
        location_info = {
            'name': location['_embedded']['pw:location']['name'],
            'address': location['_embedded']['pw:location']['address1'],
            'city': location['_embedded']['pw:location']['city'],
            'state': location['_embedded']['pw:location']['state'],
            'postal_code': location['_embedded']['pw:location']['postal_code'],
            'distance_feet': location['distance']['straight_line']['feet'],
            'bookable': False,
            'spaces_remaining': None,
            'price': None
        }

        if location['purchase_options']:
            purchase_option = location['purchase_options'][0]
            if purchase_option['space_availability']['status'] == 'limited':
                location_info['bookable'] = True
                location_info['spaces_remaining'] = purchase_option['space_availability']['spaces_remaining']
                location_info['price'] = purchase_option['price']['USD']
            elif purchase_option['space_availability']['status'] == 'unavailable':
                location_info['bookable'] = False
                location_info['spaces_remaining'] = 0
                location_info['price'] = purchase_option['price']['USD']

        locations_data.append(location_info)

    return {
        'venue_availability': venue_availability,
        'locations': locations_data
    }


if __name__ == "__main__":
    # sample
    with open('responses/manual_response.html', 'r') as f:
        html_content = f.read()

    # going to implement this soon
    # Fetch the HTML content from the URL
    # url = "http://www.parkwhiz.com/snowbird-resort-parking/mar-2-2025-daily-parking-1531202/"  # Replace with the actual URL
    # response = requests.get(url)
    # html_content = response.text

    availability_data = parse_parkwhiz_html(html_content)

    found_parking = False
    for location in availability_data['locations']:
        if 'spaces_remaining' in location and location['spaces_remaining'] > 0:
            send_message(f"Location: {location['name']}\nSpaces Remaining: {location['spaces_remaining']}\nPrice: ${location['price']}")
            found_parking = True

    if not found_parking:
        send_message("No parking available")

    if "error" in availability_data:
        print("Error:", availability_data["error"])
    else:
        print(json.dumps(availability_data, indent=4))
