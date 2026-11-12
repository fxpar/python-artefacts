import os
import re
import gradio as gr

# Importations optionnelles pour formats spécifiques
try:
    from docx import Document
except ImportError:
    Document = None

try:
    from openpyxl import Workbook
except ImportError:
    Workbook = None

try:
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None


def create_file_with_content(file_path: str):
    """Crée un fichier avec son propre nom comme contenu selon son extension."""
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if ext == ".pdf":
        if canvas:
            c = canvas.Canvas(file_path)
            c.drawString(100, 750, f"Contenu du fichier : {filename}")
            c.save()
        else:
            with open(file_path, "wb") as f:
                f.write(f"%PDF-1.4\n1 0 obj<<>>endobj\n{filename}".encode("utf-8"))

    elif ext in [".docx", ".doc"]:
        if Document:
            doc = Document()
            doc.add_paragraph(f"Contenu du fichier : {filename}")
            doc.save(file_path)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Contenu du fichier : {filename}")

    elif ext in [".xlsx", ".xls"]:
        if Workbook:
            wb = Workbook()
            ws = wb.active
            ws["A1"] = f"Contenu du fichier : {filename}"
            wb.save(file_path)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Contenu du fichier : {filename}")

    elif ext == ".json":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f'{{\n  "filename": "{filename}"\n}}')

    elif ext == ".csv":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"filename\n{filename}\n")

    elif ext == ".html":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"<!DOCTYPE html><html><body><h1>{filename}</h1></body></html>")

    else:
        # txt, md, rtf, et autres extensions texte
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Contenu du fichier : {filename}\n")


def parse_and_generate(tree_text: str, base_destination: str) -> str:
    """Analyse le texte de l'arborescence et génère les dossiers/fichiers."""
    if not tree_text.strip():
        return "❌ Veuillez coller une arborescence texte."
    
    if not base_destination.strip():
        base_destination = "."

    lines = tree_text.strip().split("\n")
    path_stack = []
    created_count = 0

    for line in lines:
        cleaned_line = re.sub(r"^[│\s├└──\t]+", "", line).strip()
        if not cleaned_line:
            continue

        # Calcul du niveau d'indentation basé sur les caractères de structure ou espaces
        prefix = line[: line.find(cleaned_line)] if cleaned_line in line else ""
        indent_level = len(prefix) // 4  # Approximation du niveau de profondeur

        # Normalisation des préfixes ASCII/Unicode d'arborescence
        match = re.search(r"(\w[\w\.\-\s\/]*)$", cleaned_line)
        node_name = match.group(1).strip() if match else cleaned_line

        is_directory = node_name.endswith("/") or "." not in node_name
        clean_node_name = node_name.rstrip("/")

        # Ajustement de la pile de dossiers selon la profondeur
        while len(path_stack) > indent_level:
            path_stack.pop()

        current_path = os.path.join(base_destination, *path_stack, clean_node_name)

        if is_directory:
            os.makedirs(current_path, exist_ok=True)
            path_stack.append(clean_node_name)
        else:
            create_file_with_content(current_path)
            created_count += 1

    return f"✅ Génération terminée avec succès dans : {os.path.abspath(base_destination)}\n📄 Fichiers créés : {created_count}"


# Interface Gradio
with gr.Blocks(title="Générateur d'Arborescence") as app:
    gr.Markdown("# 📁 Générateur Fichiers & Dossiers pour Vibe Coding")
    gr.Markdown("Collez l'arborescence générée par l'IA et indiquez le dossier cible.")

    with gr.Row():
        tree_input = gr.Textbox(
            label="Arborescence au format texte",
            lines=15,
            placeholder="devis_client/\n│\n├── 01_interieur/\n│   └── devis.pdf",
        )

    with gr.Row():
        dest_input = gr.Textbox(
            label="Dossier de destination (chemin absolu ou relatif)",
            value="./output",
        )

    btn = gr.Button("🚀 Générer l'arborescence", variant="primary")
    output_status = gr.Textbox(label="Statut / Résultat", interactive=False)

    btn.click(
        fn=parse_and_generate,
        inputs=[tree_input, dest_input],
        outputs=output_status,
    )

if __name__ == "__main__":
    app.launch()