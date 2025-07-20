import os
from openai import OpenAI
from dotenv import load_dotenv
from slugify import slugify
from datetime import datetime

# Carica le variabili d'ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Funzione per generare la storia
def generate_occult_story(name, country, birth_year, image_path):
    prompt = f"""
    Scrivi una storia originale e affascinante, di circa 1000 parole, su una persona immaginaria di nome {name},
    nata in {country} nel {birth_year}. Questa persona ha una vita segnata da un profondo interesse per l'occulto,
    la cabala, la numerologia e tutto ciò che riguarda il mistero. La storia deve essere realistica, coinvolgente
    e con dettagli storici coerenti con l'epoca. Non usare uno stile troppo moderno. Includi eventi chiave, esperienze mistiche,
    viaggi, simboli misteriosi, sogni ricorrenti o rivelazioni esoteriche. Niente elenchi o sezioni: deve sembrare un racconto narrativo continuo.
    """

    print(f"Generazione storia per {name} ({country}, {birth_year})...")

    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei uno scrittore di biografie esoteriche storiche."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
        max_tokens=3000
    )

    return chat_completion.choices[0].message.content

# Funzione per creare il file Markdown
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

# Esecuzione
if __name__ == "__main__":
    name = "Mario Rossi"
    country = "Italia"
    birth_year = 1893
    image_path = "../../assets/mario_rossi.jpg"
    description = "Occultista italiano"

    story = generate_occult_story(name, country, birth_year, image_path)
    create_markdown(name, description, image_path, story)
