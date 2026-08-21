# 📘 Configuration Multi-Pages pour Nyavodroid

## Vue d'ensemble

Ce système permet de publier automatiquement sur **plusieurs pages Facebook** simultanément, chacune avec sa propre marque (Nyavo Tech, Vis Motivation, etc.).

## Fichiers créés

1. **`pages_config.yaml`** - Configuration des pages
2. **`post_multi_pages.py`** - Script de publication multi-pages
3. **`post_content.py`** - Modifié pour exporter `publier_contenu()`

## Comment configurer

### Étape 1 : Obtenir les tokens Facebook

Pour chaque page :

1. Va sur [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer)
2. Sélectionne ta Page dans le menu "Page Access Token"
3. Demande les permissions : `publish_pages`, `manage_pages`
4. Copie le token généré

### Étape 2 : Configurer pages_config.yaml

Ouvre `pages_config.yaml` et remplace les variables :

```yaml
pages:
  # Page NYAVO TECH
  - id: "123456789012345"              # ID de ta page Nyavo
    token: "EAABsbCS1iHgBO7ZCxqQZBZAz..."  # Token Nyavo
    brand: "nyavo"
    active: true

  # Page VIS MOTIVATION
  - id: "987654321098765"              # ID de ta page Vis
    token: "EAABsbCS1iHgBO7ZC..."      # Token Vis
    brand: "vis"
    active: true
```

**OU** utilise des variables d'environnement (recommandé pour la sécurité) :

```yaml
pages:
  - id: "${FB_PAGE_ID_NYAVO}"
    token: "${FB_PAGE_ACCESS_TOKEN_NYAVO}"
    brand: "nyavo"
    active: true

  - id: "${FB_PAGE_ID_VIS}"
    token: "${FB_PAGE_ACCESS_TOKEN_VIS}"
    brand: "vis"
    active: true
```

Puis dans ton `.env` ou shell :

```bash
export FB_PAGE_ID_NYAVO="123456789012345"
export FB_PAGE_ACCESS_TOKEN_NYAVO="EAABsbCS1iHgBO7ZCxqQZBZAz..."
export FB_PAGE_ID_VIS="987654321098765"
export FB_PAGE_ACCESS_TOKEN_VIS="EAABsbCS1iHgBO7ZC..."
export GEMINI_API_KEY_CONTENT="ta-cle-gemini"
```

### Étape 3 : Tester

```bash
# Publier sur toutes les pages actives
python post_multi_pages.py

# Publier uniquement sur Nyavo
python post_multi_pages.py --brand nyavo

# Forcer un format spécifique
python post_multi_pages.py --force-format image_texte

# Combiner les options
python post_multi_pages.py --brand vis --force-format texte_seul
```

## Comment ça marche

1. Le script lit `pages_config.yaml` et filtre les pages actives
2. Pour chaque page :
   - Il définit temporairement les variables d'environnement (ID, token, brand)
   - Il recharge le module `post_content.py` avec ces nouvelles variables
   - Il appelle `publier_contenu()` qui génère et publie le contenu
   - Il restaure les variables d'origine
3. Un résumé final affiche les succès/échecs

## Ajouter une nouvelle page

Simple ! Ajoute une entrée dans `pages_config.yaml` :

```yaml
  - id: "111222333444555"
    token: "EAABsbCS1iHgBO7ZC..."
    brand: "nyavo"  # ou "vis" ou une nouvelle marque
    active: true
```

Si c'est une nouvelle marque, crée le fichier `themes/<marque>.yaml` sur le modèle de `nyavo.yaml` ou `vis.yaml`.

## Architecture technique

```
post_multi_pages.py
│
├─ Charger pages_config.yaml
│
└─ Pour chaque page active :
   ├─ Définir ENV : FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN, BRAND
   ├─ Reload post_content.py (prend les nouvelles variables)
   ├─ Appeler pc.publier_contenu()
   │  ├─ Choisir pilier et format
   │  ├─ Générer contenu (texte, image, reel)
   │  └─ Publier sur Facebook via Graph API
   └─ Restaurer ENV
```

## Dépannage

### "ID ou Token manquant"
- Vérifie que les variables d'environnement sont définies
- Ou remplace directement dans `pages_config.yaml`

### "Secret manquant : GEMINI_API_KEY_CONTENT"
- Exporte ta clé Gemini : `export GEMINI_API_KEY_CONTENT="ta-cle"`

### Erreur de permission Facebook
- Vérifie que le token a les permissions `publish_pages` et `manage_pages`
- Les tokens expirent → régénère-les régulièrement

### Contenu non adapté à la marque
- Vérifie que `brand` correspond à un fichier `themes/<brand>.yaml`
- Chaque marque a son propre style, piliers et sujets

## Limitations actuelles

- Les pages sont traitées séquentiellement (pas en parallèle)
- Si une page échoue, les autres continuent
- Pas de retry automatique en cas d'échec API (à venir)

## Améliorations futures possibles

- [ ] Retry logic avec Celery/Redis
- [ ] Publication en parallèle (threading)
- [ ] Tracking UTM pour analytics
- [ ] Dashboard de performance par page
- [ ] A/B testing automatique
- [ ] Détection de trends par marque
