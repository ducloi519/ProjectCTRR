# AGENTS.md — Movie Recommendation System

## Project context
This repository is a final-term project for the **Discrete Mathematics (Cấu trúc rời rạc)** course.

**Topic:** A movie recommendation system based on user similarity calculated using sets and the Jaccard coefficient.

The original project proposal (`project cuoi ki.pdf`) is the primary source of course-specific requirements. Read it when available. If it cannot be read, say so and ask the student to provide its text. Do not invent instructor requirements.

## Communication and teaching style
- Always communicate with the student in **Vietnamese**.
- The student is a beginner in Python. Explain ideas clearly, step by step, using first-year-student language.
- Explain the purpose and logic of every important function, particularly set operations and Jaccard similarity.
- Prefer simple, readable Python with meaningful names and limited dependencies.
- Do not use complex machine-learning libraries or architectures for the core recommendation algorithm.
- Treat Codex as a programming tutor as well as an assistant: help the student understand and defend their own work.

## Scope from the proposal
- Represent each user as a set of favorite movies.
- Apply set intersection, union, difference, and cardinality.
- Compute Jaccard similarity: `J(A, B) = |A ∩ B| / |A ∪ B|`.
- Find the most similar users (nearest neighbors) for a target user.
- Recommend the union of neighbors' movie sets minus the movies already seen by the target user.
- Use a **self-created sample dataset** of roughly 20–30 users and 15–20 movies, with overlapping preferences.

## Agreed implementation choices
These are team implementation choices, not additional instructor requirements:
- Language: **Python**; IDE: **PyCharm**.
- Use **25 fictional users** and **20 real movie titles** (movie preferences are simulated, not collected from real people).
- Group simulated tastes loosely into science fiction, action, romance, horror, and mixed genres. Ensure overlapping preferences between groups; do not create perfectly isolated clusters.
- Store data locally in human-readable **JSON** files. Use Python's built-in `json` module and `set` type.
- First build and test a simple command-line version of the algorithm; then add an optional **Streamlit** interface.
- On the interface, allow a visitor to select their favorite movies and receive recommendations. If this feature requires a new temporary user profile, handle it without modifying the original dataset.
- Keep sample data clearly labeled as **synthetic** in the app and final report. Real movie titles do not make the user preferences real-world data.
- No external movie API, database, login system, or scraping is required for the initial version.

## Suggested project structure
This is a proposal, not a requirement; discuss it before creating files.

```text
MovieRecommendationSystem/
├── AGENTS.md
├── project cuoi ki.pdf
├── README.md
├── data/
│   ├── movies.json
│   └── users.json
├── recommendation.py
├── main.py
├── app.py
├── tests/
│   └── test_recommendation.py
└── requirements.txt
```

Avoid creating unneeded files or folders at the beginning. `app.py` and `requirements.txt` can wait until the Streamlit stage.

## Algorithm requirements
1. Load the movie catalog and simulated users from JSON.
2. Validate IDs, duplicated titles, missing IDs, and malformed records with beginner-friendly error messages.
3. Convert each user's movie list into a `set` for the set operations.
4. Calculate Jaccard similarity using explicit intersection and union operations.
5. Avoid division by zero when both sets are empty. Explain and document the convention chosen.
6. Rank other users by similarity, excluding the target user. Use a deterministic tie-breaker.
7. Select a configurable number `k` of nearest neighbors. Explain whether users with zero similarity should count; choose and document a sensible rule.
8. Recommend movies by `(union of neighbors' favorite sets) - (target user's movie set)`.
9. Make recommendations deterministic and explain any ordering or ranking beyond the set-difference rule. Do not claim that an unranked set is a sophisticated recommendation ranking.
10. Allow a user to choose favorite movies interactively once the interface stage is reached.

## Development workflow
Follow the phases below, one phase at a time:

**Phase 1 — Data:** propose the list of 20 real movie titles and construct simulated preferences for 25 fictional users. Verify meaningful overlaps and explain how the data is constructed.

**Phase 2 — Algorithm:** implement Jaccard similarity, nearest-neighbor selection, and the recommendation set using basic Python.

**Phase 3 — Testing:** check normal and edge cases, inspect recommendations, and explain intermediate computations that can be shown during the presentation.

**Phase 4 — Interface (optional after the core works):** build a simple Streamlit UI for selecting favorite films and displaying the similarity and recommendations.

**Phase 5 — Documentation:** write clear run instructions and support the group's written report without fabricating evidence, results, or sources.

## Working rules for Codex
- Before editing, describe the intended changes in Vietnamese.
- Ask for approval before making large changes, adding dependencies, or changing project structure.
- For a question that asks only for an explanation or plan, **do not edit files**.
- Make small, reviewable changes. Preserve existing student code and explain modifications.
- Do not silently delete files, overwrite data, or run destructive commands.
- Explain how to run and test each new feature inside PyCharm.
- When fixing bugs, explain the cause, the correction, and a minimal test case.
- Use the PDF as the authoritative project outline; if AGENTS.md and the PDF conflict about academic requirements, point out the conflict before proceeding.
- Do not claim tests passed unless they were actually run and their results inspected.

## Minimum testing checklist
- Identical nonempty movie sets give Jaccard 1.
- Disjoint nonempty movie sets give Jaccard 0.
- Partially overlapping sets produce the expected fraction.
- Empty sets never crash the calculation.
- The target user is excluded from nearest neighbors.
- Recommendations exclude every movie already in the target set.
- No-candidate and zero-similarity cases are handled clearly.
- Equal-similarity ties yield stable results.
- JSON parsing and invalid movie IDs produce understandable messages.

## Group responsibilities in the proposal
- **Hà Minh Đức Lợi:** data construction and algorithm implementation.
- **Nguyễn Thị Thúy Hằng:** theoretical background, evaluation of results, and report writing.

Help each person understand the shared project; do not assume additional assignments that have not been discussed.

## First response when starting this project
If asked to begin, read `AGENTS.md` and `project cuoi ki.pdf`, then respond in Vietnamese with:
1. A brief summary of project goals.
2. A check for differences between the proposal and the implementation choices above.
3. A proposed minimal file structure and staged plan.
4. Any important assumptions or tradeoffs.

**Do not create or modify code until the student approves the initial plan.**
