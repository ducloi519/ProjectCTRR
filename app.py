"""Giao diện Streamlit; mọi kết quả gợi ý được lấy từ recommendation.py."""

import streamlit as st

from recommendation import (
    calculate_user_similarities,
    favorite_movies_to_set,
    jaccard_similarity,
    load_data,
    recommend_movies,
)


def format_movie_set(movie_ids):
    """Sắp ID để tập hợp luôn hiển thị cùng thứ tự khi thuyết trình."""
    return "{" + ", ".join(sorted(movie_ids)) + "}"


def display_movie_list(movies, empty_message):
    """Hiển thị cả tên và ID phim bằng thành phần giao diện có sẵn."""
    if not movies:
        st.info(empty_message)
        return
    for movie in movies:
        with st.container(border=True):
            st.write(movie["title"])
            st.caption(f"Mã phim: {movie['id']}")


def display_math_explanation(users_by_id):
    """Minh họa giao, hợp và hiệu; không thay thế hàm tính gợi ý."""
    st.subheader("Vì sao hệ thống chọn những bộ phim này?")
    st.write(
        "Mỗi người được biểu diễn bằng một tập ID phim yêu thích. "
        "Jaccard đo tỉ lệ phim chung trên tổng số phim khác nhau của hai người."
    )
    st.latex(r"J(A,B)=\frac{|A\cap B|}{|A\cup B|}")
    st.markdown(
        "- **Giao `A & B`:** những phim cả hai người cùng thích.\n"
        "- **Hợp `A | B`:** mọi phim hai người thích, không tính trùng.\n"
        "- **Lực lượng `len(A)`:** số phần tử trong tập hợp.\n"
        "- **Hiệu `N - A`:** bỏ phim đã thích khỏi tập phim của hàng xóm."
    )
    st.latex(r"R=(B_1\cup B_2\cup B_3)\setminus A")
    st.caption(
        "A là tập phim của người mục tiêu; B₁, B₂, B₃ là tập phim của "
        "tối đa 3 hàng xóm có điểm dương. Nếu cả hai tập rỗng, quy ước Jaccard = 0."
    )

    with st.expander("Ví dụ từ dữ liệu: U01 — An và U05 — Hà", expanded=True):
        if "U01" not in users_by_id or "U05" not in users_by_id:
            st.info("Cần có U01 và U05 để hiển thị ví dụ minh họa này.")
            return
        first_movies = favorite_movies_to_set(users_by_id["U01"])
        second_movies = favorite_movies_to_set(users_by_id["U05"])
        # Tính các tập trung gian chỉ để người học quan sát phép tính.
        intersection = first_movies & second_movies
        union = first_movies | second_movies
        similarity = jaccard_similarity(first_movies, second_movies)
        st.code(
            f"A (U01) = {format_movie_set(first_movies)}\n"
            f"B (U05) = {format_movie_set(second_movies)}\n"
            f"A ∩ B   = {format_movie_set(intersection)}\n"
            f"A ∪ B   = {format_movie_set(union)}",
            language="text",
        )
        if union:
            st.write(
                f"Có {len(intersection)} phim chung trên {len(union)} phim khác nhau: "
                f"J(A, B) = {len(intersection)}/{len(union)} = {similarity:.4f}."
            )
        else:
            st.write("Hai tập đều rỗng nên Jaccard = 0 theo quy ước.")


def display_results(target_user, users, movies):
    """Gọi thuật toán hiện có và chuyển kết quả thành bảng, thẻ phim."""
    try:
        comparisons = calculate_user_similarities(target_user["id"], users)
        neighbors, recommended_movies = recommend_movies(
            target_user["id"], users, movies, k=3
        )
    except ValueError as error:
        st.error(f"Không tính được gợi ý: {error}")
        return

    st.subheader(f"Kết quả dành cho {target_user['id']} — {target_user['name']}")
    comparison_column, neighbor_column, movie_column = st.columns(3)
    comparison_column.metric("Người được so sánh", len(comparisons))
    neighbor_column.metric("Hàng xóm phù hợp", len(neighbors))
    movie_column.metric("Phim được gợi ý", len(recommended_movies))

    st.markdown("### Top 3 người tương đồng")
    st.caption(
        "Chỉ lấy Jaccard > 0, loại chính người mục tiêu. Điểm giảm dần; "
        "bằng điểm thì ID tăng dần. Điểm hiển thị được làm tròn 4 chữ số."
    )
    if neighbors:
        rows = []
        for position, neighbor in enumerate(neighbors, start=1):
            rows.append({
                "Thứ tự": position,
                "ID": neighbor["id"],
                "Tên người dùng": neighbor["name"],
                "Jaccard": f"{neighbor['similarity']:.4f}",
            })
        st.table(rows)
    else:
        st.info("Không có người dùng khác có Jaccard lớn hơn 0 để chọn hàng xóm.")

    st.markdown("### Những bộ phim dành cho bạn")
    st.caption("Phim được hiển thị theo ID; đây không phải xếp hạng chất lượng phim.")
    left_column, right_column = st.columns(2)
    if recommended_movies:
        for position, movie in enumerate(recommended_movies):
            column = left_column if position % 2 == 0 else right_column
            with column:
                display_movie_list([movie], "")
    else:
        st.info("Không tìm được phim mới để gợi ý từ những hàng xóm đã chọn.")

    with st.expander(f"Xem bảng Jaccard với {len(comparisons)} người còn lại"):
        rows = []
        for comparison in comparisons:
            rows.append({
                "ID": comparison["id"],
                "Tên": comparison["name"],
                "Jaccard": f"{comparison['similarity']:.4f}",
            })
        st.table(rows)


