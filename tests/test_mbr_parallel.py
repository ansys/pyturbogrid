# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

"""Server-free tests for MBR dispatch barriers, row routing and worker failures."""

from threading import Barrier, Event
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR


@pytest.fixture
def machine():
    mbr = MBR(saas_server=False)
    mbr.tg_worker_instances = {row: SimpleNamespace(pytg=Mock()) for row in ("A", "B", "C")}
    yield mbr
    mbr.quit()


def test_actions_overlap_across_rows_but_preserve_each_rows_order(machine):
    barriers = {name: Barrier(3) for name in ("loadinlet", "loadoutlet")}
    completed = {row: [] for row in machine.tg_worker_instances}
    actions = {}
    for row, worker in machine.tg_worker_instances.items():

        def perform(action, arguments, row=row):
            barriers[action].wait(timeout=3)
            completed[row].append((action, arguments))

        worker.pytg.perform_action.side_effect = perform
        actions[row] = [("loadinlet", f"in-{row}"), ("loadoutlet", f"out-{row}")]
    machine.perform_br_actions(actions)
    assert completed == actions


def test_read_into_blank_is_parallel_and_preserves_caller_import_flags(machine, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    barrier = Barrier(3)
    for worker in machine.tg_worker_instances.values():
        worker.pytg.read_tginit.side_effect = lambda **kwargs: barrier.wait(timeout=3)
    machine.read_tginit_into_blank("case.tginit", autoregions=False, secondary=[])
    for row, worker in machine.tg_worker_instances.items():
        worker.pytg.read_tginit.assert_called_once_with(
            path="case.tginit",
            bladerow=row,
            autoregions=False,
            includemesh=False,
            secondary=[],
        )


def test_legacy_read_defaults_are_unchanged(machine):
    machine.read_tginit_into_blank("case.tginit")
    for row, worker in machine.tg_worker_instances.items():
        worker.pytg.read_tginit.assert_called_once_with(
            path="case.tginit",
            bladerow=row,
            autoregions=True,
            includemesh=False,
        )


def test_primary_only_import_is_parallel_and_emits_explicit_empty_selection(machine, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    barrier = Barrier(3)
    for worker in machine.tg_worker_instances.values():
        worker.pytg.read_tginit.side_effect = lambda **kwargs: barrier.wait(timeout=3)
    machine.read_tginit_into_blank("case.tginit", autoregions=False, include_secondary=False)
    for row, worker in machine.tg_worker_instances.items():
        worker.pytg.read_tginit.assert_called_once_with(
            path="case.tginit",
            bladerow=row,
            autoregions=False,
            includemesh=False,
            secondary=[""],
        )


def test_conflicting_secondary_import_options_fail_before_dispatch(machine):
    with pytest.raises(ValueError, match="Cannot select secondary"):
        machine.read_tginit_into_blank("case.tginit", secondary=["cavity"], include_secondary=False)
    for worker in machine.tg_worker_instances.values():
        worker.pytg.read_tginit.assert_not_called()


def test_parameter_updates_overlap_across_rows_and_remain_ordered(machine):
    barriers = {name: Barrier(3) for name in ("first=1", "second=2")}
    completed = {row: [] for row in machine.tg_worker_instances}
    states = {}
    for row, worker in machine.tg_worker_instances.items():

        def update(object, param_val_pairs, row=row):
            barriers[param_val_pairs].wait(timeout=3)
            completed[row].append((object, param_val_pairs))

        worker.pytg.set_obj_param.side_effect = update
        states[row] = [("/GEOMETRY/INLET", "first=1"), ("/MESH DATA", "second=2")]
    machine.set_br_state(states)
    assert completed == states


@pytest.mark.parametrize(
    "operation", ["params", "actions", "read", "statistics", "boundaries", "disable_lma"]
)
def test_worker_failures_propagate_after_other_dispatched_workers_finish(machine, operation):
    done = Event()
    failing = machine.tg_worker_instances["A"].pytg
    other = machine.tg_worker_instances["B"].pytg
    methods = {
        "params": "set_obj_param",
        "actions": "perform_action",
        "read": "read_tginit",
        "statistics": "query_mesh_statistics",
        "boundaries": "getBoundaryGeometry",
        "disable_lma": "set_obj_param",
    }
    getattr(failing, methods[operation]).side_effect = RuntimeError("synthetic worker error")
    getattr(other, methods[operation]).side_effect = lambda *args, **kwargs: done.set()
    calls = {
        "params": lambda: machine.set_br_state(
            {row: [("/MESH DATA", "x=1")] for row in ("A", "B")}
        ),
        "actions": lambda: machine.perform_br_actions(
            {row: [("loadinlet", "x")] for row in ("A", "B")}
        ),
        "read": lambda: machine.read_tginit_into_blank("case.tginit"),
        "statistics": machine.get_mesh_statistics,
        "boundaries": machine.get_primary_boundary_surface_dict,
        "disable_lma": machine.disable_lma,
    }
    with pytest.raises(RuntimeError, match="synthetic worker error"):
        calls[operation]()
    assert done.is_set()


def test_block_structured_parameterization_is_dispatched_to_every_worker(machine):
    barrier = Barrier(3)
    for worker in machine.tg_worker_instances.values():
        worker.pytg.set_obj_param.side_effect = lambda *args: barrier.wait(timeout=3)
    machine.disable_lma()
    for worker in machine.tg_worker_instances.values():
        worker.pytg.set_obj_param.assert_called_once_with(
            "/GEOMETRY/MACHINE DATA", "Turbo Transform Mesh Type = Block-structured"
        )
        worker.pytg.wait_engine_ready.assert_called_once()


def test_parallel_statistics_and_boundary_queries_return_every_row(machine):
    for operation in ("query_mesh_statistics", "getBoundaryGeometry"):
        barrier = Barrier(3)
        for row, worker in machine.tg_worker_instances.items():

            def query(*args, row=row, **kwargs):
                barrier.wait(timeout=3)
                return {"row": row}

            getattr(worker.pytg, operation).side_effect = query
        result = (
            machine.get_mesh_statistics()
            if operation == "query_mesh_statistics"
            else machine.get_primary_boundary_surface_dict()
        )
        assert result == {row: {"row": row} for row in machine.tg_worker_instances}


def test_unknown_action_rows_fail_before_dispatch(machine):
    with pytest.raises(ValueError, match="Unknown blade rows"):
        machine.perform_br_actions({"missing": [("loadinlet", "x")]})
    for worker in machine.tg_worker_instances.values():
        worker.pytg.perform_action.assert_not_called()
