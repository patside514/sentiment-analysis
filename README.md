# 🚀 Social Media Sentiment Analysis Tool

Une application SaaS complète en Python pour analyser le sentiment des réseaux sociaux à partir de Twitter, Facebook et Google Reviews.

## 📋 Fonctionnalités

- **Extraction multi-plateformes** : Twitter, Facebook, Google Reviews
- **Analyse de sentiment** : TextBlob + Transformers (modèles multilingues)
- **Extraction de mots-clés** : TF-IDF, fréquence, TextRank, combinaison
- **Visualisations** : Graphiques matplotlib, nuages de mots, tableaux de bord
- **Rapports complets** : HTML, CSV, JSON
- **Interface CLI** : Facile à utiliser avec options détaillées
- **Support multilingue** : Français et Anglais avec détection automatique

## 🛠️ Installation

### Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/social-media-sentiment-analyzer.git
cd social-media-sentiment-analyzer

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Télécharger les données NLTK
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Installer spaCy models (optionnel mais recommandé)
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

### Configuration des API

1. **Copier le fichier d'exemple** :
```bash
cp .env.example .env
```

2. **Configurer les clés API** :
   - **Twitter** : Créez une application sur https://developer.twitter.com/
   - **Facebook** : Obtenez un token d'accès sur https://developers.facebook.com/
   - **Google** : Créez une clé API sur https://console.cloud.google.com/

3. **Éditer le fichier `.env`** avec vos clés API

## 🚀 Utilisation

### Commande de base

```bash
python app.py --service "Uber" --source "twitter" --days 30
```

### Options avancées

```bash
python app.py --service "Netflix" \
              --source "facebook" \
              --days 15 \
              --max-posts 200 \
              --format html \
              --language fr \
              --sentiment-model transformers \
              --keyword-method combined
```

### Paramètres disponibles

| Paramètre | Description | Défaut |
|-----------|-------------|---------|
| `--service, -s` | Nom du service/marque à analyser (obligatoire) | - |
| `--source, -src` | Source (twitter/facebook/google_reviews) | twitter |
| `--days, -d` | Nombre de jours à analyser (1-60) | 30 |
| `--max-posts, -m` | Nombre maximum de posts (50-500) | 500 |
| `--output-dir, -o` | Répertoire de sortie | auto |
| `--format, -f` | Format (csv/json/html/all) | all |
| `--language, -l` | Langue (auto/fr/en) | auto |
| `--sentiment-model, -sm` | Modèle de sentiment | auto |
| `--keyword-method, -km` | Méthode d'extraction | combined |
| `--verbose, -v` | Mode verbeux | False |
| `--quiet, -q` | Mode silencieux | False |
| `--dry-run` | Simulation sans extraction | False |

## 📊 Exemples d'utilisation

### Analyse de sentiment pour Uber sur Twitter

```bash
python app.py --service "Uber" --source "twitter" --days 30 --max-posts 500
```

### Analyse détaillée avec rapport HTML

```bash
python app.py --service "Airbnb" --source "google_reviews" --days 30 --format html --verbose
```

### Analyse multi-sources

```bash
# Twitter
python app.py -s "Netflix" -src "twitter" -d 30 -m 300

# Facebook
python app.py -s "Netflix" -src "facebook" -d 30 -m 300

# Google Reviews
python app.py -s "Netflix" -src "google_reviews" -d 30 -m 300
```

## 📈 Sorties générées

L'application génère plusieurs types de fichiers :

### Fichiers de données
- `raw_data_[timestamp].csv` : Données brutes extraites
- `processed_data_[timestamp].csv` : Données nettoyées avec sentiment
- `keywords_[timestamp].csv` : Mots-clés extraits

### Visualisations
- `sentiment_pie_chart.png` : Camembert des sentiments
- `sentiment_bar_chart.png` : Graphique en barres
- `sentiment_trend_chart.png` : Tendances temporelles
- `keyword_frequency_chart.png` : Fréquence des mots-clés
- `keyword_score_chart.png` : Score de pertinence
- `analysis_dashboard.png` : Tableau de bord complet

