"""Tests for helios_bench.tasks module."""

from helios_bench.tasks import (
    TASKS,
    BenchmarkTask,
    export_tasks_json,
    get_all_tasks,
    get_task,
    get_tasks_by_category,
    get_tasks_by_difficulty,
)


class TestBenchmarkTask:
    """Test BenchmarkTask dataclass."""

    def test_task_creation(self):
        """Test creating a BenchmarkTask."""
        task = BenchmarkTask(
            id="test_task",
            name="Test Task",
            category="code_completion",
            difficulty="easy",
            prompt="Test prompt",
            timeout=30,
            max_tokens=100,
        )
        assert task.id == "test_task"
        assert task.name == "Test Task"
        assert task.category == "code_completion"
        assert task.difficulty == "easy"
        assert task.prompt == "Test prompt"
        assert task.timeout == 30
        assert task.max_tokens == 100

    def test_task_default_values(self):
        """Test BenchmarkTask with default values."""
        task = BenchmarkTask(
            id="minimal",
            name="Minimal",
            category="test",
            difficulty="easy",
            prompt="Prompt",
        )
        assert task.expected_output is None
        assert task.timeout == 30
        assert task.max_tokens == 100


class TestTasks:
    """Test TASKS dictionary."""

    def test_tasks_not_empty(self):
        """Test that TASKS has at least one task."""
        assert len(TASKS) > 0

    def test_all_tasks_have_required_fields(self):
        """Test all tasks have required fields."""
        for task_id, task in TASKS.items():
            assert hasattr(task, "id")
            assert hasattr(task, "name")
            assert hasattr(task, "category")
            assert hasattr(task, "difficulty")
            assert hasattr(task, "prompt")
            assert hasattr(task, "timeout")
            assert task.timeout > 0

    def test_task_categories(self):
        """Test expected categories exist."""
        expected_categories = {
            "code_completion",
            "code_review",
            "refactoring",
            "debugging",
            "test_generation",
            "scientific_computing",
            "system_admin",
        }
        actual_categories = {task.category for task in TASKS.values()}
        assert expected_categories.issubset(actual_categories)

    def test_task_difficulties(self):
        """Test tasks have valid difficulty levels."""
        valid_difficulties = {"easy", "medium", "hard"}
        for task in TASKS.values():
            assert task.difficulty in valid_difficulties


class TestGetTask:
    """Test get_task function."""

    def test_get_existing_task(self):
        """Test getting an existing task."""
        task = get_task("palindrome")
        assert task is not None
        assert task.id == "palindrome"

    def test_get_nonexistent_task_returns_default(self):
        """Test getting a nonexistent task returns palindrome as default."""
        task = get_task("nonexistent_task_xyz")
        assert task is not None
        assert task.id == "palindrome"


class TestGetTasksByCategory:
    """Test get_tasks_by_category function."""

    def test_get_code_completion_tasks(self):
        """Test filtering by code_completion category."""
        tasks = get_tasks_by_category("code_completion")
        assert len(tasks) > 0
        for task in tasks:
            assert task.category == "code_completion"

    def test_get_empty_category(self):
        """Test filtering by non-existent category."""
        tasks = get_tasks_by_category("nonexistent_category")
        assert len(tasks) == 0


class TestGetTasksByDifficulty:
    """Test get_tasks_by_difficulty function."""

    def test_get_easy_tasks(self):
        """Test filtering by easy difficulty."""
        tasks = get_tasks_by_difficulty("easy")
        assert len(tasks) > 0
        for task in tasks:
            assert task.difficulty == "easy"

    def test_get_empty_difficulty(self):
        """Test filtering by non-existent difficulty."""
        tasks = get_tasks_by_difficulty("impossible")
        assert len(tasks) == 0


class TestGetAllTasks:
    """Test get_all_tasks function."""

    def test_get_all_tasks_returns_list(self):
        """Test get_all_tasks returns a list."""
        tasks = get_all_tasks()
        assert isinstance(tasks, list)

    def test_get_all_tasks_count_matches_dict(self):
        """Test all tasks are returned."""
        tasks = get_all_tasks()
        assert len(tasks) == len(TASKS)


class TestExportTasksJson:
    """Test export_tasks_json function."""

    def test_export_returns_valid_json(self):
        """Test export produces valid JSON."""
        import json

        json_output = export_tasks_json()
        parsed = json.loads(json_output)
        assert isinstance(parsed, dict)

    def test_exported_json_contains_all_tasks(self):
        """Test exported JSON contains all task IDs."""
        import json

        json_output = export_tasks_json()
        parsed = json.loads(json_output)
        assert set(parsed.keys()) == set(TASKS.keys())
