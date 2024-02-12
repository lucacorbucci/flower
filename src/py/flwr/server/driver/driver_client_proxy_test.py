# Copyright 2020 Flower Labs GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""DriverClientProxy tests."""


import unittest
from typing import Union, cast
from unittest.mock import MagicMock

import numpy as np

import flwr
from flwr.common import recordset_compat as compat
from flwr.common import serde
from flwr.common.constant import (
    TASK_TYPE_EVALUATE,
    TASK_TYPE_FIT,
    TASK_TYPE_GET_PARAMETERS,
    TASK_TYPE_GET_PROPERTIES,
)
from flwr.common.typing import (
    Code,
    Config,
    EvaluateIns,
    EvaluateRes,
    FitRes,
    GetParametersIns,
    GetParametersRes,
    GetPropertiesRes,
    Parameters,
    Properties,
    Status,
)
from flwr.proto import driver_pb2, node_pb2, task_pb2  # pylint: disable=E0611
from flwr.server.driver.driver_client_proxy import DriverClientProxy

MESSAGE_PARAMETERS = Parameters(tensors=[b"abc"], tensor_type="np")

CLIENT_PROPERTIES = cast(Properties, {"tensor_type": "numpy.ndarray"})
CLIENT_STATUS = Status(code=Code.OK, message="OK")


def _make_task(
    res: Union[GetParametersRes, GetPropertiesRes, FitRes, EvaluateRes]
) -> task_pb2.Task:  # pylint: disable=E1101
    if isinstance(res, GetParametersRes):
        task_type = TASK_TYPE_GET_PARAMETERS
        recordset = compat.getparametersres_to_recordset(res, True)
    elif isinstance(res, GetPropertiesRes):
        task_type = TASK_TYPE_GET_PROPERTIES
        recordset = compat.getpropertiesres_to_recordset(res)
    elif isinstance(res, FitRes):
        task_type = TASK_TYPE_FIT
        recordset = compat.fitres_to_recordset(res, True)
    elif isinstance(res, EvaluateRes):
        task_type = TASK_TYPE_EVALUATE
        recordset = compat.evaluateres_to_recordset(res)
    else:
        raise ValueError(f"Unsupported type: {type(res)}")
    return task_pb2.Task(  # pylint: disable=E1101
        task_type=task_type,
        recordset=serde.recordset_to_proto(recordset),
    )


