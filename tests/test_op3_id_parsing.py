import pytest
from .conftest import get_gts_base_url
from httprunner import HttpRunner, Config, Step, RunRequest, Parameters


class TestCaseTestOp3IdParsing_TypeOnly(HttpRunner):
    config = Config("OP#3 - Parse ID (type only)").base_url(get_gts_base_url())

    @pytest.mark.parametrize(
        "param",
        Parameters({"id": ["gts.x.core.events.type.v1~"]}),
    )
    def test_start(self, param):
        super().test_start(param)

    teststeps = [
        Step(
            RunRequest("parse id (type)")
            .get("/parse")
            .with_params(**{"gts_id": "${id}"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "${id}")
            .assert_equal("body.segments[-1].is_type", True)
            .assert_equal("body.segments[-1].ver_minor", None)
        ),
    ]


class TestCaseTestOp3IdParsing_ChainInstance(HttpRunner):
    config = Config("OP#3 - Parse ID (chain -> instance)").base_url(get_gts_base_url())

    @pytest.mark.parametrize(
        "param",
        Parameters(
            {
                "id": [
                    (
                        "gts.x.core.events.type.v1~abc.app._."
                        "custom_event.v1.2"
                    )
                ]
            }
        ),
    )
    def test_start(self, param):
        super().test_start(param)

    teststeps = [
        Step(
            RunRequest("parse id (chain -> instance)")
            .get("/parse")
            .with_params(**{"gts_id": "${id}"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "${id}")
            .assert_equal("body.segments[-1].is_type", False)
            .assert_equal("body.segments[-1].ver_minor", 2)
        ),
    ]


class TestCaseTestOp3IdParsing_LongChainInstance(HttpRunner):
    config = Config("OP#3 - Parse ID (long chain -> instance)").base_url(get_gts_base_url())

    @pytest.mark.parametrize(
        "param",
        Parameters(
            {
                "id": [
                    (
                        "gts.x.core.events.type.v1~a.b.c.d.v1~"
                        "e.f.g.h.v1~i.j.k.l.v1.0"
                    )
                ]
            }
        ),
    )
    def test_start(self, param):
        super().test_start(param)

    teststeps = [
        Step(
            RunRequest("parse id (long chain -> instance)")
            .get("/parse")
            .with_params(**{"gts_id": "${id}"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "${id}")
            .assert_equal("body.segments[-1].is_type", False)
            .assert_equal("body.segments[-1].ver_minor", 0)
        ),
    ]