def main():
    """Đọc dữ liệu, chọn hồ sơ và hiển thị giao diện tiếng Việt."""
    st.set_page_config(
        page_title="🎬 HỆ THỐNG GỢI Ý PHIM",
        page_icon="🎬",
        layout="wide",
    )
    # CSS chỉ trang trí phần giới thiệu; các widget dùng giao diện gốc Streamlit.
    st.markdown(
        """
        <style>
        .movie-hero {
            padding: clamp(1.4rem, 4vw, 3rem);
            border-radius: 24px;
            background: linear-gradient(120deg, #101d35, #164e63);
            color: #f8fafc;
            margin-bottom: 1.5rem;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.15);
        }
        .movie-hero .eyebrow {
            color: #99f6e4;
            letter-spacing: 0.13em;
            font-size: 0.8rem;
            font-weight: 700;
        }
        .movie-hero h1 {
            color: #f8fafc;
            font-size: clamp(1.8rem, 4vw, 3.2rem);
            line-height: 1.15;
            margin: 0.7rem 0 1rem;
        }
        .movie-hero p { max-width: 740px; line-height: 1.7; }
        </style>
        <section class="movie-hero">
            <span class="eyebrow">CẤU TRÚC RỜI RẠC · KHÁM PHÁ ĐIỆN ẢNH</span>
            <h1>🎬 HỆ THỐNG GỢI Ý PHIM</h1>
            <p>Từ những bộ phim bạn yêu thích, tìm người có cùng sở thích
            và khám phá phim mới bằng tập hợp và hệ số Jaccard.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    try:
        movies, users = load_data()
    except ValueError as error:
        st.error(f"Không đọc được dữ liệu: {error}")
        st.info("Kiểm tra data/movies.json và data/users.json rồi tải lại trang.")
        st.stop()
    if not users or not movies:
        st.warning("Cần có danh mục phim và người dùng để hiển thị ứng dụng.")
        st.stop()

    users_by_id = {}
    for user in sorted(users, key=lambda user: user["id"]):
        users_by_id[user["id"]] = user

    st.caption(
        f"Dữ liệu giả lập: {len(users)} người hư cấu · {len(movies)} tên phim có thật. "
        "Sở thích được tạo thủ công, không thu thập từ người thật."
    )
    with st.container(border=True):
        st.subheader("01 · Chọn hồ sơ khám phá")
        selected_id = st.selectbox(
            "Người dùng mục tiêu",
            options=list(users_by_id),
            format_func=lambda user_id: f"{user_id} — {users_by_id[user_id]['name']}",
        )
        target_user = users_by_id[selected_id]
        favorite_ids = favorite_movies_to_set(target_user)
        st.markdown(f"**Phim yêu thích của {target_user['name']}**")
        favorites = []
        for movie in sorted(movies, key=lambda movie: movie["id"]):
            if movie["id"] in favorite_ids:
                favorites.append({"ID phim": movie["id"], "Tên phim": movie["title"]})
        if favorites:
            st.table(favorites)
        else:
            st.info("Người dùng chưa có phim yêu thích.")
        show_results = st.button("Gợi ý phim", type="primary")
        st.caption("Đổi hồ sơ rồi bấm Gợi ý phim để xem kết quả của người mới.")

    # Streamlit chạy lại khi đổi dropdown: chỉ hiện kết quả khi bấm nút cho hồ sơ hiện tại.
    if show_results:
        display_results(target_user, users, movies)
    else:
        st.info("Chọn một hồ sơ và bấm Gợi ý phim để bắt đầu.")

    st.divider()
    display_math_explanation(users_by_id)
    st.caption(
        "Hệ thống loại các phim đã thích. Vì chưa có lịch sử xem đầy đủ, "
        "phim đã xem nhưng không thích vẫn có thể xuất hiện trong gợi ý."
    )


if __name__ == "__main__":
    main()
