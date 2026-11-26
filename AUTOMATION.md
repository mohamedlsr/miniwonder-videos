# MiniWonder : mode d'emploi de la publication automatique

Ce fichier est lu par les sessions planifiées de Claude. Il décrit comment créer **et publier** une vidéo
(16:9, 3 à 4 min) ou un Short (9:16, 35 à 55 s) sur la chaîne YouTube MiniWonder (@miniwonderofficiel),
sans intervention humaine. Le propriétaire a demandé une publication **directe en public**.

## 0. Préparer la session

1. Ajouter le dépôt avec accès en écriture : `add_repo(owner="mohamedlsr", repo="miniwonder-videos", access="push")`,
   puis `git clone --depth 1 https://github.com/mohamedlsr/miniwonder-videos /home/claude/miniwonder-videos`
   (laisser un délai de 10 min) et `register_repo_root`.
2. `bash /home/claude/miniwonder-videos/tools/setup.sh` doit afficher `SETUP OK`.
   Il installe Piper, télécharge la voix française et crée le lien `/home/claude/mw` → `generator/`.
3. Charger les outils Zapier (ToolSearch « zapier youtube »). L'app YouTube (`selected_api = YouTubeV4CLIAPI`)
   est déjà activée et sa connexion par défaut pointe vers la chaîne MiniWonder
   (id de chaîne `UCyRxdZXVvYooFiPXmKkrJVg`). Vérifier avec `find_channel` (sans paramètre) que le titre est « MiniWonder ».

Si une de ces étapes échoue : **ne rien publier**, expliquer le problème dans le message final.

## 1. Choisir le sujet

- Lire `topics.json`. Prendre la **première idée** de `ideas.videos` (ou `ideas.shorts`) dont le `slug`
  n'est pas déjà dans `published`. Ne jamais republier un sujet.
- Quand il reste moins de 5 idées, en ajouter de nouvelles : sciences, nature, animaux, corps humain,
  espace, écologie, pour les 6-8 ans. Varier les thèmes d'une semaine à l'autre.
- Pour un Short, on peut aussi reprendre un fait marquant d'une vidéo déjà publiée.

## 2. Écrire le contenu (français, 6-8 ans)

- **Vérifier chaque fait** avec WebSearch (au moins une source fiable : encyclopédie, musée, agence
  scientifique, NASA/ESA, CNRS…). En cas de doute, ne pas dire le fait. Préférer « jusqu'à », « environ ».