### Nuages de mots
- `keywords_wordcloud.png` : Nuage de mots général
- `positive_sentiment_wordcloud.png` : Nuage de mots positifs
- `negative_sentiment_wordcloud.png` : Nuage de mots négatifs
- `neutral_sentiment_wordcloud.png` : Nuage de mots neutres

### Rapports
- `report_metadata.json` : Métadonnées de l'analyse
- `sentiment_summary.json` : Résumé des sentiments
- `[service]_[source]_report_[timestamp].html` : Rapport HTML complet

## 🔧 Architecture technique

### Structure du projet

```
social-media-sentiment-analyzer/
├── src/
│   ├── extractors/          # Modules d'extraction
│   │   ├── base_extractor.py
│   │   ├── twitter_extractor.py
│   │   ├── facebook_extractor.py
│   │   └── google_reviews_extractor.py
│   ├── nlp/                 # Traitement NLP
│   │   ├── sentiment_analyzer.py
│   │   ├── keyword_extractor.py
│   │   └── text_preprocessor.py
│   ├── visualization/       # Visualisation
│   │   ├── charts_generator.py
│   │   ├── wordcloud_generator.py
│   │   └── report_generator.py
│   ├── utils/               # Utilitaires
│   │   ├── logger.py
│   │   ├── data_validator.py
│   │   └── file_manager.py
│   ├── config.py            # Configuration
│   ├── main.py              # Orchestration principale
│   └── cli.py               # Interface CLI
├── data/                    # Données temporaires
├── outputs/                 # Résultats
├── requirements.txt         # Dépendances
├── app.py                   # Point d'entrée
└── setup.py                 # Installation
```

### Technologies utilisées

- **Extraction** : Tweepy, Facebook SDK, BeautifulSoup, requests
- **NLP** : NLTK, TextBlob, spaCy, Transformers (Hugging Face)
- **Analyse** : scikit-learn, pandas, numpy
- **Visualisation** : matplotlib, seaborn, wordcloud
- **Interface** : Click, colorama, tqdm
- **Configuration** : python-dotenv

## 🎯 Méthodologie

### Analyse de sentiment

1. **Prétraitement** : Nettoyage, normalisation, détection de langue
2. **Modèles utilisés** :
   - TextBlob (français/anglais)
   - Transformers (RoBERTa multilingue)
3. **Classification** : Positif/Négatif/Neutre avec score de confiance

### Extraction de mots-clés

1. **TF-IDF** : Importance relative dans le corpus
2. **Fréquence** : Occurrences brutes
3. **TextRank** : Algorithme basé sur PageRank
4. **Combinaison** : Moyenne pondérée des méthodes

### Validation des données

- Filtrage par longueur minimale
- Détection et suppression de spam
- Normalisation du texte
- Validation des métadonnées

## ⚠️ Limites et considérations

### API Limits
- **Twitter** : 300 requêtes/15 minutes
- **Facebook** : 200 requêtes/heure
- **Google** : 100 requêtes/jour

### Limitations techniques
- Dépend des API disponibles et de leurs restrictions
- L'analyse de sentiment peut varier selon la qualité du texte
- Les résultats sont indicatifs et nécessitent interprétation humaine

### Considérations éthiques
- Respect des conditions d'utilisation des plateformes
- Anonymisation des données personnelles
- Usage conforme aux réglementations (GDPR, etc.)

## 🔍 Dépannage

### Problèmes courants

**Erreur d'authentification API**
```bash
# Vérifiez vos clés API dans le fichier .env
# Assurez-vous que les clés sont actives et valides
```

**Pas de données extraites**
```bash
# Vérifiez le nom du service (essayez des variantes)
# Réduisez la période ou augmentez max-posts
# Vérifiez les limites d'API
```

**Erreurs de dépendances**
```bash
# Réinstallez les dépendances
pip install -r requirements.txt --upgrade

# Installez les modèles spaCy
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

### Support

Pour les problèmes techniques :
1. Vérifiez les logs dans `outputs/app.log`
2. Activez le mode verbose (`--verbose`)
3. Consultez la documentation des API
4. Ouvrez une issue sur le dépôt GitHub

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commit vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

