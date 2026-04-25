"""Smoke tests for heliosBench"""
import pytest
import json
import statistics
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


# === RESOURCE MONITOR: STRESS TEST ===

# Traces to: FR-003
def test_resource_monitor_high_frequency_sampling():
    """Verify ResourceMonitor handles high-frequency sampling correctly"""
    monitor = ResourceMonitor(sample_interval=0.01)
    assert monitor.sample_interval == 0.01

    # Simulate stress with many samples
    for _ in range(50):
        monitor.samples.append({
            'rss_mb': 128.5,
            'cpu_percent': 45.2,
            'threads': 8,
            'fds': 20,
        })

    stats = monitor.aggregate()
    assert abs(stats.rss_mean_mb - 128.5) < 0.1
    assert abs(stats.cpu_mean_percent - 45.2) < 0.1
    assert stats.threads_max == 8
    assert stats.fds_max == 20
    assert stats.samples == 50


# Traces to: FR-003
def test_resource_monitor_partial_samples():
    """Verify ResourceMonitor gracefully handles partial/missing metrics"""
    monitor = ResourceMonitor()

    # Add samples with missing metrics (some zero, some missing)
    monitor.samples = [
        {'rss_mb': 100.0, 'cpu_percent': 10.0, 'threads': 4, 'fds': 15},
        {'rss_mb': 0, 'cpu_percent': 0, 'threads': 0, 'fds': 0},
        {'rss_mb': 120.0, 'cpu_percent': 20.0, 'threads': 5, 'fds': 18},
    ]

    stats = monitor.aggregate()
    # Only non-zero values should be included
    assert stats.rss_mean_mb == 110.0  # (100 + 120) / 2
    assert stats.cpu_mean_percent == 15.0  # (10 + 20) / 2
    assert stats.threads_max == 5
    assert stats.fds_max == 18
    assert stats.samples == 3


# === LEAK DETECTOR: EDGE CASES ===

# Traces to: FR-002
def test_leak_detector_single_point_trend():
    """Verify LeakDetector trend calculation with single data point"""
    detector = LeakDetector()
    trend = detector._calc_trend([100.0])
    assert trend == 0.0  # Cannot calculate trend from 1 value


# Traces to: FR-002
def test_leak_detector_all_zero_values():
    """Verify LeakDetector handles all-zero memory readings"""
    detector = LeakDetector()
    trend = detector._calc_trend([0.0, 0.0, 0.0])
    assert abs(trend) < 0.01  # No trend with constant zeros


# Traces to: FR-002
def test_leak_detector_descending_trend():
    """Verify LeakDetector detects negative trends (memory release)"""
    detector = LeakDetector()
    trend = detector._calc_trend([150.0, 100.0, 50.0])
    assert trend < 0  # Negative trend indicates memory release
    assert abs(trend) > 0  # Should have measurable trend


# Traces to: FR-002
def test_leak_detector_analyze_leaks_healthy():
    """Verify LeakDetector marks healthy runs with stable memory"""
    detector = LeakDetector(runs=5)
    detector.results = [
        {'rss_max_mb': 100.0, 'fds_max': 20},
        {'rss_max_mb': 101.0, 'fds_max': 21},
        {'rss_max_mb': 99.5, 'fds_max': 19},
        {'rss_max_mb': 100.5, 'fds_max': 20},
        {'rss_max_mb': 100.2, 'fds_max': 21},
    ]

    analysis = detector._analyze_leaks()
    assert analysis['healthy'] is True
    assert analysis['memory']['leak'] is False
    assert analysis['file_descriptors']['leak'] is False


# Traces to: FR-002
def test_leak_detector_analyze_leaks_unhealthy_memory():
    """Verify LeakDetector detects memory leaks"""
    detector = LeakDetector(runs=5)
    detector.results = [
        {'rss_max_mb': 100.0, 'fds_max': 20},
        {'rss_max_mb': 115.0, 'fds_max': 20},
        {'rss_max_mb': 130.0, 'fds_max': 20},
        {'rss_max_mb': 145.0, 'fds_max': 20},
        {'rss_max_mb': 160.0, 'fds_max': 20},
    ]

    analysis = detector._analyze_leaks()
    assert analysis['memory']['leak'] is True
    assert analysis['memory']['trend'] > 0.1
    assert analysis['healthy'] is False


# === TASK REGISTRY: FILTER COMBINATIONS ===

# Traces to: FR-008
def test_task_category_difficulty_filter_combination():
    """Verify filtering by both category and difficulty"""
    # Get easy code_completion tasks
    all_tasks = get_all_tasks()
    code_tasks = [t for t in all_tasks if t.category == "code_completion"]
    easy_code_tasks = [t for t in code_tasks if t.difficulty == "easy"]

    assert len(easy_code_tasks) > 0
    for task in easy_code_tasks:
        assert task.category == "code_completion"
        assert task.difficulty == "easy"


