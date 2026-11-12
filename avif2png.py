import os
from PIL import Image

# Installer la dépendance nécessaire :
# pip install pillow-avif-plugin pillow

def convert_avif_to_png():
    # Récupérer tous les fichiers .avif du dossier courant
    avif_files = [f for f in os.listdir('.') if f.lower().endswith('.avif')]
    
    if not avif_files:
        print("❌ Aucun fichier AVIF trouvé dans le dossier courant.")
        return
    
    print(f"📁 {len(avif_files)} fichier(s) AVIF trouvé(s)")
    
    for avif_file in avif_files:
        try:
            # Ouvrir l'image AVIF
            img = Image.open(avif_file)
            
            # Générer le nom du fichier PNG
            png_file = os.path.splitext(avif_file)[0] + '.png'
            
            # Convertir en PNG avec qualité moyenne
            # Pour PNG, on utilise 'optimize=True' pour réduire la taille
            img.save(png_file, 'PNG', optimize=True)
            
            # Afficher la taille de l'image et le nom du fichier
            print(f"✅ {avif_file} → {png_file} ({img.size[0]}x{img.size[1]})")
            
        except Exception as e:
            print(f"❌ Erreur avec {avif_file} : {e}")

if __name__ == "__main__":
    convert_avif_to_png()