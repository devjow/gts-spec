import pytest
from .conftest import get_gts_base_url
from httprunner import HttpRunner, Config, Step, RunRequest, Parameters


class TestCaseTestOp3IdParsing_TypeOnly(HttpRunner):
    config = Config("OP#3 - Parse ID (type only)").base_url(get_gts_base_url())

    @pytest.mark.parametrize(
        "param",
        Parameters({"id": ["gts.x.test3.events.type.v1~"]}),
    )
    def test_start(self, param):
        super().test_start(param)

    teststeps = [
        Step(
            RunRequest("parse id (type)")
            .get("/parse-id")
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
                        "gts.x.test3.events.type.v1~abc.app._."
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
            .get("/parse-id")
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
                        "gts.x.test3.events.type.v1~a.b.c.d.v1~"
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
            .get("/parse-id")
            .with_params(**{"gts_id": "${id}"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "${id}")
            .assert_equal("body.segments[-1].is_type", False)
            .assert_equal("body.segments[-1].ver_minor", 0)
        ),
    ]


class TestCaseTestOp3Parsing_ChainedIdentifiers(HttpRunner):
    """OP#3 Extended - Chained identifier parsing"""
    config = Config("OP#3 Extended - Chained ID Parsing").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("parse chained type identifier")
            .get("/parse-id")
            .with_params(
                **{
                    "gts_id": (
                        "gts.x.test3.events.type.v1~"
                        "abc.app._.custom.v1~"
                    )
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.segments[0].vendor", "x")
            .assert_equal("body.segments[1].vendor", "abc")
        ),
        Step(
            RunRequest("parse chained instance identifier")
            .get("/parse-id")
            .with_params(
                **{
                    "gts_id": (
                        "gts.x.test3.events.type.v1~"
                        "abc.app._.custom.v1~"
                        "abc.app._.instance.v1.0"
                    )
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.segments[0].vendor", "x")
            .assert_equal("body.segments[1].namespace", "_")
            .assert_equal("body.segments[1].ver_minor", None)
            .assert_equal("body.segments[2].is_type", False)
            .assert_equal("body.segments[2].ver_minor", 0)
        ),
    ]


class TestCaseTestOp3Parsing_VersionComponents(HttpRunner):
    """OP#3 Extended - Version component extraction"""
    config = Config("OP#3 Extended - Version Component Parsing").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("parse major version only")
            .get("/parse-id")
            .with_params(**{"gts_id": "gts.x.pkg.ns.type.v1~"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.segments[0].ver_major", 1)
        ),
        Step(
            RunRequest("parse major and minor version")
            .get("/parse-id")
            .with_params(**{"gts_id": "gts.x.pkg.ns.type.v2.5~"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.segments[0].ver_major", 2)
            .assert_equal("body.segments[0].ver_minor", 5)
        ),
        Step(
            RunRequest("parse version zero")
            .get("/parse-id")
            .with_params(**{"gts_id": "gts.x.pkg.ns.type.v0~"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.segments[0].ver_major", 0)
        ),
    ]


class TestCaseTestOp3Parsing_NamespaceExtraction(HttpRunner):
    """OP#3 Extended - Namespace extraction scenarios"""
    config = Config("OP#3 Extended - Namespace Extraction").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("parse namespace with underscore placeholder")
            .get("/parse-id")
            .with_params(**{"gts_id": "gts.vendor.pkg._.type.v1~"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.segments[0].namespace", "_")
        ),
        Step(
            RunRequest("parse with actual namespace")
            .get("/parse-id")
            .with_params(
                **{"gts_id": "gts.vendor.pkg.events.type.v1~"}
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.segments[0].namespace", "events")
        ),
    ]
