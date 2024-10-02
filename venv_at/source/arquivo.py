import streamlit as st
import pandas as pd
from statsbombpy import sb
from mplsoccer import Pitch
import matplotlib.pyplot as plt

@st.cache_data
def cache_competicoes():
    return sb.competitions()

@st.cache_data
def cache_temporadas(competicao_id):
    return sb.matches(competition_id=competicao_id)

@st.cache_data
def cache_partidas(competacao_id, temporada_id):
    return sb.matches(competition_id=competacao_id, season_id=temporada_id)

@st.cache_data
def cache_eventos(partida_id):
    return sb.events(match_id=partida_id)

st.title("Estatísticas Futebolísticas")

menu = st.sidebar.radio("Navegue Entre Estatísticas", ["Estatísticas da Partida", "Dados dos Jogadores", "Gráficos Comparativos"])

competicoes = cache_competicoes()
competicao_selecionada = st.sidebar.selectbox("Selecione uma competição:", competicoes["competition_name"].unique())
competicao_filtrada = competicoes[competicoes["competition_name"] == competicao_selecionada]
temporadas = competicao_filtrada[["competition_id", "season_id", "season_name"]].drop_duplicates()
temporada_selecionada = st.sidebar.selectbox("Selecione uma temporada:", temporadas["season_name"])
temporada_filtrada = temporadas[temporadas["season_name"] == temporada_selecionada].iloc[0]
partidas = cache_partidas(temporada_filtrada["competition_id"], temporada_filtrada["season_id"])
lista_de_partidas = partidas[["match_id", "home_team", "away_team", "home_score", "away_score", "match_date"]]
lista_de_partidas["nome_partida"] = lista_de_partidas["home_team"] + " vs " + lista_de_partidas["away_team"] + " (" + lista_de_partidas["match_date"].astype(str) + ")"
partida_selecionada = st.sidebar.selectbox("Selecione uma partida:", lista_de_partidas["nome_partida"])
partida_filtrada = lista_de_partidas[lista_de_partidas["nome_partida"] == partida_selecionada].iloc[0]
eventos = cache_eventos(partida_filtrada["match_id"])

if partida_filtrada["home_score"] > partida_filtrada["away_score"]:
    vencedor = partida_filtrada["home_team"]
elif partida_filtrada["home_score"] < partida_filtrada["away_score"]:
    vencedor = partida_filtrada["away_team"]
else:
    vencedor = "Empate"

if menu == "Estatísticas da Partida":
    eventos_casa = eventos[eventos["team"] == partida_filtrada["home_team"]]
    eventos_visitante = eventos[eventos["team"] == partida_filtrada["away_team"]]
    total_gols_casa = eventos_casa[eventos_casa["type"] == "Shot"]["shot_outcome"].value_counts().get("Goal", 0)
    total_passes_casa = len(eventos_casa[eventos_casa["type"] == "Pass"])
    total_chutes_casa = len(eventos_casa[eventos_casa["type"] == "Shot"])
    total_gols_visitante = eventos_visitante[eventos_visitante["type"] == "Shot"]["shot_outcome"].value_counts().get("Goal", 0)
    total_passes_visitante = len(eventos_visitante[eventos_visitante["type"] == "Pass"])
    total_chutes_visitante = len(eventos_visitante[eventos_visitante["type"] == "Shot"])
    st.subheader(f"Estatísticas do {partida_filtrada['home_team']}")
    st.metric("Gols: ",total_gols_casa)
    st.metric("Passes: ", total_passes_casa)
    st.metric("Chutes: ",total_chutes_casa)
    st.subheader(f"Estatísticas do {partida_filtrada['away_team']}")
    st.metric("Gols: ",total_gols_visitante)
    st.metric("Passes: ", total_passes_visitante)
    st.metric("Chutes: ",total_chutes_visitante)
    total_gols = total_gols_casa + total_gols_visitante
    total_passes = total_passes_casa + total_passes_visitante
    total_chutes = total_chutes_casa + total_chutes_visitante
    st.subheader("Estatísticas gerais da partida")
    st.write(f"Competição: {competicao_selecionada}")
    st.write(f"Temporada: {temporada_selecionada}")
    st.write(f"Partida: {partida_filtrada['home_team']} vs {partida_filtrada['away_team']}")
    st.metric("Placar", f"{partida_filtrada['home_score']} - {partida_filtrada['away_score']}")
    st.write(f"Time vencedor: {vencedor}")
    st.metric("Total de Gols ",total_gols)
    st.metric("Total de Passes ", total_passes)
    st.metric("Total de Chutes ",total_chutes)

