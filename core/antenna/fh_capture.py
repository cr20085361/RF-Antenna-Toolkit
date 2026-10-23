"""跳频测向捕获的串行时间预算，版本 2.3。

固定一路参考通道，其他通道依次覆盖剩余阵元。这里只判断同一跳内
能否采齐数据，不推定实际捕获概率、测向精度或连续处理吞吐量。
所有时间以秒表示，所有频率和采样率以每秒表示，计算层不依赖界面。
"""

import math
from dataclasses import dataclass, replace
from numbers import Real
from typing import Tuple


@dataclass(frozen=True)
class CaptureParams:
    """输入参数；默认值仅用于九元双通道教学示例。"""

    elements: int = 9
    channels: int = 2
    switch_s: float = 500e-9
    acquisition_s: float = 5e-6
    hop_rate_hz: float = 10000.0
    first_group_ready: bool = False
    unavailable_s: float = 0.0
    latency_s: float = 0.0
    settling_s: float = 0.0
    blocking_s: float = 0.0
    reserve_s: float = 0.0
    processing_s: float = 0.0


@dataclass(frozen=True)
class CaptureStage:
    """相对于连续有效窗口起点的物理阶段；组号零表示公共启动阶段。"""

    kind: str
    group: int
    start_s: float
    end_s: float

    @property
    def duration_s(self) -> float:
        """从统一起止坐标取得阶段时长，供表格和图形复用。"""
        return self.end_s - self.start_s


@dataclass(frozen=True)
class CaptureGroup:
    """一组同时连接的阵元；编号一始终是参考阵元。"""

    index: int
    elements: Tuple[int, ...]
    start_s: float
    acquisition_start_s: float
    end_s: float


@dataclass(frozen=True)
class CaptureResult:
    """统一结果，图表与结论均从本对象读取，避免重复计算不同步。"""

    params: CaptureParams
    group_count: int
    switch_count: int
    period_s: float
    effective_s: float
    scan_s: float
    data_complete_s: float
    required_s: float
    actual_margin_s: float
    design_margin_s: float
    max_hop_rate_hz: float
    reserved_max_hop_rate_hz: float
    latest_start_s: float
    result_ready_s: float
    status: str
    assumptions: Tuple[str, ...]
    groups: Tuple[CaptureGroup, ...]
    stages: Tuple[CaptureStage, ...]


