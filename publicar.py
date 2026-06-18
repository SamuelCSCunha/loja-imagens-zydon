#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Le suas escolhas (escolhas.json), copia as imagens escolhidas para imagens/,
faz commit + push no repositorio GitHub e gera o resultado.csv com os links
servidos pela CDN do jsDelivr.

Pre-requisito: esta pasta precisa ser um repo git com 'origin' apontando para
um repositorio PUBLICO no GitHub. (O assistente configura isso na 1a vez.)

Uso:
    python publicar.py                 # procura escolhas.json na pasta e em ~/Downloads
    python publicar.py caminho.json
"""
import sys, os, re, json, csv, shutil, subprocess, glob

IMG_DIR = "imagens"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def achar_escolhas():
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        return sys.argv[1]
    if os.path.exists("escolhas.json"):
        return "escolhas.json"
    # navegador costuma salvar em Downloads
    home = os.path.expanduser("~")
    cands = glob.glob(os.path.join(home, "Downloads", "escolhas*.json"))
    if cands:
        return max(cands, key=os.path.getmtime)
    return None


def user_repo():
    r = git("remote", "get-url", "origin")
    if r.returncode != 0:
        sys.exit("ERRO: nao ha 'origin' git. Configure o repositorio GitHub primeiro.")
    url = r.stdout.strip()
    m = re.search(r"github\.com[:/]([^/]+)/(.+?)(?:\.git)?$", url)
    if not m:
        sys.exit(f"ERRO: nao reconheci o remote: {url}")
    return m.group(1), m.group(2)


def main():
    cam = achar_escolhas()
    if not cam:
        sys.exit("Nao achei escolhas.json. Baixe da galeria.html e rode de novo.")
    print(f"Usando escolhas: {cam}")

    escolhas = json.load(open(cam, encoding="utf-8"))
    manifest = json.load(open("manifest.json", encoding="utf-8"))
    nome_por_slug = {m["slug"]: m["produto"] for m in manifest}

    os.makedirs(IMG_DIR, exist_ok=True)
    linhas, pulados = [], []
    for slug, arq in escolhas.items():
        if not arq:
            pulados.append(nome_por_slug.get(slug, slug))
            continue
        origem = os.path.join("candidatos", arq)
        if not os.path.exists(origem):
            pulados.append(nome_por_slug.get(slug, slug))
            continue
        destino = os.path.join(IMG_DIR, f"{slug}.jpg")
        shutil.copyfile(origem, destino)
        linhas.append((slug, nome_por_slug.get(slug, slug)))

    if not linhas:
        sys.exit("Nenhuma imagem escolhida. Nada a publicar.")

    user, repo = user_repo()
    git("add", IMG_DIR)
    c = git("commit", "-m", f"imagens: +{len(linhas)} produto(s)")
    if c.returncode != 0 and "nothing to commit" not in (c.stdout + c.stderr):
        print(c.stdout, c.stderr)
    p = git("push", "origin", "HEAD")
    if p.returncode != 0:
        print("ERRO no push:", p.stderr)
        sys.exit(1)

    base = f"https://cdn.jsdelivr.net/gh/{user}/{repo}@main/{IMG_DIR}"
    with open("resultado.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["produto", "url_imagem"])
        for slug, prod in linhas:
            w.writerow([prod, f"{base}/{slug}.jpg"])

    print(f"\nPublicado {len(linhas)} imagem(ns). Links em resultado.csv")
    print(f"Exemplo: {base}/{linhas[0][0]}.jpg")
    if pulados:
        print(f"Sem imagem (pulados): {', '.join(pulados)}")


if __name__ == "__main__":
    main()
