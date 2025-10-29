import pytest
from .conftest import get_gts_base_url
from httprunner import HttpRunner, Config, Step, RunRequest, Parameters


class TestCaseTestOp1IdValidationAllValid(HttpRunner):
    config = Config("OP#1 - Validate ID (all valid cases)").base_url(get_gts_base_url())

    @pytest.mark.parametrize(
        "param",
        Parameters(
            {
                "id": [
                    "gts.x.core.events.type.v1~",
                    "gts.x.core.objects_registry.object_a.v1.0",
                    "gts.abc.commerce.orders.order.v2.15~",
                    "gts.vendor.pkg.ns.type.v0~",
                    "gts.v123.p456.n789.t000.v999.888~",
                    "gts.x.pkg._.type.v1~",
                    "gts.myvendor.mypackage.mynamespace.mytype.v1.0~",
                    "gts.x.core.events.type.v1~abc.app._.custom_event.v1~",
                    "gts.x.core.events.type.v1~abc.app._.custom_event.v1.2",
                    "gts.a.b.c.d.v1~e.f.g.h.v2~i.j.k.l.v3~",
                    "gts.vendor_name.pkg_123.ns_abc.type_xyz.v10.5~",
                    "gts.x.core.api.endpoint.v0.1",
                    "gts.a1.b2.c3.d4.v100.200~",
                    (
                        "gts.x.core.events.type.v1~vendor.app."
                        "derived.event.v2~"
                        "vendor.app._.event.v2.0"
                    ),
                    (
                        "gts.longvendorname.longpackagename."
                        "longnamespacename.longtypename.v1~"
                    ),
                    "gts._a.b2.c3._d4.v1~",
                    (
                        "gts.x.core.events.type.v1~a.b.c.d.v1~"
                        "e.f.g.h.v1~i.j.k.l.v1.0"
                    ),
                    "gts.v.v.v.v.v1~",
                    "gts.a.b.c.d.v0~",
                    "gts._._._._.v1~",
                    "gts.x.y.z.a.v999999.888888~",
                ]
            }
        ),
    )
    def test_start(self, param):
        super().test_start(param)

    teststeps = [
        Step(
            RunRequest("validate gts_id is valid (all valid)")
            .get("/validate-id")
            .with_params(**{"gts_id": "${id}"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "${id}")
            .assert_equal("body.valid", True)
            .assert_equal("body.error", "")
        ),
    ]


class TestCaseTestOp1IdValidationInvalid(HttpRunner):
    config = Config("OP#1 - Validate ID (all invalid cases)").base_url(get_gts_base_url())

    @pytest.mark.parametrize(
        "param",
        Parameters(
            {
                "id": [
                    "GTS.x.core.events.type.v1~",
                    "gts.X.core.events.type.v1~",
                    "gts.x.core.events.type.V1~",
                    "x.core.events.type.v1~",
                    "gts.x.core.events.type.1~",
                    "gts.x.core.events.type.v1.2.3~",
                    "gts.x.core.events.type.v-1~",
                    "gts.x.core.events.type.v1.~",
                    "gts.x.core.events.type.v01~",
                    "gts.x.core.events.type.v1.01~",
                    "gts.x.mq.messages._._.v1",
                    "gts.1vendor.core.events.type.v1~",
                    "gts.x.core-events.events.type.v1~",
                    "gts.x.core.events..event.v1~",
                    "gts.x.core.events.type.v1.0~~",
                    "gts.x.core.events.type.v1~gts.abc.app._.custom.v1~",
                    "gts.x.core.events.type.v1.abc.app.namespace.custom.v1",
                    "gts.x.core.events.event~",
                    "gts.x.core.events.v1~",
                    "gts.x.core.namespace.type.v1~a.b.c.v1",
                    "gts.x.core.events.type.v1.0.0~",
                ]
            }
        ),
    )
    def test_start(self, param):
        super().test_start(param)

    teststeps = [
        Step(
            RunRequest("validate gts_id is invalid")
            .get("/validate-id")
            .with_params(**{"gts_id": "${id}"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "${id}")
            .assert_equal("body.valid", False)
            .assert_not_equal("body.error", "")
        ),
    ]


if __name__ == "__main__":
    TestCaseTestOp1Validation().test_start()