- Phrases courtes, vocabulaire simple, ton joyeux. Mini (l'étoile) est la narratrice et s'adresse à l'enfant (« tu »).
- **Interdits** : contenu effrayant ou violent (pas de prédation détaillée, pas de sang, pas de mort),
  personnages ou marques protégés, personnes réelles, liens, demandes d'abonnement ou de « like »,
  conseils médicaux, sujets politiques ou religieux, comparaisons qui se moquent de quelqu'un.
  Une expérience à faire à la maison se fait toujours « avec un adulte » et sans danger (pas de feu, pas de produits chimiques).
- Écrire les nombres en lettres dans la narration (« cinq mètres et demi »), en chiffres à l'écran (« 5,5 m »).
- Titre de vidéo : `<Sujet> pour enfants <emoji> | <3-4 mots-clés> + QUIZ | MiniWonder` (100 caractères max).
- Titre de Short : `3 faits incroyables sur <sujet> <emoji> #Shorts`.

### Vidéo longue : structure (modèle : `generator/ep1b.py`)
`intro2` → 5 à 7 scènes `topic2` (une notion chacune, 2 ou 3 `chip_items`, un `fact` « Le savais-tu ? » pour la plupart)
→ une scène « RÉCAPITULONS » → 3 × `quiz2` → `outro2`. Durée visée : 3 à 4 min.

### Short : structure (modèle : `generator/short_girafe.py`)
`short_scene(first=True)` titre → 3 × `short_scene(badge=1..3, card=...)` → `short_quiz` → `short_scene(last=True)`.
Durée visée : 35 à 55 s (maximum 58 s). Lancer avec `MW_VERTICAL=1`.

## 3. Dessiner

- Réutiliser ce qui existe dans `generator/art.py` (`star`, `elephant`, `giraffe`, `lion`, `zebra`, `drop`, `sun_body`,
  `sun_rays`, `cloud`, `earth`, `plant`, `seed_cut`, `bee`, `flower`, `jar`, `butterfly`, `bird`, icônes…) et
  les décors de `engine.py` (`bg_savanna`, `bg_world`, `bg_garden`, `bg_sky`, `bg_quiz`, `bg_intro`).
- Pour un nouveau sujet, dessiner de nouveaux personnages dans le même style avec `art.Pen` : formes rondes,
  contour `#3a2e2a`, grands yeux `art.eye(...)` avec un paramètre `blink`, joues roses `art.cheek(...)`,
  fonctions décorées `@lru_cache(None)` qui acceptent `blink=False` (pour `dancer`/`hop_in`).
  Nouveaux décors : même méthode que `bg_savanna` (dégradé `vgrad` + `hills` + éléments).
- Jamais de personnage, logo ou marque existants.
- Avant le rendu complet : `python3 preview.py <module> <scène:fraction> ...` (ajouter `MW_VERTICAL=1` pour un Short)
  et **regarder les images** (`/tmp/pv_<module>_N.jpg`) au moment où l'écran est le plus chargé. Corriger les
  chevauchements, les textes coupés, les éléments hors écran.

## 4. Rendre

- Créer le script dans `generator/` : `epNN_<slug>.py` (vidéos, NN = numéro suivant) ou `short_<slug>.py`.
- Sortie dans `/home/claude/mw/out/<slug>/`. Vidéo : `render_video(..., music_fn=music_for(SCENES), sfx_fn=music2.sfx, music_gain=0.5, duck_depth=0.6)`
  comme `ep1b.py`. Short : `render_short(...)`.
- Contrôler le résultat : `ffprobe` (durée, 1920×1080 ou 1080×1920, piste audio présente),
  extraire 3 ou 4 images avec ffmpeg et les regarder.
- Vidéo longue : créer la miniature avec `kit2.make_thumbnail(path, bg, titre_court, [(sprite, x, y_bas, échelle), ...])`, puis la regarder.

## 5. Publier

1. Mettre les fichiers en ligne temporairement :
   `bash /home/claude/miniwonder-videos/tools/stage_upload.sh upload-video <video.mp4> <miniature.jpg>`
   (`upload-short` pour un Short). Le script affiche les liens directs `raw.githubusercontent.com`.
   La branche est écrasée à chaque fois : c'est voulu.
2. Zapier `execute_zapier_write_action`, `selected_api="YouTubeV4CLIAPI"`, `action="upload_video"`,
   `tool_name="youtube_upload_video"`, avec :
   - `title`, `description`, `video` (lien de la vidéo), `tags` (8 à 12),
   - `privacy_status="public"`, `made_for_kids="true"`, `category_id="27"`,
     `default_language="fr"`, `default_audio_language="fr"`, `notify_subscribers="true"`.
   - **Ne pas** passer `thumbnail` dans cet appel.
3. Vidéo longue uniquement : `action="upload_video_thumbnail"`, `tool_name="youtube_update_video_thumbnail"`,
   `video_id=<id renvoyé>`, `thumbnail=<lien de la miniature>`.
4. Si l'envoi échoue : vérifier d'abord avec `video_in_playlist` (`playlist_id="UUyRxdZXVvYooFiPXmKkrJVg"`)
   que la vidéo n'est pas déjà en ligne avant de réessayer **une seule fois**. Ne jamais créer de doublon.

**Description** (vidéo) : 2 phrases d'accroche, la liste des notions avec emojis, la phrase sur le quiz, les
chapitres `00:00 Introduction`… calculés à partir des durées de scènes affichées par `render_video`, puis
`Rejoins la famille MiniWonder pour rire, apprendre et découvrir ! 🚀` et la ligne obligatoire :
`Voix de synthèse : Piper, voix « siwis » (SIWIS French Speech Synthesis Database, CC BY 4.0).`
**Description** (Short) : 2 phrases, `#Shorts #<sujet> #enfants #MiniWonder`, puis la même ligne de crédit.

## 6. Ranger

- Ajouter l'entrée dans `topics.json` → `published` (date, slug, titre, youtube_id, script) et retirer l'idée utilisée.
- `git add generator/<script>.py topics.json` (+ tout fichier de dessin modifié). **Ne jamais commiter de .mp4.**
- Commit en français, puis `git -c push.negotiate=true push origin HEAD:main`.
- Message final : titre, lien `https://www.youtube.com/watch?v=<id>`, durée, et tout problème rencontré.
