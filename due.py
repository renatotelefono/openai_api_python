import os
import random
from openai import OpenAI
from dotenv import load_dotenv
from slugify import slugify
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Lista di paesi europei compatibili
european_countries = [
    "Italia", "Francia", "Germania", "Spagna", "Inghilterra", "Polonia",
    "Ungheria", "Romania", "Grecia", "Portogallo", "Austria", "Svezia",
    "Finlandia", "Norvegia", "Svizzera", "Belgio", "Paesi Bassi", "Irlanda",
    "Repubblica Ceca", "Slovacchia", "Croazia", "Bulgaria", "Danimarca"
]

# Genera casualmente dati coerenti (nome + paese + data)
def generate_random_profile():
    country = random.choice(european_countries)
    birth_year = random.randint(1400, 1980)

    prompt = f"""
    Genera un nome e cognome realistico appartenente a una persona nata in {country} nel {birth_year}.
    Il nome deve essere coerente con la lingua e cultura del paese e del periodo storico.
    Rispondi solo con il nome e cognome, senza spiegazioni.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=20
    )

    full_name = response.choices[0].message.content.strip().replace("\n", "")
    return full_name, country, birth_year

# Genera la storia esoterica
def generate_occult_story(name, country, birth_year):
    prompt = f"""
    Scrivi una storia originale di circa 1000 parole su una persona immaginaria di nome {name},
    nata in {country} nel {birth_year}. Questa persona ha dedicato la sua vita allo studio dell'occulto,
    della cabala, della numerologia e dei misteri esoterici. La narrazione deve essere coinvolgente,
    ambientata storicamente in modo coerente, con esperienze mistiche, sogni, incontri simbolici o viaggi iniziatici.
    Lo stile deve essere narrativo, continuo, senza elenchi.
    """

    print(f"📜 Generazione storia per {name} ({country}, {birth_year})...")

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei uno scrittore di biografie esoteriche storiche."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
        max_tokens=3000
    )

    return response.choices[0].message.content

# Scrive su file Markdown
def create_markdown(name, description, image_path, story_text):
    filename = f"{slugify(name)}.md"
    pub_date = datetime.today().strftime('%b %d %Y')

    frontmatter = f"""---
title: '{name}'
description: '{description}'
pubDate: '{pub_date}'
heroImage: '{image_path}'
---

"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(frontmatter + story_text)

    print(f"✅ File generato: {filename}")

# MAIN
if __name__ == "__main__":
    name, country, birth_year = generate_random_profile()
    description = f"Occultista {country.lower()}"
    image_path = f"../../assets/{slugify(name)}.jpg"

    story = generate_occult_story(name, country, birth_year)
    create_markdown(name, description, image_path, story)
