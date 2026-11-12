# Python artefacts — petits scripts pratiques

Une collection de scripts Python créés avec l'aide de l'IA pour automatiser des tâches du quotidien : organiser de gros PDF (recueils de partitions notamment), alléger des fichiers, créer des arborescences, petites applications de démonstration…

🌐 **Présentation des scripts : https://fxpar.github.io/python-artefacts/**

Contrairement aux outils du dépôt [artifacts](https://github.com/fxpar/artifacts), qui s'ouvrent directement dans le navigateur, ces scripts **s'exécutent sur votre ordinateur** avec Python.

> 🔒 **Vos fichiers restent chez vous.** Tous les traitements ont lieu sur votre ordinateur. Les interfaces Gradio et Streamlit s'affichent dans le navigateur, mais elles sont servies par votre propre machine (adresse `127.0.0.1`) : rien n'est envoyé sur Internet.

## Démarrage rapide

1. Installez [Python](https://www.python.org/downloads/) 3.10 ou plus récent (sous Windows, cochez « Add Python to PATH »).
2. Installez les bibliothèques du script voulu (voir le tableau plus bas), par exemple :
   ```bash
   pip install pypdf gradio
   ```
3. Lancez le script depuis un terminal ouvert dans le dossier :
   ```bash
   python pdf-insertion-signets.py
   ```

Les scripts à **interface graphique Gradio** affichent dans le terminal une adresse du type `http://127.0.0.1:7860` : ouvrez-la dans votre navigateur. Les applications **Streamlit** se lancent avec `streamlit run nom-du-script.py`.

## 🎵 PDF : créer les signets de gros recueils

Quatre scripts qui s'enchaînent pour ajouter un sommaire cliquable (signets) à des PDF volumineux, typiquement des recueils de partitions (*songbooks*).

| Étape | Script | Rôle |
| - | - | - |
| 1 | `pdf-signets-extracteur.py` | Parcourt les PDF du dossier courant et produit `signets_pdf.json` : la liste des signets existants, avec **en tête les PDF qui n'en ont aucun** (ceux qui restent à indexer). |
| 2 | `json-pdf-sommaires.py` | *(Gradio)* À partir de ce JSON, choisissez un PDF sans signets et indiquez les pages de son sommaire (ex. `1, 3-5`) : elles sont copiées dans un sous-dossier `sommaires`. Donnez ensuite ces quelques pages à une IA pour qu'elle en extraie la liste des titres (avec une IA locale si les documents sont confidentiels). |
| 3 | `pdf-insertion-signets.py` | *(Gradio)* Collez la liste « titre + numéro de page » obtenue : les signets sont créés dans le PDF. Un **décalage (offset)** corrige l'écart entre la numérotation imprimée et les pages réelles du fichier. |
| — | `pdf-pages-extracteur.py` | *(Gradio)* Extrait certaines pages d'un PDF dans un nouveau fichier. Syntaxe : `15,3,5-8,10` donne les pages 15, 3, 5, 6, 7, 8 et 10 (le tiret signifie « jusqu'à »). Fonctionne aussi sur les PDF protégés uniquement par des restrictions d'usage (mot de passe « propriétaire »), pas sur ceux qui demandent un mot de passe à l'ouverture. |

**Format attendu par `pdf-insertion-signets.py`** : une ligne par signet, terminée par le numéro de page.

```text
Autumn Leaves 12
Blue Bossa 14
```

**Réglage utile** : à la dernière ligne de `pdf-insertion-signets.py`, `allowed_paths=["C:/", "D:/"]` liste les lecteurs auxquels l'interface a le droit d'accéder. Ajoutez-y le lecteur où se trouvent vos PDF si besoin.

## 📄 PDF : alléger et aplatir

Certains PDF scannés (souvent les partitions) sont composés de nombreux calques d'images et s'affichent lentement. Ces scripts transforment chaque page en une seule image **tout en conservant le texte reconnu (OCR)** : le fichier reste consultable par recherche, mais devient fluide.

| Script | Rôle |
| - | - |
| `pdf-raster-multi.py` | *(Gradio)* Aplatit un ou plusieurs PDF déposés dans l'interface, avec choix de la résolution et suivi de la progression. |
| `pdf-rasterize-dossier.py` | *(Gradio)* Traite tout un dossier de PDF en une fois, avec choix du dossier de sortie et du suffixe des fichiers produits. |

## 📎 PDF : pièces jointes

| Script | Rôle |
| - | - |
| `pdf_extract_attachments.py` + `Extraire_PDF_attachments.bat` | Glissez un PDF sur le fichier `.bat` (Windows) : les pièces jointes du PDF sont extraites dans un dossier, et le script propose de créer une copie du PDF sans pièces jointes. |

## 🗂️ Fichiers et images

| Script | Rôle |
| - | - |
| `arborescence-creator.py` | *(Gradio)* Collez une arborescence sous forme de texte (comme celle produite par la commande `tree` ou par une IA) : les dossiers et fichiers sont créés. Les fichiers `.docx`, `.xlsx` et `.pdf` reçoivent un contenu minimal si les bibliothèques correspondantes sont installées. Pratique pour préparer des exercices de classement de fichiers. |
| `avif2png.py` | Convertit en PNG toutes les images AVIF du dossier courant. |

## 🧪 Applications et exemples pédagogiques

| Dossier | Rôle |
| - | - |
| `mini-crm-db/` | *(Streamlit)* Mini CRM de gestion de prospects avec base SQLite : tableau de bord, ajout, modification et suppression. Exemple pour découvrir les bases de données. La base est créée au premier lancement. |
| `micro-learning/` | *(Streamlit, en cours de développement)* Construit des modules de micro-learning à partir de fichiers Markdown (formats : dialogue, roue, processus, pyramide). Illustrations [unDraw](https://undraw.co). |
| `nb-premiers/` | Affiche les nombres premiers jusqu'à 100 avec le crible d'Ératosthène : exemple minimal de script Python. |

## Bibliothèques nécessaires

| Bibliothèque | Installation | Utilisée par |
| - | - | - |
| [pypdf](https://pypdf.readthedocs.io) | `pip install pypdf` | signets, pages, sommaires, pièces jointes |
| [PyMuPDF](https://pymupdf.readthedocs.io) | `pip install pymupdf` | aplatissement de PDF |
| [Gradio](https://www.gradio.app) | `pip install gradio` | toutes les interfaces graphiques *(Gradio)* |
| [Streamlit](https://streamlit.io) | `pip install streamlit` | mini-crm-db, micro-learning |
| [pandas](https://pandas.pydata.org) | `pip install pandas` | mini-crm-db |
| [PyYAML](https://pyyaml.org) | `pip install pyyaml` | micro-learning |
| [Pillow](https://python-pillow.org) + pillow-avif-plugin | `pip install pillow pillow-avif-plugin` | avif2png |
| python-docx, openpyxl, reportlab *(facultatives)* | `pip install python-docx openpyxl reportlab` | arborescence-creator (contenu des fichiers Word, Excel, PDF) |

## Licence

[MIT](LICENSE) : vous pouvez utiliser, copier, modifier et redistribuer ces scripts librement, y compris à des fins commerciales, à condition de conserver la mention de copyright. Aucune garantie n'est fournie.
