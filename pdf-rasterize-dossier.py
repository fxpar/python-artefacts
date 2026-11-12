import os
import shutil
import tempfile
import fitz  # PyMuPDF
import gradio as gr

# ==========================================
# 1. LE MOTEUR : Traitement d'un PDF unique
# ==========================================
def aplatir_calques_conserver_ocr(pdf_entree, pdf_sortie, dpi=150):
    try:
        doc_source = fitz.open(pdf_entree)
        doc_cible = fitz.open()
        
        for num_page in range(len(doc_source)):
            page_origine = doc_source[num_page]
            
            # Dessine la page en image
            pix = page_origine.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
            jpeg_bytes = pix.tobytes("jpeg")
            
            # Nouvelle page vierge de même dimension
            nouvelle_page = doc_cible.new_page(width=page_origine.rect.width, height=page_origine.rect.height)
            nouvelle_page.insert_image(nouvelle_page.rect, stream=jpeg_bytes)
            
            # Ré-insertion du texte invisible
            mots = page_origine.get_text("words")
            for mot in mots:
                x0, y0, x1, y1, texte, _, _, _ = mot
                taille_police = max(5, y1 - y0)
                try:
                    nouvelle_page.insert_text(
                        fitz.Point(x0, y1), 
                        texte, 
                        fontsize=taille_police, 
                        render_mode=3
                    )
                except:
                    pass
                    
        doc_cible.save(pdf_sortie, garbage=4, deflate=True)
        doc_source.close()
        doc_cible.close()
        return True, "OK"
    except Exception as e:
        return False, str(e)

# ==========================================
# 2. L'ORCHESTRATEUR : Logique de traitement par lot
# ==========================================
def executer_traitement_dossier(
    dossier_source, 
    dest_type, 
    nom_sous_dossier, 
    dossier_autre_destination, 
    suffixe_fichier, 
    recursif, 
    dpi
):
    # Sécurité anti-NoneType et nettoyage des guillemets/espaces
    dossier_source = dossier_source.strip().strip('"').strip("'") if dossier_source else ""
    nom_sous_dossier = nom_sous_dossier.strip() if nom_sous_dossier else ""
    dossier_autre_destination = dossier_autre_destination.strip().strip('"').strip("'") if dossier_autre_destination else ""
    suffixe_fichier = suffixe_fichier.strip() if suffixe_fichier else ""

    if not dossier_source or not os.path.exists(dossier_source):
        return "Erreur : Le dossier source spécifié n'existe pas."

    # Détermination du dossier de destination global si "autre dossier"
    if dest_type == "Dans un autre dossier spécifique":
        if not dossier_autre_destination:
            return "Erreur : Veuillez spécifier le chemin du dossier de destination."
        os.makedirs(dossier_autre_destination, exist_ok=True)

    fichiers_traites = 0
    fichiers_erreurs = 0
    historique_logs = []

    # Parcours des fichiers
    for root, dirs, files in os.walk(dossier_source):
        # Si on ne veut pas de récursivité, on vide la liste des dossiers à explorer pour stopper os.walk
        if not recursif:
            dirs.clear()

        for file in files:
            if not file.lower().endswith(".pdf"):
                continue

            chemin_complet_entree = os.path.join(root, file)
            
            # Calcul du chemin de sortie selon les options choisies
            if dest_type == "Dans un sous-dossier (au même endroit)":
                # ex: dossier_source/sous_dossier/fichier.pdf
                dossier_cible_courant = os.path.join(root, nom_sous_dossier)
                os.makedirs(dossier_cible_courant, exist_ok=True)
                
                # Pas besoin de suffixe obligatoire ici car le fichier est dans un dossier séparé
                nom_fichier_sortie = file if not suffixe_fichier else f"{os.path.splitext(file)[0]}{suffixe_fichier}.pdf"
                chemin_complet_sortie = os.path.join(dossier_cible_courant, nom_fichier_sortie)

            elif dest_type == "Dans un autre dossier spécifique":
                # Conserver la hiérarchie si récursif
                if recursif:
                    rel_path = os.path.relpath(root, dossier_source)
                    dossier_cible_courant = os.path.normpath(os.path.join(dossier_autre_destination, rel_path))
                else:
                    dossier_cible_courant = dossier_autre_destination
                
                os.makedirs(dossier_cible_courant, exist_ok=True)
                nom_fichier_sortie = file if not suffixe_fichier else f"{os.path.splitext(file)[0]}{suffixe_fichier}.pdf"
                chemin_complet_sortie = os.path.join(dossier_cible_courant, nom_fichier_sortie)

            else:  # "Au même endroit (avec suffixe)"
                nom_sans_ext = os.path.splitext(file)[0]
                # Sécurité pour éviter une boucle infinie si on relance le script sur un fichier déjà traité
                effective_suffix = suffixe_fichier if suffixe_fichier else "_raster"
                if file.endswith(f"{effective_suffix}.pdf"):
                    continue
                
                nom_fichier_sortie = f"{nom_sans_ext}{effective_suffix}.pdf"
                chemin_complet_sortie = os.path.join(root, nom_fichier_sortie)

            # Traitement effectif du PDF
            success, err_msg = aplatir_calques_conserver_ocr(chemin_complet_entree, chemin_complet_sortie, dpi=int(dpi))
            if success:
                fichiers_traites += 1
                historique_logs.append(f"✓ Traité : {file} -> {os.path.basename(chemin_complet_sortie)}")
            else:
                fichiers_erreurs += 1
                historique_logs.append(f"✗ Échec sur {file} : {err_msg}")

    # Génération du bilan
    bilan = f"Traitement terminé !\n- Fichiers convertis avec succès : {fichiers_traites}\n- Échecs : {fichiers_erreurs}\n\n"
    bilan += "\n".join(historique_logs)
    return bilan


