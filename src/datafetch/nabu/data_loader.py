import requests
from bs4 import BeautifulSoup
import json
import logging
import re
from constants import SPECIES_URL_FILE, BASE_URL
from models.species import Species
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_species_urls():
    with open(SPECIES_URL_FILE, "r") as f:
        return json.load(f)


def load_species_data(species_url):
    response = requests.get(f"https://{BASE_URL}/{species_url}")
    return response.text


def extract_species_data(species_data):
    soup = BeautifulSoup(species_data, "html.parser")
    return soup


def species_html_to_model(species_html):
    """
    Parse HTML content and extract species information into a Species model.

    Args:
        species_html: HTML content as string
        species_url: URL of the species page (optional)

    Returns:
        Species: Parsed species data model
    """
    soup = BeautifulSoup(species_html, "html.parser")

    # Helper function to safely extract text
    def safe_extract(element, default=""):
        if element:
            return element.get_text(strip=True)
        return default

    # Helper function to extract card content by header text
    def extract_card_content(header_text):
        cards = soup.find_all("div", class_="vogelartendetail-single-factcards-card")
        for card in cards:
            header = card.find("h3")
            if header and header_text.lower() in header.get_text(strip=True).lower():
                body = card.find(
                    "div", class_="vogelartendetail-single-factcards-card-body"
                )
                return safe_extract(body)
        return ""

    try:
        # Extract German name
        german_name_elem = soup.find("h1")
        german_name = safe_extract(german_name_elem)
        if not german_name:
            logger.warning("German name not found")

        # Extract Latin name
        latin_name_elem = soup.find("h2").find("em") if soup.find("h2") else None
        latin_name = safe_extract(latin_name_elem)
        if not latin_name:
            logger.warning("Latin name not found")

        # Extract description
        description_elem = soup.find("div", class_="single-bird-description")
        description = safe_extract(description_elem)
        if not description:
            logger.warning("Description not found")

        # Extract facts from the factlist using icon-based approach
        factlist = soup.find("div", class_="vogelartendetail-single-factlist")
        size = ""
        migration_short = ""
        timetable = ""
        short_look = ""

        if factlist:
            facts = factlist.find_all("li")
            for fact in facts:
                fact_text = fact.get_text(strip=True)
                icon = fact.find("i")

                if icon:
                    icon_class = icon.get("class", [])

                    # Size - identified by expand-alt icon
                    if "fa-expand-alt" in icon_class:
                        size = fact_text

                    # Migration behavior - identified by suitcase icon
                    elif "fa-suitcase" in icon_class:
                        migration_short = fact_text

                    # Observation time - identified by calendar icon
                    elif "fa-calendar-alt" in icon_class:
                        timetable = fact_text

                    # Short identification tip - identified by lightbulb icon
                    elif "fa-lightbulb" in icon_class:
                        short_look = fact_text
                else:
                    # Fallback: if no icon, try to identify by content patterns
                    if "cm groß" in fact_text:
                        size = fact_text
                    elif any(
                        keyword in fact_text.lower()
                        for keyword in [
                            "standvogel",
                            "zugvogel",
                            "zieher",
                            "überwintert",
                        ]
                    ):
                        migration_short = fact_text
                    elif any(
                        keyword in fact_text.lower()
                        for keyword in [
                            "beobachten",
                            "sichtbar",
                            "anzutreffen",
                            "zu sehen",
                        ]
                    ):
                        timetable = fact_text

        # Extract card contents
        long_look = extract_card_content("Aussehen")
        behavior = extract_card_content("Verhalten")
        habitat = extract_card_content("Lebensraum")
        migration_long = extract_card_content("Zugverhalten")
        diet = extract_card_content("Nahrung")
        voice = extract_card_content("Stimme")

        # Extract endangerment status
        endangerment = ""
        endangerment_elem = soup.find("h4", string=re.compile("Gefährdungsgrad"))
        if not endangerment_elem:
            # Try alternative approach - find h4 that contains "Gefährdungsgrad" text
            h4_elements = soup.find_all("h4")
            for h4 in h4_elements:
                if "Gefährdungsgrad" in h4.get_text():
                    endangerment_elem = h4
                    break

        if endangerment_elem:
            # Find the sibling <div> tag that contains the actual status
            sibling_div = endangerment_elem.find_next_sibling("div")
            if sibling_div:
                # Get the first text node, which should be the endangerment status
                endangerment = sibling_div.get_text(strip=True).split("\n")[0].strip()
                logger.debug(f"Found endangerment status: '{endangerment}'")
        if not endangerment:
            logger.warning("Endangerment status not found")

        # Extract breeding pairs
        breeding_pairs_elem = soup.find("h4", string=re.compile("Bestandszahl"))
        if not breeding_pairs_elem:
            # Try alternative approach - find h4 that contains "Bestandszahl" text
            h4_elements = soup.find_all("h4")
            for h4 in h4_elements:
                if "Bestandszahl" in h4.get_text():
                    breeding_pairs_elem = h4
                    break

        breeding_pairs = "Keine Angabe"
        if breeding_pairs_elem:
            # Find the sibling <p> tag that contains the actual number
            sibling_p = breeding_pairs_elem.find_next_sibling("p")
            if sibling_p:
                breeding_pairs = sibling_p.get_text(strip=True)
                logger.debug(f"Found breeding pairs: '{breeding_pairs}'")

        # Extract observation tips
        other_tips = ""
        tips_section = soup.find("h4", string=re.compile("Beobachtungstipp"))
        if tips_section:
            tips_container = tips_section.find_parent().find_parent()
            if tips_container:
                tips_body = tips_container.find("div", class_="single-teaser-text-body")
                other_tips = safe_extract(tips_body)

        # Log missing information
        missing_fields = []
        if not german_name:
            missing_fields.append("german_name")
        if not latin_name:
            missing_fields.append("latin_name")
        if not description:
            missing_fields.append("description")
        if not size:
            missing_fields.append("size")
        if not migration_short:
            missing_fields.append("migration_description_short")
        if not timetable:
            missing_fields.append("timetable")
        if not short_look:
            missing_fields.append("short_look")
        if not long_look:
            missing_fields.append("long_look")
        if not behavior:
            missing_fields.append("behavior")
        if not habitat:
            missing_fields.append("habitat")
        if not endangerment:
            missing_fields.append("endangerment")
        if not migration_long:
            missing_fields.append("migration_description_long")
        if not diet:
            missing_fields.append("diet")
        if not voice:
            missing_fields.append("voice")

        if missing_fields:
            logger.warning(
                f"Missing fields for species {german_name}: {', '.join(missing_fields)}"
            )

        # Create and return Species model
        species = Species(
            german_name=german_name,
            latin_name=latin_name,
            description=description,
            size=size,
            migration_description_short=migration_short,
            timetable=timetable,
            short_look=short_look,
            long_look=long_look,
            behavior=behavior,
            habitat=habitat,
            endangerment=endangerment,
            breeding_pairs=breeding_pairs,
            migration_description_long=migration_long,
            diet=diet,
            voice=voice,
            other_tips=other_tips,
        )

        logger.info(f"Successfully parsed species: {german_name} ({latin_name})")
        return species

    except Exception as e:
        logger.error(f"Error parsing species HTML: {str(e)}")
        # Return a minimal Species object with empty fields
        return Species(
            german_name="",
            latin_name="",
            description="",
            size="",
            migration_description_short="",
            timetable="",
            short_look="",
            long_look="",
            behavior="",
            habitat="",
            endangerment="",
            breeding_pairs=0,
            migration_description_long="",
            diet="",
            voice="",
            other_tips="",
        )


if __name__ == "__main__":
    # load species urls
    species_urls = load_species_urls()
    for species_name, url in species_urls.items():
        print(species_name, url)
        species_data = load_species_data(url)
        with open(
            f"species_data/{species_name.replace(' ', '_').split('/')[0]}.html",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(species_data)

    # List all files in species_data
    for file in os.listdir("species_data"):
        with open(f"species_data/{file}", "r", encoding="utf-8") as f:
            species_data = f.read()
        species = species_html_to_model(species_data)
        with open(
            f"species_data_json/{file.replace('.html', '.json')}", "w", encoding="utf-8"
        ) as f:
            json.dump(species.model_dump(), f, ensure_ascii=False, indent=4)
