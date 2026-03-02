#!/usr/bin/env python3
"""
Hamsters' Primitive Executor

The static layer of the Hamsters' execution pipeline.
Registers and executes atomic storage operations.

These are the vocabulary — the smallest meaningful units of work.
The ExecutionPlanner (execution_planner.py) composes these into sequences.
The primitives themselves do not change. What changes is which sequences
the system learns to compose from them.

🐹🐹🐹 "We know HOW to do things. The brain figures out WHAT to do."
"""

import asyncio
import gzip
import logging
import os
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ai_agents.distributed.base_primitive_executor import (
    PrimitiveDefinition,
    PrimitiveExecutor,
    PrimitiveResult,
)

logger = logging.getLogger('HamstersPrimitiveExecutor')


class HamsterPrimitiveExecutor(PrimitiveExecutor):
    """
    Executes atomic storage operations for the Hamsters.

    Primitives registered:
    - fstrim       : TRIM unused blocks (SSD optimization)
    - e4defrag     : Defragment ext4 filesystem
    - logrotate    : Force log rotation via logrotate
    - gzip_logs    : Compress old log files in-place (Python impl)
    - rm_temp      : Remove temporary files from /tmp and /var/tmp (Python impl)
    - apt_clean    : Clear package manager cache (apt-get clean)
    - tar_archive  : Archive old files to .tar.gz (Python impl)
    """

    def _register_primitives(self):
        self.register(PrimitiveDefinition(
            name='fstrim',
            command='fstrim -av',
            requires_sudo=True,
            domain='disk_optimization',
            description='TRIM unused blocks on SSDs',
            risk_level=1,
            estimated_duration=10.0,
        ))
        self.register(PrimitiveDefinition(
            name='e4defrag',
            command='e4defrag -c /',
            requires_sudo=True,
            domain='disk_optimization',
            description='Defragment ext4 filesystem',
            risk_level=2,
            estimated_duration=60.0,
        ))
        self.register(PrimitiveDefinition(
            name='logrotate',
            command='logrotate -f /etc/logrotate.conf',
            requires_sudo=True,
            domain='log_management',
            description='Force log rotation',
            risk_level=1,
            estimated_duration=5.0,
        ))
        self.register(PrimitiveDefinition(
            name='gzip_logs',
            command=None,
            requires_sudo=False,
            domain='log_management',
            description='Compress old log files in-place',
            risk_level=1,
            estimated_duration=15.0,
        ))
        self.register(PrimitiveDefinition(
            name='rm_temp',
            command=None,
            requires_sudo=False,
            domain='cleanup',
            description='Remove temporary files from /tmp and /var/tmp',
            risk_level=1,
            estimated_duration=10.0,
        ))
        self.register(PrimitiveDefinition(
            name='apt_clean',
            command='apt-get clean',
            requires_sudo=True,
            domain='cleanup',
            description='Clear package manager cache',
            risk_level=1,
            estimated_duration=5.0,
        ))
        self.register(PrimitiveDefinition(
            name='tar_archive',
            command=None,
            requires_sudo=False,
            domain='archival',
            description='Archive old files to .tar.gz',
            risk_level=2,
            estimated_duration=30.0,
        ))

    async def _execute_python_primitive(
        self, name: str, context: Dict[str, Any]
    ) -> PrimitiveResult:
        """Route Python-implemented primitives."""
        if name == 'gzip_logs':
            return await self._gzip_old_logs(context)
        elif name == 'rm_temp':
            return await self._remove_temp_files(context)
        elif name == 'tar_archive':
            return await self._archive_old_files(context)
        else:
            raise ValueError(
                f"No Python implementation for primitive '{name}'. "
                f"Python primitives: gzip_logs, rm_temp, tar_archive"
            )

    async def _collect_metrics(self) -> Dict[str, Any]:
        """
        Collect current storage-domain metrics.

        Returns the same metric keys the perception layer uses so that
        improvement calculations are consistent across the pipeline.
        """
        try:
            disk = shutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100.0
            available_space_gb = disk.free / (1024 ** 3)

            # Inode usage
            statvfs = os.statvfs('/')
            total_inodes = statvfs.f_files
            free_inodes = statvfs.f_ffree
            inode_usage_percent = (
                ((total_inodes - free_inodes) / total_inodes) * 100.0
                if total_inodes > 0 else 0.0
            )

            # Fragmentation — e4defrag -c / outputs fragmentation score to stdout.
            # We run it non-destructively (-c = check only) in a subprocess.
            # If it fails or times out, we use 0.0 (unknown) rather than crashing.
            fragmentation_level = await self._get_fragmentation_level()

            return {
                'disk_usage_percent': disk_usage_percent,
                'available_space_gb': available_space_gb,
                'inode_usage_percent': inode_usage_percent,
                'fragmentation_level': fragmentation_level,
                'collected_at': datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Metric collection failed: {e}", exc_info=True)
            raise

    async def _get_fragmentation_level(self) -> float:
        """
        Get fragmentation level via e4defrag -c (check-only, non-destructive).
        Returns 0.0 if unavailable (not ext4, permission denied, etc.).
        """
        try:
            process = await asyncio.create_subprocess_shell(
                'e4defrag -c / 2>/dev/null | grep -oP "\\d+\\.\\d+" | tail -1',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=10.0)
            if stdout:
                return float(stdout.decode().strip())
            return 0.0
        except Exception:
            return 0.0

    def _calculate_improvement(
        self, pre: Dict[str, Any], post: Dict[str, Any]
    ) -> float:
        """
        Storage-specific improvement calculation.

        Primary metric: disk_usage_percent decrease (weighted 0.6).
        Secondary: inode_usage_percent decrease (weighted 0.25).
        Tertiary: fragmentation_level decrease (weighted 0.15).

        Returns float in [-1.0, 1.0]:
        - Positive = improvement (things got better)
        - Negative = degradation (things got worse)
        - 0.0 = no change or metrics unavailable
        """
        improvements = []
        weights = []

        # Disk usage (primary)
        pre_disk = pre.get('disk_usage_percent')
        post_disk = post.get('disk_usage_percent')
        if pre_disk is not None and post_disk is not None and pre_disk > 0:
            disk_delta = (pre_disk - post_disk) / pre_disk
            improvements.append(max(-1.0, min(1.0, disk_delta)))
            weights.append(0.6)

        # Inode usage (secondary)
        pre_inode = pre.get('inode_usage_percent')
        post_inode = post.get('inode_usage_percent')
        if pre_inode is not None and post_inode is not None and pre_inode > 0:
            inode_delta = (pre_inode - post_inode) / pre_inode
            improvements.append(max(-1.0, min(1.0, inode_delta)))
            weights.append(0.25)

        # Fragmentation (tertiary)
        pre_frag = pre.get('fragmentation_level')
        post_frag = post.get('fragmentation_level')
        if (pre_frag is not None and post_frag is not None
                and pre_frag > 0 and pre_frag != post_frag):
            frag_delta = (pre_frag - post_frag) / pre_frag
            improvements.append(max(-1.0, min(1.0, frag_delta)))
            weights.append(0.15)

        if not improvements:
            return 0.0

        total_weight = sum(weights)
        weighted_sum = sum(imp * w for imp, w in zip(improvements, weights))
        return weighted_sum / total_weight

    # =========================================================================
    # Python primitive implementations
    # =========================================================================

    async def _gzip_old_logs(self, context: Dict[str, Any]) -> PrimitiveResult:
        """
        Compress log files older than age_days in log_directory.
        Skips files already compressed (.gz, .bz2, .xz).
        """
        log_directory = context.get('log_directory', '/var/log')
        age_days = context.get('age_days', 7)
        files_compressed = 0
        bytes_saved = 0
        errors: List[str] = []

        try:
            cutoff = datetime.now(timezone.utc).timestamp() - (age_days * 86400)
            log_path = Path(log_directory)

            if not log_path.exists():
                return PrimitiveResult(
                    primitive_name='gzip_logs',
                    success=False,
                    pre_metrics={},
                    post_metrics={},
                    improvement=0.0,
                    duration_seconds=0.0,
                    error=f"Log directory does not exist: {log_directory}"
                )

            for log_file in log_path.rglob('*'):
                if not log_file.is_file():
                    continue
                if log_file.suffix in ('.gz', '.bz2', '.xz', '.zip'):
                    continue
                try:
                    if log_file.stat().st_mtime < cutoff:
                        original_size = log_file.stat().st_size
                        gz_path = log_file.with_suffix(log_file.suffix + '.gz')
                        with log_file.open('rb') as f_in:
                            with gzip.open(gz_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        compressed_size = gz_path.stat().st_size
                        log_file.unlink()
                        bytes_saved += original_size - compressed_size
                        files_compressed += 1
                except Exception as e:
                    errors.append(f"{log_file.name}: {e}")

            self.logger.info(
                f"🐹🗜️ gzip_logs: compressed {files_compressed} files, "
                f"saved {bytes_saved / (1024**2):.1f} MB"
            )

            return PrimitiveResult(
                primitive_name='gzip_logs',
                success=True,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                stdout=(
                    f"Compressed {files_compressed} files, "
                    f"saved {bytes_saved / (1024**2):.1f} MB"
                ),
                stderr='; '.join(errors) if errors else None
            )

        except Exception as e:
            self.logger.error(f"gzip_logs failed: {e}", exc_info=True)
            return PrimitiveResult(
                primitive_name='gzip_logs',
                success=False,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                error=str(e)
            )

    async def _remove_temp_files(self, context: Dict[str, Any]) -> PrimitiveResult:
        """
        Remove files from /tmp and /var/tmp older than min_age_hours.
        Skips files currently open by processes.
        """
        min_age_hours = context.get('min_age_hours', 24)
        temp_dirs = context.get('temp_dirs', ['/tmp', '/var/tmp'])
        files_removed = 0
        bytes_freed = 0
        errors: List[str] = []

        try:
            cutoff = datetime.now(timezone.utc).timestamp() - (min_age_hours * 3600)

            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if not temp_path.exists():
                    continue
                for item in temp_path.iterdir():
                    try:
                        stat = item.stat()
                        if stat.st_mtime < cutoff:
                            size = stat.st_size
                            if item.is_file():
                                item.unlink()
                                bytes_freed += size
                                files_removed += 1
                            elif item.is_dir():
                                dir_size = sum(
                                    f.stat().st_size
                                    for f in item.rglob('*')
                                    if f.is_file()
                                )
                                shutil.rmtree(item, ignore_errors=True)
                                bytes_freed += dir_size
                                files_removed += 1
                    except PermissionError:
                        pass  # File in use or protected — skip silently
                    except Exception as e:
                        errors.append(f"{item.name}: {e}")

            self.logger.info(
                f"🐹🗑️ rm_temp: removed {files_removed} items, "
                f"freed {bytes_freed / (1024**2):.1f} MB"
            )

            return PrimitiveResult(
                primitive_name='rm_temp',
                success=True,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                stdout=(
                    f"Removed {files_removed} items, "
                    f"freed {bytes_freed / (1024**2):.1f} MB"
                ),
                stderr='; '.join(errors) if errors else None
            )

        except Exception as e:
            self.logger.error(f"rm_temp failed: {e}", exc_info=True)
            return PrimitiveResult(
                primitive_name='rm_temp',
                success=False,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                error=str(e)
            )

    async def _archive_old_files(self, context: Dict[str, Any]) -> PrimitiveResult:
        """
        Archive files older than age_days from source_directory into
        archive_directory as a timestamped .tar.gz.
        """
        source_directory = context.get('source_directory', '/var/log')
        archive_directory = context.get('archive_directory', '/var/archive')
        age_days = context.get('age_days', 30)
        files_archived = 0
        errors: List[str] = []

        try:
            source_path = Path(source_directory)
            archive_path = Path(archive_directory)
            archive_path.mkdir(parents=True, exist_ok=True)

            cutoff = datetime.now(timezone.utc).timestamp() - (age_days * 86400)
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            archive_name = archive_path / f"archive_{timestamp}.tar.gz"

            old_files = [
                f for f in source_path.rglob('*')
                if f.is_file() and f.stat().st_mtime < cutoff
            ]

            if not old_files:
                return PrimitiveResult(
                    primitive_name='tar_archive',
                    success=True,
                    pre_metrics={},
                    post_metrics={},
                    improvement=0.0,
                    duration_seconds=0.0,
                    stdout=f"No files older than {age_days} days found in {source_directory}"
                )

            with tarfile.open(archive_name, 'w:gz') as tar:
                for f in old_files:
                    try:
                        tar.add(f, arcname=f.relative_to(source_path))
                        files_archived += 1
                    except Exception as e:
                        errors.append(f"{f.name}: {e}")

            # Remove originals only if archive succeeded
            for f in old_files:
                try:
                    f.unlink()
                except Exception as e:
                    errors.append(f"unlink {f.name}: {e}")

            self.logger.info(
                f"🐹📦 tar_archive: archived {files_archived} files → {archive_name}"
            )

            return PrimitiveResult(
                primitive_name='tar_archive',
                success=True,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                stdout=f"Archived {files_archived} files to {archive_name}",
                stderr='; '.join(errors) if errors else None
            )

        except Exception as e:
            self.logger.error(f"tar_archive failed: {e}", exc_info=True)
            return PrimitiveResult(
                primitive_name='tar_archive',
                success=False,
                pre_metrics={},
                post_metrics={},
                improvement=0.0,
                duration_seconds=0.0,
                error=str(e)
            )
