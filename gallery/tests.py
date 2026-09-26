from urllib.parse import quote

from django.test import TestCase
from django.urls import reverse

from .data import PAINTINGS
from .forms import SearchForm


class IndexViewTests(TestCase):

    def test_index_returns_200(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "gallery/index.html")

    def test_index_shows_all_paintings_by_default(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context["paintings"]), len(PAINTINGS))

    def test_index_contains_every_painting_title(self):
        response = self.client.get(reverse("index"))
        for p in PAINTINGS:
            self.assertContains(response, p["title"])


class SearchTests(TestCase):

    def test_search_by_author_cyrillic(self):
        response = self.client.get(reverse("index"), {"query": "Моне"})
        titles = [p["title"] for p in response.context["paintings"]]
        self.assertIn("Водяные лилии", titles)

    def test_search_by_title_cyrillic(self):
        response = self.client.get(reverse("index"), {"query": "Крик"})
        titles = [p["title"] for p in response.context["paintings"]]
        self.assertIn("Крик", titles)

    def test_search_is_case_insensitive(self):
        lower = self.client.get(reverse("index"), {"query": "моне"})
        upper = self.client.get(reverse("index"), {"query": "МОНЕ"})
        self.assertEqual(
            len(lower.context["paintings"]),
            len(upper.context["paintings"]),
        )

    def test_search_partial_match(self):
        response = self.client.get(reverse("index"), {"query": "ван"})
        titles = [p["title"] for p in response.context["paintings"]]
        self.assertIn("Звёздная ночь", titles)

    def test_search_no_results(self):
        response = self.client.get(reverse("index"), {"query": "xyz123"})
        self.assertEqual(len(response.context["paintings"]), 0)

    def test_search_empty_query_shows_all(self):
        response = self.client.get(reverse("index"), {"query": ""})
        self.assertEqual(len(response.context["paintings"]), len(PAINTINGS))


class LastQueryCookieTests(TestCase):

    def test_cookie_set_after_search(self):
        response = self.client.get(reverse("index"), {"query": "Моне"})
        self.assertIn("last_query", response.cookies)

    def test_cookie_cyrillic_is_ascii_encoded(self):
        response = self.client.get(reverse("index"), {"query": "Моне"})
        value = response.cookies["last_query"].value
        self.assertEqual(value, quote("Моне"))
        self.assertTrue(value.isascii())

    def test_cookie_restored_into_form_on_next_visit(self):
        self.client.get(reverse("index"), {"query": "Моне"})
        response = self.client.get(reverse("index"))
        self.assertEqual(response.context["form"].initial["query"], "Моне")

    def test_cookie_not_set_on_empty_search(self):
        response = self.client.get(reverse("index"))
        self.assertNotIn("last_query", response.cookies)


class PaintingDetailTests(TestCase):

    def test_detail_returns_200(self):
        response = self.client.get(
            reverse("painting_detail", args=["mona-lisa"])
        )
        self.assertEqual(response.status_code, 200)

    def test_detail_uses_correct_template(self):
        response = self.client.get(
            reverse("painting_detail", args=["mona-lisa"])
        )
        self.assertTemplateUsed(response, "gallery/painting_detail.html")

    def test_detail_context_contains_painting(self):
        response = self.client.get(
            reverse("painting_detail", args=["mona-lisa"])
        )
        self.assertEqual(response.context["painting"]["id"], "mona-lisa")

    def test_recent_cookie_set_after_viewing(self):
        response = self.client.get(
            reverse("painting_detail", args=["mona-lisa"])
        )
        self.assertIn("recent_paintings", response.cookies)
        self.assertEqual(
            response.cookies["recent_paintings"].value, "mona-lisa"
        )

    def test_recent_cookie_accumulates_in_reverse_order(self):
        self.client.get(reverse("painting_detail", args=["mona-lisa"]))
        self.client.get(reverse("painting_detail", args=["the-scream"]))
        self.assertEqual(
            self.client.cookies["recent_paintings"].value,
            "the-scream,mona-lisa",
        )

    def test_recent_cookie_moves_duplicate_to_front(self):
        self.client.get(reverse("painting_detail", args=["mona-lisa"]))
        self.client.get(reverse("painting_detail", args=["the-scream"]))
        self.client.get(reverse("painting_detail", args=["mona-lisa"]))
        self.assertEqual(
            self.client.cookies["recent_paintings"].value,
            "mona-lisa,the-scream",
        )

    def test_recent_cookie_limited_to_five(self):
        ids = [p["id"] for p in PAINTINGS[:6]]
        for pid in ids:
            self.client.get(reverse("painting_detail", args=[pid]))
        stored = self.client.cookies["recent_paintings"].value.split(",")
        self.assertEqual(len(stored), 5)
        self.assertEqual(stored[0], ids[-1])

    def test_recent_paintings_shown_on_index(self):
        self.client.get(reverse("painting_detail", args=["mona-lisa"]))
        response = self.client.get(reverse("index"))
        recent_titles = [p["title"] for p in response.context["recent_paintings"]]
        self.assertIn("Мона Лиза", recent_titles)


class SetThemeTests(TestCase):

    def test_set_theme_redirects(self):
        response = self.client.get(reverse("set_theme"))
        self.assertEqual(response.status_code, 302)

    def test_set_theme_redirects_to_next(self):
        response = self.client.get(
            reverse("set_theme"), {"next": "/painting_detail/mona-lisa/"}
        )
        self.assertEqual(response.url, "/painting_detail/mona-lisa/")

    def test_set_theme_default_redirect_is_index(self):
        response = self.client.get(reverse("set_theme"))
        self.assertEqual(response.url, "/")

    def test_theme_cookie_set_to_dark_from_light(self):
        response = self.client.get(reverse("set_theme"))
        self.assertEqual(response.cookies["theme"].value, "dark")

    def test_theme_toggles_back_to_light(self):
        self.client.get(reverse("set_theme"))
        response = self.client.get(reverse("set_theme"))
        self.assertEqual(response.cookies["theme"].value, "light")

    def test_dark_theme_class_applied_on_index(self):
        self.client.cookies["theme"] = "dark"
        response = self.client.get(reverse("index"))
        self.assertContains(response, "theme-dark")


class SearchFormTests(TestCase):

    def test_form_valid_with_empty_query(self):
        form = SearchForm({"query": ""})
        self.assertTrue(form.is_valid())

    def test_form_valid_with_cyrillic(self):
        form = SearchForm({"query": "Моне"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["query"], "Моне")

    def test_form_invalid_with_too_long_query(self):
        form = SearchForm({"query": "x" * 101})
        self.assertFalse(form.is_valid())

    def test_form_placeholder(self):
        form = SearchForm()
        html = str(form["query"])
        self.assertIn("Художник или название картины", html)