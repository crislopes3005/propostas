import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# =========================
# CONFIG
# =========================
COR_PRINCIPAL = "#002E73"

st.set_page_config(layout="wide")

# =========================
# UPLOAD
# =========================
st.sidebar.header("📂 Base de dados")

arquivo_upload = st.sidebar.file_uploader(
    "Envie um arquivo Excel",
    type=["xlsx"]
)

if arquivo_upload:
    df_comentarios = pd.read_excel(arquivo_upload, sheet_name='comentarios')
    df_propostas = pd.read_excel(arquivo_upload, sheet_name='propostas')
    df_pordia = pd.read_excel(arquivo_upload, sheet_name='pordia')
    df_paisestado = pd.read_excel(arquivo_upload, sheet_name='paisestado')
    df_dispositivo = pd.read_excel(arquivo_upload, sheet_name='dispositivo')
else:
    st.warning("Envie um arquivo para continuar")
    st.stop()

# =========================
# TRATAMENTOS
# =========================

# Datas
df_comentarios['data_publicacao'] = pd.to_datetime(
    df_comentarios['data_publicacao'],
    format='%d/%m/%Y %H:%M',
    errors='coerce'
)

df_comentarios['data'] = df_comentarios['data_publicacao'].dt.date
df_pordia['Date'] = pd.to_datetime(df_pordia['Date'], dayfirst=True)

# Descrição curta
df_paragrafos['descricao_curta'] = df_paragrafos['descricao'].apply(
    lambda x: (
        lambda cleaned: cleaned[:60] + "..." if len(cleaned) > 60 else cleaned
    )(' '.join(x.split()) if isinstance(x, str) else x)
    if isinstance(x, str) else x
)

# Estados
df_paisestado['Region'] = df_paisestado['Region'].str.title()

# Duração (limpeza)
df_pordia['Avg Session Duration (Sec)'] = pd.to_numeric(
    df_pordia['Avg Session Duration (Sec)'],
    errors='coerce'
)

df_duracao = df_pordia[
    (df_pordia['Avg Session Duration (Sec)'] > 0) &
    (df_pordia['Avg Session Duration (Sec)'] < 3600)
]

# =========================
# KPIs
# =========================
st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Propostas", df_propostas['id_proposta'].nunique())
col2.metric("Proponentes distintos", df_comentarios['autor/id'].nunique())
col3.metric("Votos", df_propostas['quantidade_votos'].sum())
col4.metric("Comentários", df_comentarios['id'].count())

st.divider()

col5, col6, col7, col8, col9 = st.columns(5)

col5.metric("Visitantes únicos", df_pordia['Users'].sum())
col6.metric("Visualizações", df_pordia['Views'].sum())
col7.metric("Taxa de rejeição", f"{df_pordia['Bounce Rate'].mean():.2%}")

avg_sec = df_duracao['Avg Session Duration (Sec)'].median()
col8.metric("Duração média", f"{int(avg_sec//60)}m {int(avg_sec%60)}s")

col9.metric("Países distintos", df_paisestado['Country'].nunique())

st.divider()

# =========================
# KPIs DE PARTICIPAÇÃO NAS PROPOSTAS - COMENTÁRIOS
# =========================
st.subheader("Distribuição de participação nas propostas - comentários")

total_paragrafos = len(df_propostas)

sem_comentario = (df_propostas['quantidade_comentarios'] == 0).sum()

ate_5 = (
    (df_propostas['quantidade_comentarios'] >= 1) &
    (df_propostas['quantidade_comentarios'] <= 5)
).sum()

mais_de_5 = (df_propostas['quantidade_comentarios'] > 5).sum()

total = len(df_propostas)

pct_sem = sem_comentario / total
pct_ate5 = ate_5 / total
pct_mais5 = mais_de_5 / total

col1, col2, col3 = st.columns(3)

col1.metric("Sem comentários", f"{pct_sem:.0%}")
col2.metric("1 a 5 comentários", f"{pct_ate5:.0%}")
col3.metric("Mais de 5 comentários", f"{pct_mais5:.0%}")

st.divider()

# =========================
# KPIs DE PARTICIPAÇÃO NAS PROPOSTAS - VOTOS
# =========================
st.subheader("Distribuição de participação nas propostas - votos")

total_propostas = len(df_propostas)

sem_votos = (df_propostas['quantidade_votos'] == 0).sum()

ate_100 = (
    (df_propostas['quantidade_votos'] >= 1) &
    (df_propostas['quantidade_votos'] <= 100)
).sum()

mais_de_5 = (df_propostas['quantidade_votos'] > 100).sum()

total = len(df_propostas)

pct_sem = sem_votos / total
pct_ate5 = ate_100 / total
pct_mais5 = mais_de_100 / total

col1, col2, col3 = st.columns(3)

col1.metric("Sem votos", f"{pct_sem:.0%}")
col2.metric("1 a 100 votos", f"{pct_ate5:.0%}")
col3.metric("Mais de 100 votos", f"{pct_mais5:.0%}")

# =========================
# GRÁFICOS
# =========================

# 🔹 Comentários por parágrafo
st.subheader("Comentários por parágrafo")

