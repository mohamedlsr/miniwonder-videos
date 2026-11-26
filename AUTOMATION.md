# MiniWonder : mode d'emploi de la publication automatique

Ce fichier est lu par les sessions planifiées de Claude. Il décrit comment créer **et publier** une vidéo
(16:9, **6 à 8 min**) ou un Short (9:16, 35 à 55 s) sur la chaîne YouTube MiniWonder (@miniwonderofficiel),
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

**Lire aussi `STRATEGY.md` en entier** : formats, règles anti-répétition, référencement, playlists.

## 1. Choisir le sujet

- Lire `topics.json`. Prendre la **première idée** de `ideas.videos` (ou `ideas.shorts`) dont le `slug`
  n'est pas déjà dans `published`. Ne jamais republier un sujet.
- Chaque idée a un `format` et une `playlist`. Vérifier que le format **et** la playlist diffèrent de ceux de la
  dernière vidéo publiée (`published`, dernière entrée) ; sinon prendre l'idée suivante qui respecte cette règle.
- Style musical : `style = len(published.videos) % 4` (ou `len(published.shorts) % 4` pour un Short).
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
- Titre de vidéo : commencer par la recherche des parents (« Les planètes pour enfants », « Pourquoi … ? »), puis emoji,
  2 ou 3 mots-clés, « | MiniWonder ». Moins de 70 caractères si possible, 100 maximum.

### Vidéo longue : structure selon le `format` (voir le tableau de STRATEGY.md)
Briques disponibles dans `generator/kit2.py` : `intro2`, `topic2` (scène avec acteur, étiquettes `chip_items`,
encadré `fact`), `quiz2`, `outro2`, plus `dancer`, `hop_in`, `mini2`, `wavy_text`, `pop_label`, `sparkle_burst`,
`confetti_burst`, `sun2`, `birds`, `butterflies`, `drift_clouds`, `camera`, `star_wipe`. Modèle complet : `generator/ep1b.py`.
- `exploration` : `intro2` → 7 à 10 `topic2` → « RÉCAPITULONS » → 3 `quiz2` → `outro2`.
- `aventure` : `intro2` (Mini présente le compagnon) → 8 à 11 scènes `topic2` qui racontent le voyage dans l'ordre
  (le compagnon parle aussi : ses répliques sont des lignes de narration annoncées par Mini, ex. « Plic s'écrie : … »),
  décors qui changent au fil de l'histoire → récap → 3 `quiz2` → `outro2`.
- `pourquoi` : `intro2` → 6 à 8 scènes `topic2` dont le titre est la question (« POURQUOI LE CIEL EST BLEU ? ») et dont
  la première ligne pose la question, puis la réponse en 3 ou 4 phrases → 3 `quiz2` → `outro2`.
- `grand-quiz` : `intro2` → 10 à 12 `quiz2` (numérotés 1/12 … : adapter le libellé `QUIZ n/N` dans une copie de `quiz2`
  si besoin), chaque réponse suivie d'une courte scène `topic2` qui explique (15 à 25 s) → `outro2` (« Combien as-tu
  de bonnes réponses ? »).
- `experience` : `intro2` → pour chaque expérience (2 ou 3) : matériel, étapes (« avec un adulte »), résultat,
  explication → récap → 3 `quiz2` → `outro2`. Expériences sans feu, sans produit dangereux, sans objet coupant.
**Durée visée : 6 à 8 minutes.** Si le rendu fait moins de 5 min 30, ajouter des notions ou des questions avant de publier.
Une accroche dans les 10 premières secondes et une annonce à mi-parcours (« Et tout à l'heure… ») sont obligatoires.

### Short : structure selon le `format` (modèle : `generator/short_girafe.py`, briques de `generator/kit_short.py`)
- `3-faits` : `short_scene(first=True)` titre → 3 × `short_scene(badge=1..3, card=...)` → `short_quiz` → `short_scene(last=True)`.
- `vrai-ou-faux` : titre → 3 affirmations, chacune avec la réponse « VRAI ! » ou « FAUX ! » révélée (`short_scene` + `card`) → fin.
- `devinette` : « Qui suis-je ? » → 3 indices (personnage caché en silhouette ou flou, `card` = indice) → révélation → fin.
- `quiz-eclair` : titre → 2 `short_quiz` → fin.
Durée visée : 35 à 55 s (maximum 58 s). Lancer avec `MW_VERTICAL=1`. Titre :
`<Format> : <sujet> <emoji> #Shorts` (ex. « Vrai ou faux : le manchot 🐧 #Shorts », « 3 faits incroyables sur la tortue 🐢 #Shorts »).

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
- Sortie dans `/home/claude/mw/out/<slug>/`. Vidéo : `render_video(..., music_fn=music_for(SCENES, style), sfx_fn=music2.sfx, music_gain=0.5, duck_depth=0.6)`
  comme `ep1b.py`. Short : `render_short(name, SCENES, outdir, style)`.
- Une vidéo de 7 min se rend en 15 à 25 min : lancer le rendu en arrière-plan (`nohup … &`) et attendre la fin
  avec une boucle `until grep -q FINAL log; do sleep 15; done` (délai de commande de 10 min, répéter si besoin).
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
4. Ajouter la vidéo à sa playlist : `action="add_video_to_playlist"`, `playlist_id` = `topics.json → playlists[<playlist>].id`.
   Pour un Short : l'ajouter à la playlist `shorts` **et** à celle de son thème.
5. Si l'envoi échoue : vérifier d'abord avec `video_in_playlist` (`playlist_id="UUyRxdZXVvYooFiPXmKkrJVg"`)
   que la vidéo n'est pas déjà en ligne avant de réessayer **une seule fois**. Ne jamais créer de doublon.

**Description** (vidéo) : 2 phrases d'accroche, la liste des notions avec emojis, la phrase sur le quiz, les
chapitres `00:00 Introduction`… calculés à partir des durées de scènes affichées par `render_video`, puis
`Rejoins la famille MiniWonder pour rire, apprendre et découvrir ! 🚀` et la ligne obligatoire :
`Voix de synthèse : Piper, voix « siwis » (SIWIS French Speech Synthesis Database, CC BY 4.0).`
**Description** (Short) : 2 phrases, `#Shorts #<sujet> #enfants #MiniWonder`, puis la même ligne de crédit.

## 6. Ranger

- Ajouter l'entrée dans `topics.json` → `published` (date, slug, titre, youtube_id, script, format, playlist, duration_s)
  et retirer l'idée utilisée.
- `git add generator/<script>.py topics.json` (+ tout fichier de dessin modifié). **Ne jamais commiter de .mp4.**
- Commit en français, puis `git -c push.negotiate=true push origin HEAD:main`.
- Message final : titre, lien `https://www.youtube.com/watch?v=<id>`, durée, et tout problème rencontré.
