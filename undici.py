import os
import random
import requests
import base64
from openai import OpenAI
from dotenv import load_dotenv
from slugify import slugify
from datetime import datetime
from PIL import Image
from io import BytesIO

# Load env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

REPO_OWNER = "renatotelefono"
REPO_NAME = "astro_9"

european_countries = [
    "Italia", "Francia", "Germania", "Spagna", "Inghilterra", "Polonia",
    "Ungheria", "Romania", "Grecia", "Portogallo", "Austria", "Svezia",
    "Finlandia", "Norvegia", "Svizzera", "Belgio", "Paesi Bassi", "Irlanda",
    "Repubblica Ceca", "Slovacchia", "Croazia", "Bulgaria", "Danimarca"
]

def check_if_file_exists_on_github(path_in_repo):
    github_token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path_in_repo}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def upload_to_github(repo_owner, repo_name, path_in_repo, file_path_local, commit_message, branch="master"):
    with open(file_path_local, "rb") as f:
        content = f.read()
        content_base64 = base64.b64encode(content).decode("utf-8")

    github_token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path_in_repo}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url + f"?ref={branch}", headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    payload = {
        "message": commit_message,
        "content": content_base64,
        "branch": branch
    }
    if sha:
        payload["sha"] = sha

    put_response = requests.put(url, headers=headers, json=payload)

    if put_response.status_code in [200, 201]:
        print(f"\U0001F680 Caricato su GitHub: {path_in_repo}")
    else:
        print(f"❌ Errore GitHub: {put_response.status_code}")
        print(put_response.json())

def generate_random_profile():
    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
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
        name_slug = slugify(full_name)

        markdown_path = f"src/content/blog/{name_slug}.md"
        image_path = f"src/assets/{name_slug}.jpg"

        if not check_if_file_exists_on_github(markdown_path) and not check_if_file_exists_on_github(image_path):
            return full_name, country, birth_year, gender

        print(f"⚠️ Nome o file già presente: {full_name}")
        attempts += 1

    raise Exception("❌ Impossibile trovare un nome univoco dopo 10 tentativi.")

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

def generate_character_image(name, country, birth_year, gender, filename_jpg, story_text):
    base_prompt = (
        f"A realistic black and white portrait of a {'man' if gender == 'uomo' else 'woman'} named {name}, "
        f"from {country}, with an enigmatic and mystical appearance. "
        "The subject is surrounded by occult symbols, ancient books, candlelight, and esoteric imagery. "
        "Atmosphere should be dark, spiritual, and historically rich."
    )

    story_excerpt = story_text.strip().replace("\n", " ")
    story_excerpt = story_excerpt[:400] + "..." if len(story_excerpt) > 400 else story_excerpt

    full_prompt = base_prompt + f" Context: {story_excerpt}"

    print(f"🖼️ Generazione immagine per {name}...")

    response = client.images.generate(
        model="dall-e-3",
        prompt=full_prompt,
        n=1,
        size="1024x1024"
    )

    image_url = response.data[0].url
    image_data = requests.get(image_url).content
    image = Image.open(BytesIO(image_data)).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=40, optimize=True)

    with open(filename_jpg, "wb") as f:
        f.write(buffer.getvalue())

    print(f"✅ Immagine salvata: {filename_jpg}")
    return filename_jpg

def create_markdown(name, description, image_path, story_text):
    filename = f"{slugify(name)}.md"
    pub_date = datetime.today().strftime('%b %d %Y')

    safe_name = name.replace("'", "''")
    safe_description = description.replace("'", "''")

    frontmatter = f"""---
title: '{safe_name}'
description: '{safe_description}'
pubDate: '{pub_date}'
heroImage: '{image_path}'
---

"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(frontmatter + story_text)

    print(f"✅ File generato: {filename}")
    return filename

if __name__ == "__main__":
    name, country, birth_year, gender = generate_random_profile()
    description = f"Occultista {country.lower()}"
    image_filename = f"{slugify(name)}.jpg"
    image_path_in_repo = f"src/assets/{image_filename}"

    story_text = generate_occult_story(name, country, birth_year)

    markdown_filename = create_markdown(
        name, description, f"../../assets/{image_filename}", story_text
    )

    generate_character_image(name, country, birth_year, gender, image_filename, story_text)

    upload_to_github(
        repo_owner=REPO_OWNER,
        repo_name=REPO_NAME,
        path_in_repo=f"src/content/blog/{markdown_filename}",
        file_path_local=markdown_filename,
        commit_message=f"Aggiunta storia: {name}",
        branch="master"
    )

    upload_to_github(
        repo_owner=REPO_OWNER,
        repo_name=REPO_NAME,
        path_in_repo=f"src/assets/{image_filename}",
        file_path_local=image_filename,
        commit_message=f"Aggiunta immagine: {name}",
        branch="master"
    )
