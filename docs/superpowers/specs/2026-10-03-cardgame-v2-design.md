# CardGame V2 — conception proposée

## Objectif et périmètre validés

Faire évoluer « Rouge gagne, noir perd » en un jeu professionnel pour le portfolio de Denos Kume, disponible comme application Python/Pygame et comme jeu web accessible par lien. Conserver un code lisible et explicable en entretien. L'utilisateur a validé une interface premium, trois difficultés, des commandes souris/clavier/tactiles, des réglages audio, une aide intégrée, des statistiques et une livraison documentée.

Ce document précise cette direction pour revue avant le plan d'implémentation. Il ne décrit pas une V2 déjà réalisée.

## État réel du dépôt

Référence examinée : `b60eec7` sur `main`.

- `src/main.py` possède déjà une boucle asynchrone compatible navigateur.
- Pygbag et GitHub Pages sont configurés dans `scripts/build_web.sh` et `.github/workflows/deploy-web.yml`.
- Historique navigateur, profils persistants, saisie native et difficulté adaptative sont déjà présents.
- Les extensions utilisent plusieurs fonctions `install()` qui remplacent des méthodes à l'exécution ; leur ordre influence le comportement.
- Le README omet ces évolutions et affirme à tort l'absence de tests.
- `Bet.is_valid()` vérifie la mise de base mais pas le montant multiplié. Le règlement plafonne ensuite silencieusement la mise au solde.
- Le bilan de fin de partie compte deux fois la mise gagnante, alors que `User.apply_win()` ajoute une seule mise comme bénéfice net.
- Le rendu recrée des polices et redimensionne des images à chaque frame. Il modifie aussi la géométrie des cartes et peut interrompre un échange lors d'un redimensionnement.

Ces observations sont issues de la lecture du code ; la qualité actuelle de la version déployée n'a pas encore été vérifiée par une partie dans le navigateur.

## Architecture retenue

Conserver Python/Pygame et la chaîne Pygbag existante pour partager règles et rendu entre desktop et web. Une réécriture JavaScript créerait deux moteurs à maintenir ; elle n'est pas retenue. Un serveur Python distant ajouterait un hébergement et des échanges réseau inutiles pour ce jeu local.

La documentation officielle Pygbag confirme le modèle de boucle asynchrone déjà employé. La validation d'un build V2 et d'une partie réelle dans le navigateur restera obligatoire : la présence du code compatible ne prouve pas à elle seule son bon fonctionnement.

Responsabilités cibles :

| Élément | Responsabilité |
| --- | --- |
| `main.py` | initialisation, boucle asynchrone, événements plateforme, fermeture |
| `game.py` | états, progression temporelle, identité des cartes, règlement unique |
| `user.py`, `bet.py` | profil actif, solde, validation des mises |
| `settings.py` | difficultés et préférences audio |
| `layout.py` | géométrie commune au dessin et aux zones cliquables |
| `theme.py`, `dashboard.py` | ressources mises en cache, composants visuels, écrans |
| `storage.py` | lecture validée et sauvegarde desktop/navigateur |
| `menu_input.py` | saisie native navigateur et saisie desktop |

Intégrer progressivement les comportements des modules d'extension dans ces responsabilités explicites, avec tests de non-régression avant de supprimer un ancien module. Conserver la saisie navigateur existante jusqu'à validation de son remplacement éventuel.

## Expérience visuelle et parcours

Table anthracite, surfaces légèrement contrastées, accent rouge profond, texte ivoire, espacement régulier. Conserver le titre et les crédits des deux participants. Les cartes doivent rester reconnaissables, avec un symbole et un libellé au dévoilement pour ne pas dépendre seulement de la couleur.

Parcours : accueil avec Jouer/Aide/Réglages et historique ; profil avec pseudonyme et avatar ; préparation avec solde, mise, multiplicateur et difficulté ; observation ; mélange ; choix ; résultat ; manche suivante ou bilan de session.

Afficher la mise totale et son effet avant de lancer. Sur le plateau, distinguer clairement phase, temps restant et action attendue. Les résultats montrent la bonne carte, la carte sélectionnée et le bénéfice ou la perte réellement appliqué.

Trois cartes restent visibles côte à côte sur mobile. Les panneaux secondaires se réorganisent verticalement, les textes se replient et les boutons ont une zone tactile minimale de 44 px. Vérifier les formats 360×640, 390×844, 844×390, 960×630 et 1440×900.

