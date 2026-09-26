from django.shortcuts import render, redirect
from .data import PAINTINGS
from .forms import SearchForm

from urllib.parse import quote, unquote


def index(request):
    if request.GET:
        form = SearchForm(request.GET)
    else:
        last_query = unquote(request.COOKIES.get("last_query", "")) #last_query = request.COOKIES.get("last_query", "")
        form = SearchForm(initial={"query": last_query})

    paintings = PAINTINGS

    if form.is_valid() and form.cleaned_data["query"]:
        query = form.cleaned_data["query"].lower()
        paintings = []
        for p in PAINTINGS:
            if query in p["title"].lower() or query in p["author"].lower():
                paintings.append(p)

    recent = request.COOKIES.get("recent_paintings", "")
    if recent:
        recent_ids = recent.split(",")
    else:
        recent_ids = []

    recent_paintings = []
    for rid in recent_ids:
        for p in PAINTINGS:
            if p["id"] == rid:
                recent_paintings.append(p)
                break

    response = render(
        request,
        "gallery/index.html",
        {
            "paintings": paintings,
            "form": form,
            "recent_paintings": recent_paintings,
        },
    )

    if form.is_valid() and form.cleaned_data.get("query"):
        response.set_cookie(
            "last_query",
            quote(form.cleaned_data["query"]), #form.cleaned_data["query"],
            max_age=60 * 60 * 24 * 7
        )

    return response


def painting_detail(request, id):
    painting = None
    for p in PAINTINGS:
        if p["id"] == id:
            painting = p
            break

    response = render(request, "gallery/painting_detail.html", {"painting": painting})

    recent = request.COOKIES.get("recent_paintings", "")
    if recent:
        recent_ids = recent.split(",")
    else:
        recent_ids = []

    if id in recent_ids:
        recent_ids.remove(id)

    recent_ids.insert(0, id)
    recent_ids = recent_ids[:5]

    response.set_cookie(
        "recent_paintings",
        ",".join(recent_ids),
        max_age=60 * 60 * 24 * 30,
    )
    return response


def set_theme(request):
    current = request.COOKIES.get("theme", "light")
    new_theme = "dark" if current == "light" else "light"
    next_url = request.GET.get("next") or "/"

    response = redirect(next_url)
    response.set_cookie("theme", new_theme, max_age=60 * 60 * 24 * 365)
    return response