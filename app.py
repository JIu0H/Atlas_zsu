# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import os

from news_feed import get_news
from structure_data import STRUCTURE

app = Flask(__name__)


RIGHT_CATEGORIES = [
    {"id": "flags", "name": "Бойові прапори", "anchor": "#regalia"},
    {"id": "heroes", "name": "Герої України", "anchor": "#heroes"},
    {"id": "cavaliers", "name": "Кавалери державних орденів", "anchor": "#cavaliers"},
    {"id": "patches", "name": "Нарукавні знаки", "anchor": "#symbols"},
    {"id": "combatpath", "name": "Бойовий шлях", "anchor": "#combat-path"},
]

MATERIALS = [
    {"kind": "Статут", "name": "Статут внутрішньої служби Збройних Сил України", "url": "#knowledge"},
    {"kind": "Статут", "name": "Стройовий статут Збройних Сил України", "url": "#knowledge"},
    {"kind": "Статут", "name": "Статут гарнізонної та вартової служб Збройних Сил України", "url": "#knowledge"},
    {"kind": "Статут", "name": "Дисциплінарний статут Збройних Сил України", "url": "#knowledge"},
    {"kind": "Бойовий статут", "name": "Бойовий статут Сухопутних військ. Частина II (батальйон, рота)", "url": "#knowledge"},
    {"kind": "Бойовий статут", "name": "Бойовий статут Сухопутних військ. Частина III (взвод, відділення, танк)", "url": "#knowledge"},
    {"kind": "Посібник", "name": "Рекомендації з морально-психологічного забезпечення", "url": "#knowledge"},
    {"kind": "Посібник", "name": "Пам'ятка командиру підрозділу щодо роботи з особовим складом", "url": "#knowledge"},
    {"kind": "Посібник", "name": "Методичні рекомендації з бойової підготовки підрозділу", "url": "#knowledge"},
    {"kind": "Наказ", "name": "Організація внутрішньої комунікації у військовій частині", "url": "#knowledge"},
]


@app.route("/")
def index():
    return render_template(
        "index.html",
        structure=STRUCTURE,
        right_categories=RIGHT_CATEGORIES,
        materials=MATERIALS,
        news=get_news(),
    )


@app.route("/brigade/37obrmp")
def brigade_37():
    return render_template("brigade.html")


@app.route("/brigade/77oaembr")
def brigade_77():
    return render_template("brigade_77.html")


@app.route("/brigade/92oshbr")
def brigade_92():
    return render_template("brigade_92.html")


@app.route("/search")
def search():
    query = (request.args.get("q") or "").strip()
    q = query.casefold()
    results = []
    seen = set()

    def add(typ, name, url):
        key = (name, url)
        if key in seen or not name:
            return
        seen.add(key)
        results.append({"type": typ, "name": name, "url": url or "#"})

    if q:
        aliases = {
            "37": "37",
            "77": "77",
            "92": "92",
            "ошбр": "штурмов",
            "обрмп": "морськ",
            "оаембр": "аеромоб",
            "дшв": "десантно",
            "статут": "статут",
        }
        q_extra = [q]
        for k, v in aliases.items():
            if k in q:
                q_extra.append(v)

        def match(text):
            tcf = (text or "").casefold()
            return any(x in tcf for x in q_extra)

        for cat in STRUCTURE:
            if match(cat["name"]):
                add("Вид військ", cat["name"], "/#structure")
            for corps in cat.get("corps", []):
                cname = corps.get("name", "")
                if match(cname):
                    add("Корпус", cname, "/#structure")
                for u in corps.get("units", []):
                    if isinstance(u, dict):
                        name = u.get("name", "")
                        url = u.get("url") or "/#structure"
                        if match(name):
                            add("Бригада", name, url)
                    else:
                        if match(str(u)):
                            add("Підрозділ", str(u), "/#structure")

        for cat in RIGHT_CATEGORIES:
            if match(cat.get("name", "")):
                add("Розділ", cat["name"], "/#" + cat["id"])

        if match("база знань") or match("базу знань") or match("методичн") or match("статут") or match("посібник") or match("матеріал"):
            add("Розділ", "База знань", "/#knowledge")
        for m in MATERIALS:
            if match(m["name"]) or match(m["kind"]):
                add(m["kind"], m["name"], "/#knowledge")

    return jsonify({"query": query, "results": results[:40]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