if menu == "Dados dos Jogadores":
    jogadores = eventos["player"].dropna().unique()
    jogador1 = st.sidebar.selectbox("Selecione o Jogador 1", jogadores)    
    jogadores_2 = [jogador for jogador in jogadores if jogador != jogador1]
    jogador2 = st.sidebar.selectbox("Selecione o Jogador 2", jogadores_2)
    eventos_jogador1 = eventos[eventos["player"] == jogador1]
    eventos_jogador2 = eventos[eventos["player"] == jogador2]
    total_passes_jogador1 = len(eventos_jogador1[eventos_jogador1["type"] == "Pass"])
    total_chutes_jogador1 = len(eventos_jogador1[eventos_jogador1["type"] == "Shot"])
    gols_jogador1 = eventos_jogador1[eventos_jogador1["type"] == "Shot"]["shot_outcome"].value_counts().get("Goal", 0)
    total_passes_jogador2 = len(eventos_jogador2[eventos_jogador2["type"] == "Pass"])
    total_chutes_jogador2 = len(eventos_jogador2[eventos_jogador2["type"] == "Shot"])
    gols_jogador2 = eventos_jogador2[eventos_jogador2["type"] == "Shot"]["shot_outcome"].value_counts().get("Goal", 0)
    st.write(f"Estatísticas de {jogador1}")
    st.metric("Passes: ", total_passes_jogador1)
    st.metric("Chutes: ", total_chutes_jogador1)
    st.metric("Gols: ", gols_jogador1)
    st.write(f"Estatísticas de {jogador2}")
    st.metric("Passes: ", total_passes_jogador2)
    st.metric("Chutes: ", total_chutes_jogador2)
    st.metric("Gols: ", gols_jogador2)
    intervalo_tempo = st.sidebar.slider("Selecione o intervalo de minutos", 0, 90, (0, 90))
    eventos_filtrados1 = eventos_jogador1[(eventos_jogador1["minute"] >= intervalo_tempo[0]) & (eventos_jogador1["minute"] <= intervalo_tempo[1])]
    eventos_filtrados2 = eventos_jogador2[(eventos_jogador2["minute"] >= intervalo_tempo[0]) & (eventos_jogador2["minute"] <= intervalo_tempo[1])]
    st.write(f"Eventos de {jogador1} entre {intervalo_tempo[0]} e {intervalo_tempo[1]} minutos")
    st.dataframe(eventos_filtrados1[["minute", "type", "location", "player", "team"]])
    st.write(f"Eventos de {jogador2} entre {intervalo_tempo[0]} e {intervalo_tempo[1]} minutos")
    st.dataframe(eventos_filtrados2[["minute", "type", "location", "player", "team"]])
    st.download_button(f"Baixar dados de {jogador1} em CSV", eventos_filtrados1.to_csv(), file_name=f"{jogador1}_eventos.csv")
    st.download_button(f"Baixar dados de {jogador2} em CSV", eventos_filtrados2.to_csv(), file_name=f"{jogador2}_eventos.csv")

if menu == "Gráficos Comparativos":
    jogadores = eventos["player"].dropna().unique()
    jogador1 = st.sidebar.selectbox("Selecione o Jogador 1:", jogadores, key="grafico_jogador1")
    jogadores_2 = [jogador for jogador in jogadores if jogador != jogador1]
    jogador2 = st.sidebar.selectbox("Selecione o Jogador 2:", jogadores_2, key="grafico_jogador2")
    campo = Pitch(line_color="black")    
    figura_passes, eixo_passes = campo.draw(figsize=(10, 6))
    passes_jogador1 = eventos[eventos["player"] == jogador1][eventos["type"] == "Pass"]
    passes_jogador2 = eventos[eventos["player"] == jogador2][eventos["type"] == "Pass"]

    for i, passe in passes_jogador1.iterrows():
        campo.arrows(passe["location"][0], passe["location"][1], passe["pass_end_location"][0], passe["pass_end_location"][1], 
                     ax=eixo_passes, color="blue", width=2, headwidth=3, headlength=4, label=f"{jogador1} (Azul)")

    for i, passe in passes_jogador2.iterrows():
        campo.arrows(passe["location"][0], passe["location"][1], passe["pass_end_location"][0], passe["pass_end_location"][1], 
                     ax=eixo_passes, color="orange", width=2, headwidth=3, headlength=4, label=f"{jogador2} (Laranja)")

    eixo_passes.set_title("Mapa de Passes", fontsize=14)
    eixo_passes.legend(handles=[
        plt.Line2D([0], [0], color="blue", lw=4, label=f"{jogador1} (Azul)"),
        plt.Line2D([0], [0], color="orange", lw=4, label=f"{jogador2} (Laranja)")
    ])
    st.pyplot(figura_passes)
    figura_chutes1, eixo_chutes1 = campo.draw(figsize=(10, 6))
    chutes_jogador1 = eventos[eventos["player"] == jogador1][eventos["type"] == "Shot"]

    for i, chute in chutes_jogador1.iterrows():
        cor = "green" if chute["shot_outcome"] == "Goal" else "red"
        campo.scatter(chute["location"][0], chute["location"][1], ax=eixo_chutes1, color=cor, s=100, edgecolor="black", lw=1)
    eixo_chutes1.set_title(f"Mapa de Chutes - {jogador1}", fontsize=14)
    eixo_chutes1.legend(handles=[
        plt.Line2D([0], [0], color="green", marker="o", lw=0, label="Chute com Gol (Verde)"),
        plt.Line2D([0], [0], color="red", marker="o", lw=0, label="Chute Sem Gol (Vermelho)")
    ])
    st.pyplot(figura_chutes1)

    figura_chutes2, eixo_chutes2 = campo.draw(figsize=(10, 6))
    chutes_jogador2 = eventos[eventos["player"] == jogador2][eventos["type"] == "Shot"]
    for i, chute in chutes_jogador2.iterrows():
        cor = "green" if chute["shot_outcome"] == "Goal" else "red"
        campo.scatter(chute["location"][0], chute["location"][1], ax=eixo_chutes2, color=cor, s=100, edgecolor="black", lw=1)
    eixo_chutes2.set_title(f"Mapa de Chutes - {jogador2}", fontsize=14)
    eixo_chutes2.legend(handles=[
        plt.Line2D([0], [0], color="green", marker="o", lw=0, label="Chute com Gol (Verde)"),
        plt.Line2D([0], [0], color="red", marker="o", lw=0, label="Chute Sem Gol (Vermelho)")
    ])
    st.pyplot(figura_chutes2)
