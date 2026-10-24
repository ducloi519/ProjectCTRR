"""Gợi ý phim từ dữ liệu giả lập bằng hệ số Jaccard và các phép tập hợp."""

import json
from pathlib import Path


def load_json(file_path):
    """Đọc một tệp JSON UTF-8 và báo lỗi dễ hiểu khi không đọc được."""
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Tệp {file_path} sai cú pháp JSON ở dòng {error.lineno}, "
            f"cột {error.colno}."
        ) from error
    except UnicodeError as error:
        raise ValueError(f"Tệp {file_path} cần được lưu bằng UTF-8.") from error
    except OSError as error:
        raise ValueError(
            f"Không đọc được tệp {file_path}. Hãy kiểm tra đường dẫn và quyền đọc."
        ) from error


def validate_records(records, label, text_fields):
    """Kiểm tra danh sách bản ghi, các trường chữ bắt buộc và ID duy nhất."""
    if not isinstance(records, list):
        raise ValueError(f"{label} phải là một danh sách JSON.")

    used_ids = set()
    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"{label}: bản ghi thứ {position} phải là một đối tượng.")
        for field in text_fields:
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{label}: bản ghi thứ {position} thiếu hoặc sai trường '{field}'."
                )
        if record["id"] in used_ids:
            raise ValueError(f"{label}: ID '{record['id']}' bị trùng.")
        used_ids.add(record["id"])


def load_data(data_directory=None):
    """Đọc và kiểm tra danh mục phim cùng danh sách người dùng."""
    if data_directory is None:
        # Tìm data theo vị trí tệp Python để chạy được từ thư mục khác.
        data_directory = Path(__file__).resolve().parent / "data"
    data_directory = Path(data_directory)

    movies = load_json(data_directory / "movies.json")
    user_data = load_json(data_directory / "users.json")
    validate_records(movies, "Danh mục phim", ["id", "title"])
    if not isinstance(user_data, dict) or "users" not in user_data:
        raise ValueError("users.json phải chứa một đối tượng có trường 'users'.")
    users = user_data["users"]
    validate_records(users, "Danh sách người dùng", ["id", "name"])

    movie_ids = set()
    movie_titles = set()
    for movie in movies:
        normalized_title = movie["title"].strip().casefold()
        if normalized_title in movie_titles:
            raise ValueError(f"Tên phim '{movie['title']}' bị trùng.")
        movie_titles.add(normalized_title)
        movie_ids.add(movie["id"])

    for user in users:
        favorites = user.get("favorite_movie_ids")
        if not isinstance(favorites, list):
            raise ValueError(
                f"Người dùng {user['id']}: 'favorite_movie_ids' phải là danh sách."
            )
        for movie_id in favorites:
            if not isinstance(movie_id, str) or movie_id not in movie_ids:
                raise ValueError(
                    f"Người dùng {user['id']}: ID phim {movie_id!r} không hợp lệ "
                    "hoặc không có trong movies.json."
                )
        if len(favorites) != len(set(favorites)):
            raise ValueError(f"Người dùng {user['id']}: danh sách phim bị lặp ID.")

    return movies, users


def favorite_movies_to_set(user):
    """Chuyển danh sách ID phim của một người thành tập hợp, không sửa dữ liệu gốc."""
    return set(user["favorite_movie_ids"])


def jaccard_similarity(user_a, user_b):
    """Nhận hai tập ID phim; trả về 0 nếu cả hai tập đều rỗng."""
    intersection = user_a & user_b  # Các phim mà cả hai người đều thích.
    union = user_a | user_b  # Tất cả phim hai người thích, mỗi phim chỉ tính một lần.

    if not union:
        return 0.0
    return len(intersection) / len(union)


def calculate_user_similarities(target_user_id, users):
    """So sánh người mục tiêu với mọi người còn lại, trả kết quả theo ID."""
    target_user = None
    for user in users:
        if user["id"] == target_user_id:
            target_user = user
            break
    if target_user is None:
        raise ValueError(f"Không tìm thấy người dùng có ID '{target_user_id}'.")

    target_movies = favorite_movies_to_set(target_user)
    results = []
    for user in users:
        if user["id"] == target_user_id:
            continue  # Không so sánh người mục tiêu với chính họ.
        other_movies = favorite_movies_to_set(user)
        results.append({
            "id": user["id"],
            "name": user["name"],
            "similarity": jaccard_similarity(target_movies, other_movies),
        })

    # Giữ bảng so sánh theo ID để dễ đối chiếu với dữ liệu gốc.
    return sorted(results, key=lambda result: result["id"])


def select_nearest_neighbors(target_user_id, users, k=3):
    """Chọn tối đa k người có điểm dương; bằng điểm thì ưu tiên ID tăng dần."""
    if type(k) is not int or k < 1:
        raise ValueError("Số hàng xóm k phải là số nguyên lớn hơn 0.")

    similarities = calculate_user_similarities(target_user_id, users)
    positive_results = []
    for result in similarities:
        if result["similarity"] > 0:
            positive_results.append(result)

    # Dấu trừ giúp điểm cao đứng trước; ID xử lý trường hợp bằng điểm.
    ranked_results = sorted(
        positive_results, key=lambda result: (-result["similarity"], result["id"])
    )
    return ranked_results[:k]


