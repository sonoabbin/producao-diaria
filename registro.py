#!/usr/bin/env python
"""Registro de producao diaria. Stdlib only.

  python registro.py add --titulo "..." --tipo codigo --resumo "..." [--artefato PATH] [--tags "a,b"]
  python registro.py index      # regenera index.html
  python registro.py stats      # numeros no terminal
"""
import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, date
from html import escape

BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "ledger.jsonl")
INDEX = os.path.join(BASE, "index.html")

TIPOS = {
    "codigo":   {"label": "Código",    "cor": "#22d3ee"},
    "decisao":  {"label": "Decisão",   "cor": "#a78bfa"},
    "projeto":  {"label": "Projeto",   "cor": "#34d399"},
    "duvida":   {"label": "Dúvida",    "cor": "#fbbf24"},
    "estudo":   {"label": "Estudo",    "cor": "#60a5fa"},
    "entrega":  {"label": "Entrega",   "cor": "#f472b6"},
}


def ler():
    if not os.path.exists(LEDGER):
        return []
    itens = []
    with open(LEDGER, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                try:
                    itens.append(json.loads(linha))
                except json.JSONDecodeError:
                    pass
    return itens


def add(args):
    if args.tipo not in TIPOS:
        raise SystemExit(f"tipo invalido: {args.tipo}. use: {', '.join(TIPOS)}")
    itens = ler()
    item = {
        "id": len(itens) + 1,
        "data": args.data or date.today().isoformat(),
        "hora": datetime.now().strftime("%H:%M"),
        "tipo": args.tipo,
        "titulo": args.titulo.strip(),
        "resumo": " ".join(args.resumo.split()),
        "artefato": args.artefato or "",
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
    }
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"OK #{item['id']} {item['data']} [{item['tipo']}] {item['titulo']}")
    gerar(existente=None)


