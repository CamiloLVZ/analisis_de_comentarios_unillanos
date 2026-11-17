"""Verificación reproducible de las reglas temáticas (solo lectura; no modifica el repo).

Uso (desde la raíz del repositorio, con las dependencias del proyecto instaladas):
    python verificacion_reglas.py
Imprime solo cifras agregadas; no muestra textos, IDs ni autores.
"""
from __future__ import annotations
import json, re, sys, unicodedata, importlib.util
from pathlib import Path
import pandas as pd

ROOT = Path.cwd()
try:
    from pysentimiento.preprocessing import preprocess_tweet
except ImportError:
    spec = importlib.util.spec_from_file_location("pre", sys.argv[1])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    preprocess_tweet = mod.preprocess_tweet
import emoji

def sa(t): return "".join(c for c in unicodedata.normalize("NFKD", str(t)) if not unicodedata.combining(c))
def words(t): return len(re.findall(r"\b\w+\b", re.sub(r"(@\w+|https?://\S+)", "", str(t))))

# Cargar datos preparados (que ya contienen text_normalized) o unificados
prep_file = ROOT / "data/preparados/prepared_comments.csv"
if prep_file.exists():
    d = pd.read_csv(prep_file, encoding="utf-8-sig")
else:
    d = pd.read_csv(ROOT / "data/final/comments_unified.csv", low_memory=False)
    d = d[d["text"].fillna("").str.strip() != ""].copy()
    d["text_normalized"] = d["text"].map(lambda t: preprocess_tweet(t, lang="es"))

R = json.loads((ROOT / "crisp_dm/04_modeling/theme_rules.json").read_text(encoding="utf-8"))
comp = [(c["name"], [(k, re.compile(sa(k), re.I)) for k in c["keywords"]]) for c in R["categories"]]
INS, FB = R["insufficient_content_label"], R["fallback"]

def hits(n):
    n = sa(str(n).lower())
    return [(nm, [k for k, p in ps if p.search(n)]) for nm, ps in comp if any(p.search(n) for _, p in ps)]

d["norm"] = d["text_normalized"].fillna("").map(lambda t: sa(str(t).lower()))
d["h"] = d["norm"].map(hits)

def theme(row):
    if row.h: return row.h[0][0]
    if bool(row.get("emoji_only", False)) or not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]", str(row.text)):
        return INS
    return INS if words(row.text) <= 2 else FB

d["theme"] = d.apply(theme, axis=1)

print("== Réplica de conteos por tema (comparar con theme_counts.csv) ==")
print(d["theme"].value_counts().to_string())
N = len(d); spec_n = int((~d.theme.isin([INS, FB])).sum())
print(f"\nCobertura de temas específicos: {spec_n}/{N} = {spec_n/N:.1%}")
print(f"Coincidencias en más de una categoría: {(d.h.map(len)>1).sum()} de {d.h.map(bool).sum()} con coincidencia")

# Protesta y movilización
protest = d[d.theme == "Protesta y movilización"]
print(f"\nProtesta y movilización asignados: {len(protest)} ({len(protest)/N:.2%})")

# Oferta académica
of = d[d.theme.str.startswith("Oferta")]
gen = re.compile(r"estudiante|programa|docente|profesor|clase|grado|academia|academic")
only_gen = of.h.map(lambda h: all(gen.search(k) for k in h[0][1]))
print(f"Oferta académica asignada solo por términos genéricos: {only_gen.sum()}/{len(of)} = {only_gen.mean():.1%}")

# Felicitaciones y expresiones de aprecio
F = d[d.theme.str.startswith("Felicit")]
weak = re.compile(r"gracias|excelente|feliz|hermos|maravillos|bendici|bravo")
strong = re.compile(r"felicit|felicidades|exito|orgullo|enhorabuena|buen trabajo|gran labor")
wk = F.norm.map(lambda t: bool(weak.search(sa(t.lower()))) and not strong.search(sa(t.lower())))
print(f"Felicitaciones asignada solo por términos de cortesía/elogio genérico: {wk.sum()}/{len(F)} = {wk.mean():.1%}")

# Efecto de descripción textual de emojis
alt = d["text"].map(lambda t: preprocess_tweet(emoji.replace_emoji(str(t), " "), lang="es")).map(hits)
alt1 = alt.map(lambda h: h[0][0] if h else "")
cur1 = d.h.map(lambda h: h[0][0] if h else "")
print(f"\nAsignaciones que cambian si se quita la descripción textual de emojis: {(alt1!=cur1).sum()} ({(alt1!=cur1).mean():.2%})")

# Residual y sin contenido
o = d[d.theme == FB]; ow = o.text.map(words)
print(f"\nResidual: {len(o)}; con 11+ palabras: {(ow>=11).sum()}; con signo '?': {o.text.str.contains(chr(63), regex=False).sum()}")
ins = d[d.theme == INS]; iw = ins.text.map(words)
eo = ins.text.map(lambda t: not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]", str(t)))
print(f"Sin contenido suficiente: {len(ins)}; sin letras ni números: {eo.sum()}; 1-2 palabras: {((iw>=1)&(iw<=2)&~eo).sum()}")
