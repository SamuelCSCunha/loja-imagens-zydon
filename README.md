# Gerador de imagens de produto (para lojas admin.zydon)

A partir do **nome** do produto, acha a foto real e devolve o **link** pronto.

## Jeito mais facil: app de tela (duplo-clique)
1. Duplo-clique no atalho **"Gerador de Imagens"** (area de trabalho) ou no
   arquivo **`Gerador de Imagens.bat`**. Na 1a vez ele prepara o ambiente sozinho.
2. O navegador abre. **Arraste sua planilha .xlsx** (varias abas, ok).
3. Acompanhe o progresso. Aparece uma grade com a imagem escolhida de cada
   produto — clique para **trocar** por outra opcao, ou digite outro nome e ↻
   para buscar de novo.
4. Clique em **Gerar links e baixar planilha**.

> Deixe a janela preta (o "motor") aberta enquanto usa. Feche para encerrar.

---

## Alternativa por comando: planilha (1 linha)
```
python planilha.py minha_planilha.xlsx
```
- Le TODAS as abas do .xlsx.
- Em cada aba acha por cabecalho a coluna de nome (`produto`/`nome`/`item`/...)
  e a de imagem (`imagem`/`foto`/`url`/...). Se nao houver, cria a coluna `imagem`.
- Para cada produto SEM imagem, busca a 1a foto boa, publica e grava o link.
- Celulas ja preenchidas sao puladas (pode rodar de novo para completar).
- Salva `minha_planilha_COM_IMAGENS.xlsx` (nao altera o original).

> Planilha precisa ser `.xlsx` (Google Sheets: Arquivo > Baixar > .xlsx).

---

## Fluxo alternativo: escolher na mao (2 passos)
Use quando quiser revisar 3 opcoes por produto antes de publicar.

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
