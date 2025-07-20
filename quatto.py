import os
import random
import requests
from openai import OpenAI
from dotenv import load_dotenv
from slugify import slugify
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

european_countries = [
    "Italia", "Francia", "Germania", "Spagna", "Inghilterra", "Polonia",
    "Ungheria", "Romania", "Grecia", "Portogallo", "Austria", "Svezia",
    "Finlandia", "Norvegia", "Svizzera", "Belgio", "Paesi Bassi", "Irlanda",
    "Repubblica Ceca", "Slovacchia", "Croazia", "Bulgaria", "Danimarca"
]

def generate_random_profile():
    country = random.choice(european_countries)
    birth_year = random.randint(1400, 1980)
    gender = random.choice(["uomo", "donna"])

    gender_prompt = "maschile" if gender == "uomo" else "femminile"

    prompt = f"""
    Genera un nome e cognome realistico di genere {gender_prompt}, appartenente a una persona nata in {country} nel {birth_year}.
    Il nome deve essere coerente con la lingua e cultura del paese e del periodo storico.
    Rispondi solo con il nome e cognome, senza spiegazioni.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=20
    )

    full_name = response.choices[0].message.content.strip().replace("\n", "")
    return full_name, country, birth_year, gender

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

def generate_character_image(name, country, birth_year, gender, filename_jpg):
    if birth_year < 1800:
        style = (
            f"A realistic oil painting portrait of a mysterious historical {'man' if gender == 'uomo' else 'woman'} named {name}, "
            f"born in {country} in {birth_year}, wearing period-accurate clothing, surrounded by esoteric symbols, books, candles. "
            "Dark, moody background. Renaissance or Baroque style."
        )
    elif birth_year <= 1930:
        style = (
            f"A black and white vintage photograph of a {'man' if gender == 'uomo' else 'woman'} named {name}, born in {country} in {birth_year}. "
            "Sitting in a shadowy study or old library, wearing period-appropriate clothes, with a mysterious expression and occult hints in the background."
        )
    else:
        style = (
            f"A realistic color photograph of a {'man' if gender == 'uomo' else 'woman'} named {name}, born in {country} in {birth_year}. "
            "Wearing mid-20th century clothing, with subtle mystical symbols around, looking thoughtful. Color photo, realistic lighting."
        )

    print(f"🖼️ Generazione immagine per {name} ({birth_year})...")

    response = client.images.generate(
        model="dall-e-3",
        prompt=style,
        n=1,
        size="1024x1024"
    )

    image_url = response.data[0].url
    image_data = requests.get(image_url).content

    with open(filename_jpg, 'wb') as handler:
        handler.write(image_data)

    print(f"✅ Immagine salvata: {filename_jpg}")
    return filename_jpg

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
    name, country, birth_year, gender = generate_random_profile()
    description = f"Occultista {country.lower()}"
    image_filename = f"{slugify(name)}.jpg"
    image_path = f"../../assets/{image_filename}"

    story = generate_occult_story(name, country, birth_year)
    generate_character_image(name, country, birth_year, gender, image_filename)
    create_markdown(name, description, image_path, story)
