=======================================
NOXCO – 3D Model Platform
=======================================

Beschrijving:
-------------
Noxco is een online platform waar gebruikers 3D-modellen (STL-bestanden) kunnen uploaden, bekijken en verkopen. Het systeem is beveiligd met Auth0 en werkt met een persoonlijke gebruikersprofiel. Gebruikers kunnen hun modellen beheren, andere modellen bekijken en reacties of likes achterlaten.

Belangrijkste functies:
-----------------------
- Inloggen via Auth0 (e-mail of telefoon)
- Persoonlijk profiel met 3D-modelbeheer
- Uploaden en bekijken van STL-bestanden via een 3D-viewer (Three.js)
- Statistieken per model: views, likes, reacties
- Zoeken naar gebruikers of modellen
- Driestaps registratie:
  1. Persoonlijke gegevens (ook via It'sMe)
  2. Bankgegevens
  3. Contract goedkeuren (via checkbox)

Gebruikte technologieën:
-------------------------
- Backend: Flask (Python), SQLAlchemy
- Database: PostgreSQL (via Docker container)
- Authenticatie: Auth0
- Frontend: HTML, Bootstrap 5, CSS (goud-zwart thema)
- 3D Viewer: Three.js
- Containerisatie: Docker + Docker Compose

Projectstructuur:
------------------
flask_3d_platform/
│
├── app/
│   ├── templates/         -> HTML-bestanden
│   ├── static/            -> CSS, JS, STL
│   ├── database/          -> Databasemodellen
│   ├── routes/
│   │   ├── main.py        -> Hoofdpagina’s
│   │   ├── auth.py        -> Login/Logout routes
│   └── __init__.py        -> App setup
│
├── config.py              -> Instellingen (Auth0, DB)
├── .env                   -> Gevoelige sleutels
├── run.py                 -> App starten
├── requirements.txt       -> Benodigde Python libraries
└── docker-compose.yml     -> Docker configuratie

Installatie (voor ontwikkelaars):
----------------------------------
1. Installeer Python en Docker
2. Maak een virtuele omgeving:
   python3 -m venv venv
   source venv/bin/activate

3. Installeer dependencies:
   pip install -r requirements.txt

4. Vul het bestand `.env` in met:
   - AUTH0_CLIENT_ID
   - AUTH0_CLIENT_SECRET
   - AUTH0_DOMAIN
   - AUTH0_CALLBACK_URL

5. Start het project met:
   docker-compose up --build

6. Open in je browser:
   http://localhost:5000

Auteurs:
--------
Aslambek Chamutaev

Copyright:
----------
MIT-licentie – vrij voor gebruik en aanpassing.

Vragen of feedback?
-------------------
Stuur een bericht of open een issue in het project.