def gerar(existente=None):
    itens = existente if existente is not None else ler()
    itens.sort(key=lambda i: (i.get("data", ""), i.get("hora", "")), reverse=True)

    por_tipo = Counter(i.get("tipo", "?") for i in itens)
    por_dia = Counter(i.get("data", "?") for i in itens)
    tags = Counter(t for i in itens for t in i.get("tags", []))
    dias_ativos = len(por_dia)

    def dia_da_escrita():
        if not itens:
            return "—"
        ds = sorted(por_dia)
        d1 = date.fromisoformat(ds[0])
        d2 = date.fromisoformat(ds[-1])
        fmt = lambda d: f"{d.day:02d}/{d.month:02d}"
        return fmt(d1) if len(ds) == 1 else f"{fmt(d1)} → {fmt(d2)}"

    # agrupa por data
    grupos = {}
    for i in itens:
        grupos.setdefault(i.get("data", "?"), []).append(i)

    tipos_html = "".join(
        f'<div class="kpi"><b style="color:{TIPOS.get(t,{}).get("cor","#94a3b8")}">{n}</b>'
        f'<span>{escape(TIPOS.get(t,{}).get("label",t))}</span></div>'
        for t, n in por_tipo.most_common()
    )

    tags_html = "".join(
        f'<span class="tag">{escape(t)}<i>{n}</i></span>' for t, n in tags.most_common(14)
    )

    blocos = []
    for d in sorted(grupos, reverse=True):
        linhas = []
        for i in grupos[d]:
            cor = TIPOS.get(i.get("tipo", ""), {}).get("cor", "#94a3b8")
            label = TIPOS.get(i.get("tipo", ""), {}).get("label", i.get("tipo", ""))
            art = ""
            if i.get("artefato"):
                a = escape(i["artefato"])
                art = f'<div class="art">↳ {a}</div>'
            tg = "".join(f'<span class="t">#{escape(t)}</span>' for t in i.get("tags", []))
            hora = i.get("hora", "")
            hora_html = f'<span class="hora">{escape(hora)}</span>' if hora not in ("", "—") else ""
            linhas.append(
                f'<li style="--c:{cor}">'
                f'<div class="head"><span class="badge">{escape(label)}</span>'
                f'<b>{escape(i.get("titulo",""))}</b>'
                f'{hora_html}</div>'
                f'<p>{escape(i.get("resumo",""))}</p>{art}'
                f'<div class="tags">{tg}</div></li>'
            )
        n = len(grupos[d])
        blocos.append(
            f'<section><h2>{escape(d)}<small>{n} registro{"s" if n>1 else ""}</small></h2>'
            f'<ul>{"".join(linhas)}</ul></section>'
        )

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Produção diária — Abbin</title>
<style>
  *{{box-sizing:border-box}}
  body{{margin:0;font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
       color:var(--foreground,#e6e8eb);background:transparent;padding:22px 24px 40px}}
  header{{border-bottom:1px solid var(--border,#2a2f38);padding-bottom:16px;margin-bottom:22px}}
  h1{{margin:0 0 4px;font-size:21px;letter-spacing:-.2px}}
  .sub{{color:var(--muted-foreground,#98a2b3);font-size:13px}}
  .bar{{display:flex;flex-wrap:wrap;gap:26px;margin:18px 0 8px}}
  .kpi{{display:flex;flex-direction:column;font-size:12px;color:var(--muted-foreground,#98a2b3)}}
  .kpi b{{font-size:24px;line-height:1.1;font-variant-numeric:tabular-nums}}
  .tagsbar{{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 0}}
  .tag{{font-size:11px;border:1px solid var(--border,#2a2f38);border-radius:20px;padding:2px 9px;
        color:var(--muted-foreground,#98a2b3)}}
  .tag i{{font-style:normal;opacity:.6;margin-left:6px}}
  section{{margin:26px 0 0}}
  h2{{font-size:14px;letter-spacing:.4px;text-transform:uppercase;margin:0 0 10px;
      color:var(--muted-foreground,#98a2b3);display:flex;gap:10px;align-items:baseline}}
  h2 small{{font-size:11px;text-transform:none;letter-spacing:0;opacity:.65}}
  ul{{list-style:none;margin:0;padding:0}}
  li{{position:relative;border-left:2px solid var(--c,#333);padding:2px 0 16px 16px;margin-left:3px}}
  li:last-child{{padding-bottom:0}}
  .head{{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap}}
  .head b{{font-size:14.5px;font-weight:600}}
  .badge{{font-size:10px;letter-spacing:.5px;text-transform:uppercase;color:var(--c);
          border:1px solid color-mix(in srgb,var(--c) 45%,transparent);border-radius:4px;padding:1px 6px}}
  .hora{{font-size:11px;color:var(--muted-foreground,#98a2b3);margin-left:auto;font-variant-numeric:tabular-nums}}
  li p{{margin:5px 0 0;font-size:13.5px;color:var(--foreground,#e6e8eb);opacity:.88;max-width:88ch}}
  .art{{font-size:11.5px;color:var(--muted-foreground,#98a2b3);margin-top:5px;
        font-family:ui-monospace,SFMono-Regular,Consolas,monospace;word-break:break-all}}
  .tags{{margin-top:6px;display:flex;gap:6px;flex-wrap:wrap}}
  .t{{font-size:10.5px;color:var(--accent,#7dd3fc);opacity:.8}}
  footer{{margin-top:34px;padding-top:14px;border-top:1px solid var(--border,#2a2f38);
          font-size:11.5px;color:var(--muted-foreground,#98a2b3)}}
  .vazio{{color:var(--muted-foreground,#98a2b3);font-size:13px}}
</style></head><body>
<header>
  <h1>Produção diária</h1>
  <div class="sub">Abbin + Hermes · histórico de trabalho com IA · atualizado {datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
  <div class="bar">
    <div class="kpi"><b>{len(itens)}</b><span>registros</span></div>
    <div class="kpi"><b>{dias_ativos}</b><span>dias ativos</span></div>
    <div class="kpi"><b>{dia_da_escrita()}</b><span>período</span></div>
    {tipos_html}
  </div>
  <div class="tagsbar">{tags_html}</div>
</header>
{"".join(blocos) if blocos else '<p class="vazio">Nenhum registro ainda. Rode <code>python registro.py add ...</code></p>'}
<footer>Fonte: ledger.jsonl · <code>python registro.py index</code> regenera este painel</footer>
</body></html>"""
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(html)
    return len(itens)


def stats(args):
    itens = ler()
    if not itens:
        print("ledger vazio")
        return
    por_tipo = Counter(i.get("tipo") for i in itens)
    por_dia = sorted({i.get("data") for i in itens})
    print(f"registros: {len(itens)}  |  dias ativos: {len(por_dia)}  |  {por_dia[0]} -> {por_dia[-1]}")
    for t, n in por_tipo.most_common():
        print(f"  {t:9s} {n}")
    print(f"  tags: {len({t for i in itens for t in i.get('tags', [])})}")


def main():
    p = argparse.ArgumentParser(description="Registro de producao diaria")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--titulo", required=True)
    a.add_argument("--tipo", required=True, choices=list(TIPOS))
    a.add_argument("--resumo", required=True)
    a.add_argument("--artefato", default="")
    a.add_argument("--tags", default="")
    a.add_argument("--data", default="")
    a.set_defaults(func=add)

    i = sub.add_parser("index")
    i.set_defaults(func=lambda x: print(f"index.html gerado com {gerar()} registros"))

    s = sub.add_parser("stats")
    s.set_defaults(func=stats)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
