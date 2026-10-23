"""跳频时间预算的手算基准、物理边界与时间轴一致性验证。"""

import math
from dataclasses import replace

import pytest

from core.antenna.fh_capture import CaptureCalculator, CaptureParams


def calculate(**changes):
    """基于公开的九元双通道教学输入修改待测参数。"""
    return CaptureCalculator.calculate(replace(CaptureParams(), **changes))


def test_default_hand_calculation():
    """八次切换四微秒，加八组采样四十微秒。"""
    result = calculate()
    assert result.group_count == result.switch_count == 8
    assert result.scan_s == pytest.approx(44e-6)
    assert result.actual_margin_s == pytest.approx(56e-6)
    assert result.max_hop_rate_hz == pytest.approx(22727.27272727)
    assert result.latest_start_s == pytest.approx(56e-6)
    assert result.status == "feasible"
    assert [group.elements for group in result.groups] == [(1, i) for i in range(2, 10)]


@pytest.mark.parametrize("rate,margin,status", [
    (10000, 56e-6, "feasible"), (20000, 6e-6, "feasible"),
    (25000, -4e-6, "insufficient"), (1 / 44e-6, 0, "boundary"),
])
def test_target_rates(rate, margin, status):
    """用用户可手算的三档跳速及临界点验证判定。"""
    result = calculate(hop_rate_hz=rate)
    assert result.actual_margin_s == pytest.approx(margin)
    assert result.status == status


def test_ready_first_group_skips_both_switch_and_settling():
    """首组稳定时同时少计一次切换和一次额外稳定，采集仍是八组。"""
    assert calculate(first_group_ready=True).scan_s == pytest.approx(43.5e-6)
    cold = calculate(settling_s=2e-6)
    ready = calculate(settling_s=2e-6, first_group_ready=True)
    assert ready.group_count == 8
    assert ready.switch_count == 7
    assert cold.scan_s - ready.scan_s == pytest.approx(2.5e-6)
    assert ready.stages[1].kind == "acquire"


@pytest.mark.parametrize("channels,groups,last", [(3, 4, (1, 8, 9)), (4, 3, (1, 8, 9)), (9, 1, tuple(range(1, 10)))])
def test_parallel_channels_cover_each_nonreference_element_once(channels, groups, last):
    """验证并行采样、向上取整及最后一组的闲置通道。"""
    result = calculate(channels=channels)
    assert result.group_count == groups
    assert result.groups[-1].elements == last
    assert [element for group in result.groups for element in group.elements[1:]] == list(range(2, 10))
    sampling = sum(s.duration_s for s in result.stages if s.kind == "acquire")
    assert sampling == pytest.approx(groups * 5e-6)


def test_fully_parallel_ready_has_no_switch_settle_or_intergroup_blocking():
    """全通道并行且已就绪时只需要一次有效采集。"""
    result = calculate(channels=9, first_group_ready=True, settling_s=1, blocking_s=2)
    assert result.switch_count == 0
    assert result.scan_s == pytest.approx(5e-6)


def test_all_overheads_and_timeline_match_independent_budget():
    """两次组间阻塞、三次切换稳定，不重复计入启动延迟和后处理。"""
    result = calculate(channels=4, switch_s=0.5e-6, settling_s=1e-6, acquisition_s=5e-6,
                       blocking_s=2e-6, latency_s=3e-6, unavailable_s=10e-6,
                       reserve_s=4e-6, processing_s=20e-6)
    assert result.scan_s == pytest.approx(23.5e-6)
    assert result.data_complete_s == pytest.approx(26.5e-6)
    assert result.required_s == pytest.approx(30.5e-6)
    assert result.result_ready_s == pytest.approx(46.5e-6)
    assert result.effective_s == pytest.approx(90e-6)
    assert result.design_margin_s == pytest.approx(59.5e-6)
    assert result.max_hop_rate_hz == pytest.approx(1 / 36.5e-6)
    assert result.reserved_max_hop_rate_hz == pytest.approx(1 / 40.5e-6)
    for left, right in zip(result.stages, result.stages[1:]):
        assert left.end_s == right.start_s
    assert result.stages[-1].end_s == pytest.approx(result.data_complete_s)
    assert sum(stage.duration_s for stage in result.stages) == pytest.approx(result.data_complete_s)
    for group in result.groups:
        acquisition = next(s for s in result.stages if s.group == group.index and s.kind == "acquire")
        assert acquisition.start_s == group.acquisition_start_s
        assert acquisition.end_s == group.end_s