def recommend_movies(target_user_id, users, movies, k=3):
    """Trả về hàng xóm và danh sách phim gợi ý theo ID, không chấm điểm phim."""
    neighbors = select_nearest_neighbors(target_user_id, users, k)
    neighbor_ids = set()
    for neighbor in neighbors:
        neighbor_ids.add(neighbor["id"])

    target_movies = set()
    neighbor_movies = set()
    for user in users:
        if user["id"] == target_user_id:
            target_movies = favorite_movies_to_set(user)
        elif user["id"] in neighbor_ids:
            # Hợp: gom phim của các hàng xóm, mỗi phim chỉ xuất hiện một lần.
            neighbor_movies = neighbor_movies | favorite_movies_to_set(user)

    # Hiệu: bỏ tất cả phim mà người mục tiêu đã thích.
    recommended_ids = neighbor_movies - target_movies
    recommended_movies = []
    for movie in movies:
        if movie["id"] in recommended_ids:
            recommended_movies.append(movie)

    # Đây là thứ tự hiển thị ổn định, không phải xếp hạng chất lượng phim.
    recommended_movies = sorted(recommended_movies, key=lambda movie: movie["id"])
    return neighbors, recommended_movies


def choose_target_user(users):
    """Hiển thị danh sách và yêu cầu nhập đến khi chọn đúng ID hoặc thoát."""
    print("\nDanh sách người dùng:")
    for user in sorted(users, key=lambda user: user["id"]):
        print(f"{user['id']} - {user['name']}")

    while True:
        try:
            user_id = input("\nNhập ID (Enter chọn U01, Q để thoát): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            # Kết thúc nhẹ nhàng khi luồng nhập đóng hoặc người dùng nhấn Ctrl+C.
            print()
            return None

        if user_id == "Q":
            return None
        if user_id == "":
            user_id = "U01"

        for user in users:
            if user["id"] == user_id:
                return user
        print(f"ID '{user_id}' không tồn tại. Hãy nhập ID trong danh sách.")


def display_user_recommendations(target_user, users, movies, number_of_neighbors=3):
    """Hiển thị sở thích, bảng Jaccard, hàng xóm và phim gợi ý của người đã chọn."""
    target_user_id = target_user["id"]
    results = calculate_user_similarities(target_user_id, users)
    neighbors, recommended_movies = recommend_movies(
        target_user_id, users, movies, number_of_neighbors
    )

    print(f"\nNgười được chọn: {target_user_id} - {target_user['name']}")
    print("Phim yêu thích:")
    favorite_ids = favorite_movies_to_set(target_user)
    if not favorite_ids:
        print("Người dùng chưa có phim yêu thích.")
    else:
        for movie in sorted(movies, key=lambda movie: movie["id"]):
            if movie["id"] in favorite_ids:
                print(f"{movie['id']} - {movie['title']}")

    print(f"\nSo sánh {target_user_id} với {len(results)} người còn lại:")
    print(f"{'ID':<6} {'Tên':<15} {'Jaccard':>10}")
    for result in results:
        print(f"{result['id']:<6} {result['name']:<15} {result['similarity']:>10.4f}")

    print(f"\nTop {number_of_neighbors} người tương đồng (tìm được {len(neighbors)}):")
    if not neighbors:
        print("Không có người dùng khác có Jaccard lớn hơn 0.")
    else:
        for neighbor in neighbors:
            print(
                f"{neighbor['id']} - {neighbor['name']}: "
                f"Jaccard = {neighbor['similarity']:.4f}"
            )

    print("\nPhim được gợi ý (theo ID, không xếp hạng chất lượng):")
    if not recommended_movies:
        print("Không tìm được phim để gợi ý từ các hàng xóm đã chọn.")
    else:
        for movie in recommended_movies:
            print(f"{movie['id']} - {movie['title']}")


def main():
    """Đọc dữ liệu một lần và cho phép chọn nhiều người trong cùng phiên chạy."""
    try:
        movies, users = load_data()
    except ValueError as error:
        print(f"Lỗi dữ liệu: {error}")
        return 1

    print("Dữ liệu sở thích giả lập, không thu thập từ người thật.")
    print(f"Đã đọc {len(movies)} phim và {len(users)} người dùng.")
    if not users:
        print("Danh sách người dùng trống, không thể chọn người để so sánh.")
        return 0

    # Sau mỗi kết quả, quay lại chọn ID mà không cần chạy lại chương trình.
    while True:
        target_user = choose_target_user(users)
        if target_user is None:
            print("Đã thoát chương trình.")
            break
        display_user_recommendations(target_user, users, movies)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
