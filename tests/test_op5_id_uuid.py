import pytest
from .conftest import get_gts_base_url
from httprunner import HttpRunner, Config, Step, RunRequest


class TestCaseTestOp5IdToUuid_Type(HttpRunner):
    config = Config("OP#5 - ID to UUID (type)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("uuid mapping (type)")
            .get("/uuid")
            .with_params(**{"gts_id": "gts.x.core.events.type.v1~"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "gts.x.core.events.type.v1~")
            .assert_equal("body.uuid", "914ba16d-39d5-518b-9800-490e2144bf98")
        ),
        Step(
            RunRequest("uuid mapping deterministic (type)")
            .get("/uuid")
            .with_params(**{"gts_id": "gts.x.core.events.type.v1~"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.uuid", "914ba16d-39d5-518b-9800-490e2144bf98")
        ),
    ]


class TestCaseTestOp5IdToUuid_Instance(HttpRunner):
    config = Config("OP#5 - ID to UUID (instance)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("uuid mapping (instance)")
            .get("/uuid")
            .with_params(
                **{
                    "gts_id": (
                        "gts.x.core.events.type.v1~abc.app._."
                        "custom_event.v1.2"
                    )
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal(
                "body.id",
                "gts.x.core.events.type.v1~abc.app._.custom_event.v1.2",
            )
            .assert_equal("body.uuid", "7b97631e-3649-5131-a761-cb6067e27e5f")
        ),
        Step(
            RunRequest("uuid mapping deterministic (instance)")
            .get("/uuid")
            .with_params(
                **{
                    "gts_id": (
                        "gts.x.core.events.type.v1~abc.app._."
                        "custom_event.v1.2"
                    )
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.uuid", "7b97631e-3649-5131-a761-cb6067e27e5f")
        ),
    ]
