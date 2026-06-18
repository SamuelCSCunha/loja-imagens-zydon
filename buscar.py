#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Busca fotos reais de produtos no DuckDuckGo (sem chave), baixa os 3 melhores
candidatos de cada e gera uma galeria HTML para voce escolher.

Uso:
    python buscar.py                      # le os produtos de produtos.txt (1 por linha)
    python buscar.py "Tenis Nike" "..."   # ou passa os produtos como argumentos

Saidas:
    candidatos/<slug>__1.jpg ...   imagens baixadas
    manifest.json                  mapa produto -> candidatos
    galeria.html                   abra no navegador para escolher
"""
import sys, os, re, json, io, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from ddgs import DDGS
from PIL import Image

# ---------- configuracao ----------
N_CANDIDATOS = 3        # quantas opcoes guardar por produto
BUSCA_MAX    = 18       # quantos resultados pedir ao buscador (antes de filtrar)
MIN_LADO     = 500      # px: descarta imagem com lado menor que isso
ASPECTO_MIN  = 0.5      # razao largura/altura aceitavel
ASPECTO_MAX  = 2.0
WORKERS      = 6        # buscas simultaneas (baixo de proposito: evita rate-limit)
TIMEOUT      = 15
OUT_DIR      = "candidatos"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
# ----------------------------------


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "produto"


def baixar_validar(url: str):
    """Baixa a imagem e valida com Pillow. Retorna (bytes_jpeg, w, h) ou None."""
    try:
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content))
        img.load()
        w, h = img.size
        if w < MIN_LADO or h < MIN_LADO:
            return None
        if not (ASPECTO_MIN <= w / h <= ASPECTO_MAX):
            return None
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        elif img.mode == "L":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue(), w, h
    except Exception:
        return None


def buscar_produto(produto: str):
    s = slug(produto)
    try:
        resultados = DDGS().images(produto, max_results=BUSCA_MAX)
    except Exception as e:
        print(f"  [ERRO busca] {produto}: {e}")
        return {"produto": produto, "slug": s, "candidatos": []}

    candidatos = []
    for item in resultados:
        if len(candidatos) >= N_CANDIDATOS:
            break
        url = item.get("image")
        if not url:
            continue
        out = baixar_validar(url)
        if not out:
            continue
        data, w, h = out
        idx = len(candidatos) + 1
        nome = f"{s}__{idx}.jpg"
        with open(os.path.join(OUT_DIR, nome), "wb") as f:
            f.write(data)
        candidatos.append({"arquivo": nome, "origem": url, "w": w, "h": h})

    status = "ok" if candidatos else "VAZIO"
    print(f"  [{status}] {produto} -> {len(candidatos)} candidato(s)")
    return {"produto": produto, "slug": s, "candidatos": candidatos}


def carregar_produtos():
    if len(sys.argv) > 1:
        return [a.strip() for a in sys.argv[1:] if a.strip()]
    if os.path.exists("produtos.txt"):
        with open("produtos.txt", encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return []


def gerar_galeria(manifest):
    cards = []
    for item in manifest:
        s, prod = item["slug"], item["produto"]
        opts = ['<label class="op"><input type="radio" name="%s" value=""><span class="nao">sem imagem</span></label>' % s]
        for c in item["candidatos"]:
            opts.append(
                '<label class="op"><input type="radio" name="{s}" value="{f}">'
                '<img src="candidatos/{f}" loading="lazy"><small>{w}x{h}</small></label>'.format(
                    s=s, f=c["arquivo"], w=c["w"], h=c["h"]))
        cards.append(
            '<section><h2>{p}</h2><div class="row">{o}</div></section>'.format(
                p=prod, o="".join(opts)))

    html = """<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<title>Galeria - escolher imagens</title><style>
body{{font-family:system-ui,Arial;margin:0;background:#0f1115;color:#e8e8e8}}
header{{position:sticky;top:0;background:#161a22;padding:14px 20px;display:flex;
gap:16px;align-items:center;box-shadow:0 2px 8px #0008;z-index:9}}
h1{{font-size:16px;margin:0}} h2{{font-size:14px;margin:18px 20px 6px;color:#9fb4ff}}
.row{{display:flex;gap:12px;flex-wrap:wrap;padding:0 20px 8px}}
.op{{cursor:pointer;border:2px solid #2a2f3a;border-radius:10px;padding:6px;
display:flex;flex-direction:column;align-items:center;gap:4px;background:#161a22}}
.op img{{width:150px;height:150px;object-fit:contain;background:#fff;border-radius:6px}}
.op:has(input:checked){{border-color:#5b8cff;background:#1d2740}}
.op input{{display:none}} .nao{{width:150px;height:150px;display:flex;
align-items:center;justify-content:center;color:#888;font-size:13px}}
small{{color:#888;font-size:11px}}
button{{background:#5b8cff;border:0;color:#fff;padding:10px 18px;border-radius:8px;
font-weight:600;cursor:pointer}} #cnt{{color:#9aa}}</style></head><body>
<header><h1>Escolha 1 imagem por produto</h1>
<span id="cnt"></span><button onclick="baixar()">Baixar escolhas.json</button></header>
{cards}
<script>
const slugs={slugs};
function atualiza(){{let n=0;for(const s of slugs){{const v=document.querySelector(
'input[name="'+s+'"]:checked');if(v&&v.value)n++;}}
document.getElementById('cnt').textContent=n+'/'+slugs.length+' escolhidos';}}
document.addEventListener('change',atualiza);atualiza();
function baixar(){{const out={{}};for(const s of slugs){{const v=document.querySelector(
'input[name="'+s+'"]:checked');out[s]=v?v.value:"";}}
const b=new Blob([JSON.stringify(out,null,2)],{{type:'application/json'}});
const a=document.createElement('a');a.href=URL.createObjectURL(b);
a.download='escolhas.json';a.click();}}
</script></body></html>""".format(
        cards="\n".join(cards),
        slugs=json.dumps([m["slug"] for m in manifest]))

    with open("galeria.html", "w", encoding="utf-8") as f:
        f.write(html)


def main():
    produtos = carregar_produtos()
    if not produtos:
        with open("produtos.txt", "w", encoding="utf-8") as f:
            f.write("# 1 produto por linha. Apague estas linhas e liste os seus.\n"
                    "Tenis Nike Air Max masculino\nCamiseta polo azul marinho\n")
        print("Criei produtos.txt com exemplos. Edite e rode de novo.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Buscando {len(produtos)} produto(s) com {WORKERS} buscas simultaneas...\n")
    manifest = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(buscar_produto, p): p for p in produtos}
        for fut in as_completed(futs):
            manifest.append(fut.result())

    # mantem a ordem original dos produtos
    ordem = {p: i for i, p in enumerate(produtos)}
    manifest.sort(key=lambda m: ordem.get(m["produto"], 0))

    with open("manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    gerar_galeria(manifest)

    vazios = [m["produto"] for m in manifest if not m["candidatos"]]
    print(f"\nPronto. Abra galeria.html no navegador para escolher.")
    if vazios:
        print(f"ATENCAO: sem candidato para: {', '.join(vazios)}")


if __name__ == "__main__":
    main()
