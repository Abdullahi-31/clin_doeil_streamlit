import streamlit as st
from pathlib import Path
import datetime
import re

# ==============================
# CONFIG PAGE
# ==============================
st.set_page_config(
    page_title="Mon site d'articles",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# LOGO
# ==============================
BASE_DIR = Path(__file__).parent
logo_path = BASE_DIR / "clin_doeil.png"  # ton logo dans le dossier de base

# ==============================
# NAVIGATION SIMPLE
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "Accueil"
if "article_selected" not in st.session_state:
    st.session_state.article_selected = None
if "btn_clicked" not in st.session_state:
    st.session_state.btn_clicked = {}

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("🏠 Accueil"):
        st.session_state.page = "Accueil"
        st.session_state.article_selected = None
        st.session_state.btn_clicked = {}
with col2:
    if st.button("📰 Articles"):
        st.session_state.page = "Articles"
        st.session_state.article_selected = None
        st.session_state.btn_clicked = {}
with col3:
    if st.button("👥 Qui sommes-nous"):
        st.session_state.page = "Qui sommes-nous"
        st.session_state.article_selected = None
        st.session_state.btn_clicked = {}
with col4:
    if st.button("📬 Contact"):
        st.session_state.page = "Contact"
        st.session_state.article_selected = None
        st.session_state.btn_clicked = {}

page = st.session_state.page

# ==============================
# CHARGER ARTICLES AVEC DATE DU MD
# ==============================
def charger_articles():
    articles_dir = BASE_DIR / "articles"
    dossiers = {
        "Interviews": articles_dir / "interviews",
        "Reportages": articles_dir / "reportages",
        "Comptes rendus": articles_dir / "comptes_rendus",
    }

    articles = []
    for categorie, chemin in dossiers.items():
        if chemin.exists():
            for fichier in chemin.glob("*.md"):
                with open(fichier, "r", encoding="utf-8") as f:
                    contenu = f.read()
                lignes = contenu.split("\n")
                titre = lignes[0].replace("#", "").strip() or fichier.stem

                # Cherche la date dans le Markdown (format: Date: YYYY/MM/DD)
                date_str = None
                for ligne in lignes:
                    if ligne.lower().startswith("date:"):
                        date_str = ligne.split(":", 1)[1].strip()
                        break

                if date_str:
                    try:
                        date_article = datetime.datetime.strptime(date_str, "%Y/%m/%d")
                    except ValueError:
                        date_article = datetime.datetime.fromtimestamp(fichier.stat().st_mtime)
                else:
                    date_article = datetime.datetime.fromtimestamp(fichier.stat().st_mtime)

                contenu_sans_titre = "\n".join(lignes[1:])

                # Cherche uniquement la première image pour la vignette
                match_img = re.search(r"!\[.*?\]\((images/.*?)\)", contenu_sans_titre)
                image_path = str((articles_dir / match_img.group(1)).resolve()) if match_img else None

                articles.append((titre, contenu_sans_titre, date_article, categorie, fichier, image_path))

    # Trier par date du Markdown (la plus récente en premier)
    articles.sort(key=lambda x: x[2], reverse=True)
    return articles

# ==============================
# REMPLACER YOUTUBE PAR IFRAME
# ==============================
def embed_youtube_links(contenu):
    def replacer(match):
        url = match.group(1)
        video_id = url.split("v=")[-1]
        return f"""
        <iframe width="100%" height="400" 
        src="https://www.youtube.com/embed/{video_id}" 
        frameborder="0" allowfullscreen></iframe>
        """
    return re.sub(r"(https?://(www\.)?youtube\.com/watch\?v=[\w-]+)", replacer, contenu)

# ==============================
# AFFICHER LES CARDS
# ==============================
def afficher_cards(articles):
    for i in range(0, len(articles), 3):
        cols = st.columns(3)
        for j, article in enumerate(articles[i:i+3]):
            titre, contenu, date, categorie, fichier, image_path = article
            with cols[j]:
                st.markdown(f"**{titre}**")
                st.markdown(f"*{categorie} – {date.strftime('%d/%m/%Y')}*")
                if image_path:
                    st.image(image_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/150", use_container_width=True)

                key_name = f"btn_{i+j}"
                if st.button("Lire", key=key_name):
                    st.session_state.article_selected = article

# ==============================
# AFFICHER ARTICLE SELECTIONNE
# ==============================
def afficher_article():
    titre, contenu, date, categorie, fichier, image_path = st.session_state.article_selected
    st.markdown(f"# {titre}")
    st.markdown(f"*{categorie} – {date.strftime('%d/%m/%Y')}*")

    # Afficher toutes les images dans le contenu avec une largeur réduite
    lignes = contenu.split("\n")
    for ligne in lignes:
        match_img = re.match(r"!\[.*?\]\((images/.*?)\)", ligne)
        if match_img:
            img_path = (BASE_DIR / "articles" / match_img.group(1)).resolve()
            if img_path.exists():
                st.image(str(img_path), width=700)  # ✅ taille réduite
        else:
            # Transformer YouTube si besoin
            ligne = embed_youtube_links(ligne)
            st.markdown(ligne, unsafe_allow_html=True)

    if st.button("⬅️ Retour"):
        st.session_state.article_selected = None
        st.session_state.btn_clicked = {}

# ==============================
# PAGE ACCUEIL
# ==============================
if page == "Accueil":
    st.title("Accueil")
    st.subheader("Bienvenue sur Clin d'Oeil ! Voici les derniers articles publiés :")
    articles = charger_articles()
    if st.session_state.article_selected:
        afficher_article()
    elif articles:
        afficher_cards(articles[:6])

# ==============================
# PAGE ARTICLES
# ==============================
elif page == "Articles":
    st.title("📰 Tous les articles")
    articles = charger_articles()
    if not articles:
        st.info("Aucun article disponible.")
    else:
        categories = ["Toutes", "Interviews", "Reportages", "Comptes rendus"]
        filtre = st.selectbox("Filtrer par catégorie :", categories)
        if filtre != "Toutes":
            articles = [a for a in articles if a[3] == filtre]

        if st.session_state.article_selected:
            afficher_article()
        else:
            afficher_cards(articles)

# ==============================
# PAGE QUI SOMMES-NOUS
# ==============================
elif page == "Qui sommes-nous":
    st.title("👥 Qui sommes-nous")

    st.header("Notre mission")
    st.write(
        "Nous sommes une agence média spécialisée dans le sport, avec une passion particulière pour le football en Occitanie et Toulouse. "
        "Notre mission est de couvrir tous les aspects du sport local, en offrant des articles de qualités, des interviews exclusives et des reportages détaillés, "
        "tout en donnant la parole aux acteurs de tous niveaux, des plus petits clubs aux grandes infrastructures."
    )
    st.image("10.jpeg", width=400)

    st.header("Nos activités")
    st.write(
        "- **Reportages** : nous allons sur le terrain pour raconter l'actualité des clubs et des compétitions.\n"
        "- **Interviews** : nous donnons la parole à tous les acteurs du sport, des joueurs aux entraîneurs et dirigeants, amateurs comme professionnels.\n"
        "- **Comptes rendus** : nous analysons et résumons les matchs et événements sportifs."
    )
    st.image("3.jpeg", width=400)

    st.header("Notre couverture")
    st.write(
        "Nous suivons de près le football dans toute la région Occitanie, mais nous couvrons également tous types de sports et événements. "
        "Nous mettons en lumière tant les clubs amateurs que les structures professionnelles, pour que nos lecteurs restent informés et connectés à l'actualité sportive locale."
    )
    st.image("6.jpeg", width=400)

    st.header("Notre approche")
    st.write(
        "Notre équipe combine passion, professionnalisme et curiosité pour créer des contenus riches et engageants. "
        "Chaque article est pensé pour captiver le lecteur tout en offrant une information fiable, complète et proche du terrain."
    )
    st.image("8.jpeg", width=300)

# ==============================
# PAGE CONTACT
# ==============================
elif page == "Contact":
    st.title("📬 Contact")
    st.image("clin_doeil.png", width=150)
    st.write("Vous pouvez nous joindre par mail : clindoeil327@gmail.com")
    
    st.markdown(
        'Ou via les réseaux sociaux en cliquant sur les logos : '
        '[<img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png" width="24"/>](https://www.instagram.com/clind_oeil31/) Instagram '
        '&nbsp;&nbsp;'
        '[<img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" width="24"/>](https://www.youtube.com/@c0ach-amin) YouTube',
        unsafe_allow_html=True
    )

    st.write("Merci de ta visite !")
    st.write("© 2024 Clin d'Oeil")
