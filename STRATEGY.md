# MiniWonder : stratégie de croissance et de monétisation

Objectif : atteindre le seuil de la publicité YouTube (Programme Partenaire) avec une chaîne pour enfants
de qualité, sans être refusée pour « contenu générique ou répétitif ».

## Les seuils à viser (vérifiés en novembre 2026)

- **Publicité (le vrai revenu)** : 1 000 abonnés **et** soit 4 000 heures de visionnage de vidéos longues
  sur 12 mois, soit 10 millions de vues de Shorts sur 90 jours.
  **À partir du 1er février 2027 : 8 000 heures ou 20 millions de vues de Shorts** (1 000 abonnés inchangé).
  C'est ce seuil-là qu'on vise.
- Les heures regardées sur les Shorts **ne comptent pas** dans les heures : les heures viennent des vidéos longues.
- Palier à 500 abonnés (disponible au Maroc) : il ne donne que les dons et abonnements payants, qui sont
  **désactivés sur les vidéos « conçues pour les enfants »**. Inutile pour MiniWonder.
- Contenu pour enfants : pas de publicité personnalisée, pas de commentaires, pas de cloche → revenus par vue plus faibles,
  il faut donc beaucoup d'heures de visionnage.
- Règle « contenu générique ou répétitif » (juillet 2026) : YouTube refuse de rémunérer le contenu
  « qui semble fait à partir d'un modèle » ou qui paraît répétitif quand on enchaîne les vidéos de la chaîne.
  → **chaque vidéo doit être visiblement différente** (format, décor, personnages, musique, déroulé).

## Le plan

### 1. Vidéos longues : 3 par semaine, 6 à 8 minutes
Plus de minutes par vue = plus d'heures. Cinq formats qui tournent (jamais deux fois le même d'affilée) :

| Format | Déroulé | Pourquoi |
|---|---|---|
| `exploration` | Mini présente 6 à 9 notions, « Le savais-tu ? », récap, quiz de 3 questions | Le format pilote, clair et complet |
| `aventure` | Une petite histoire : Mini et un compagnon récurrent (Plic la goutte d'eau, Pépin la graine, ou un nouveau personnage du sujet) vivent un voyage ; chaque étape apprend quelque chose ; quiz final | Les histoires retiennent les enfants plus longtemps |
| `pourquoi` | 6 à 8 « grandes questions » d'enfants (« Pourquoi… ? ») avec une réponse simple et illustrée chacune | Correspond à ce que les parents et enfants tapent dans la recherche |
| `grand-quiz` | 10 à 12 questions, compte à rebours, réponse expliquée en 15 à 25 s après chaque question, score à la fin | Très interactif, se regarde en famille et jusqu'au bout |
| `experience` | 2 ou 3 expériences sans danger « avec un adulte » + l'explication scientifique | Utile, original, se partage entre parents |

Chaque vidéo : accroche dans les 10 premières secondes (une question ou une promesse : « À la fin, tu sauras… »),
une annonce à mi-parcours (« Et tout à l'heure, le grand quiz ! »), chapitres dans la description.

### 2. Shorts : 5 par semaine, pour attirer de nouveaux spectateurs
Formats qui tournent : `3-faits`, `vrai-ou-faux`, `devinette` (« Qui suis-je ? »), `quiz-eclair`.
Quand c'est possible, le Short reprend le sujet d'une vidéo longue publiée et la cite dans la description
(« Retrouve la vidéo complète « … » sur la chaîne MiniWonder »).

### 3. Ne pas ressembler à un modèle
- Alterner les playlists (animaux, espace, corps humain, nature, sciences) d'une vidéo à l'autre.
- Changer le style musical à chaque vidéo : `music_for(SCENES, style=N)` avec N = nombre de vidéos publiées modulo 4.
- Dessiner de nouveaux personnages et décors propres au sujet ; varier les couleurs des étiquettes et les ambiances.
- Varier les phrases d'intro et de fin (ne jamais réutiliser mot pour mot celles d'une vidéo précédente).
- Mini reste la présentatrice : c'est l'identité de la chaîne.

### 4. Être trouvé (référencement)
- Titre : commence par ce que les parents cherchent (« Les planètes pour enfants », « Pourquoi le ciel est bleu ? »),
  puis un emoji, puis 2 ou 3 mots-clés, puis « | MiniWonder ». Idéalement moins de 70 caractères.
- Les 2 premières lignes de la description reprennent le sujet en phrases naturelles.
- 8 à 12 tags : sujet, « pour enfants », « vidéo éducative », « dessin animé éducatif », notions clés, « MiniWonder ».
- Miniature : 3 ou 4 mots maximum, un personnage expressif en grand, couleurs vives.
- Chaque vidéo est ajoutée à sa playlist (voir `topics.json` → `playlists`), les Shorts à la playlist Shorts **et** à la playlist du thème.

### 5. Mesurer et ajuster (tâche du dimanche)
Chaque dimanche, une tâche lit les statistiques YouTube de la semaine (vues, heures, abonnés, durée moyenne de
visionnage par vidéo), note ce qui marche dans la section « Ce qu'on a appris » ci-dessous, remonte dans
`topics.json` les sujets et formats proches de ceux qui marchent le mieux, et envoie un rapport au propriétaire
avec la progression vers les seuils.

### 6. Le jour où les seuils sont atteints (action du propriétaire)
Le rapport du dimanche le signalera. Le propriétaire devra alors, dans YouTube Studio → « Gagner de l'argent » :
activer la validation en deux étapes du compte Google, créer ou relier un compte AdSense, accepter les conditions
et soumettre la chaîne. YouTube examine ensuite la chaîne (environ un mois).

## Ce qu'on a appris (mis à jour chaque dimanche)

- 26/11/2026 : lancement. 1 vidéo (savane, 3 min 22) et 1 Short (girafe) publiés.
