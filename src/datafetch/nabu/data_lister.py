from constants import LIST_URL
import requests
from bs4 import BeautifulSoup
import json


def load_list_data():
    response = requests.get(LIST_URL)
    return response.text


def extract_species_urls():
    """
    Extract species URLs and titles from the NABU bird list HTML.

    Returns:
        dict: Dictionary with species titles as keys and URLs as values
              e.g. {"Zaunammer": "/tiere-und-pflanzen/voegel/portraets/zaunammer/"}
    """
    html_content = load_list_data()
    soup = BeautifulSoup(html_content, "html.parser")

    species_dict = {}

    # Find all bird-result divs
    bird_results = soup.find_all("div", class_="bird-result")

    for bird_div in bird_results:
        # Find the anchor tag within each bird-result div
        link = bird_div.find("a")
        if link:
            # Extract href and title attributes
            href = link.get("href")
            title = link.get("title")

            if href and title:
                species_dict[title] = href

    return species_dict


def save_species_urls(species_dict):
    with open("species_urls.json", "w") as f:
        json.dump(species_dict, f)


if __name__ == "__main__":
    species_dict = extract_species_urls()
    save_species_urls(species_dict)