class CaptureCalculator:
    """串行预算计算器，切换完成后的额外稳定才另行计时。"""

    @staticmethod
    def _number(value: float, label: str, positive: bool = False) -> None:
        """拒绝非数值、非有限值及物理上无效的时间或速率。"""
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError(f"{label}必须是有限数值")
        if value < 0 or (positive and value == 0):
            raise ValueError(f"{label}必须{'大于零' if positive else '大于或等于零'}")

    @staticmethod
    def acquisition_from_samples(samples: int, sample_rate_hz: float) -> float:
        """将每通道有效点数换成采集时长，不推断这些点是否满足算法精度。"""
        if type(samples) is not int or samples <= 0:
            raise ValueError("每通道采样点数必须是正整数")
        CaptureCalculator._number(sample_rate_hz, "有效采样率", positive=True)
        try:
            duration = samples / sample_rate_hz
        except OverflowError as exc:
            raise ValueError("采样时间超出可计算范围") from exc
        CaptureCalculator._number(duration, "采样时间", positive=True)
        return duration

    @staticmethod
    def calculate(params: CaptureParams) -> CaptureResult:
        """计算完整分组时间轴及单跳可行性；所有阶段默认不重叠。"""
        if type(params.elements) is not int or params.elements < 2:
            raise ValueError("阵元总数必须是至少为二的整数，且包含参考阵元")
        if type(params.channels) is not int or not 2 <= params.channels <= params.elements:
            raise ValueError("相干接收通道数必须是二至阵元总数之间的整数")
        if type(params.first_group_ready) is not bool:
            raise ValueError("首组就绪状态必须为布尔值")
        for field, label in (
            ("switch_s", "单次切换时间"), ("settling_s", "额外稳定时间"),
            ("latency_s", "启动延迟"), ("blocking_s", "组间阻塞时间"),
            ("unavailable_s", "每跳不可用时间"), ("reserve_s", "预留余量"),
            ("processing_s", "采集后处理时间"),
        ):
            CaptureCalculator._number(getattr(params, field), label)
        CaptureCalculator._number(params.acquisition_s, "每组有效采集时间", positive=True)
        CaptureCalculator._number(params.hop_rate_hz, "跳速", positive=True)

        # 整数向上取整，最后一组不足时保留空闲通道，不多算一组。
        parallel = params.channels - 1
        group_count = (params.elements - 1 + parallel - 1) // parallel
        switch_count = group_count - int(params.first_group_ready)
        period = 1.0 / params.hop_rate_hz
        effective = max(0.0, period - params.unavailable_s)
        scan = (switch_count * (params.switch_s + params.settling_s)
                + group_count * params.acquisition_s
                + (group_count - 1) * params.blocking_s)
        data_complete = params.latency_s + scan
        required = data_complete + params.reserve_s
        result_ready = data_complete + params.processing_s
        physical_period = params.unavailable_s + data_complete
        reserved_period = params.unavailable_s + required
        derived = (period, scan, data_complete, required, result_ready,
                   physical_period, reserved_period)
        if not all(math.isfinite(value) and value > 0 for value in derived):
            raise ValueError("时间预算超出可计算范围，请调整数值量级")
        max_rate = 1.0 / physical_period
        reserved_rate = 1.0 / reserved_period
        if not math.isfinite(max_rate) or not math.isfinite(reserved_rate):
            raise ValueError("跳速上限超出可计算范围")

        # 容差只消除浮点舍入误差，不用显示小数位决定是否可行。
        tolerance = 32 * math.ulp(max(period, required))

        def margin(value: float) -> float:
            return 0.0 if abs(value) <= tolerance else value

        actual_margin = margin(effective - data_complete)
        design_margin = margin(effective - required)
        if effective == 0 or actual_margin < 0:
            status = "insufficient"
        elif actual_margin == 0:
            status = "boundary"
        elif design_margin < 0:
            status = "reserve_shortfall"
        else:
            status = "feasible"

        stages = []
        groups = []
        cursor = 0.0

        def append_stage(kind: str, group: int, duration: float) -> None:
            """每段紧接上一段，保留零时长切换以便核对切换次数。"""
            nonlocal cursor
            end = cursor + duration
            stages.append(CaptureStage(kind, group, cursor, end))
            cursor = end

        append_stage("latency", 0, params.latency_s)
        for index in range(1, group_count + 1):
            start = cursor
            if index > 1 or not params.first_group_ready:
                append_stage("switch", index, params.switch_s)
                append_stage("settle", index, params.settling_s)
            acquisition_start = cursor
            append_stage("acquire", index, params.acquisition_s)
            first = 2 + (index - 1) * parallel
            members = (1,) + tuple(range(first, min(first + parallel, params.elements + 1)))
            groups.append(CaptureGroup(index, members, start, acquisition_start, cursor))
            if index < group_count:
                append_stage("block", index, params.blocking_s)

        assumptions = [
            "固定一路参考；各组通道同时采样；整套数据来自同一跳的一个连续有效窗口。",
            "时间足够不代表实际捕获成功；带宽、信噪比、相干校准和多径仍需验证。",
            "跳速上限假定所填净开销与启动延迟不变，不代表连续处理每一跳的吞吐能力。",
        ]
        if params.latency_s == 0:
            assumptions.append("启动延迟为零：当前按有效窗口起点立即启动的最佳情况评估。")
        if params.unavailable_s >= period:
            assumptions.append("每跳不可用时间已耗尽跳周期，没有连续有效窗口。")
        return CaptureResult(
            params, group_count, switch_count, period, effective, scan, data_complete,
            required, actual_margin, design_margin, max_rate, reserved_rate,
            margin(effective - scan - params.reserve_s), result_ready, status,
            tuple(assumptions), tuple(groups), tuple(stages),
        )

    @staticmethod
    def sweep(params: CaptureParams, rates: Tuple[float, ...]) -> Tuple[CaptureResult, ...]:
        """跳速扫描仍使用同一计算模型，图表不另写近似公式。"""
        return tuple(CaptureCalculator.calculate(replace(params, hop_rate_hz=rate)) for rate in rates)
