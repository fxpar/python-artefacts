import sys
import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter

def process_pdf(pdf_path):
    path = Path(pdf_path)
    if not path.is_file() or path.suffix.lower() != '.pdf':
        print(f"Erreur : '{pdf_path}' n'est pas un fichier PDF valide.")
        return

    # Création du nom de dossier (50 premiers caractères du nom du fichier sans extension)
    folder_name = path.stem[:50].strip()
    output_dir = path.parent / folder_name

    reader = PdfReader(path)
    attachments = reader.attachments

    if not attachments:
        print("Aucune pièce jointe trouvée dans ce PDF.")
    else:
        # Création du dossier d'extraction si nécessaire
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Extraction vers : {output_dir}\n")

        for name, content_list in attachments.items():
            for content in content_list:
                file_path = output_dir / name
                with open(file_path, "wb") as f:
                    f.write(content)
                print(f" - Extrait : {name}")

    # Demande pour la version sans pièces jointes
    print("\n" + "-" * 40)
    choice = input("Voulez-vous créer une version du PDF sans les pièces jointes ? (o/N) : ")
    
    if choice.lower().strip() in ['o', 'oui']:
        writer = PdfWriter()
        writer.append(reader)
        
        # Supprime l'entrée globale des pièces jointes si elle existe
        if "/EmbeddedFiles" in writer._root_object.get("/Names", {}):
            del writer._root_object["/Names"]["/EmbeddedFiles"]

        no_attach_path = path.parent / f"{path.stem}_no_attach.pdf"
        with open(no_attach_path, "wb") as f:
            writer.write(f)
        
        print(f"Nouveau PDF créé : {no_attach_path.name}")

    input("\nAppuyez sur Entrée pour fermer cette fenêtre...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_pdf(sys.argv[1])
    else:
        print("Veuillez glisser-déposer un fichier PDF sur le script.")
        input("\nAppuyez sur Entrée pour fermer...")