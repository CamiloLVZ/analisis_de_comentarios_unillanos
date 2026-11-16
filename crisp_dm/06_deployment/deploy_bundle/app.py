"""Interactive, aggregate-only exploration of the project results."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT = next(
    (candidate for candidate in (APP_DIR, *APP_DIR.parents)
     if (candidate / "data" / "app" / "overview.json").exists()),
    APP_DIR,
)
DATA = ROOT / "data" / "app"
MIN_GROUP = 10

st.set_page_config(page_title="Voces en la conversación | Unillanos", page_icon="🎓", layout="wide")


@st.cache_data
def load_data() -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overview = json.loads((DATA / "overview.json").read_text(encoding="utf-8"))
    themes = pd.read_csv(DATA / "themes.csv", encoding="utf-8-sig")
    sentiment = pd.read_csv(DATA / "sentiment.csv", encoding="utf-8-sig")
    emotions = pd.read_csv(DATA / "emotions.csv", encoding="utf-8-sig")
    confidence_path = DATA / "sentiment_confidence.csv"
    confidence = pd.read_csv(confidence_path, encoding="utf-8-sig") if confidence_path.exists() else pd.DataFrame()
    return overview, themes, sentiment, emotions, confidence


def filtered(df: pd.DataFrame, platforms: list[str], post_types: list[str]) -> pd.DataFrame:
    result = df[df["platform"].isin(platforms)]
    result = result[result["post_type"].isin(post_types)]
    return result


def distribution(df: pd.DataFrame, label: str) -> tuple[pd.DataFrame, int]:
    counts = df.groupby(label, dropna=False)["n"].sum().sort_values(ascending=False).rename("Comentarios").reset_index()
    total = int(counts["Comentarios"].sum())
    counts["Porcentaje"] = (counts["Comentarios"] / total * 100).round(1) if total else 0
    small = int(counts.loc[counts["Comentarios"] < MIN_GROUP, "Comentarios"].sum())
    shown = counts[counts["Comentarios"] >= MIN_GROUP].copy()
    if small:
        shown.loc[len(shown)] = {label: "Grupos con menos de 10", "Comentarios": small, "Porcentaje": round(small / total * 100, 1) if total else 0}
    return shown.sort_values("Comentarios", ascending=False), total


try:
    overview, themes, sentiment, emotions, confidence = load_data()
except FileNotFoundError:
    st.title("Voces en la conversación | Unillanos")
    st.warning("Aún no están generados los resultados agregados. Ejecute las fases 2 a 6 en orden; consulte el README.")
    st.stop()

st.title("Voces en la conversación")
st.caption("Temas, sentimiento y emociones en los comentarios recolectados de redes institucionales de Unillanos")
st.info("Exploración descriptiva de comentarios capturados. Las etiquetas de sentimiento y emoción son estimaciones automáticas y no representan a toda la comunidad universitaria.")
if overview.get("evaluation_status") == "evaluated_with_two_human_annotators":
    st.info("La comparación se basa en una muestra pequeña y solo en los casos concordantes no ambiguos; no representa a todas las plataformas ni a toda la comunidad.")
elif overview.get("evaluation_status") != "evaluated_with_small_manual_sample":
    st.warning("La evaluación local contra etiquetas manuales aún no está completada. Interprete las clases del modelo como resultados exploratorios.")

with st.sidebar:
    st.header("Filtros")
    platform_options = sorted(overview["platforms"])
    selected_platforms = st.multiselect("Plataformas", platform_options, default=platform_options)
    type_options = sorted(overview["post_types"])
    selected_types = st.multiselect("Tipo de publicación", type_options, default=type_options)
    st.divider()
    st.caption(f"{overview['comments_scored']:,} comentarios con texto analizados")
    st.caption("Sin evolución temporal ni análisis de hilos.")

themes_f = filtered(themes, selected_platforms, selected_types)
sentiment_f = filtered(sentiment, selected_platforms, selected_types)
emotions_f = filtered(emotions, selected_platforms, selected_types)
selected_n = int(themes_f["n"].sum())

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Comentarios analizados", f"{selected_n:,}")
metric2.metric("Plataformas seleccionadas", len(selected_platforms))
metric3.metric("Temas categorizados", themes_f["theme"].nunique() if not themes_f.empty else 0)

tab_summary, tab_topics, tab_sentiment, tab_emotions, tab_method = st.tabs(["Resumen", "Temas", "Sentimiento", "Emociones", "Método y límites"])

with tab_summary:
    st.subheader("Comentarios incluidos por plataforma")
    platform_counts = themes_f.groupby("platform")["n"].sum().sort_values(ascending=False)
    st.bar_chart(platform_counts, horizontal=True)
    st.caption("El número de comentarios por plataforma depende de la recolección y del uso de cada red; no está normalizado por alcance o impresiones.")

with tab_topics:
    st.subheader("Temas sugeridos por reglas léxicas")
    topic_table, topic_total = distribution(themes_f.rename(columns={"theme": "Tema"}), "Tema")
    if not topic_table.empty:
        st.bar_chart(topic_table.set_index("Tema")["Comentarios"], horizontal=True)
        st.dataframe(topic_table, width="stretch", hide_index=True)
    else:
        st.info("No hay comentarios en los filtros seleccionados.")
    st.caption("Las reglas asignan categorías por términos asociados. ‘Otros / tema no identificado’ significa que no coincidió una regla y no equivale a un tema homogéneo.")

with tab_sentiment:
    st.subheader("Sentimiento estimado")
    sent_table, sent_total = distribution(sentiment_f.rename(columns={"sentiment_label": "Sentimiento"}), "Sentimiento")
    if not sent_table.empty:
        st.bar_chart(sent_table.set_index("Sentimiento")["Comentarios"])
        st.dataframe(sent_table, width="stretch", hide_index=True)
    else:
        st.info("No hay comentarios en los filtros seleccionados.")
    st.caption("POS = positivo, NEG = negativo, NEU = neutral. El clasificador puede equivocarse con ironía, mensajes cortos y contexto faltante.")
    if not confidence.empty:
        st.subheader("Confianza de las predicciones de sentimiento")
        confidence_f = filtered(confidence, selected_platforms, selected_types)
        confidence_table, confidence_total = distribution(
            confidence_f.rename(columns={"confidence_band": "Banda de confianza"}),
            "Banda de confianza",
        )
        if not confidence_table.empty:
            high_n = int(confidence_f.loc[confidence_f["confidence_band"] == "0,7 o más", "n"].sum())
            high_pct = high_n / confidence_total * 100 if confidence_total else 0
            st.metric("Con confianza ≥ 0,7", f"{high_n:,} ({high_pct:.1f} %)")
            st.bar_chart(confidence_table.set_index("Banda de confianza")["Comentarios"])
        st.caption("La banda ≥ 0,7 es una referencia exploratoria: en la muestra humana concordante logró 92,9 % de accuracy en 56 casos (71,8 % de cobertura). No cambia las etiquetas originales y no garantiza ese desempeño en todos los comentarios.")

with tab_emotions:
    st.subheader("Emoción estimada")
    emotion_table, emotion_total = distribution(emotions_f.rename(columns={"emotion_label": "Emoción"}), "Emoción")
    if not emotion_table.empty:
        st.bar_chart(emotion_table.set_index("Emoción")["Comentarios"], horizontal=True)
        st.dataframe(emotion_table, width="stretch", hide_index=True)
    else:
        st.info("No hay comentarios en los filtros seleccionados.")
    st.caption("Clases observadas: alegría, enojo, tristeza, miedo, sorpresa, disgusto y ‘otros / sin emoción básica clara’ (others en el modelo). Son estimaciones del texto, no estados psicológicos comprobados.")

with tab_method:
    st.subheader("Cómo leer esta aplicación")
    st.markdown("""
    - Se conservaron comentarios principales y respuestas; cada texto se analizó individualmente y sin contexto del hilo.
    - Se conservaron los emojis para la entrada a los analizadores. Su interpretación puede variar según contexto y cultura.
    - Sentimiento y emoción son clasificaciones preentrenadas de `pysentimiento` para español. El modelo instalado devuelve `others` para la clase que el model card describe como neutral/sin emoción básica identificada.
    - Los temas se asignan mediante reglas léxicas transparentes y requieren interpretación humana.
    - Las plataformas tienen tamaños de muestra distintos y los conteos no están ajustados por alcance.
    - No se muestran comentarios, autores, IDs, URLs ni fechas. Las categorías con menos de 10 casos se agrupan para reducir lecturas de grupos pequeños.
    """)

st.divider()
st.caption("Proyecto académico exploratorio · Universidad de los Llanos · CRISP-DM")
