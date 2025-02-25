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
- `abonnement` : Indique si l'utilisateur est abonné ou non.
- `For_All_Ages` : Contenu destiné aux familles et aux jeunes enfants.
- `Educational_Informational` : Somme des genres éducatifs et informatifs.
- `Fiction_Entertainment` : Somme des genres de fiction et divertissement.
- `Talk_Show_Reality` : Somme des émissions de talk-show et téléréalité.
- `Adventure_Youth` : Somme des contenus axés sur l’aventure et la jeunesse.
- `pct_not_logged_in` : % de sessions où l’utilisateur n'était pas connecté.
- `pct_gratuit` : % de contenus gratuits regardés.
- `pct_enchainement` : % de vidéos auto-lancées.
- `pct_reprise` : % de vidéos reprises.
- `pct_actif` : % de vidéos lancées manuellement.
- `pct_progress_75` : % de vidéos où l’utilisateur a atteint 75 % du contenu.
- `avg_videoinitiate` : Nombre moyen de vidéos initiées par utilisateur.
- `Ados, Pour la famille, Pour les petits, Pour les plus grands`: Pourcentage de visionnages par cible d’audience.

### Variables descriptives (profilage)
Utilisées pour **décrire les segments** mais **non incluses dans le clustering**.  

### Variables de base (segmentation)
Utilisées pour **différencier les utilisateurs** et créer les segments :  
- `num_devices` : Nombre d’appareils utilisés  
- `unique_programs` : Diversité des contenus regardés  
- `total_watch_time` / `avg_watch_time` : Temps total et moyen de visionnage  
- `subscription_duration` : Durée de l’abonnement  

Le jeu de données final **`df_segmented.csv`** est sauvegardé et prêt pour la segmentation.

# Approche de Segmentation des Utilisateurs

`Segmentation.py` & `Segmentation.R`: Ces scripts implémentent la segmentation des utilisateurs en deux étapes : une **pré-segmentation** basée sur des critères observables, suivie d’un **clustering post hoc** pour affiner les groupes. L’approche est réalisée à la fois en **Python** et en **R** pour une meilleure validation des résultats.

## Pré-segmentation (Segmentation A Priori)
Avant d’appliquer des méthodes de clustering, nous divisons les utilisateurs en deux groupes selon leur **historique d’abonnement** :

1. **Ex-abonnés (`abonnement = 1`)**  
   - Utilisateurs ayant déjà souscrit un abonnement mais qui l’ont annulé.  
   - **Objectif** : Analyser les comportements menant à l’annulation et explorer des stratégies de réengagement.

2. **Utilisateurs gratuits (`abonnement = 0`)**  
   - Utilisateurs qui n'ont jamais été abonnés et ont uniquement consommé du contenu gratuit.  
   - **Objectif** : Identifier les leviers qui pourraient les inciter à souscrire un abonnement.

⚠️ Cette distinction est essentielle car **les stratégies marketing** pour convertir un ancien abonné et un utilisateur gratuit sont différentes.

## Segmentation Post Hoc (Clustering)
Après la pré-segmentation, un **clustering séparé** est appliqué pour chaque groupe afin d'identifier des sous-profils comportementaux.

### **1. Clustering sur les ex-abonnés (`abonnement = 1`)**
   - Détection des motifs de consommation précédant une annulation.
   - Identification des profils d’utilisateurs les plus susceptibles de se réabonner.

### **2. Clustering sur les utilisateurs gratuits (`abonnement = 0`)**
   - Analyse des habitudes de visionnage sans abonnement.
   - Identification des **facteurs de conversion potentiels**.

## Méthodes de Clustering

Nous appliquons trois méthodes de clustering pour comparer les performances et obtenir des résultats robustes :

### **Clustering Hiérarchique (Dendrogramme)**
   - Permet une structure arborescente des clusters.
   - **Avantages** : Interprétable, ne nécessite pas de définir un nombre de clusters (`K`) à l’avance.
   - **Inconvénients** : Lenteur sur les grands jeux de données.

### **K-Means Clustering**
   - Regroupe les données en **K clusters** en minimisant la variance intra-cluster.
   - **Avantages** : Rapide, efficace et évolutif.
   - **Inconvénients** : Sensible aux outliers, nécessite de fixer `K` à l’avance.

### **GMM (Gaussian Mixture Model)**
   - Modèle probabiliste permettant des clusters **non rigides** (un utilisateur peut appartenir partiellement à plusieurs groupes).
   - **Avantages** : Détecte des formes complexes et des distributions chevauchantes.
   - **Inconvénients** : Plus lent et moins interprétable que K-Means.

## Évaluation du Clustering

Pour évaluer la qualité des clusters obtenus, nous utilisons plusieurs métriques :

- **Rand Index (RI)** : Compare la segmentation obtenue avec une classification de référence. Plus il est proche de 1, plus le clustering est précis.
- **Silhouette Score** : Évalue la qualité de séparation des clusters. Une valeur proche de 1 indique des clusters bien définis.
- **BIC (Bayesian Information Criterion)** : Permet d’optimiser le nombre de clusters pour les modèles GMM.

Les résultats finaux sont sauvegardés et comparés dans **`df_clusters.csv`**.




