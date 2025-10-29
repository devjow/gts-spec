import pytest
from .conftest import get_gts_base_url
from httprunner import HttpRunner, Config, Step, RunRequest


# Positive cases (3)
class TestCaseTestOp4WildcardMatch_Positive_1(HttpRunner):
    config = Config("OP#4 - Wildcard Match (pos 1)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match (pos 1)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": (
                        "gts.x.core.events.type.v1~abc.app._."
                        "custom_event.v1.2"
                    ),
                    "pattern": "gts.x.core.events.type.v1~abc.*",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.match", True)
        ),
    ]


class TestCaseTestOp4WildcardMatch_Positive_2(HttpRunner):
    config = Config("OP#4 - Wildcard Match (pos 2)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match (pos 2)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": "gts.vendor.pkg.ns.type.v0~",
                    "pattern": "gts.vendor.pkg.ns.type.v0~*",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.match", True)
        ),
    ]


class TestCaseTestOp4WildcardMatch_Positive_3(HttpRunner):
    config = Config("OP#4 - Wildcard Match (pos 3)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match (pos 3)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": "gts.vendor.pkg.ns.type.v0.1~",
                    "pattern": "gts.vendor.pkg.ns.type.v0~*",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.match", True)
        ),
    ]


# Negative cases (3)
class TestCaseTestOp4WildcardMatch_Negative_1(HttpRunner):
    config = Config("OP#4 - Wildcard Match (neg 1)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match (neg 1)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": (
                        "gts.x.core.events.type.v1~abc.app._."
                        "custom_event.v1.3"
                    ),
                    "pattern": "gts.x.core.events.type.v2~abc.*",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.match", False)
        ),
    ]


class TestCaseTestOp4WildcardMatch_Negative_2(HttpRunner):
    config = Config("OP#4 - Wildcard Match (neg 2)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match (neg 2)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": "gts.vendor.pkg.ns.type.v1.1~",
                    "pattern": "gts.vendor.pkg.ns.type.v0~*",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.match", False)
        ),
    ]


class TestCaseTestOp4WildcardMatch_Negative_3(HttpRunner):
    config = Config("OP#4 - Wildcard Match (neg 3)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match (neg 3)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": (
                        "gts.x.core.events.type.v1~abc.app._."
                        "custom_event.v1.2"
                    ),
                    "pattern": "gts.x.core.events.type.v1~abc",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.match", False)
        ),
    ]


# Invalid patterns (3)
class TestCaseTestOp4WildcardInvalid_1(HttpRunner):
    config = Config("OP#4 - Wildcard Match (invalid 1)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match invalid (1)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": "gts.x.core.events.type.v1~abc.app._.custom_event.v1.2",
                    "pattern": "GTS.vendor.pkg.ns.type.v0.*",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_not_equal("body.error", "")
        ),
    ]


class TestCaseTestOp4WildcardInvalid_2(HttpRunner):
    config = Config("OP#4 - Wildcard Match (invalid 2)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match invalid (2)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": "gts.vendor.pkg.ns.type.v0~",
                    "pattern": "gts.x.core.events.type.v1*abc",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_not_equal("body.error", "")
        ),
    ]


class TestCaseTestOp4WildcardInvalid_3(HttpRunner):
    config = Config("OP#4 - Wildcard Match (invalid 3)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("wildcard match invalid (3)")
            .get("/wildcard-match")
            .with_params(
                **{
                    "candidate": "gts.vendor.pkg.ns.type.v0~",
                    "pattern": "gts.x.core.events.type",
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_not_equal("body.error", "")
        ),
    ]
