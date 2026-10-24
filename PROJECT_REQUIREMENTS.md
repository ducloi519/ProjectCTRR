# PROJECT REQUIREMENTS

## Course
Cấu trúc rời rạc (Discrete Mathematics)

## Topic
Movie Recommendation System Using Jaccard Similarity

## 1. Reason for Choosing the Topic
Platforms such as Netflix and Spotify offer personalized recommendations. The project demonstrates how recommendation systems can be developed using set operations learned in Discrete Mathematics.

## 2. Problem Statement
Each user has a list of favorite movies. The system must identify users with similar preferences and recommend movies that the target user has not watched.

## 3. Mathematical Concepts
- Set intersection (∩)
- Set union (∪)
- Set difference (−)
- Set cardinality
- Jaccard similarity: J(A, B) = |A ∩ B| / |A ∪ B|

## 4. Implementation Method
1. Represent each user's favorite movies as a set.
2. Calculate Jaccard similarity between the target user and other users.
3. Select the most similar users (nearest neighbors).
4. Combine the neighbors' favorite movie sets using union.
5. Remove movies already watched by the target user using set difference.

## 5. Dataset
Create a simulated dataset containing approximately 20–30 users and 15–20 movies, ensuring overlapping preferences.

## 6. Team Responsibilities
- Hà Minh Đức Lợi: Dataset construction and algorithm implementation.
- Nguyễn Thị Thúy Hằng: Theoretical foundations, result evaluation, and report writing.

## 7. Important Notes
This document represents the original project proposal. Additional implementation choices are described in AGENTS.md.