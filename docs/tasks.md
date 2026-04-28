# Tasks

The current task catalog is small and intentionally mixed so the harness can exercise
different benchmark shapes.

| Task | Category | Difficulty | Prompt |
| --- | --- | --- | --- |
| `palindrome` | `code_completion` | easy | Write `is_palindrome(s: str) -> bool`. |
| `fibonacci` | `code_completion` | medium | Write iterative `fib(n: int) -> int`. |
| `buggy_add` | `code_review` | easy | Review code that divides by zero on an empty list. |
| `refactor_loop` | `refactoring` | easy | Refactor a loop into list comprehension. |
| `debug_division` | `debugging` | easy | Fix unsafe division by zero. |
| `write_tests` | `test_generation` | medium | Generate pytest coverage for email validation. |
| `bayesian_sampler` | `scientific_computing` | hard | Implement a simple adaptive rejection sampler. |
| `log_parser` | `system_admin` | medium | Parse logs and print only ERROR entries. |

## Task selection

- `helios-bench tasks` lists the full catalog.
- `helios-bench run --task <id>` executes one task.
- `helios-bench leak` repeats a task to look for drift.
