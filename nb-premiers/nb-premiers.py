#!/usr/bin/env python3
"""
Script Python pour afficher les nombres premiers jusqu'à 100.
Compatible macOS et Python 3.x (et versions récentes).
"""

def trouver_nombres_premiers(limite):
    # Initialisation d'une liste de booléens pour le crible
    premiers = [True] * (limite + 1)
    premiers[0] = premiers[1] = False  # 0 et 1 ne sont pas premiers

    for p in range(2, int(limite**0.5) + 1):
        if premiers[p]:
            # Marquer les multiples de p comme non premiers
            for i in range(p * p, limite + 1, p):
                premiers[i] = False

    # Retourner la liste des nombres restés à True
    return [p for p in range(limite + 1) if premiers[p]]

if __name__ == "__main__":
    limite = 100
    liste_premiers = trouver_nombres_premiers(limite)
    
    print(f"Nombres premiers jusqu'à {limite} :")
    print(liste_premiers)