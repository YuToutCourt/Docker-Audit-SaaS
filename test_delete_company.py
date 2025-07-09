#!/usr/bin/env python3
"""
Script de test pour vérifier la suppression d'entreprise et de sa CA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import dbo
from entity.company import Company
from entity.ca import Ca
from entity.user import User
from entity.agent import Agent
from entity.report import Report
from icecream import ic

def test_delete_company():
    """Test de suppression d'entreprise avec sa CA"""
    
    print("=== Test de suppression d'entreprise ===")
    
    # 1. Compter les entreprises et CAs avant suppression
    companies_before = Company.get_all_company()
    print(f"Entreprises avant suppression: {len(companies_before)}")
    
    # Récupérer toutes les CAs
    session = dbo()
    cas_before = session.query(Ca).all()
    session.close()
    print(f"CAs avant suppression: {len(cas_before)}")
    
    if not companies_before:
        print("Aucune entreprise à supprimer")
        return
    
    # 2. Sélectionner la première entreprise pour le test
    test_company = companies_before[0]
    print(f"Entreprise à supprimer: {test_company.name} (ID: {test_company.id_company})")
    print(f"CA ID de l'entreprise: {test_company.company_pki_id}")
    
    # 3. Vérifier que la CA existe
    ca = Ca.get_ca_from_id(test_company.company_pki_id)
    if ca:
        print(f"CA trouvée: ID {ca.id_ca}")
    else:
        print("CA non trouvée!")
        return
    
    # 4. Supprimer l'entreprise
    print("\nSuppression de l'entreprise...")
    success = Company.delete_company_by_id(test_company.id_company)
    
    if success:
        print("✅ Entreprise supprimée avec succès")
    else:
        print("❌ Échec de la suppression de l'entreprise")
        return
    
    # 5. Vérifier que l'entreprise a été supprimée
    companies_after = Company.get_all_company()
    print(f"Entreprises après suppression: {len(companies_after)}")
    
    # 6. Vérifier que la CA a été supprimée
    session = dbo()
    cas_after = session.query(Ca).all()
    session.close()
    print(f"CAs après suppression: {len(cas_after)}")
    
    # 7. Vérifier spécifiquement que la CA de l'entreprise a été supprimée
    ca_after = Ca.get_ca_from_id(test_company.company_pki_id)
    if ca_after:
        print("❌ La CA existe encore!")
    else:
        print("✅ La CA a été supprimée avec succès")
    
    print("\n=== Test terminé ===")

if __name__ == "__main__":
    test_delete_company() 