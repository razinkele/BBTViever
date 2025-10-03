"""
Application monitoring and health check utilities
"""

import time
import psutil
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .logging_config import get_logger


@dataclass
class SystemMetrics:
    """System metrics data structure"""

    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float


@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""

    timestamp: str
    uptime_seconds: float
    wms_response_time: Optional[float] = None
    wms_status: str = "unknown"
    active_connections: int = 0
    cache_hit_rate: float = 0.0


class HealthChecker:
    """Health check and monitoring service"""

    def __init__(self, wms_base_url: str, timeout: int = 10):
        self.wms_base_url = wms_base_url
        self.timeout = timeout
        self.logger = get_logger("health_check")
        self.startup_time = time.time()

    def check_system_health(self) -> SystemMetrics:
        """Check system resource health"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_used_mb = (memory.total - memory.available) / 1024 / 1024
            memory_available_mb = memory.available / 1024 / 1024

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / 1024 / 1024 / 1024

            return SystemMetrics(
                timestamp=datetime.utcnow().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=round(memory_used_mb, 2),
                memory_available_mb=round(memory_available_mb, 2),
                disk_usage_percent=round(disk_usage_percent, 2),
                disk_free_gb=round(disk_free_gb, 2),
            )

        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            raise

    def check_wms_health(self) -> Dict[str, Any]:
        """Check WMS service health"""
        try:
            start_time = time.time()

            params = {"service": "WMS", "version": "1.3.0", "request": "GetCapabilities"}

            response = requests.get(self.wms_base_url, params=params, timeout=self.timeout)

            response_time = time.time() - start_time

            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": round(response_time, 3),
                "status_code": response.status_code,
                "content_length": len(response.content),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "response_time": self.timeout,
                "error": "Request timeout",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_error",
                "error": "Could not connect to WMS service",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Unexpected error checking WMS health: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def get_application_metrics(self) -> ApplicationMetrics:
        """Get application-specific metrics"""
        uptime = time.time() - self.startup_time

        # Check WMS health
        wms_health = self.check_wms_health()

        return ApplicationMetrics(
            timestamp=datetime.utcnow().isoformat(),
            uptime_seconds=round(uptime, 2),
            wms_response_time=wms_health.get("response_time"),
            wms_status=wms_health.get("status", "unknown"),
        )

    def get_comprehensive_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        try:
            system_metrics = self.check_system_health()
            app_metrics = self.get_application_metrics()
            wms_health = self.check_wms_health()

            # Determine overall health status
            overall_status = "healthy"

            # Check system health thresholds
            if system_metrics.cpu_percent > 80:
                overall_status = "warning"
            if system_metrics.memory_percent > 85:
                overall_status = "warning"
            if system_metrics.disk_usage_percent > 90:
                overall_status = "critical"

            # Check WMS health
            if wms_health["status"] != "healthy":
                if overall_status == "healthy":
                    overall_status = "warning"

            return {
                "overall_status": overall_status,
                "timestamp": datetime.utcnow().isoformat(),
                "system": asdict(system_metrics),
                "application": asdict(app_metrics),
                "wms_service": wms_health,
                "checks": {
                    "system_resources": (
                        "pass"
                        if system_metrics.cpu_percent < 80 and system_metrics.memory_percent < 85
                        else "fail"
                    ),
                    "disk_space": "pass" if system_metrics.disk_usage_percent < 90 else "fail",
                    "wms_connectivity": "pass" if wms_health["status"] == "healthy" else "fail",
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to generate health report: {e}")
            return {
                "overall_status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""

    def __init__(self):
        self.logger = get_logger("performance")
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "total_response_time": 0.0,
            "wms_requests": 0,
            "wms_errors": 0,
            "wms_total_time": 0.0,
        }

    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """Record HTTP request metrics"""
        self.metrics["request_count"] += 1
        self.metrics["total_response_time"] += response_time

        if status_code >= 400:
            self.metrics["error_count"] += 1

        self.logger.debug(
            f"Request recorded - {endpoint}: {response_time:.3f}s, status: {status_code}"
        )

    def record_wms_request(self, response_time: float, success: bool):
        """Record WMS request metrics"""
        self.metrics["wms_requests"] += 1
        self.metrics["wms_total_time"] += response_time

        if not success:
            self.metrics["wms_errors"] += 1

        self.logger.debug(f"WMS request recorded: {response_time:.3f}s, success: {success}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        request_count = self.metrics["request_count"]
        wms_requests = self.metrics["wms_requests"]

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "requests": {
                "total": request_count,
                "errors": self.metrics["error_count"],
                "error_rate": (
                    (self.metrics["error_count"] / request_count) * 100 if request_count > 0 else 0
                ),
                "avg_response_time": (
                    (self.metrics["total_response_time"] / request_count)
                    if request_count > 0
                    else 0
                ),
            },
            "wms": {
                "total_requests": wms_requests,
                "errors": self.metrics["wms_errors"],
                "error_rate": (
                    (self.metrics["wms_errors"] / wms_requests) * 100 if wms_requests > 0 else 0
                ),
                "avg_response_time": (
                    (self.metrics["wms_total_time"] / wms_requests) if wms_requests > 0 else 0
                ),
            },
        }

    def reset_metrics(self):
        """Reset all metrics counters"""
        self.metrics = {
            key: 0 if isinstance(value, int) else 0.0 for key, value in self.metrics.items()
        }
        self.logger.info("Performance metrics reset")


# Global instances
performance_monitor = PerformanceMonitor()


def create_health_checker(wms_base_url: str, timeout: int = 10) -> HealthChecker:
    """Create a health checker instance"""
    return HealthChecker(wms_base_url, timeout)


def log_performance_metrics():
    """Log current performance metrics"""
    logger = get_logger("metrics")
    summary = performance_monitor.get_performance_summary()

    logger.info(
        f"Performance Summary - Requests: {summary['requests']['total']}, "
        f"Avg Response Time: {summary['requests']['avg_response_time']:.3f}s, "
        f"Error Rate: {summary['requests']['error_rate']:.1f}%"
    )

    if summary["wms"]["total_requests"] > 0:
        logger.info(
            f"WMS Performance - Requests: {summary['wms']['total_requests']}, "
            f"Avg Response Time: {summary['wms']['avg_response_time']:.3f}s, "
            f"Error Rate: {summary['wms']['error_rate']:.1f}%"
        )