fig1 = px.bar(
    df_propostas.sort_values('quantidade_comentarios').tail(10),
    y="titulo",
    x="quantidade_comentarios",
    orientation="h",
    text="quantidade_comentarios",
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# 🔹 Comentários por dia
st.subheader("Comentários por dia")

comentarios_dia = df_comentarios.groupby('data')['id'].count().reset_index()

fig2 = px.line(
    comentarios_dia.sort_values('data'),
    x='data',
    y='id',
    markers=True,
    text='id',
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig2.update_traces(textposition="top center")
st.plotly_chart(fig2, use_container_width=True)

# 🔹 Votos por parágrafo
st.subheader("Votos por parágrafo")

fig1 = px.bar(
    df_propostas.sort_values('quantidade_votos').tail(10),
    y="titulo",
    x="quantidade_votos",
    orientation="h",
    text="quantidade_votos",
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# 🔹 Votos por eixo
votos_eixo = df_propostas.groupby('categoria/nome')['id'].count().reset_index()
st.subheader("Votos por eixo")

fig1 = px.bar(
    votos_eixo.sort_values('id').tail(10),
    y="categoria/nome",
    x="id",
    orientation="h",
    text="quantidade_votos",
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# 🔹 Propostas por dia
st.subheader("Propostas por dia")

propostas_dia = df_propostas.groupby('data')['id'].count().reset_index()

fig2 = px.line(
    propostas_dia.sort_values('data'),
    x='data',
    y='id',
    markers=True,
    text='id',
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig2.update_traces(textposition="top center")
st.plotly_chart(fig2, use_container_width=True)

# 🔹 Visitantes e visualizações por dia
st.subheader("Visitantes e visualizações por dia")

df_agg = df_pordia.groupby('Date', as_index=False)[['Users', 'Views']].sum()
df_agg = df_agg.sort_values('Date')

# 🔹 Visitantes (base)
fig3 = px.line(
    df_agg,
    x='Date',
    y='Users',
    markers=True,
    color_discrete_sequence=["#5A7BBF"]
)

# 🔥 GARANTIR legenda correta
fig3.data[0].name = "Visitantes"
fig3.data[0].showlegend = True

# 🔹 Visualizações (com rótulo)
fig3.add_scatter(
    x=df_agg['Date'],
    y=df_agg['Views'],
    mode='lines+markers+text',
    name='Visualizações',
    text=df_agg['Views'],
    textposition='top center',
    line=dict(color=COR_PRINCIPAL, width=3),
    showlegend=True
)

# 🔹 Layout
fig3.update_layout(
    xaxis_title="Data",
    yaxis_title="Quantidade",
    hovermode="x unified",
    legend=dict(
        orientation="h",   # horizontal
        yanchor="top",
        y=-0.2,            # posição abaixo do gráfico
        xanchor="center",
        x=0.5              # centralizado
    )
)

st.plotly_chart(fig3, use_container_width=True)

# 🔹 Top 10 estados
st.subheader("Top 10 estados com mais visitas")

df_estados = df_paisestado[df_paisestado['Country'].str.lower() == 'brazil']
df_estados = df_estados.groupby('Region')['Sessions'].sum().reset_index()
df_estados = df_estados.sort_values('Sessions', ascending=True).tail(10)

fig4 = px.bar(
    df_estados,
    x='Sessions',
    y='Region',
    orientation='h',
    text='Sessions',
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig4.update_traces(textposition="outside")
st.plotly_chart(fig4, use_container_width=True)

# 🔹 Dispositivos
st.subheader("Acesso por dispositivo")

fig5 = px.pie(
    df_dispositivo,
    names='Device Type',
    values='Sessions',
    color_discrete_sequence=[COR_PRINCIPAL, "#5A7BBF", "#A5B8E1"]
)

fig5.update_traces(textinfo='percent+label')
st.plotly_chart(fig5, use_container_width=True)

# =========================
# TABELA FINAL
# =========================
st.subheader("Detalhamento dos parágrafos")

df_tabela = df_paragrafos[['descricao_curta', 'quantidade_comentarios', 'url_proposta']].copy()
df_tabela = df_tabela.sort_values('quantidade_comentarios', ascending=False).head(20)

df_tabela['🔗'] = df_tabela['url_proposta'].apply(
    lambda x: f'<a href="{x}" target="_blank">🔗</a>'
)

st.markdown(
    df_tabela[['descricao_curta', 'quantidade_comentarios', '🔗']]
    .rename(columns={
        'descricao_curta': 'Descrição',
        'quantidade_comentarios': 'Comentários'
    })
    .to_html(escape=False, index=False),
    unsafe_allow_html=True
)

# =========================
# NUVEM DE PALAVRAS
# =========================
st.subheader("Nuvem de palavras dos comentários")

texto = " ".join(df_comentarios['texto'].dropna().astype(str))

stopwords = set(STOPWORDS)
stopwords = set(STOPWORDS)

stopwords.update([
    # artigos
    "o", "a", "os", "as", "um", "uma", "uns", "umas",

    # preposições
    "de", "da", "do", "das", "dos",
    "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem",
    "sob", "sobre", "entre", "até",
    "desde", "contra", "perante",
    "ante", "após", "trás",

    # contrações comuns
    "ao", "aos", "à", "às",
    "pelo", "pela", "pelos", "pelas",
    "num", "numa", "nuns", "numas",
    "dum", "duma", "duns", "dumas",

    # pronomes e conectivos (melhora muito a nuvem)
    "que", "se", "isso", "isto", "aquele", "aquela",
    "ele", "ela", "eles", "elas",
    "me", "te", "lhe", "nos", "vos",
    "eu", "tu", "você", "vocês",
    "nós", "eles", "elas",
    "qual", "quais", "quem",
    "onde", "quando", "como",

    # conectores muito comuns
    "e", "ou", "mas", "porque", "pois", "logo",
    "também", "já", "ainda", "muito", "mais",
    "menos", "tudo", "todos", "todas"
])

wordcloud = WordCloud(
    width=800,
    height=400,
    background_color='white',
    colormap='Blues',
    stopwords=stopwords
).generate(texto)

fig, ax = plt.subplots()
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis("off")

st.pyplot(fig)
