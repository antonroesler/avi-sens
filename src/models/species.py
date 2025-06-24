from pydantic import BaseModel


class Species(BaseModel):
    german_name: str
    latin_name: str
    description: str
    size: str
    migration_description_short: str
    timetable: str
    short_look: str
    long_look: str
    behavior: str
    habitat: str
    endangerment: str
    breeding_pairs: str
    migration_description_long: str
    diet: str
    voice: str
    other_tips: str
