import os
import tempfile
import fitz  # PyMuPDF
import gradio as gr
import urllib.parse

# ==========================================
# 1. LE MOTEUR : Votre fonction d'aplatissement
# ==========================================
def aplatir_calques_conserver_ocr(pdf_entree, pdf_sortie, dpi=150):
    yield "Ouverture du fichier d'origine..."
    doc_source = fitz.open(pdf_entree)
    doc_cible = fitz.open()  # On crée un PDF tout neuf, vide
    
    total_pages = len(doc_source)
    yield f"Début du traitement de {total_pages} pages..."
    
    for num_page in range(total_pages):
        page_origine = doc_source[num_page]
        
        # 1. On "dessine" la page en image
        pix = page_origine.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
        jpeg_bytes = pix.tobytes("jpeg")
        
        # 2. Nouvelle page vierge de même taille
        nouvelle_page = doc_cible.new_page(width=page_origine.rect.width, height=page_origine.rect.height)
        
        # 3. Collage de l'image de fond
        nouvelle_page.insert_image(nouvelle_page.rect, stream=jpeg_bytes)
        
        # 4. Ré-insertion du texte invisible (OCR)
        mots = page_origine.get_text("words")
        
        for mot in mots:
            x0, y0, x1, y1, texte, block_no, line_no, word_no = mot
            taille_police = max(5, y1 - y0)
            
            try:
                nouvelle_page.insert_text(
                    fitz.Point(x0, y1), 
                    texte, 
                    fontsize=taille_police, 
                    render_mode=3  # 3 = Texte invisible
                )
            except:
                pass  # Sécurité si un caractère bizarre bloque
                
        # On envoie la progression de la page en temps réel vers Gradio
        yield f"Progression : Page {num_page + 1}/{total_pages} aplatie."

    yield "Sauvegarde et optimisation du fichier final..."
    doc_cible.save(pdf_sortie, garbage=4, deflate=True)
    doc_source.close()
    doc_cible.close()
    yield "Sauvegarde terminée avec succès !"

# ==========================================
# 2. LA PASSERELLE : Fonction appelée par Gradio
# ==========================================


def process_pdf_via_gradio(pdf_files, dpi):
    if not pdf_files:
        yield None, "Veuillez glisser au moins un fichier PDF.", ""
        return
    
    if not isinstance(pdf_files, list):
        pdf_files = [pdf_files]
        
    fichiers_traites = []
    messages_statut = []
    liens_html_list = []  # Pour stocker les liens HTML de chaque fichier réussi
    
    total_fichiers = len(pdf_files)
    
    for i, pdf_file in enumerate(pdf_files, 1):
        chemin_entree = pdf_file.name
        nom_base = os.path.splitext(os.path.basename(chemin_entree))[0]
        
        dir_temp_global = tempfile.gettempdir()
        chemin_sortie = os.path.normpath(os.path.join(dir_temp_global, f"{nom_base}_raster.pdf"))
        
        prefixe_log = f"[{i}/{total_fichiers}] {nom_base}.pdf : "
        messages_statut.append(f"{prefixe_log}Démarrage...")
        
        # On génère le HTML à la volée
        html_actuel = "<br>".join(liens_html_list)
        yield fichiers_traites, "\n".join(messages_statut), html_actuel
        
        try:
            # On consomme le générateur de progression de la fonction d'aplatissement
            for progression in aplatir_calques_conserver_ocr(chemin_entree, chemin_sortie, dpi=int(dpi)):
                temp_status = messages_statut[:-1] + [f"{prefixe_log}{progression}"]
                yield fichiers_traites, "\n".join(temp_status), html_actuel
            
            # Succès
            fichiers_traites.append(chemin_sortie)
            messages_statut[-1] = f"{prefixe_log}✓ Réussi : {nom_base}_raster.pdf"
            
            # Génération du lien cliquable au format HTML
            chemin_url_local = urllib.parse.urljoin('file:', urllib.request.pathname2url(chemin_sortie))
            lien_html = f'💡 <a href="{chemin_url_local}" target="_blank" style="color: #2196F3; text-decoration: underline; font-weight: bold;">Ouvrir {nom_base}_raster.pdf</a>'
            liens_html_list.append(lien_html)
            
        except Exception as e:
            messages_statut[-1] = f"{prefixe_log}✗ Échec : {str(e)}"
            
        html_actuel = "<br>".join(liens_html_list)
        yield fichiers_traites, "\n".join(messages_statut), html_actuel

# ==========================================
# 3. L'INTERFACE : Définition de l'UI Gradio
# ==========================================
with gr.Blocks(title="Aplatisseur de PDF (Conserve l'OCR)") as demo:
    gr.Markdown("""
    # 📄 Aplatisseur de PDF & Optimiseur de Songbooks (Multi)
    Glissez un ou plusieurs fichiers PDF pour les aplatir tout en conservant le texte recherchable. 
    Les fichiers optimisés seront enregistrés au même endroit avec le suffixe `_raster.pdf`.
    """)
    
    with gr.Row():
        with gr.Column():
            # Zone de dépôt multi-fichiers
            pdf_input = gr.File(
                label="Déposez vos PDF ici (un ou plusieurs)", 
                file_types=[".pdf"], 
                file_count="multiple"
            )
            
            # Paramètre de résolution (DPI)
            dpi_slider = gr.Slider(
                minimum=72, 
                maximum=300, 
                value=150, 
                step=10, 
                label="Qualité d'image (DPI)", 
                info="150 DPI est le compromis idéal pour les tablettes."
            )
            
            btn_run = gr.Button("Optimiser le(s) PDF", variant="primary")
            
        with gr.Column():
            # Zone de téléchargement en sortie (gère aussi le multi)
            pdf_output = gr.File(
                label="Télécharger les PDF optimisés", 
                file_count="multiple"
            )
            # Console de log
            status_text = gr.Textbox(
                label="Statut du traitement", 
                interactive=False, 
                lines=10
            )
            # NOUVEAU : Zone pour afficher les vrais liens HTML cliquables
            html_links = gr.HTML(
                label="Liens d'ouverture rapide",
                value="<p style='color: gray; font-style: italic;'>Les liens directs s'afficheront ici à la fin du traitement.</p>"
            )

    # Association de l'action au clic du bouton
    btn_run.click(
        fn=process_pdf_via_gradio,
        inputs=[pdf_input, dpi_slider],
        outputs=[pdf_output, status_text, html_links]
    )

# Lancement de l'application
if __name__ == "__main__":
    demo.launch()