Commandes : clic/toucher ; Tab et Entrée pour les boutons ; 1/2/3 pour choisir la position gauche/centre/droite ; Espace pour suspendre uniquement la partie active ; Échap pour fermer une aide ou un réglage. La saisie du nom conserve les espaces et le clavier mobile natif. Un bouton pause reste accessible au toucher.

## Règles et difficulté

- Trois cartes, une seule rouge ; son identité reste attachée au même objet pendant les échanges.
- Crédits fictifs : bonus initial de 30 accordé une fois par profil, solde persistant, minimum 10, maximum de base 1000, pas de 5, multiplicateurs 1/2/3. Ces valeurs suivent le code actuel plutôt que le README obsolète.
- La mise totale est `mise × multiplicateur`. Refuser une manche si elle dépasse le solde ; ne plus la plafonner silencieusement lors du résultat.
- Figer la mise au début de la manche. Une victoire ajoute cette mise, une défaite ou expiration la soustrait. Un résultat ne peut être appliqué qu'une fois.
- Un clic reçu après l'échéance ne gagne pas une course contre la mise à jour : le contrôleur vérifie aussi l'heure dans le traitement de sélection.
- Pause et perte de focus suspendent les délais et l'animation. Le temps actif de la manche exclut la pause.
- Le redimensionnement conserve l'identité, les positions logiques et l'avancement du mélange.
- Un profil sous le minimum voit un bilan explicite et peut revenir au choix de profil. Aucun réapprovisionnement automatique n'est ajouté.

Les trois difficultés gardent les phases de 10 secondes et modifient seulement le mélange : Facile 420 ms d'intervalle / 420 ms d'échange ; Normal utilise l'adaptation existante de 300 à 170 ms selon les victoires consécutives ; Expert 150/150 ms. Normal est sélectionné par défaut. La difficulté est figée pour chaque manche et les séries sont réinitialisées lors d'un changement de profil ou de difficulté.

## Historique, statistiques et erreurs

Conserver au maximum 200 manches avec profil, difficulté, mise totale, résultat, motif d'expiration éventuel, solde et durée active. Calculer le bénéfice net avec `+mise` ou `−mise`, et le taux de réussite sur le nombre de manches terminées ; zéro manche affiche une valeur neutre.

Préserver les anciennes clés de stockage et importer les anciennes entrées valides sans inventer leur difficulté. Valider les champs et ignorer les entrées corrompues individuellement. Sur desktop, écrire via fichier temporaire et remplacement atomique ; dans le navigateur, utiliser localStorage. Les données restent locales à l'appareil et ne sont pas synchronisées entre web et desktop.

Une erreur de sauvegarde laisse la partie jouable et affiche un message discret indiquant que les résultats ne seront pas conservés. L'absence d'audio ne bloque jamais le jeu. Les réglages comprennent activation du son et volume, sauvegardés localement. Le navigateur initialise le son après une interaction utilisateur.

## Fluidité et diffusion

Mettre en cache polices, images redimensionnées et surfaces statiques par taille. Le rendu ne modifie plus l'état de jeu. Animer sans attente bloquante, avec trajectoires d'échange séparées pour garder les cartes suivables.

Conserver la construction web et GitHub Pages du dépôt. Le chargement doit présenter un état visible et une erreur compréhensible si le démarrage échoue. La version desktop reste lançable avec une commande documentée. Les exécutables Windows/macOS, comptes en ligne, multijoueur et classements distants sont hors périmètre de cette V2.

## Critères de livraison

1. Tests significatifs des mises multipliées, victoire/défaite/expiration, règlement unique, pause, redimensionnement et statistiques.
2. Tests de migration et de stockage indisponible, conservant le bonus unique par profil.
3. Régression des fonctions déjà présentes, notamment saisie native et difficultés adaptatives.
4. Inspection visuelle de chaque écran et parcours complet sur desktop et navigateur, aux dimensions prévues ; aucun bouton tronqué ou zone cliquable désalignée.
5. Vérification du toucher et du clavier mobile dans la mesure permise par les outils disponibles ; toute limite de validation est signalée.
6. Build web et CI réussis ; essai de la version publiée avant annonce de disponibilité.
7. README à jour avec règles exactes, commandes, installation, lien jouable, architecture, captures et limites connues. Ne pas présenter une compatibilité plateforme non testée comme acquise.

## Références techniques

- https://github.com/pygame-web/pygbag
- https://pygame-web.github.io/wiki/pygbag/
- https://pygame-web.github.io/wiki/pygbag-code/
