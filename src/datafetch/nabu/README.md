# NABU Data Fetcher Module

This module provides tools for scraping and processing bird species data from the NABU (Naturschutzbund Deutschland) website. It consists of two main components: a data lister for discovering species URLs and a data loader for extracting detailed species information.

## Overview

The NABU module extracts comprehensive bird species information from the NABU bird portrait pages at `www.nabu.de/tiere-und-pflanzen/voegel/portraets/`. It processes both the species list and individual species pages to create structured data that conforms to the `Species` data model.

## Components

### 1. `constants.py`

Contains configuration constants for the NABU website:

- `BASE_URL`: The base NABU website URL
- `BASE_PREFIX`: The path prefix for bird portraits
- `LIST_URL`: The complete URL for the bird species list page
- `SPECIES_URL_FILE`: The filename for storing species URLs

### 2. `data_lister.py`

Handles discovery and extraction of species URLs from the main NABU bird list page.

**Key Functions:**

- `load_list_data()`: Fetches the HTML content from the NABU bird list page
- `extract_species_urls()`: Parses the HTML to extract species names and their corresponding URLs
- `save_species_urls()`: Saves the extracted URLs to a JSON file for later use

### 3. `data_loader.py`

The main data extraction module that processes individual species pages and converts them into structured `Species` objects.

**Key Functions:**

- `load_species_urls()`: Loads previously saved species URLs from JSON
- `load_species_data(species_url)`: Fetches HTML content for a specific species page
- `species_html_to_model(species_html)`: Parses HTML content and extracts species information

**Extracted Data Fields:**

- Basic information: German name, Latin name, description
- Physical characteristics: Size, appearance details
- Behavioral data: Migration patterns, behavior, habitat preferences
- Conservation status: Endangerment level, breeding pair counts
- Observation details: Best viewing times, identification tips, voice characteristics
- Additional information: Diet, observation tips

## Workflow

1. **Discovery Phase** (`data_lister.py`):

   - Scrapes the main NABU bird list page
   - Extracts species names and URLs
   - Saves URLs to `species_urls.json`

2. **Data Collection Phase** (`data_loader.py`):

   - Loads species URLs from JSON
   - Fetches individual species pages
   - Saves raw HTML to `species_data/` directory

3. **Data Processing Phase** (`data_loader.py`):

   - Parses HTML files from `species_data/`
   - Extracts structured information using the `Species` model
   - Saves processed data as JSON to `species_data_json/` directory

## Output

The module generates two types of output:

1. **Raw HTML files** in `species_data/`: Original HTML content from NABU pages
2. **Structured JSON files** in `species_data_json/`: Processed species data conforming to the Species model