# ==========================================
# 3. L'INTERFACE GRADI0
# ==========================================
with gr.Blocks(title="Aplatisseur de PDF - Batch Mode") as demo:
    gr.Markdown("""
    # 📁 Aplatisseur de PDF - Traitement par Lot
    Cette interface vous permet d'appliquer l'aplatissement de calques (avec conservation de l'OCR) sur des dossiers entiers.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            # 1) Saisie du dossier source
            dossier_input = gr.Textbox(
                label="1. Chemin du dossier source", 
                placeholder="Collez ou glissez le chemin du dossier ici (ex: C:\\Partitions)",
                info="Vous pouvez faire glisser le dossier depuis votre explorateur de fichiers pour copier son chemin."
            )
            
            # 2) Options de destination
            dest_mode = gr.Radio(
                choices=[
                    "Dans un sous-dossier (au même endroit)", 
                    "Dans un autre dossier spécifique", 
                    "Au même endroit (avec suffixe)"
                ],
                value="Dans un sous-dossier (au même endroit)",
                label="2. Où enregistrer les fichiers traités ?"
            )
            
            # Options dynamiques conditionnées par le choix ci-dessus
            with gr.Group():
                sous_dossier_input = gr.Textbox(
                    label="Nom du sous-dossier à créer", 
                    value="Aplatit",
                    visible=True
                )
                autre_dossier_input = gr.Textbox(
                    label="Chemin de l'autre dossier de destination", 
                    placeholder="ex: D:\\Partitions_Optimisees",
                    visible=False
                )
                suffixe_input = gr.Textbox(
                    label="3. Suffixe à ajouter au nom du fichier", 
                    value="_raster",
                    info="Sera ajouté juste avant l'extension .pdf (laissé vide si non désiré dans les sous-dossiers)."
                )

            # 4) Option de récursivité
            recursive_checkbox = gr.Checkbox(
                label="4. Parcourir les sous-dossiers récursivement", 
                value=False,
                info="Si coché, la structure des dossiers sera recréée dans la destination."
            )
            
            # Paramètre DPI
            dpi_slider = gr.Slider(
                minimum=72, maximum=300, value=150, step=10, 
                label="Qualité d'image (DPI)", 
                info="150 est idéal pour l'affichage sur tablette."
            )
            
            btn_run = gr.Button("Lancer le traitement par lot", variant="primary")
            
        with gr.Column(scale=1):
            # Console de log pour suivre l'avancée
            output_console = gr.Textbox(
                label="Console et statut du traitement", 
                interactive=False, 
                lines=20
            )

    # --- Logique d'affichage dynamique des champs ---
    def maj_visibilite_options(choix):
        if choix == "Dans un sous-dossier (au même endroit)":
            return gr.update(visible=True), gr.update(visible=False), gr.update(interactive=True)
        elif choix == "Dans un autre dossier spécifique":
            return gr.update(visible=False), gr.update(visible=True), gr.update(interactive=True)
        else: # Au même endroit (avec suffixe)
            return gr.update(visible=False), gr.update(visible=False), gr.update(interactive=False, value="_raster")

    dest_mode.change(
        fn=maj_visibilite_options,
        inputs=[dest_mode],
        outputs=[sous_dossier_input, autre_dossier_input, suffixe_input]
    )

    # --- Liaison du bouton de lancement ---
    btn_run.click(
        fn=executer_traitement_dossier,
        inputs=[
            dossier_input, 
            dest_mode, 
            sous_dossier_input, 
            autre_dossier_input, 
            suffixe_input, 
            recursive_checkbox, 
            dpi_slider
        ],
        outputs=[output_console]
    )

if __name__ == "__main__":
    demo.launch()