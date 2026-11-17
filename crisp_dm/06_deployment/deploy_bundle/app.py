"""Exploración visual e interactiva de resultados agregados del proyecto."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

APP_DIR = Path(__file__).resolve().parent
ROOT = next(
    (candidate for candidate in (APP_DIR, *APP_DIR.parents)
     if (candidate / "data" / "app" / "overview.json").exists()),
    APP_DIR,
)
DATA = ROOT / "data" / "app"
MIN_GROUP = 10

st.set_page_config(page_title="Análisis de comentarios Unillanos", page_icon="📊", layout="wide")

# Paletas de color semánticas y armónicas
SENTIMENT_COLORS = {
    "POS": "#2ecc71",
    "Positivo": "#2ecc71",
    "NEU": "#95a5a6",
    "Neutral": "#95a5a6",
    "NEG": "#e74c3c",
    "Negativo": "#e74c3c"
}

PLATFORM_COLORS = {
    "facebook": "#1877F2",
    "Facebook": "#1877F2",
    "instagram": "#E1306C",
    "Instagram": "#E1306C",
    "youtube": "#FF0000",
    "YouTube": "#FF0000"
}

EMOTION_COLORS = {
    "joy": "#f39c12",
    "Alegría": "#f39c12",
    "others": "#7f8c8d",
    "Otros": "#7f8c8d",
    "anger": "#e74c3c",
    "Enojo": "#e74c3c",
    "sadness": "#3498db",
    "Tristeza": "#3498db",
    "surprise": "#9b59b6",
    "Sorpresa": "#9b59b6",
    "fear": "#34495e",
    "Miedo": "#34495e",
    "disgust": "#16a085",
    "Disgusto": "#16a085"
}

EMOTION_ES_MAP = {
    "joy": "Alegría",
    "anger": "Enojo",
    "sadness": "Tristeza",
    "fear": "Miedo",
    "surprise": "Sorpresa",
    "disgust": "Disgusto",
    "others": "Otros"
}


@st.cache_data
def load_data() -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overview = json.loads((DATA / "overview.json").read_text(encoding="utf-8"))
    themes = pd.read_csv(DATA / "themes.csv", encoding="utf-8-sig")
    sentiment = pd.read_csv(DATA / "sentiment.csv", encoding="utf-8-sig")
    emotions = pd.read_csv(DATA / "emotions.csv", encoding="utf-8-sig")
    confidence_path = DATA / "sentiment_confidence.csv"
    confidence = pd.read_csv(confidence_path, encoding="utf-8-sig") if confidence_path.exists() else pd.DataFrame()
    ts_path = DATA / "theme_sentiment.csv"
    theme_sentiment = pd.read_csv(ts_path, encoding="utf-8-sig") if ts_path.exists() else pd.DataFrame()
    return overview, themes, sentiment, emotions, confidence, theme_sentiment


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


def make_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str = "", color_map: dict = None, hole: float = 0.45) -> go.Figure | None:
    if not HAS_PLOTLY or df.empty:
        return None
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        title=title,
        hole=hole,
        color=names_col if color_map else None,
        color_discrete_map=color_map if color_map else None,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#ffffff", width=2))
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=40, b=30),
        height=360
    )
    return fig


try:
    overview, themes, sentiment, emotions, confidence, theme_sentiment = load_data()
except FileNotFoundError:
    st.title("Análisis de comentarios Unillanos")
    st.warning("Aún no están generados los resultados agregados. Ejecute las fases 2 a 6 en orden; consulte el README.")
    st.stop()

st.title("Análisis de comentarios Unillanos")
st.caption("Estructura temática, polaridad de sentimiento y emociones en comentarios institucionales de Unillanos")
st.info("Exploración descriptiva de comentarios institucionales capturados. La taxonomía temática clasifica mediante reglas léxicas auditadas y desacopla interacciones sociales o emojis; sentimiento y emoción son estimaciones automáticas preentrenadas con RoBERTuito.")

with st.sidebar:
    st.header("Filtros")
    platform_options = sorted(overview["platforms"])
    selected_platforms = st.multiselect("Plataformas", platform_options, default=platform_options)
    type_options = sorted(overview["post_types"])
    selected_types = st.multiselect("Tipo de publicación", type_options, default=type_options)

themes_f = filtered(themes, selected_platforms, selected_types)
sentiment_f = filtered(sentiment, selected_platforms, selected_types)
emotions_f = filtered(emotions, selected_platforms, selected_types)
selected_n = int(themes_f["n"].sum())

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Comentarios analizados", f"{selected_n:,}")
metric2.metric("Plataformas activas", f"{len(selected_platforms)} / {len(overview['platforms'])}")
metric3.metric("Tipos de publicación", f"{len(selected_types)} / {len(overview['post_types'])}")
metric4.metric("Temas observados", themes_f["theme"].nunique() if not themes_f.empty else 0)

tab_summary, tab_topics, tab_theme_sent, tab_sentiment, tab_emotions, tab_advanced, tab_method = st.tabs([
    "Resumen", "Temas", "Sentimiento por tema", "Sentimiento global", "Emociones", "Visualizaciones avanzadas", "Método y límites"
])

# -----------------------------------------------------------------------------
# TAB 1: RESUMEN
# -----------------------------------------------------------------------------
with tab_summary:
    st.subheader("Distribución general por plataforma y formato")
    col_p1, col_p2 = st.columns([1, 1])

    plat_df = themes_f.groupby("platform")["n"].sum().rename("Comentarios").reset_index()
    plat_df["Plataforma"] = plat_df["platform"].str.capitalize()

    with col_p1:
        st.markdown("**Participación por plataforma**")
        fig_plat = make_pie_chart(plat_df, "Plataforma", "Comentarios", color_map=PLATFORM_COLORS)
        if fig_plat:
            st.plotly_chart(fig_plat, use_container_width=True)
        else:
            st.bar_chart(plat_df.set_index("Plataforma")["Comentarios"], horizontal=True)

    with col_p2:
        st.markdown("**Volumen por tipo de publicación**")
        type_df = themes_f.groupby("post_type")["n"].sum().sort_values(ascending=False).rename("Comentarios").reset_index()
        type_df["Tipo"] = type_df["post_type"].str.capitalize()
        if HAS_PLOTLY:
            fig_types = px.bar(
                type_df,
                x="Comentarios",
                y="Tipo",
                orientation="h",
                color="Tipo",
                color_discrete_sequence=px.colors.qualitative.Safe,
                text_auto=True
            )
            fig_types.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=20), height=360)
            st.plotly_chart(fig_types, use_container_width=True)
        else:
            st.bar_chart(type_df.set_index("Tipo")["Comentarios"], horizontal=True)

    st.caption("Nota: El volumen de comentarios depende de la intensidad de publicación y uso en cada red; no está normalizado por alcance o impresiones.")

# -----------------------------------------------------------------------------
# TAB 2: TEMAS
# -----------------------------------------------------------------------------
with tab_topics:
    st.subheader("Distribución de categorías temáticas")
    topic_table, topic_total = distribution(themes_f.rename(columns={"theme": "Tema"}), "Tema")

    if not topic_table.empty:
        col_t1, col_t2 = st.columns([6, 4])
        with col_t1:
            if HAS_PLOTLY:
                fig_topic = px.bar(
                    topic_table.sort_values("Comentarios", ascending=True),
                    x="Comentarios",
                    y="Tema",
                    orientation="h",
                    color="Comentarios",
                    color_continuous_scale="Blues",
                    text="Porcentaje"
                )
                fig_topic.update_traces(texttemplate="%{text}%", textposition="outside")
                fig_topic.update_layout(
                    coloraxis_showscale=False,
                    margin=dict(l=20, r=40, t=20, b=20),
                    height=450,
                    xaxis_title="Número de comentarios",
                    yaxis_title=""
                )
                st.plotly_chart(fig_topic, use_container_width=True)
            else:
                st.bar_chart(topic_table.set_index("Tema")["Comentarios"], horizontal=True)

        with col_t2:
            st.markdown("**Composición macro de la taxonomía**")
            sin_cont = topic_table.loc[topic_table["Tema"].str.contains("Sin contenido", case=False, na=False), "Comentarios"].sum()
            otros = topic_table.loc[topic_table["Tema"].str.contains("Otros temas", case=False, na=False), "Comentarios"].sum()
            especificos = topic_total - sin_cont - otros
            macro_df = pd.DataFrame([
                {"Macro": "Temas específicos", "Comentarios": especificos},
                {"Macro": "Otros (residual)", "Comentarios": otros},
                {"Macro": "Sin contenido temático", "Comentarios": sin_cont}
            ])
            macro_colors = {
                "Temas específicos": "#2980b9",
                "Otros (residual)": "#7f8c8d",
                "Sin contenido temático": "#bdc3c7"
            }
            fig_macro = make_pie_chart(macro_df, "Macro", "Comentarios", color_map=macro_colors, hole=0.5)
            if fig_macro:
                st.plotly_chart(fig_macro, use_container_width=True)

        st.dataframe(topic_table, use_container_width=True, hide_index=True)
    else:
        st.info("No hay comentarios en los filtros seleccionados.")

    st.caption("Las reglas asignan categorías mediante expresiones regulares léxicas con límites de palabra (\\b). 'Sin contenido temático suficiente' separa emojis y saludos para evitar sobrestimar el residual.")

# -----------------------------------------------------------------------------
# TAB 3: SENTIMIENTO POR TEMA
# -----------------------------------------------------------------------------
with tab_theme_sent:
    st.subheader("Sentimiento condicionado por área temática")
    st.warning("Advertencia metodológica: La categoría de felicitaciones y expresiones de aprecio se define con vocabulario de elogio, que el modelo de sentimiento asocia fuertemente con polaridad positiva. Por tanto, parte sustancial de esa correlación positiva es de construcción del clasificador y no un hallazgo empírico independiente.")

    if not theme_sentiment.empty:
        ts_f = filtered(theme_sentiment, selected_platforms, selected_types)
        theme_list = sorted(ts_f["theme"].unique())

        selected_theme = st.selectbox("Seleccione un área temática para inspeccionar su polaridad detallada:", theme_list)

        if selected_theme:
            sub_ts = ts_f[ts_f["theme"] == selected_theme]
            sent_dist, total_ts = distribution(sub_ts.rename(columns={"sentiment_label": "Sentimiento"}), "Sentimiento")

            if not sent_dist.empty:
                col_ts1, col_ts2 = st.columns([1, 1])

                with col_ts1:
                    st.markdown(f"**Proporción afectiva en _{selected_theme}_**")
                    fig_sent_pie = make_pie_chart(sent_dist, "Sentimiento", "Comentarios", color_map=SENTIMENT_COLORS, hole=0.45)
                    if fig_sent_pie:
                        st.plotly_chart(fig_sent_pie, use_container_width=True)
                    else:
                        st.bar_chart(sent_dist.set_index("Sentimiento")["Comentarios"])

                with col_ts2:
                    st.markdown(f"**Métricas y tabla de frecuencia** (Total: {total_ts:,})")
                    col_m1, col_m2, col_m3 = st.columns(3)
                    pos_row = sent_dist[sent_dist["Sentimiento"] == "POS"]
                    neu_row = sent_dist[sent_dist["Sentimiento"] == "NEU"]
                    neg_row = sent_dist[sent_dist["Sentimiento"] == "NEG"]

                    col_m1.metric("Positivo", f"{pos_row['Porcentaje'].values[0]}%" if not pos_row.empty else "0%")
                    col_m2.metric("Neutral", f"{neu_row['Porcentaje'].values[0]}%" if not neu_row.empty else "0%")
                    col_m3.metric("Negativo", f"{neg_row['Porcentaje'].values[0]}%" if not neg_row.empty else "0%")

                    st.dataframe(sent_dist, use_container_width=True, hide_index=True)
            else:
                st.info("Sin registros suficientes para esta categoría bajo los filtros activos.")

        # Gráfico comparativo general de todas las áreas temáticas
        st.divider()
        st.subheader("Comparativa general: Polaridad a través de todas las áreas temáticas")
        all_ts_piv = ts_f.groupby(["theme", "sentiment_label"])["n"].sum().reset_index()
        all_ts_tot = ts_f.groupby("theme")["n"].sum().rename("total").reset_index()
        all_ts_merged = pd.merge(all_ts_piv, all_ts_tot, on="theme")
        all_ts_merged["pct"] = (all_ts_merged["n"] / all_ts_merged["total"] * 100).round(1)

        if HAS_PLOTLY:
            fig_stacked = px.bar(
                all_ts_merged,
                y="theme",
                x="pct",
                color="sentiment_label",
                orientation="h",
                color_discrete_map=SENTIMENT_COLORS,
                category_orders={"sentiment_label": ["POS", "NEU", "NEG"]},
                labels={"pct": "Porcentaje (%)", "theme": "Área Temática", "sentiment_label": "Sentimiento"},
                text="pct"
            )
            fig_stacked.update_traces(texttemplate="%{text}%", textposition="inside")
            fig_stacked.update_layout(
                barmode="stack",
                xaxis=dict(range=[0, 100]),
                margin=dict(l=20, r=20, t=30, b=30),
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_stacked, use_container_width=True)
        st.caption("Comparación visual de polaridades normalizada al 100% en cada temática.")
    else:
        st.info("Datos de cruce temático no disponibles.")

# -----------------------------------------------------------------------------
# TAB 4: SENTIMIENTO GLOBAL
# -----------------------------------------------------------------------------
with tab_sentiment:
    st.subheader("Distribución de polaridad de sentimiento (global)")
    sent_table, sent_total = distribution(sentiment_f.rename(columns={"sentiment_label": "Sentimiento"}), "Sentimiento")

    if not sent_table.empty:
        col_s1, col_s2 = st.columns([1, 1])

        with col_s1:
            st.markdown("**Proporción porcentual global**")
            fig_global_sent = make_pie_chart(sent_table, "Sentimiento", "Comentarios", color_map=SENTIMENT_COLORS, hole=0.5)
            if fig_global_sent:
                st.plotly_chart(fig_global_sent, use_container_width=True)
            else:
                st.bar_chart(sent_table.set_index("Sentimiento")["Comentarios"])

        with col_s2:
            st.markdown(f"**Detalle cuantitativo** (Total: {sent_total:,})")
            st.dataframe(sent_table, use_container_width=True, hide_index=True)

            if not confidence.empty:
                confidence_f = filtered(confidence, selected_platforms, selected_types)
                high_n = int(confidence_f.loc[confidence_f["confidence_band"] == "0,7 o más", "n"].sum())
                high_pct = high_n / sent_total * 100 if sent_total else 0
                st.metric("Predicciones con alta confianza (≥ 0,7)", f"{high_n:,}", f"{high_pct:.1f}% del total")

        if not confidence.empty:
            st.divider()
            st.subheader("Distribución por bandas de confianza del modelo")
            conf_table, conf_total = distribution(
                confidence_f.rename(columns={"confidence_band": "Banda de confianza"}),
                "Banda de confianza",
            )
            if HAS_PLOTLY:
                fig_conf = px.bar(
                    conf_table,
                    x="Banda de confianza",
                    y="Comentarios",
                    color="Comentarios",
                    color_continuous_scale="Viridis",
                    text="Porcentaje"
                )
                fig_conf.update_traces(texttemplate="%{text}%", textposition="outside")
                fig_conf.update_layout(coloraxis_showscale=False, height=320, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_conf, use_container_width=True)
            else:
                st.bar_chart(conf_table.set_index("Banda de confianza")["Comentarios"])
    else:
        st.info("No hay comentarios en los filtros seleccionados.")
    st.caption("POS = positivo, NEG = negativo, NEU = neutral. El clasificador puede presentar incertidumbre frente a ironía o comentarios telegráficos.")

# -----------------------------------------------------------------------------
# TAB 5: EMOCIONES
# -----------------------------------------------------------------------------
with tab_emotions:
    st.subheader("Distribución estimada de emociones")
    emotion_table, emotion_total = distribution(emotions_f.rename(columns={"emotion_label": "Emoción"}), "Emoción")

    if not emotion_table.empty:
        col_e1, col_e2 = st.columns([1, 1])

        with col_e1:
            st.markdown("**Composición relativa de emociones**")
            fig_emo_pie = make_pie_chart(emotion_table, "Emoción", "Comentarios", color_map=EMOTION_COLORS, hole=0.45)
            if fig_emo_pie:
                st.plotly_chart(fig_emo_pie, use_container_width=True)
            else:
                st.bar_chart(emotion_table.set_index("Emoción")["Comentarios"], horizontal=True)

        with col_e2:
            st.markdown("**Frecuencias y porcentajes**")
            st.dataframe(emotion_table, use_container_width=True, hide_index=True)

            if HAS_PLOTLY:
                fig_emo_bar = px.bar(
                    emotion_table.sort_values("Comentarios", ascending=True),
                    x="Comentarios",
                    y="Emoción",
                    orientation="h",
                    color="Emoción",
                    color_discrete_map=EMOTION_COLORS,
                    text_auto=True
                )
                fig_emo_bar.update_layout(showlegend=False, height=280, margin=dict(l=20, r=20, t=10, b=10))
                st.plotly_chart(fig_emo_bar, use_container_width=True)
    else:
        st.info("No hay comentarios en los filtros seleccionados.")
    st.caption("Clases: alegría, enojo, tristeza, miedo, sorpresa, disgusto y ‘otros / sin emoción básica clara’ (others en RoBERTuito).")

# -----------------------------------------------------------------------------
# TAB 6: VISUALIZACIONES AVANZADAS (NUEVA SECCIÓN)
# -----------------------------------------------------------------------------
with tab_advanced:
    st.subheader("Exploración visual avanzada y multidimensional")
    st.markdown("Esta sección reúne cuatro perspectivas visuales complementarias para auditar patrones cruzados entre plataformas, temáticas y respuestas afectivas.")

    if HAS_PLOTLY and not theme_sentiment.empty:
        adv_ts = filtered(theme_sentiment, selected_platforms, selected_types)

        # ---------------------------------------------------------------------
        # 1. Cuadrante de Impacto: Volumen vs. Negatividad
        # ---------------------------------------------------------------------
        st.markdown("### 1. Cuadrante de impacto: Volumen vs. Tasa de Negatividad")
        st.caption("Posiciona cada área temática según su volumen de conversación (eje X) y su tasa de sentimiento negativo (eje Y). Las líneas punteadas indican la mediana de volumen y la tasa promedio de negatividad del corpus (14,6%). El tamaño refleja el volumen total y el color indica positividad.")

        ts_b_sum = adv_ts.groupby(["theme", "sentiment_label"])["n"].sum().unstack(fill_value=0)
        ts_b_sum["total"] = ts_b_sum.sum(axis=1)
        ts_b_sum["pct_neg"] = (ts_b_sum.get("NEG", 0) / ts_b_sum["total"] * 100).round(1)
        ts_b_sum["pct_pos"] = (ts_b_sum.get("POS", 0) / ts_b_sum["total"] * 100).round(1)
        ts_b_sum["pct_neu"] = (ts_b_sum.get("NEU", 0) / ts_b_sum["total"] * 100).round(1)
        ts_b_sum = ts_b_sum.reset_index()
        ts_b_sum = ts_b_sum[~ts_b_sum["theme"].str.contains("baja frecuencia", case=False, na=False)]

        if not ts_b_sum.empty:
            fig_bubble = px.scatter(
                ts_b_sum,
                x="total",
                y="pct_neg",
                size="total",
                color="pct_pos",
                text="theme",
                hover_name="theme",
                hover_data={"total": ":,", "pct_neg": ":.1f%", "pct_pos": ":.1f%", "pct_neu": ":.1f%"},
                color_continuous_scale="RdYlGn",
                labels={"total": "Volumen de comentarios", "pct_neg": "% Negatividad", "pct_pos": "% Positividad"},
                size_max=45
            )
            fig_bubble.update_traces(
                textposition="top center",
                textfont=dict(size=10),
                marker=dict(line=dict(width=1.5, color="DarkSlateGrey"))
            )
            avg_neg = (adv_ts.loc[adv_ts["sentiment_label"] == "NEG", "n"].sum() / adv_ts["n"].sum() * 100) if adv_ts["n"].sum() else 14.6
            median_vol = ts_b_sum["total"].median() if not ts_b_sum.empty else 500

            fig_bubble.add_hline(y=avg_neg, line_dash="dash", line_color="red", annotation_text=f"Promedio negatividad ({avg_neg:.1f}%)", annotation_position="bottom right")
            fig_bubble.add_vline(x=median_vol, line_dash="dash", line_color="gray", annotation_text=f"Mediana volumen ({int(median_vol):,})", annotation_position="top left")

            fig_bubble.update_layout(
                height=520,
                margin=dict(l=20, r=20, t=30, b=30),
                xaxis_title="Volumen total de comentarios en la temática",
                yaxis_title="% Sentimiento negativo dentro del tema"
            )
            st.plotly_chart(fig_bubble, use_container_width=True)

        st.divider()

        # ---------------------------------------------------------------------
        # 2. Diagrama de Sankey: Flujo de la Conversación
        # ---------------------------------------------------------------------
        st.markdown("### 2. Flujo de la conversación (Diagrama de Sankey)")
        st.caption("Visualiza el recorrido del volumen de comentarios: desde la plataforma de captura (izquierda), atravesando las áreas temáticas (centro), hasta la polaridad afectiva estimada (derecha). Pasa el cursor sobre cualquier nodo o flujo para ver su volumen exacto.")

        plat_theme = adv_ts.groupby(["platform", "theme"])["n"].sum().reset_index()
        theme_sent = adv_ts.groupby(["theme", "sentiment_label"])["n"].sum().reset_index()

        platforms_list = sorted(plat_theme["platform"].unique())
        themes_list = sorted(list(set(plat_theme["theme"].unique()) | set(theme_sent["theme"].unique())))
        sentiments_list = ["POS", "NEU", "NEG"]
        all_nodes = platforms_list + themes_list + sentiments_list
        node_map = {name: i for i, name in enumerate(all_nodes)}

        sankey_sources = [node_map[r["platform"]] for _, r in plat_theme.iterrows()]
        sankey_targets = [node_map[r["theme"]] for _, r in plat_theme.iterrows()]
        sankey_values = plat_theme["n"].tolist()

        sankey_sources += [node_map[r["theme"]] for _, r in theme_sent.iterrows()]
        sankey_targets += [node_map[r["sentiment_label"]] for _, r in theme_sent.iterrows()]
        sankey_values += theme_sent["n"].tolist()

        # Colores para los nodos de Sankey
        node_colors = []
        for n in all_nodes:
            if n in PLATFORM_COLORS:
                node_colors.append(PLATFORM_COLORS[n])
            elif n in SENTIMENT_COLORS:
                node_colors.append(SENTIMENT_COLORS[n])
            else:
                node_colors.append("#3498db")

        fig_sankey = go.Figure(go.Sankey(
            node=dict(
                label=[n.capitalize() if n in platforms_list else n for n in all_nodes],
                color=node_colors,
                pad=15,
                thickness=20
            ),
            link=dict(
                source=sankey_sources,
                target=sankey_targets,
                value=sankey_values,
                color="rgba(180, 180, 180, 0.3)"
            )
        ))
        fig_sankey.update_layout(height=560, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_sankey, use_container_width=True)

        st.divider()

        # ---------------------------------------------------------------------
        # 3. Gráfico Sunburst y 4. Radar Emocional en dos columnas
        # ---------------------------------------------------------------------
        col_adv_1, col_adv_2 = st.columns([1, 1])

        with col_adv_1:
            st.markdown("### 3. Jerarquía temática y afectiva (Sunburst)")
            st.caption("Estructura jerárquica multinivel interactiva: haz clic en cualquier segmento para hacer zoom (*drill-down*) desde la macro-categoría hacia el tema y su polaridad.")

            sun_df = adv_ts.copy()
            sun_df["macro"] = sun_df["theme"].apply(
                lambda t: "Sin contenido" if "Sin contenido" in t else ("Residual" if "Otros temas" in t else "Temas específicos")
            )
            fig_sunburst = px.sunburst(
                sun_df,
                path=["macro", "theme", "sentiment_label"],
                values="n",
                color="sentiment_label",
                color_discrete_map=SENTIMENT_COLORS
            )
            fig_sunburst.update_traces(textinfo="label+percent parent")
            fig_sunburst.update_layout(height=480, margin=dict(l=10, r=10, t=20, b=20))
            st.plotly_chart(fig_sunburst, use_container_width=True)

        with col_adv_2:
            st.markdown("### 4. Perfil emocional por plataforma (Radar)")
            st.caption("Compara las siluetas porcentuales de emociones entre Facebook, Instagram y YouTube, reflejando la 'huella afectiva' relativa de cada comunidad digital.")

            emotions_adv = filtered(emotions, selected_platforms, selected_types).copy()
            emotions_adv["emo_es"] = emotions_adv["emotion_label"].map(EMOTION_ES_MAP).fillna(emotions_adv["emotion_label"])

            emo_plat = emotions_adv.groupby(["platform", "emo_es"])["n"].sum().unstack(fill_value=0)
            emo_plat_pct = (emo_plat.div(emo_plat.sum(axis=1), axis=0) * 100).round(1)
            radar_categories = list(emo_plat_pct.columns)

            fig_radar = go.Figure()
            for p in emo_plat_pct.index:
                vals = emo_plat_pct.loc[p].tolist()
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=radar_categories + [radar_categories[0]],
                    name=p.capitalize(),
                    fill="toself",
                    line=dict(color=PLATFORM_COLORS.get(p, "#333333"), width=2),
                    opacity=0.5
                ))

            max_radial = max(emo_plat_pct.max().max() + 10, 40) if not emo_plat_pct.empty else 80
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, max_radial], ticksuffix="%")),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                height=480,
                margin=dict(l=20, r=20, t=30, b=30)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Visualizaciones avanzadas no disponibles para la configuración seleccionada.")

# -----------------------------------------------------------------------------
# TAB 7: MÉTODO Y LÍMITES
# -----------------------------------------------------------------------------
with tab_method:
    st.subheader("Marco metodológico y consideraciones analíticas")
    st.markdown("""
    - **Eje Temático Principal:** La taxonomía clasifica los comentarios mediante reglas léxicas compiladas con delimitadores de palabra (`\\b`), distinguiendo temas sustantivos (admisiones, bienestar, trámites, oferta académica, infraestructura, eventos, felicitaciones), comentarios sin sustancia proposicional (solo emojis o menciones aisladas) y otros temas no contemplados.
    - **Independencia del Contexto del Post:** Cada comentario se analizó por su propio texto sin fusionarlo con el texto de la publicación original, previniendo atribuciones erróneas de temas a comentarios ambiguos.
    - **Conservación de Emojis y Respuestas:** Se conservaron todos los registros para el modelado afectivo. Los comentarios solo emoji se identifican explícitamente en temas para no inflar artificialmente categorías académicas ni residuales.
    - **Sentimiento y Emoción Secundarios:** Corresponden a modelos preentrenados de `pysentimiento` para español (RoBERTuito). La clase `others` en emoción describe ausencia de emoción básica identificada/neutralidad emocional, no ausencia comprobada de afecto.
    - **Evaluación y Límites Éticos:** Las métricas de sentimiento y emoción proceden de una muestra pequeña (120 comentarios) filtrada a casos concordantes no ambiguos (78 en sentimiento, 67 en emoción). La taxonomía temática es heurística-exploratoria y no se acompaña de falsas métricas de exactitud humana al no disponer de verdad terreno manual en dicha muestra.
    - **Privacidad Estricta:** La aplicación opera exclusivamente sobre agregaciones agrupadas (`groupby`) con supresión de frecuencias menores a 10 ($n < 10$). Ningún texto, ID, autor ni URL forma parte del despliegue.
    """)