def test_postprocessing_only_changes_result_latency():
    """离线运算不需要信号继续存在，不误判成采集失败。"""
    ordinary = calculate()
    slow = calculate(processing_s=1)
    assert ordinary.scan_s == slow.scan_s
    assert ordinary.max_hop_rate_hz == slow.max_hop_rate_hz
    assert ordinary.status == slow.status
    assert slow.result_ready_s == pytest.approx(1.000044)


def test_reserve_shortfall_and_exact_reserved_boundary():
    """有六微秒实际余量，但要求七微秒时必须给出不同结论。"""
    shortfall = calculate(hop_rate_hz=20000, reserve_s=7e-6)
    assert shortfall.status == "reserve_shortfall"
    assert shortfall.design_margin_s == pytest.approx(-1e-6)
    boundary = calculate(hop_rate_hz=20000, reserve_s=6e-6)
    assert boundary.status == "feasible"
    assert boundary.design_margin_s == 0


def test_late_start_and_dead_time_consume_available_window():
    """五微秒不可用再加三微秒启动延迟，使原本可用的五十微秒周期失败。"""
    result = calculate(hop_rate_hz=20000, unavailable_s=5e-6, latency_s=3e-6)
    assert result.effective_s == pytest.approx(45e-6)
    assert result.actual_margin_s == pytest.approx(-2e-6)
    assert result.status == "insufficient"
    assert result.latest_start_s == pytest.approx(1e-6)


@pytest.mark.parametrize("unavailable", [100e-6, 120e-6])
def test_no_effective_window_is_not_negative_duration(unavailable):
    """不可用时间耗尽周期时显示零窗口及不足结论。"""
    result = calculate(unavailable_s=unavailable)
    assert result.effective_s == 0
    assert result.status == "insufficient"
    assert any("耗尽" in item for item in result.assumptions)


def test_classification_does_not_use_display_rounding():
    """远小于显示分辨率的真实超时仍判失败，只吸收浮点舍入误差。"""
    result = calculate(hop_rate_hz=1 / (44e-6 - 1e-13))
    assert result.status == "insufficient"
    assert result.actual_margin_s < 0


def test_sampling_conversion_and_sweep_use_public_model():
    """换算得到五微秒，扫描包含正常、临界、超时及零窗口情形。"""
    assert CaptureCalculator.acquisition_from_samples(50, 10e6) == pytest.approx(5e-6)
    params = CaptureParams(unavailable_s=5e-6)
    rates = (10000, 1 / 49e-6, 25000, 250000)
    results = CaptureCalculator.sweep(params, rates)
    assert [point.status for point in results] == ["feasible", "boundary", "insufficient", "insufficient"]
    for rate, point in zip(rates, results):
        assert point == CaptureCalculator.calculate(replace(params, hop_rate_hz=rate))


@pytest.mark.parametrize("changes", [
    {"elements": 1}, {"elements": 9.5}, {"elements": True}, {"channels": 1},
    {"channels": 10}, {"channels": 2.5}, {"first_group_ready": 1},
    {"acquisition_s": 0}, {"acquisition_s": -1}, {"hop_rate_hz": 0},
    {"hop_rate_hz": -1}, {"hop_rate_hz": 1e-320},
    {"switch_s": -1}, {"latency_s": -1}, {"settling_s": -1},
    {"blocking_s": -1}, {"unavailable_s": -1}, {"reserve_s": -1}, {"processing_s": -1},
    {"latency_s": math.nan}, {"hop_rate_hz": math.inf}, {"acquisition_s": -math.inf},
    {"switch_s": "500"}, {"processing_s": True}, {"switch_s": 1e308},
])
def test_invalid_inputs_fail_clearly(changes):
    """核心接口也校验输入，不能仅依赖界面控件。"""
    with pytest.raises(ValueError):
        calculate(**changes)


@pytest.mark.parametrize("points,rate", [(0, 10e6), (2.5, 10e6), (True, 10e6), (50, 0), (50, math.nan), (50, 1e-320)])
def test_invalid_sampling_parameters(points, rate):
    """拒绝无意义点数及会产生溢出的采样率。"""
    with pytest.raises(ValueError):
        CaptureCalculator.acquisition_from_samples(points, rate)
