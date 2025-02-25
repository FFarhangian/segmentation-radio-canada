# segmentation-radio-canada

Ce projet analyse et segmente les utilisateurs de [ICI TOU.TV](https://ici.tou.tv/) pour l'optimisation du funnel de conversion en fonction de leur comportement de visionnage et d’abonnement afin d’optimiser le tunnel de conversion, améliorer l’expérience utilisateur et affiner les stratégies d’engagement. L'approche repose sur l'exploration des données (`visionnements.csv`, `abo.csv`, `cms.csv`), la détection de tendances, et la création de segments pour mieux cibler les audiences et maximiser la rétention.

![Plateforme ICI TOU.TV](ICITUOTV.png)




# Prétraitement des Données

`Data_Preprocessing.py`: Ce script est responsable du **chargement, de l’exploration, de la visualisation et du prétraitement** de trois ensembles de données avant de les fusionner en un **seul dataset** pour l'étape suivante. Les données **ne sont pas encore agrégées** et restent sous leur forme brute, en préparation pour des analyses ultérieures, telles que le clustering.


## Étapes Clés

### 1. Chargement & Inspection des Données
- Chargement des datasets : **`abo.csv`**, **`visionnements.csv`**, **`cms.csv`**.
- Affichage des **statistiques de base** et **exploration initiale**.
- Vérification des **valeurs manquantes**, **doublons** et **valeurs aberrantes**.

### 2. Analyse Exploratoire des Données (EDA)
- **Analyse individuelle des datasets** : Visualisation des caractéristiques clés **séparément** avant fusion.
- **Analyse de la longitudinalité & de la durée de vie** : Évaluation de la possibilité de suivre les utilisateurs au fil du temps et analyse des durées d’abonnement.

### 3. Ingénierie des Caractéristiques (Feature Engineering)
- Extraction de nouvelles caractéristiques pertinentes :
  - **Tendances d’abonnement** (mensuelles, hebdomadaires, annuelles).
  - **Mesures d’engagement des utilisateurs** (temps de visionnage, comportements de session, pourcentages d'activité).
  - **Préférences de contenu** (distribution par thème et audience).
- Création de nouvelles variables :
  - `subscription_duration`
  - `engagement_percentages`
  - `content_preferences`

### 4. Fusion des Données
- Fusion des trois ensembles de données à l'aide **d'identifiants communs**, tout en conservant les nouvelles caractéristiques extraites.
- Traitement des **valeurs manquantes** et garantie de la **cohérence des données**.

### 5. Résultat Final
- Sauvegarde du **dataset fusionné** sous le nom **`df.csv`**, intégrant les nouvelles caractéristiques pour les analyses futures.
Ce traitement garantit que les données sont **structurées, exploitables et prêtes** pour les prochaines étapes d’analyse et de modélisation.


# Segmentation des Variables

`Segmentation_variables.py`: Ce script affine l’ensemble de données issu de l’étape précédente en conservant uniquement les variables agrégées et pertinentes pour la segmentation. Il comprend une **exploration approfondie des données, une réduction de dimension, une sélection des variables et une détection des valeurs aberrantes** afin d’assurer des données propres et significatives.

## Étapes clés

1. **Chargement des données** : Importation du jeu de données prétraité.  
2. **Exploration des variables agrégées** : Analyse des variables clés pour la segmentation.  
3. **Réduction de dimension** : Suppression des variables inutiles et fusion de certaines catégories.  
4. **Vérification des valeurs aberrantes** : Détection et traitement des outliers pour garantir la qualité des segments.  

## Variables de segmentation

Pour créer des segments d’utilisateurs pertinents, nous distinguons deux types de variables :  

### Variables descriptives (profilage)
Utilisées pour **décrire les segments** mais **non incluses dans le clustering**.  

### Variables de base (segmentation)
Utilisées pour **différencier les utilisateurs** et créer les segments :  
- `num_devices` : Nombre d’appareils utilisés  
- `unique_programs` : Diversité des contenus regardés  
- `total_watch_time` / `avg_watch_time` : Temps total et moyen de visionnage  
- `subscription_duration` : Durée de l’abonnement  

Ce traitement permet de préparer les données pour la segmentation et l’analyse des utilisateurs.




