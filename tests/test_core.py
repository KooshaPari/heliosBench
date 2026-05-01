"""Tests for helios_bench core module."""

import pytest

from helios_bench import LeakDetector, ResourceMonitor, ResourceStats


class TestResourceStats:
    """Test ResourceStats dataclass."""

    def test_default_values(self):
        """Test ResourceStats with default values."""
        stats = ResourceStats()
        assert stats.rss_mean_mb == 0
        assert stats.rss_max_mb == 0
        assert stats.cpu_mean_percent == 0
        assert stats.cpu_max_percent == 0
        assert stats.threads_mean == 0
        assert stats.threads_max == 0
        assert stats.fds_mean == 0
        assert stats.fds_max == 0
        assert stats.samples == 0

    def test_custom_values(self):
        """Test ResourceStats with custom values."""
        stats = ResourceStats(
            rss_mean_mb=100.5,
            rss_max_mb=150.0,
            cpu_mean_percent=45.0,
            cpu_max_percent=80.0,
            threads_mean=4.5,
            threads_max=8,
            fds_mean=12.3,
            fds_max=20,
            samples=100,
        )
        assert stats.rss_mean_mb == 100.5
        assert stats.rss_max_mb == 150.0
        assert stats.cpu_mean_percent == 45.0
        assert stats.cpu_max_percent == 80.0
        assert stats.threads_mean == 4.5
        assert stats.threads_max == 8
        assert stats.fds_mean == 12.3
        assert stats.fds_max == 20
        assert stats.samples == 100


class TestResourceMonitor:
    """Test ResourceMonitor class."""

    def test_initialization(self):
        """Test ResourceMonitor initializes correctly."""
        monitor = ResourceMonitor(sample_interval=0.5)
        assert monitor.sample_interval == 0.5
        assert monitor.samples == []
        assert monitor._running is False
        assert monitor._thread is None
        assert monitor._process is None

    def test_aggregate_empty_samples(self):
        """Test aggregation with no samples."""
        monitor = ResourceMonitor()
        stats = monitor.aggregate()
        assert stats.rss_mean_mb == 0
        assert stats.rss_max_mb == 0
        assert stats.samples == 0

    def test_aggregate_with_samples(self):
        """Test aggregation with sample data."""
        monitor = ResourceMonitor()
        monitor.samples = [
            {"rss_mb": 100, "cpu_percent": 50, "threads": 4, "fds": 10},
            {"rss_mb": 110, "cpu_percent": 60, "threads": 5, "fds": 12},
            {"rss_mb": 105, "cpu_percent": 55, "threads": 4, "fds": 11},
        ]
        stats = monitor.aggregate()

        assert stats.rss_mean_mb == pytest.approx(105, rel=0.01)
        assert stats.rss_max_mb == 110
        assert stats.cpu_mean_percent == pytest.approx(55, rel=0.01)
        assert stats.cpu_max_percent == 60
        assert stats.threads_mean == pytest.approx(4.33, rel=0.01)
        assert stats.threads_max == 5
        assert stats.fds_mean == pytest.approx(11, rel=0.01)
        assert stats.fds_max == 12
        assert stats.samples == 3

    def test_aggregate_filters_zero_values(self):
        """Test aggregation filters out zero values."""
        monitor = ResourceMonitor()
        monitor.samples = [
            {"rss_mb": 0, "cpu_percent": 0, "threads": 0, "fds": 0},
            {"rss_mb": 100, "cpu_percent": 50, "threads": 4, "fds": 10},
        ]
        stats = monitor.aggregate()

        # Should only count non-zero values
        assert stats.rss_mean_mb == 100
        assert stats.rss_max_mb == 100


class TestLeakDetector:
    """Test LeakDetector class."""

    def test_initialization(self):
        """Test LeakDetector initializes correctly."""
        detector = LeakDetector(runs=5, warmup=3)
        assert detector.runs == 5
        assert detector.warmup == 3
        assert detector.results == []

    def test_calc_trend_single_value(self):
        """Test trend calculation with single value returns 0."""
        detector = LeakDetector()
        trend = detector._calc_trend([100.0])
        assert trend == 0.0

    def test_calc_trend_empty_list(self):
        """Test trend calculation with empty list returns 0."""
        detector = LeakDetector()
        trend = detector._calc_trend([])
        assert trend == 0.0

    def test_calc_trend_no_trend(self):
        """Test trend calculation with constant values."""
        detector = LeakDetector()
        trend = detector._calc_trend([100.0, 100.0, 100.0, 100.0])
        assert trend == 0.0

    def test_calc_trend_positive(self):
        """Test trend calculation with increasing values."""
        detector = LeakDetector()
        # Linear increase: 100, 200, 300, 400
        trend = detector._calc_trend([100.0, 200.0, 300.0, 400.0])
        assert trend > 0

    def test_calc_trend_negative(self):
        """Test trend calculation with decreasing values."""
        detector = LeakDetector()
        # Linear decrease: 400, 300, 200, 100
        trend = detector._calc_trend([400.0, 300.0, 200.0, 100.0])
        assert trend < 0

    def test_analyze_leaks_no_leak(self):
        """Test leak analysis with stable values."""
        detector = LeakDetector(runs=5)
        detector.results = [
            {"rss_max_mb": 100, "fds_max": 10},
            {"rss_max_mb": 101, "fds_max": 10},
            {"rss_max_mb": 100, "fds_max": 11},
            {"rss_max_mb": 100, "fds_max": 10},
            {"rss_max_mb": 100, "fds_max": 10},
        ]
        analysis = detector._analyze_leaks()
        assert analysis["runs"] == 5
        assert analysis["healthy"] is True
        assert analysis["memory"]["leak"] is False
        assert analysis["file_descriptors"]["leak"] is False

    def test_analyze_leaks_with_memory_leak(self):
        """Test leak analysis detects memory leak."""
        detector = LeakDetector()
        # Strong increasing trend in RSS
        detector.results = [
            {"rss_max_mb": 100, "fds_max": 10},
            {"rss_max_mb": 150, "fds_max": 10},
            {"rss_max_mb": 200, "fds_max": 10},
            {"rss_max_mb": 250, "fds_max": 10},
            {"rss_max_mb": 300, "fds_max": 10},
        ]
        analysis = detector._analyze_leaks()
        assert analysis["memory"]["leak"] is True
        assert analysis["healthy"] is False

    def test_analyze_leaks_with_fd_leak(self):
        """Test leak analysis detects file descriptor leak."""
        detector = LeakDetector()
        # Strong increasing trend in FDs
        detector.results = [
            {"rss_max_mb": 100, "fds_max": 10},
            {"rss_max_mb": 100, "fds_max": 20},
            {"rss_max_mb": 100, "fds_max": 30},
            {"rss_max_mb": 100, "fds_max": 40},
            {"rss_max_mb": 100, "fds_max": 50},
        ]
        analysis = detector._analyze_leaks()
        assert analysis["file_descriptors"]["leak"] is True
        assert analysis["healthy"] is False
