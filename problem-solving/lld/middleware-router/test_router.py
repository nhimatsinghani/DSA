import unittest

from router import Router


class TestRouter(unittest.TestCase):
    def test_exact_route(self):
        r = Router()
        r.add_route("/bar", "result")
        self.assertEqual(r.call_route("/bar"), "result")
        self.assertIsNone(r.call_route("/baz"))

    def test_wildcard_route(self):
        r = Router()
        r.add_route("/static/*", "static")
        self.assertEqual(r.call_route("/static/css/app.css"), "static")
        self.assertEqual(r.call_route("/static/js/app.js"), "static")
        self.assertIsNone(r.call_route("/stats"))

    def test_path_params(self):
        r = Router()
        r.add_route("/users/:id", "user")
        r.add_route("/users/:id/books/:bookId", "user-book")
        self.assertEqual(r.call_route("/users/123"), "user")
        self.assertEqual(r.call_route("/users/123/books/abc"), "user-book")

    def test_ordered_matching(self):
        r = Router()
        r.add_route("/api/*", "wildcard")
        r.add_route("/api/users/:id", "param")
        # Ordered: wildcard added first, so matches before the param route
        self.assertEqual(r.call_route("/api/users/123"), "wildcard")
        # If we add a more specific route earlier, it will match first
        r2 = Router()
        r2.add_route("/api/users/:id", "param")
        r2.add_route("/api/*", "wildcard")
        self.assertEqual(r2.call_route("/api/users/123"), "param")


if __name__ == "__main__":
    unittest.main(verbosity=2) 