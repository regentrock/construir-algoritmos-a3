#baixar: requests, folium, python-dotenv

import requests
import folium

import os
from dotenv import load_dotenv

#variáveis .env
load_dotenv()

#token da SPTrans
TOKEN = os.getenv("SPTRANS_TOKEN")

LINHA = "875A-10"

URL = "https://api.olhovivo.sptrans.com.br/v2.1"

#sessão autenticada
sessao = requests.Session()


#Autenticação API
resposta = sessao.post(
    URL + "/Login/Autenticar",
    params={"token": TOKEN}
)

if resposta.text.lower() != "true":
    print("Erro na autenticação. Verifique seu token.")
    exit()

print("Autenticação realizada com sucesso.")


# Busca a linha de ônibus
resposta = sessao.get(
    URL + "/Linha/Buscar",
    params={"termosBusca": LINHA}
)
linhas = resposta.json()
print(linhas)

codigo_linha = None

for linha in linhas:
    if linha["lt"] == "875A" and linha["tl"] == 10:
        codigo_linha = linha["cl"]
        break

if codigo_linha is None:
    print("Linha não encontrada. Verifique o número escolhido.")
    exit()


# Busca as paradas da linha
resposta = sessao.get(
    URL + "/Parada/BuscarParadasPorLinha",
    params={"codigoLinha": codigo_linha}
)
paradas = resposta.json()


# Busca a posição dos ônibus em circulação
resposta = sessao.get(
    URL + "/Posicao/Linha",
    params={"codigoLinha": codigo_linha}
)
dados = resposta.json()
onibus = dados.get("vs", [])


# mapa
latitudes = [p["py"] for p in paradas if p["py"]]
longitudes = [p["px"] for p in paradas if p["px"]]

if latitudes:
    centro = [sum(latitudes) / len(latitudes),
              sum(longitudes) / len(longitudes)]
else:
    centro = [-23.5505, -46.6333]

mapa = folium.Map(location=centro, zoom_start=13, tiles=None)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri",
    name="Mapa de ruas",
    overlay=False,
    control=True
).add_to(mapa)


# paradas - azul
for parada in paradas:
    if parada["py"] and parada["px"]:
        folium.Marker(
            location=[parada["py"], parada["px"]],
            popup=parada["np"],
            tooltip="Parada de ônibus",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mapa)


# ônibus - vermelho
for veiculo in onibus:
    if veiculo["py"] and veiculo["px"]:
        folium.Marker(
            location=[veiculo["py"], veiculo["px"]],
            popup="Ônibus: " + str(veiculo["p"]),
            tooltip="Ônibus em circulação",
            icon=folium.Icon(color="red", icon="bus")
        ).add_to(mapa)


# mapa
mapa.save("mapa.html")

print("Paradas encontradas:", len(paradas))
print("Ônibus encontrados:", len(onibus))
print("Mapa salvo em mapa.html")
