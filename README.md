# Gerador de imagens de produto (para lojas admin.zydon)

Fluxo em 2 passos para popular produtos com imagem a partir do **nome**.

## 1. Buscar candidatos
```
python buscar.py "Tenis Nike Air Max" "Camiseta polo azul"
```
ou liste 1 produto por linha em `produtos.txt` e rode `python buscar.py`.

Baixa as 3 melhores fotos reais de cada produto (busca DuckDuckGo, sem chave)
e gera `galeria.html`.

## 2. Escolher
Abra `galeria.html` no navegador, clique na imagem certa de cada produto e
clique em **Baixar escolhas.json**.

## 3. Publicar
```
python publicar.py
```
Copia as escolhidas para `imagens/`, faz push neste repo e gera `resultado.csv`
com os links da CDN jsDelivr (prontos para colar no produto do admin.zydon).

## Avisos
- As imagens vêm da web aberta: **risco de direito de imagem/marca**. Ideal é
  trocar pela foto oficial do fornecedor quando a loja for real.
- A busca usa endpoint não-oficial: para lotes grandes, rode em blocos.
- O repositório é **público** (requisito do jsDelivr) — as imagens ficam visíveis.
