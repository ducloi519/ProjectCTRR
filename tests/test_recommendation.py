"""Chạy từ thư mục project: python -m unittest discover -s tests -v."""

import copy
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from recommendation import (
    calculate_user_similarities,
    choose_target_user,
    favorite_movies_to_set,
    jaccard_similarity,
    load_data,
    load_json,
    recommend_movies,
    select_nearest_neighbors,
)


class TestJaccard(unittest.TestCase):
    def test_identical_nonempty_sets(self):
        self.assertEqual(jaccard_similarity({"M01", "M02"}, {"M02", "M01"}), 1)

    def test_disjoint_sets(self):
        self.assertEqual(jaccard_similarity({"M01"}, {"M02"}), 0)

    def test_partial_overlap(self):
        self.assertAlmostEqual(
            jaccard_similarity({"M01", "M02"}, {"M02", "M03"}), 1 / 3
        )

    def test_two_empty_sets(self):
        self.assertEqual(jaccard_similarity(set(), set()), 0)

    def test_one_empty_set_in_both_orders(self):
        self.assertEqual(jaccard_similarity(set(), {"M01"}), 0)
        self.assertEqual(jaccard_similarity({"M01"}, set()), 0)

    def test_range_and_symmetry_for_all_subsets_of_three_movies(self):
        # Tám tập con tạo thành 64 cặp, gồm cả các trường hợp rỗng.
        subsets = [
            set(), {"M01"}, {"M02"}, {"M03"},
            {"M01", "M02"}, {"M01", "M03"}, {"M02", "M03"},
            {"M01", "M02", "M03"},
        ]
        for first in subsets:
            for second in subsets:
                with self.subTest(first=first, second=second):
                    score = jaccard_similarity(first, second)
                    self.assertGreaterEqual(score, 0)
                    self.assertLessEqual(score, 1)
                    self.assertEqual(score, jaccard_similarity(second, first))

    def test_convert_favorites_without_changing_original(self):
        user = {"favorite_movie_ids": ["M01", "M02"]}
        converted = favorite_movies_to_set(user)
        self.assertIsInstance(converted, set)
        self.assertEqual(converted, {"M01", "M02"})
        converted.add("M03")
        self.assertEqual(user["favorite_movie_ids"], ["M01", "M02"])


class TestDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_directory = Path(__file__).resolve().parents[1] / "data"
        # Đọc độc lập bằng json để kiểm tra chính dữ liệu lưu trong tệp.
        cls.movies = json.loads((data_directory / "movies.json").read_text(encoding="utf-8"))
        cls.user_data = json.loads((data_directory / "users.json").read_text(encoding="utf-8"))
        cls.users = cls.user_data["users"]

    def test_record_counts(self):
        self.assertEqual(len(self.movies), 20)
        self.assertEqual(len(self.users), 25)

    def test_unique_ids_and_titles(self):
        self.assertEqual(len({movie["id"] for movie in self.movies}), 20)
        self.assertEqual(len({user["id"] for user in self.users}), 25)
        self.assertEqual(len({movie["title"].strip().casefold() for movie in self.movies}), 20)

    def test_favorite_ids_and_counts(self):
        movie_ids = {movie["id"] for movie in self.movies}
        for user in self.users:
            with self.subTest(user=user["id"]):
                favorites = user["favorite_movie_ids"]
                self.assertGreaterEqual(len(favorites), 4)
                self.assertLessEqual(len(favorites), 7)
                self.assertEqual(len(favorites), len(set(favorites)))
                self.assertTrue(set(favorites).issubset(movie_ids))

    def test_synthetic_label_and_five_equal_groups(self):
        self.assertIs(self.user_data["synthetic"], True)
        counts = {}
        for user in self.users:
            group = user["preference_group"]
            counts[group] = counts.get(group, 0) + 1
        self.assertEqual(len(counts), 5)
        self.assertTrue(all(count == 5 for count in counts.values()))

    def test_loader_returns_original_records(self):
        movies, users = load_data()
        self.assertEqual(movies, self.movies)
        self.assertEqual(users, self.users)


