"""Smoke tests for heliosBench"""
import pytest
from dataclasses import asdict
from helios_bench import (
    ResourceStats, RunResult, BenchmarkResult,
    ResourceMonitor, LeakDetector, BenchmarkRunner
)
from helios_bench.tasks import (
    BenchmarkTask, TASKS, get_task, get_tasks_by_category,
    get_tasks_by_difficulty, get_all_tasks, export_tasks_json
)


# === CORE MODULE IMPORTS ===

# Traces to: FR-001
def test_package_imports():
    """Verify core modules can be imported"""
    import helios_bench
    assert hasattr(helios_bench, 'ResourceMonitor')
    assert hasattr(helios_bench, 'BenchmarkRunner')
    assert hasattr(helios_bench, 'LeakDetector')


# === DATA STRUCTURES ===

# Traces to: FR-002
def test_resource_stats_construction():
    """Verify ResourceStats dataclass initializes correctly"""
    stats = ResourceStats()
    assert stats.rss_mean_mb == 0.0
    assert stats.rss_max_mb == 0.0
    assert stats.samples == 0

    stats_full = ResourceStats(
        rss_mean_mb=128.5, rss_max_mb=256.0,
        cpu_mean_percent=15.2, cpu_max_percent=45.0,
        threads_mean=4.0, threads_max=8,
        fds_mean=10.0, fds_max=20, samples=100
    )
    assert stats_full.rss_mean_mb == 128.5
    assert stats_full.samples == 100


# Traces to: FR-003
def test_run_result_construction():
    """Verify RunResult dataclass can be created"""
    stats = ResourceStats(samples=50)
    result = RunResult(
        run_id=1,
        elapsed_seconds=5.2,
        success=True,
        resources=stats,
        timestamp="2024-01-01T00:00:00"
    )
    assert result.run_id == 1
    assert result.elapsed_seconds == 5.2
    assert result.success is True
    assert asdict(result)['resources']['samples'] == 50


# Traces to: FR-004
def test_benchmark_result_construction():
    """Verify BenchmarkResult dataclass initializes"""
    result = BenchmarkResult(
        binary="/path/to/binary",
        task_id="test_id",
        task_name="Test Task",
        category="test_category",
        difficulty="easy",
        runs=5,
        timestamp="2024-01-01T00:00:00"
    )
    assert result.binary == "/path/to/binary"
    assert result.task_id == "test_id"
    assert result.runs == 5
    assert len(result.run_results) == 0


# === RESOURCE MONITOR ===

# Traces to: FR-005
def test_resource_monitor_initialization():
    """Verify ResourceMonitor can be instantiated"""
    monitor = ResourceMonitor(sample_interval=0.1)
    assert monitor.sample_interval == 0.1
    assert monitor.samples == []
    assert monitor._running is False


# Traces to: FR-006
def test_resource_monitor_aggregate_empty():
    """Verify ResourceMonitor aggregates empty samples correctly"""
    monitor = ResourceMonitor()
    stats = monitor.aggregate()
    assert isinstance(stats, ResourceStats)
    assert stats.samples == 0
    assert stats.rss_mean_mb == 0


# === TASK QUERIES ===

# Traces to: FR-007
def test_task_dict_not_empty():
    """Verify TASKS dict contains benchmark definitions"""
    assert len(TASKS) > 0
    assert "palindrome" in TASKS
    assert isinstance(TASKS["palindrome"], BenchmarkTask)


# Traces to: FR-008
def test_get_task():
    """Verify get_task retrieves tasks from registry"""
    task = get_task("palindrome")
    assert task.id == "palindrome"
    assert task.name == "Palindrome Check"
    assert task.category == "code_completion"
    assert task.difficulty == "easy"


# Traces to: FR-009
def test_get_task_fallback():
    """Verify get_task returns default for missing task"""
    task = get_task("nonexistent")
    assert task.id == "palindrome"  # falls back to default


# Traces to: FR-010
def test_get_all_tasks():
    """Verify get_all_tasks returns complete list"""
    tasks = get_all_tasks()
    assert len(tasks) > 0
    assert all(isinstance(t, BenchmarkTask) for t in tasks)
    task_ids = [t.id for t in tasks]
    assert "palindrome" in task_ids
    assert "fibonacci" in task_ids


# Traces to: FR-011
def test_get_tasks_by_category():
    """Verify category filtering works"""
    code_completion_tasks = get_tasks_by_category("code_completion")
    assert len(code_completion_tasks) > 0
    assert all(t.category == "code_completion" for t in code_completion_tasks)


# Traces to: FR-012
def test_get_tasks_by_difficulty():
    """Verify difficulty filtering works"""
    easy_tasks = get_tasks_by_difficulty("easy")
    assert len(easy_tasks) > 0
    assert all(t.difficulty == "easy" for t in easy_tasks)


# === TASK PROPERTIES ===

# Traces to: FR-013
def test_task_has_required_fields():
    """Verify all tasks have required fields"""
    for task_id, task in TASKS.items():
        assert task.id == task_id
        assert isinstance(task.name, str) and len(task.name) > 0
        assert isinstance(task.category, str) and len(task.category) > 0
        assert task.difficulty in ["easy", "medium", "hard"]
        assert isinstance(task.prompt, str) and len(task.prompt) > 0
        assert isinstance(task.timeout, int) and task.timeout > 0
        assert isinstance(task.max_tokens, int) and task.max_tokens > 0


# Traces to: FR-014
def test_task_export_json():
    """Verify export_tasks_json produces valid output"""
    json_output = export_tasks_json()
    assert isinstance(json_output, str)
    assert len(json_output) > 0
    assert '"palindrome"' in json_output
    assert '"code_completion"' in json_output


# === BENCHMARK RUNNER INITIALIZATION ===

# Traces to: FR-015
def test_benchmark_runner_initialization():
    """Verify BenchmarkRunner initializes with correct system info"""
    runner = BenchmarkRunner(binary="/mock/binary", profile="proxy-minimax")
    assert runner.binary == "/mock/binary"
    assert runner.profile == "proxy-minimax"
    assert "cpu_count" in runner.system_info
    assert "memory_total_gb" in runner.system_info
    assert "platform" in runner.system_info
    assert runner.system_info["cpu_count"] > 0
    assert runner.system_info["memory_total_gb"] > 0


# === LEAK DETECTOR ===

# Traces to: FR-016
def test_leak_detector_initialization():
    """Verify LeakDetector initializes with defaults"""
    detector = LeakDetector(runs=5, warmup=1)
    assert detector.runs == 5
    assert detector.warmup == 1
    assert len(detector.results) == 0


# Traces to: FR-017
def test_leak_detector_calc_trend():
    """Verify LeakDetector trend calculation logic"""
    detector = LeakDetector()
    # Test with constant values (no trend)
    trend = detector._calc_trend([100.0, 100.0, 100.0])
    assert abs(trend) < 0.01

    # Test with increasing values (positive trend)
    trend = detector._calc_trend([100.0, 110.0, 120.0])
    assert trend > 0


# === INTEGRATION: TASK + RUNNER ===

# Traces to: FR-018
def test_runner_system_info_validity():
    """Verify BenchmarkRunner captures valid system metrics"""
    runner = BenchmarkRunner("/bin/true")
    info = runner.system_info

    # All required fields present
    assert "cpu_count" in info
    assert "memory_total_gb" in info
    assert "platform" in info

    # Values are sensible
    assert info["cpu_count"] >= 1
    assert info["memory_total_gb"] > 0
    assert info["platform"] in ["linux", "darwin", "win32"]