# Traces to: FR-007
def test_task_category_distribution():
    """Verify task distribution across categories"""
    all_tasks = get_all_tasks()
    categories = {}
    for task in all_tasks:
        cat = task.category
        categories[cat] = categories.get(cat, 0) + 1

    assert len(categories) > 1  # Multiple categories present
    for cat in categories:
        assert categories[cat] > 0


# === BENCHMARK RESULT AGGREGATION ===

# Traces to: FR-004
def test_benchmark_result_run_aggregation():
    """Verify BenchmarkResult correctly aggregates run data"""
    stats1 = ResourceStats(rss_mean_mb=128.0, rss_max_mb=256.0, samples=50)
    stats2 = ResourceStats(rss_mean_mb=130.0, rss_max_mb=260.0, samples=50)

    run1 = RunResult(run_id=1, elapsed_seconds=5.2, success=True, resources=stats1, timestamp="2024-01-01T00:00:00")
    run2 = RunResult(run_id=2, elapsed_seconds=5.1, success=True, resources=stats2, timestamp="2024-01-01T00:00:01")

    result = BenchmarkResult(
        binary="/bin/test",
        task_id="test_task",
        task_name="Test Task",
        category="code_completion",
        difficulty="easy",
        runs=2,
        run_results=[run1, run2],
        timestamp="2024-01-01T00:00:00"
    )

    assert len(result.run_results) == 2
    assert result.runs == 2
    assert all(r.success for r in result.run_results)


# Traces to: FR-005
def test_benchmark_result_metric_calculation():
    """Verify basic metrics can be calculated from BenchmarkResult"""
    stats = [ResourceStats(rss_mean_mb=100 + i*10, rss_max_mb=200 + i*10) for i in range(3)]
    runs = [RunResult(run_id=i+1, elapsed_seconds=5.0 + i*0.1, success=True, resources=stats[i]) for i in range(3)]

    result = BenchmarkResult(
        binary="/bin/test",
        task_id="metric_test",
        task_name="Metric Test",
        category="code_completion",
        difficulty="medium",
        runs=3,
        run_results=runs,
        timestamp="2024-01-01T00:00:00"
    )

    # Calculate mean elapsed time
    elapsed_times = [r.elapsed_seconds for r in result.run_results]
    mean_elapsed = statistics.mean(elapsed_times)
    assert abs(mean_elapsed - 5.1) < 0.01

    # Calculate memory stats
    rss_max_values = [r.resources.rss_max_mb for r in result.run_results]
    max_rss = max(rss_max_values)
    assert max_rss == 220.0


# === JSON EXPORT & SERIALIZATION ===

# Traces to: FR-006
def test_resource_stats_json_serialization():
    """Verify ResourceStats can be serialized to JSON and back"""
    original = ResourceStats(
        rss_mean_mb=128.5, rss_max_mb=256.0,
        cpu_mean_percent=15.2, cpu_max_percent=45.0,
        threads_mean=4.0, threads_max=8,
        fds_mean=10.0, fds_max=20, samples=100
    )

    # Serialize
    json_str = json.dumps(asdict(original))
    assert len(json_str) > 0

    # Deserialize
    data = json.loads(json_str)
    reconstructed = ResourceStats(**data)

    assert reconstructed.rss_mean_mb == original.rss_mean_mb
    assert reconstructed.samples == original.samples


# Traces to: FR-006
def test_run_result_json_serialization():
    """Verify RunResult round-trip JSON serialization"""
    stats = ResourceStats(rss_mean_mb=128.0, samples=50)
    original = RunResult(
        run_id=1,
        elapsed_seconds=5.2,
        success=True,
        resources=stats,
        timestamp="2024-01-01T00:00:00"
    )

    # Serialize
    json_str = json.dumps(asdict(original), default=str)
    assert '"run_id": 1' in json_str
    assert '"elapsed_seconds": 5.2' in json_str


# Traces to: FR-006
def test_benchmark_result_json_export():
    """Verify BenchmarkResult can be exported to JSON"""
    stats = ResourceStats(rss_mean_mb=128.0, rss_max_mb=256.0, samples=50)
    run = RunResult(run_id=1, elapsed_seconds=5.2, success=True, resources=stats)

    result = BenchmarkResult(
        binary="/bin/test",
        task_id="export_test",
        task_name="Export Test",
        category="code_completion",
        difficulty="easy",
        runs=1,
        run_results=[run],
        timestamp="2024-01-01T00:00:00"
    )

    # Verify it can be serialized
    json_str = json.dumps(asdict(result), default=str)
    assert '"task_id": "export_test"' in json_str
    assert '"binary": "/bin/test"' in json_str
    assert '"run_results"' in json_str