class TestRecommendations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.movies, cls.users = load_data()

    def test_all_targets_have_24_comparisons_and_valid_neighbors(self):
        for target in self.users:
            with self.subTest(target=target["id"]):
                comparisons = calculate_user_similarities(target["id"], self.users)
                self.assertEqual(len(comparisons), 24)
                self.assertNotIn(target["id"], [result["id"] for result in comparisons])
                neighbors = select_nearest_neighbors(target["id"], self.users)
                self.assertEqual(len(neighbors), 3)
                for neighbor in neighbors:
                    self.assertNotEqual(neighbor["id"], target["id"])
                    self.assertGreater(neighbor["similarity"], 0)
                    self.assertLessEqual(neighbor["similarity"], 1)
                for previous, following in zip(neighbors, neighbors[1:]):
                    self.assertGreaterEqual(previous["similarity"], following["similarity"])
                    if previous["similarity"] == following["similarity"]:
                        self.assertLess(previous["id"], following["id"])

    def test_known_results_for_three_targets(self):
        # Kết quả mong đợi được tính đối chiếu trước, không gọi lại thuật toán để tạo.
        examples = {
            "U01": (["U05", "U21", "U02"], [3 / 7, 3 / 7, 3 / 8],
                    ["M04", "M09", "M11", "M15", "M17", "M19"]),
            "U05": (["U02", "U12", "U01"], [4 / 7, 4 / 7, 3 / 7],
                    ["M03", "M04", "M07", "M10", "M11", "M17"]),
            "U10": (["U07", "U06", "U13"], [3 / 7, 3 / 8, 2 / 7],
                    ["M01", "M03", "M06", "M12", "M17", "M18", "M20"]),
        }
        for target_id, (expected_ids, expected_scores, expected_movies) in examples.items():
            with self.subTest(target=target_id):
                neighbors, movies = recommend_movies(target_id, self.users, self.movies)
                self.assertEqual([neighbor["id"] for neighbor in neighbors], expected_ids)
                for neighbor, expected_score in zip(neighbors, expected_scores):
                    self.assertAlmostEqual(neighbor["similarity"], expected_score)
                self.assertEqual([movie["id"] for movie in movies], expected_movies)

    def test_all_recommendations_are_new_unique_and_named(self):
        catalog = {movie["id"]: movie["title"] for movie in self.movies}
        for target in self.users:
            with self.subTest(target=target["id"]):
                neighbors, movies = recommend_movies(target["id"], self.users, self.movies)
                suggested_ids = [movie["id"] for movie in movies]
                self.assertEqual(len(suggested_ids), len(set(suggested_ids)))
                self.assertTrue(set(suggested_ids).isdisjoint(target["favorite_movie_ids"]))
                self.assertEqual(suggested_ids, sorted(suggested_ids))
                for movie in movies:
                    self.assertEqual(movie["title"], catalog[movie["id"]])
                neighbor_ids = {neighbor["id"] for neighbor in neighbors}
                expected = set()
                for user in self.users:
                    if user["id"] in neighbor_ids:
                        expected.update(user["favorite_movie_ids"])
                expected.difference_update(target["favorite_movie_ids"])
                self.assertEqual(set(suggested_ids), expected)

    def test_tie_break_at_top_three_boundary(self):
        users = [
            {"id": user_id, "name": user_id, "favorite_movie_ids": ["M01"]}
            for user_id in ["U05", "U04", "U03", "U02", "U01"]
        ]
        neighbors = select_nearest_neighbors("U01", users)
        self.assertEqual([user["id"] for user in neighbors], ["U02", "U03", "U04"])

    def test_no_other_users(self):
        users = [{"id": "U01", "name": "An", "favorite_movie_ids": ["M01"]}]
        self.assertEqual(recommend_movies("U01", users, self.movies), ([], []))

    def test_no_positive_neighbors(self):
        users = [
            {"id": "U01", "name": "An", "favorite_movie_ids": ["M01"]},
            {"id": "U02", "name": "Bình", "favorite_movie_ids": ["M02"]},
        ]
        self.assertEqual(recommend_movies("U01", users, self.movies), ([], []))

    def test_empty_target(self):
        users = copy.deepcopy(self.users)
        users[0]["favorite_movie_ids"] = []
        self.assertEqual(recommend_movies("U01", users, self.movies), ([], []))

    def test_positive_neighbor_but_no_new_movies(self):
        users = [
            {"id": "U01", "name": "An", "favorite_movie_ids": ["M01", "M02"]},
            {"id": "U02", "name": "Bình", "favorite_movie_ids": ["M01"]},
        ]
        neighbors, movies = recommend_movies("U01", users, self.movies)
        self.assertEqual([user["id"] for user in neighbors], ["U02"])
        self.assertEqual(movies, [])

    def test_order_independent_and_no_input_changes(self):
        original_users = copy.deepcopy(self.users)
        original_movies = copy.deepcopy(self.movies)
        expected = recommend_movies("U01", self.users, self.movies)
        actual = recommend_movies("U01", list(reversed(self.users)), list(reversed(self.movies)))
        self.assertEqual(actual, expected)
        self.assertEqual(self.users, original_users)
        self.assertEqual(self.movies, original_movies)

    def test_configurable_neighbor_count(self):
        self.assertEqual(len(select_nearest_neighbors("U01", self.users, k=1)), 1)
        for invalid in [0, -1, 1.5, True, "3"]:
            with self.subTest(k=invalid), self.assertRaises(ValueError):
                select_nearest_neighbors("U01", self.users, k=invalid)

    def test_unknown_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Không tìm thấy"):
            recommend_movies("U99", self.users, self.movies)


class TestUserSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.movies, cls.users = load_data()

    def test_select_every_id_u01_to_u25(self):
        for number in range(1, 26):
            user_id = f"U{number:02d}"
            with self.subTest(user_id=user_id):
                with patch("builtins.input", return_value=user_id):
                    with redirect_stdout(io.StringIO()) as output:
                        selected = choose_target_user(self.users)
                self.assertEqual(selected["id"], user_id)
                for user in self.users:
                    self.assertIn(f"{user['id']} - {user['name']}", output.getvalue())

    def test_default_normalized_input_and_exit(self):
        for entered, expected in [("", "U01"), (" u25 ", "U25"), ("q", None)]:
            with self.subTest(entered=entered):
                with patch("builtins.input", return_value=entered):
                    with redirect_stdout(io.StringIO()):
                        selected = choose_target_user(self.users)
                self.assertEqual(selected["id"] if selected else None, expected)

    def test_invalid_id_is_retried(self):
        with patch("builtins.input", side_effect=["U99", "U05"]) as mocked_input:
            with redirect_stdout(io.StringIO()) as output:
                selected = choose_target_user(self.users)
        self.assertEqual(selected["id"], "U05")
        self.assertEqual(mocked_input.call_count, 2)
        self.assertIn("không tồn tại", output.getvalue())


class TestInvalidJson(unittest.TestCase):
    def setUp(self):
        # Mọi dữ liệu sai đều nằm trong thư mục tạm, không sửa data của dự án.
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.directory = Path(temporary_directory.name)
        self.movies = [{"id": "M01", "title": "Inception"}]
        self.user_data = {"users": [
            {"id": "U01", "name": "An", "favorite_movie_ids": ["M01"]}
        ]}
        self.write_fixtures()

    def write_fixtures(self):
        for filename, records in [("movies.json", self.movies), ("users.json", self.user_data)]:
            (self.directory / filename).write_text(
                json.dumps(records, ensure_ascii=False), encoding="utf-8"
            )

    def test_malformed_json(self):
        (self.directory / "movies.json").write_text('{"id":', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "sai cú pháp JSON.*dòng"):
            load_data(self.directory)

    def test_missing_file(self):
        with self.assertRaisesRegex(ValueError, "Không đọc được tệp"):
            load_json(self.directory / "missing.json")

    def test_unknown_movie_id(self):
        self.user_data["users"][0]["favorite_movie_ids"] = ["M99"]
        self.write_fixtures()
        with self.assertRaisesRegex(ValueError, "U01.*M99"):
            load_data(self.directory)

    def test_duplicate_movie_and_user_ids(self):
        for filename, records in [("movies.json", self.movies), ("users.json", self.user_data["users"])]:
            with self.subTest(filename=filename):
                duplicate = records + [copy.deepcopy(records[0])]
                contents = duplicate if filename == "movies.json" else {"users": duplicate}
                (self.directory / filename).write_text(json.dumps(contents), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "ID.*bị trùng"):
                    load_data(self.directory)
                self.write_fixtures()

    def test_duplicate_titles(self):
        self.movies.append({"id": "M02", "title": " inception "})
        self.write_fixtures()
        with self.assertRaisesRegex(ValueError, "Tên phim.*bị trùng"):
            load_data(self.directory)

    def test_missing_id_and_malformed_record(self):
        for record in [{"title": "Inception"}, "not an object"]:
            with self.subTest(record=record):
                self.movies = [record]
                self.write_fixtures()
                with self.assertRaises(ValueError):
                    load_data(self.directory)

    def test_invalid_favorites(self):
        for favorites in [None, "M01", [None], [["M01"]], ["M01", "M01"]]:
            with self.subTest(favorites=favorites):
                self.user_data["users"][0]["favorite_movie_ids"] = favorites
                self.write_fixtures()
                with self.assertRaises(ValueError):
                    load_data(self.directory)


if __name__ == "__main__":
    unittest.main()
