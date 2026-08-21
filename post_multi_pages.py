#!/usr/bin/env python3
"""
Nyavodroid — Publication MULTI-PAGES Facebook
Publie automatiquement sur toutes les pages configurées dans pages_config.yaml

Usage:
  python post_multi_pages.py [--force-format image_texte|texte_seul] [--brand nyavo|vis]

Variables d'environnement requises (dans .env ou export):
  - FB_PAGE_ID_NYAVO, FB_PAGE_ACCESS_TOKEN_NYAVO
  - FB_PAGE_ID_VIS, FB_PAGE_ACCESS_TOKEN_VIS
  - GEMINI_API_KEY_CONTENT
  - BRAND (optionnel, sinon utilise celui défini dans le config de chaque page)
"""

import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any

# Charger la configuration multi-pages
def charger_pages_config() -> List[Dict[str, Any]]:
    """Charge la liste des pages depuis pages_config.yaml"""
    config_path = Path(__file__).parent / "pages_config.yaml"
    
    if not config_path.exists():
        print(f"❌ Fichier de configuration introuvable : {config_path}")
        print("💡 Créez pages_config.yaml avec la structure indiquée dans l'exemple.")
        sys.exit(1)
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    pages = config.get("pages", [])
    if not pages:
        print("⚠️ Aucune page configurée dans pages_config.yaml")
        sys.exit(1)
    
    # Filtrer uniquement les pages actives
    pages_actives = [p for p in pages if p.get("active", True)]
    
    print(f"📄 {len(pages_actives)} page(s) active(s) trouvée(s)")
    return pages_actives


def publier_sur_page(page_config: Dict[str, Any], force_format: str = None) -> bool:
    """
    Publie un contenu sur une page Facebook spécifique
    
    Args:
        page_config: Dict avec id, token, brand
        force_format: Format imposé (optionnel)
    
    Returns:
        True si succès, False sinon
    """
    page_id = page_config["id"]
    access_token = page_config["token"]
    brand = page_config.get("brand", "nyavo")
    
    # Remplacer les variables d'environnement si nécessaire
    if page_id.startswith("${") and page_id.endswith("}"):
        env_var = page_id[2:-1]
        page_id = os.environ.get(env_var, "")
    
    if access_token.startswith("${") and access_token.endswith("}"):
        env_var = access_token[2:-1]
        access_token = os.environ.get(env_var, "")
    
    if not page_id or not access_token:
        print(f"  ⚠️ Page {page_config.get('id', 'inconnue')} : ID ou Token manquant")
        return False
    
    print(f"\n{'='*60}")
    print(f"📘 Publication sur la page : {page_id}")
    print(f"   Marque : {brand}")
    print(f"{'='*60}")
    
    # Sauvegarder les variables actuelles
    old_page_id = os.environ.get("FB_PAGE_ID", "")
    old_token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
    old_brand = os.environ.get("BRAND", "")
    
    try:
        # Définir les variables pour cette page
        os.environ["FB_PAGE_ID"] = page_id
        os.environ["FB_PAGE_ACCESS_TOKEN"] = access_token
        os.environ["BRAND"] = brand
        
        # Forcer le format si demandé
        if force_format:
            os.environ["FORCE_FORMAT"] = force_format
        
        # Importer et appeler la fonction de publication
        # On recharge le module à chaque fois pour prendre en compte les nouvelles variables
        import importlib
        import post_content as pc
        importlib.reload(pc)  # Recharge avec les nouvelles variables ENV
        
        # Appeler la fonction exportée
        pc.publier_contenu(force_format)
        
        print(f"  ✅ Publication réussie sur {page_id}")
        return True
        
    except Exception as e:
        print(f"  ❌ Échec de publication sur {page_id}: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Restaurer les variables d'origine
        if old_page_id:
            os.environ["FB_PAGE_ID"] = old_page_id
        elif "FB_PAGE_ID" in os.environ:
            del os.environ["FB_PAGE_ID"]
            
        if old_token:
            os.environ["FB_PAGE_ACCESS_TOKEN"] = old_token
        elif "FB_PAGE_ACCESS_TOKEN" in os.environ:
            del os.environ["FB_PAGE_ACCESS_TOKEN"]
            
        if old_brand:
            os.environ["BRAND"] = old_brand
        elif "BRAND" in os.environ:
            del os.environ["BRAND"]
            
        if force_format and "FORCE_FORMAT" in os.environ:
            del os.environ["FORCE_FORMAT"]


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Publication multi-pages Facebook pour Nyavodroid"
    )
    parser.add_argument(
        "--force-format",
        choices=["image_texte", "texte_seul", "reel"],
        help="Force un format de contenu spécifique"
    )
    parser.add_argument(
        "--brand",
        choices=["nyavo", "vis"],
        help="Filtre par marque (optionnel)"
    )
    
    args = parser.parse_args()
    
    # Charger la configuration
    pages = charger_pages_config()
    
    # Filtrer par marque si demandé
    if args.brand:
        pages = [p for p in pages if p.get("brand") == args.brand]
        print(f"🎯 Filtrage par marque : {args.brand} ({len(pages)} page(s))")
    
    if not pages:
        print("❌ Aucune page à traiter après filtrage")
        sys.exit(1)
    
    # Publier sur chaque page
    resultats = {}
    for page in pages:
        success = publier_sur_page(page, args.force_format)
        page_name = f"{page.get('brand', 'inconnue')}_{page.get('id', 'unknown')[-6:]}"
        resultats[page_name] = success
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES PUBLICATIONS")
    print(f"{'='*60}")
    succes = sum(1 for v in resultats.values() if v)
    echecs = len(resultats) - succes
    
    for page_name, success in resultats.items():
        status = "✅" if success else "❌"
        print(f"  {status} {page_name}")
    
    print(f"\nTotal: {succes}/{len(resultats)} réussites")
    
    if echecs > 0:
        print(f"⚠️ {echecs} échec(s) détecté(s)")
        sys.exit(1)
    else:
        print("🎉 Toutes les publications ont réussi !")
        sys.exit(0)


if __name__ == "__main__":
    main()
