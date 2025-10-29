import pytest
from .conftest import get_gts_base_url
from httprunner import HttpRunner, Config, Step, RunRequest


class TestCaseTestOp2IdExtraction_Case1(HttpRunner):
    config = Config("OP#2 - Extract ID (case 1)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("extract id (case 1)")
            .post("/extract-id")
            .with_json({
                "id": "gts.x.core.api.endpoint.v0.1",
                "schema": "gts.x.core.api.endpoint.v0~",
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "gts.x.core.api.endpoint.v0.1")
            .assert_equal("body.schema_id", "gts.x.core.api.endpoint.v0~")
            .assert_equal("body.selected_entity_field", "id")
            .assert_equal("body.selected_schema_id_field", "schema")
            .assert_equal("body.is_schema", False)
        ),
    ]


class TestCaseTestOp2IdExtraction_Case2(HttpRunner):
    config = Config("OP#2 - Extract ID (case 2)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("extract id (case 2)")
            .post("/extract-id")
            .with_json({
                "gtsId": (
                    "gts.x.core.events.type.v1~abc.app._."
                    "custom_event.v1.2"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal(
                "body.id",
                "gts.x.core.events.type.v1~abc.app._.custom_event.v1.2",
            )
            .assert_equal("body.schema_id", "gts.x.core.events.type.v1~")
            .assert_equal("body.selected_entity_field", "gtsId")
            .assert_equal("body.selected_schema_id_field", "gtsId")
            .assert_equal("body.is_schema", False)
        ),
    ]


class TestCaseTestOp2IdExtraction_Case3(HttpRunner):
    config = Config("OP#2 - Extract ID (case 3)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("extract id (case 3)")
            .post("/extract-id")
            .with_json({"id": "gts.v123.p456.n789.t000.v999.888~"})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.id", "gts.v123.p456.n789.t000.v999.888~")
            .assert_equal("body.schema_id", "gts.v123.p456.n789.t000.v999.888~")
            .assert_equal("body.selected_entity_field", "id")
            .assert_equal("body.selected_schema_id_field", None)
            .assert_equal("body.is_schema", False)
        ),
    ]


class TestCaseTestOp2IdExtraction_Case4(HttpRunner):
    config = Config("OP#2 - Extract ID (case 4)").base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("extract id (case 4)")
            .post("/extract-id")
            .with_json({
                "gts_id": "gts.x.core.objects_registry.object_a.v1.0",
                "schema": "https://json-schema.org/draft/2020-12/schema",
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal(
                "body.id", "gts.x.core.objects_registry.object_a.v1.0"
            )
            .assert_equal(
                "body.schema_id",
                "https://json-schema.org/draft/2020-12/schema",
            )
            .assert_equal("body.selected_entity_field", "gts_id")
            .assert_equal("body.selected_schema_id_field", "schema")
            .assert_equal("body.is_schema", False)
        ),
    ]