class DriverClientProxyTestCase(unittest.TestCase):
    """Tests for DriverClientProxy."""

    def setUp(self) -> None:
        """Set up mocks for tests."""
        self.driver = MagicMock()
        self.driver.get_nodes.return_value = (
            driver_pb2.GetNodesResponse(  # pylint: disable=E1101
                nodes=[
                    node_pb2.Node(node_id=1, anonymous=False)  # pylint: disable=E1101
                ]
            )
        )

    def test_get_properties(self) -> None:
        """Test positive case."""
        # Prepare
        self.driver.push_task_ins.return_value = (
            driver_pb2.PushTaskInsResponse(  # pylint: disable=E1101
                task_ids=["19341fd7-62e1-4eb4-beb4-9876d3acda32"]
            )
        )
        self.driver.pull_task_res.return_value = (
            driver_pb2.PullTaskResResponse(  # pylint: disable=E1101
                task_res_list=[
                    task_pb2.TaskRes(  # pylint: disable=E1101
                        task_id="554bd3c8-8474-4b93-a7db-c7bec1bf0012",
                        group_id="",
                        run_id=0,
                        task=_make_task(
                            GetPropertiesRes(
                                status=CLIENT_STATUS, properties=CLIENT_PROPERTIES
                            )
                        ),
                    )
                ]
            )
        )
        client = DriverClientProxy(
            node_id=1, driver=self.driver, anonymous=True, run_id=0
        )
        request_properties: Config = {"tensor_type": "str"}
        ins: flwr.common.GetPropertiesIns = flwr.common.GetPropertiesIns(
            config=request_properties
        )

        # Execute
        value: flwr.common.GetPropertiesRes = client.get_properties(ins, timeout=None)

        # Assert
        assert value.properties["tensor_type"] == "numpy.ndarray"

    def test_get_parameters(self) -> None:
        """Test positive case."""
        # Prepare
        self.driver.push_task_ins.return_value = (
            driver_pb2.PushTaskInsResponse(  # pylint: disable=E1101
                task_ids=["19341fd7-62e1-4eb4-beb4-9876d3acda32"]
            )
        )
        self.driver.pull_task_res.return_value = (
            driver_pb2.PullTaskResResponse(  # pylint: disable=E1101
                task_res_list=[
                    task_pb2.TaskRes(  # pylint: disable=E1101
                        task_id="554bd3c8-8474-4b93-a7db-c7bec1bf0012",
                        group_id="",
                        run_id=0,
                        task=_make_task(
                            GetParametersRes(
                                status=CLIENT_STATUS,
                                parameters=MESSAGE_PARAMETERS,
                            )
                        ),
                    )
                ]
            )
        )
        client = DriverClientProxy(
            node_id=1, driver=self.driver, anonymous=True, run_id=0
        )
        get_parameters_ins = GetParametersIns(config={})

        # Execute
        value: flwr.common.GetParametersRes = client.get_parameters(
            ins=get_parameters_ins, timeout=None
        )

        # Assert
        assert value.parameters.tensors[0] == b"abc"

    def test_fit(self) -> None:
        """Test positive case."""
        # Prepare
        self.driver.push_task_ins.return_value = (
            driver_pb2.PushTaskInsResponse(  # pylint: disable=E1101
                task_ids=["19341fd7-62e1-4eb4-beb4-9876d3acda32"]
            )
        )
        self.driver.pull_task_res.return_value = (
            driver_pb2.PullTaskResResponse(  # pylint: disable=E1101
                task_res_list=[
                    task_pb2.TaskRes(  # pylint: disable=E1101
                        task_id="554bd3c8-8474-4b93-a7db-c7bec1bf0012",
                        group_id="",
                        run_id=0,
                        task=_make_task(
                            FitRes(
                                status=CLIENT_STATUS,
                                parameters=MESSAGE_PARAMETERS,
                                num_examples=10,
                                metrics={},
                            )
                        ),
                    )
                ]
            )
        )
        client = DriverClientProxy(
            node_id=1, driver=self.driver, anonymous=True, run_id=0
        )
        parameters = flwr.common.ndarrays_to_parameters([np.ones((2, 2))])
        ins: flwr.common.FitIns = flwr.common.FitIns(parameters, {})

        # Execute
        fit_res = client.fit(ins=ins, timeout=None)

        # Assert
        assert fit_res.parameters.tensor_type == "np"
        assert fit_res.parameters.tensors[0] == b"abc"
        assert fit_res.num_examples == 10

    def test_evaluate(self) -> None:
        """Test positive case."""
        # Prepare
        self.driver.push_task_ins.return_value = (
            driver_pb2.PushTaskInsResponse(  # pylint: disable=E1101
                task_ids=["19341fd7-62e1-4eb4-beb4-9876d3acda32"]
            )
        )
        self.driver.pull_task_res.return_value = (
            driver_pb2.PullTaskResResponse(  # pylint: disable=E1101
                task_res_list=[
                    task_pb2.TaskRes(  # pylint: disable=E1101
                        task_id="554bd3c8-8474-4b93-a7db-c7bec1bf0012",
                        group_id="",
                        run_id=0,
                        task=_make_task(
                            EvaluateRes(
                                status=CLIENT_STATUS,
                                loss=0.0,
                                num_examples=0,
                                metrics={},
                            )
                        ),
                    )
                ]
            )
        )
        client = DriverClientProxy(
            node_id=1, driver=self.driver, anonymous=True, run_id=0
        )
        parameters = Parameters(tensors=[], tensor_type="np")
        evaluate_ins = EvaluateIns(parameters, {})

        # Execute
        evaluate_res = client.evaluate(evaluate_ins, timeout=None)

        # Assert
        assert 0.0 == evaluate_res.loss
        assert 0 == evaluate_res.num_examples
