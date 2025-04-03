# About the Heuristics

Following the guidelines provided in the assignment, the main objectives were to:

1. **Remove redundancy**;
2. **Assign a score to each rule based on its usefulness and rank them accordingly**.

---

## 1. Removing Redundancy

After reading the rules with the `read_rules` function, we implemented the following steps to remove redundant rules:

- Using the `compress_rules` function:
  - We split each rule into its **Left-Hand Side (LHS)** and **Right-Hand Side (RHS)** using `.split(" => ")`.
  - For each rule, we checked whether its LHS conditions were a subset of another rule's LHS conditions. If so, the moyre specific rule was removed because it was redundant.

- Additionally:
  - We implemented the `can_merge` function to check whether two rules could be merged by verifying if there was a non-empty intersection between their sets of conditions.
  - If two rules could be merged, the `merge_conditions` function combined them. For example:
    ```plaintext
    Rule 1: A AND B => donor_is_old
    Rule 2: A AND C => donor_is_old
    Merged Rule: A AND (B OR C) => donor_is_old
    ```

- Finally:
  - The `merge_rules` function was used to efficiently compress a list of rules by applying the above logic, completing the first objective.

---

## 2. Assigning Scores and Ranking Rules

To evaluate the usefulness of each rule, we implemented the following scoring mechanism:

- In the `evaluate_rule_support` function:
  - We created a boolean mask initialized to `True` for all rows in the dataset.
  - For each condition in the rule:
    - If the condition started with `NOT`, we applied the negation of the biomarker.
    - Otherwise, we checked whether the biomarker was `True`.
  - The function returned the number of rows in the dataset where the rule was satisfied.

- In the `calculate_rule_score` function:
  - We calculated the score for each rule as:
    ```python
    score = support / (1 + specificity_penalty)
    ```
    - Here, `support` is the number of rows satisfying the rule (calculated using `evaluate_rule_support`).
    - `specificity_penalty` is the number of conditions in the rule. Fewer conditions result in a higher score, favoring simpler and more general rules.

- Finally:
  - The `rank_rules_by_usefulness` function ranked the rules in descending order of their scores, ensuring that the most useful rules appeared first.

---

## Final Output

The compressed and ranked rules were saved to an output file, along with their scores. This provides a clear and concise representation of the most significant rules.

---

