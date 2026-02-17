from .conftest import get_gts_base_url
from httprunner import HttpRunner, Config, Step, RunRequest


class TestCaseTestOp12SchemaValidation_DerivedSchemaFullyMatches(HttpRunner):
    """OP#12 - Schema vs Schema: Derived schema fully matches base"""
    config = Config("OP#12 - Fully Matching Derived Schema").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12a.base.user.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["userId", "email"],
                "properties": {
                    "userId": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"},
                    "tier": {"type": "string", "maxLength": 100}
                },
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema that matches base")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12a.base.user.v1~"
                    "x.test12a._.premium_user.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12a.base.user.v1~"},
                    {
                        "type": "object",
                        "required": ["tier"],
                        "properties": {
                            "tier": {
                                "type": "string",
                                "enum": ["gold", "platinum"]
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate derived schema against base")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12a.base.user.v1~x.test12a._.premium_user.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_DerivedSchemaAddsNewFieldsToBaseOne(HttpRunner):
    """OP#12 - Schema vs Schema: Derived schema adds new fields to base"""
    config = Config("OP#12 - Derived Schema Adds New Fields To Base").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12b.base.user.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["userId", "email"],
                "properties": {
                    "userId": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"},
                    "name": {"type": "string", "maxLength": 100}
                },
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema that matches base")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12b.base.user.v1~"
                    "x.test12b._.premium_user.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12b.base.user.v1~"},
                    {
                        "type": "object",
                        "required": ["subscriptionTier"],
                        "properties": {
                            "subscriptionTier": {
                                "type": "string",
                                "enum": ["gold", "platinum"]
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate derived schema against base")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12b.base.user.v1~x.test12b._.premium_user.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_AdditionalPropertiesFalse(
    HttpRunner
):
    """OP#12 - Schema vs Schema: Base has additionalProperties false"""
    config = Config(
        "OP#12 - additionalProperties False Violation"
    ).base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register closed base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.closed.account.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["accountId", "email"],
                "properties": {
                    "accountId": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"},
                    "name": {"type": "string", "maxLength": 100}
                },
                "additionalProperties": False
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema adding properties")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.closed.account.v1~"
                    "x.test12._.premium_account.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.closed.account.v1~"},
                    {
                        "type": "object",
                        "required": ["tier"],
                        "properties": {
                            "tier": {
                                "type": "string",
                                "enum": ["gold", "platinum"]
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate should fail - base forbids extra properties")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.closed.account.v1~"
                    "x.test12._.premium_account.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12SchemaValidation_CloseOpenModel(HttpRunner):
    """OP#12 - Schema vs Schema: Derived closes an open model"""
    config = Config(
        "OP#12 - Close Open Model"
    ).base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register open base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.close.user.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["userId", "email"],
                "properties": {
                    "userId": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema closing model")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.close.user.v1~"
                    "x.test12._.closed_user.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.close.user.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "userId": {
                                "type": "string",
                                "format": "uuid"
                            },
                            "email": {
                                "type": "string",
                                "format": "email"
                            }
                        },
                        "additionalProperties": False
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate derived schema should pass")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.close.user.v1~"
                    "x.test12._.closed_user.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_NestedAdditionalPropertiesFalse(
    HttpRunner
):
    """OP#12 - Schema vs Schema: Nested additionalProperties false"""
    config = Config(
        "OP#12 - Nested additionalProperties False"
    ).base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with closed nested object")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.nested.closed.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["profileId", "profile"],
                "properties": {
                    "profileId": {"type": "string"},
                    "profile": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string"},
                            "age": {
                                "type": "integer",
                                "minimum": 0
                            }
                        },
                        "additionalProperties": False
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema adding nested property")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.nested.closed.v1~"
                    "x.test12._.profile_plus.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.nested.closed.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "profile": {
                                "type": "object",
                                "properties": {
                                    "nickname": {"type": "string"}
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate derived schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.nested.closed.v1~"
                    "x.test12._.profile_plus.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12SchemaValidation_InvalidDerivedSchema(
    HttpRunner
):
    """OP#12 - Schema vs Schema: Invalid derived schema"""
    config = Config("OP#12 - Invalid Derived Schema").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with required fields")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.base.order.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["orderId", "customerId", "total"],
                "properties": {
                    "orderId": {"type": "string"},
                    "customerId": {"type": "string"},
                    "total": {"type": "number", "minimum": 0}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema contradicting base")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.base.order.v1~"
                    "x.test12._.bad_order.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.base.order.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "customerId": False
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate derived schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.base.order.v1~x.test12._.bad_order.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12SchemaValidation_DerivedSchemaConstraintTighten(
    HttpRunner
):
    """OP#12 - Schema vs Schema: Derived schema tightens constraints"""
    config = Config("OP#12 - Tightened Constraints").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with loose constraints")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.base.text.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["textId", "content"],
                "properties": {
                    "textId": {"type": "string"},
                    "content": {"type": "string", "maxLength": 1000},
                    "priority": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema with tighter constraints")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.base.text.v1~"
                    "x.test12._.short_text.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.base.text.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "maxLength": 500
                            },
                            "priority": {
                                "type": "integer",
                                "minimum": 10,
                                "maximum": 50
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate derived schema with tighter constraints")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.base.text.v1~x.test12._.short_text.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_DerivedSchemaConstraintLoosen(
    HttpRunner
):
    """OP#12 - Schema vs Schema: Derived schema loosens constraints"""
    config = Config("OP#12 - Loosened Constraints (Invalid)").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with strict constraints")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.base.data.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["dataId"],
                "properties": {
                    "dataId": {"type": "string"},
                    "value": {"type": "string", "maxLength": 128}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema with looser constraints")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.base.data.v1~"
                    "x.test12._.loose_data.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.base.data.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string", "maxLength": 256}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate schema with looser constraints should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.base.data.v1~x.test12._.loose_data.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12SchemaValidation_DerivedSpecifiesObject(HttpRunner):
    """OP#12 - Schema vs Schema: Base has object property,
    derived specifies it
    """
    config = Config(
        "OP#12 - Derived Specifies Base Object Property"
    ).base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with object property")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.objspec.event.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["eventId", "payload"],
                "properties": {
                    "eventId": {"type": "string", "format": "uuid"},
                    "payload": {"type": "object"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema specifying the object")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.objspec.event.v1~"
                    "x.test12._.order_event.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.objspec.event.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "payload": {
                                "type": "object",
                                "required": ["orderId", "amount"],
                                "properties": {
                                    "orderId": {"type": "string"},
                                    "amount": {
                                        "type": "number",
                                        "minimum": 0
                                    }
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate derived schema specifying object")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.objspec.event.v1~"
                    "x.test12._.order_event.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_3Level_L2SpecifiesObject(HttpRunner):
    """OP#12 - 3-level: base has object, L2 specifies it, L3 tightens"""
    config = Config(
        "OP#12 - 3-Level L2 Specifies Object"
    ).base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with object property")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.obj3a.resource.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["resourceId", "metadata"],
                "properties": {
                    "resourceId": {"type": "string", "format": "uuid"},
                    "metadata": {"type": "object"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema specifying the object")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.obj3a.resource.v1~"
                    "x.test12._.file.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.obj3a.resource.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "metadata": {
                                "type": "object",
                                "required": ["fileName", "size"],
                                "properties": {
                                    "fileName": {
                                        "type": "string",
                                        "maxLength": 255
                                    },
                                    "size": {
                                        "type": "integer",
                                        "minimum": 0
                                    },
                                    "mimeType": {"type": "string"}
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.obj3a.resource.v1~"
                    "x.test12._.file.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 schema tightening the object")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.obj3a.resource.v1~"
                    "x.test12._.file.v1~x.test12._.image.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.obj3a.resource.v1~"
                            "x.test12._.file.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "metadata": {
                                "type": "object",
                                "properties": {
                                    "fileName": {
                                        "type": "string",
                                        "maxLength": 128
                                    },
                                    "mimeType": {
                                        "type": "string",
                                        "enum": [
                                            "image/png",
                                            "image/jpeg",
                                            "image/webp"
                                        ]
                                    },
                                    "width": {"type": "integer"},
                                    "height": {"type": "integer"}
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.obj3a.resource.v1~"
                    "x.test12._.file.v1~x.test12._.image.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_3Level_L2CompositionL3NestedObject(
    HttpRunner
):
    """OP#12 - 3-level: L2 specifies object as composition,
    L3 specifies nested
    """
    config = Config(
        "OP#12 - 3-Level L2 Composition L3 Nested Object"
    ).base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with object property")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.obj3b.config.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["configId", "settings"],
                "properties": {
                    "configId": {"type": "string"},
                    "settings": {"type": "object"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 specifying settings as composition")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.obj3b.config.v1~"
                    "x.test12._.app_config.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.obj3b.config.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "settings": {
                                "type": "object",
                                "required": ["theme", "notifications"],
                                "properties": {
                                    "theme": {
                                        "type": "string",
                                        "enum": [
                                            "light", "dark", "system"
                                        ]
                                    },
                                    "language": {
                                        "type": "string",
                                        "maxLength": 10
                                    },
                                    "notifications": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.obj3b.config.v1~"
                    "x.test12._.app_config.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 specifying the nested object")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.obj3b.config.v1~"
                    "x.test12._.app_config.v1~"
                    "x.test12._.mobile_config.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.obj3b.config.v1~"
                            "x.test12._.app_config.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "settings": {
                                "type": "object",
                                "properties": {
                                    "theme": {
                                        "type": "string",
                                        "enum": ["light", "dark"]
                                    },
                                    "notifications": {
                                        "type": "object",
                                        "required": [
                                            "pushEnabled",
                                            "frequency"
                                        ],
                                        "properties": {
                                            "pushEnabled": {
                                                "type": "boolean"
                                            },
                                            "frequency": {
                                                "type": "string",
                                                "enum": [
                                                    "realtime",
                                                    "hourly",
                                                    "daily"
                                                ]
                                            },
                                            "quietHours": {
                                                "type": "object",
                                                "properties": {
                                                    "start": {
                                                        "type": "string",
                                                        "format": "time"
                                                    },
                                                    "end": {
                                                        "type": "string",
                                                        "format": "time"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.obj3b.config.v1~"
                    "x.test12._.app_config.v1~"
                    "x.test12._.mobile_config.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_3LevelHierarchy_Valid(HttpRunner):
    """OP#12 - Schema vs Schema: 3-level hierarchy with valid constraints"""
    config = Config("OP#12 - 3-Level Valid Hierarchy").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema level 1")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.hierarchy.entity.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["entityId", "type"],
                "properties": {
                    "entityId": {"type": "string", "format": "uuid"},
                    "type": {"type": "string"},
                    "description": {"type": "string", "maxLength": 500}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register level 2 schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.hierarchy.entity.v1~"
                    "x.test12._.document.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.hierarchy.entity.v1~"},
                    {
                        "type": "object",
                        "required": ["title"],
                        "properties": {
                            "title": {"type": "string", "maxLength": 200},
                            "content": {"type": "string"},
                            "description": {
                                "type": "string",
                                "maxLength": 300
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.hierarchy.entity.v1~"
                    "x.test12._.document.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register level 3 schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.hierarchy.entity.v1~"
                    "x.test12._.document.v1~x.test12._.article.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.hierarchy.entity.v1~"
                            "x.test12._.document.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "required": ["author", "publishedAt"],
                        "properties": {
                            "author": {"type": "string"},
                            "publishedAt": {
                                "type": "string",
                                "format": "date-time"
                            },
                            "title": {"type": "string", "maxLength": 150},
                            "description": {
                                "type": "string",
                                "maxLength": 200
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 3 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.hierarchy.entity.v1~"
                    "x.test12._.document.v1~x.test12._.article.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_3LevelHierarchy_L3ViolatesL2(
    HttpRunner
):
    """OP#12 - Schema vs Schema: 3-level where L3 violates L2"""
    config = Config("OP#12 - 3-Level L3 Violates L2").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema level 1")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.hier2.base.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["id"],
                "properties": {
                    "id": {"type": "string"},
                    "size": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 1000
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register level 2 schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.hier2.base.v1~"
                    "x.test12._.medium.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.hier2.base.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "size": {
                                "type": "integer",
                                "minimum": 100,
                                "maximum": 500
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.hier2.base.v1~x.test12._.medium.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register level 3 schema violating level 2")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.hier2.base.v1~"
                    "x.test12._.medium.v1~x.test12._.bad_large.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.hier2.base.v1~"
                            "x.test12._.medium.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "size": {
                                "type": "integer",
                                "minimum": 100,
                                "maximum": 800
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.hier2.base.v1~"
                    "x.test12._.medium.v1~x.test12._.bad_large.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12SchemaValidation_3LevelHierarchy_L3ViolatesL1(
    HttpRunner
):
    """OP#12 - Schema vs Schema: 3-level where L3 violates L1"""
    config = Config("OP#12 - 3-Level L3 Violates L1").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema level 1")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.hier3.root.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["rootId", "status"],
                "properties": {
                    "rootId": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive", "pending"]
                    },
                    "capacity": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 1000
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register level 2 schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.hier3.root.v1~"
                    "x.test12._.branch.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.hier3.root.v1~"},
                    {
                        "type": "object",
                        "required": ["branchName"],
                        "properties": {
                            "branchName": {"type": "string"},
                            "capacity": {
                                "type": "integer",
                                "minimum": 100,
                                "maximum": 800
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.hier3.root.v1~x.test12._.branch.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register level 3 schema violating level 1")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.hier3.root.v1~"
                    "x.test12._.branch.v1~x.test12._.bad_leaf.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.hier3.root.v1~"
                            "x.test12._.branch.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": [
                                    "active",
                                    "inactive",
                                    "pending",
                                    "archived"
                                ]
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.hier3.root.v1~"
                    "x.test12._.branch.v1~x.test12._.bad_leaf.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12SchemaValidation_3LevelHierarchy_ConstraintCascade(
    HttpRunner
):
    """OP#12 - Schema vs Schema: 3-level progressive constraint tightening"""
    config = Config("OP#12 - 3-Level Constraint Cascade").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with max 1024")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.cascade.message.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["msgId", "payload"],
                "properties": {
                    "msgId": {"type": "string"},
                    "payload": {"type": "string", "maxLength": 1024}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register level 2 schema with max 512")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.cascade.message.v1~"
                    "x.test12._.sms.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.cascade.message.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "payload": {
                                "type": "string",
                                "maxLength": 512
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.cascade.message.v1~x.test12._.sms.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register level 3 schema with max 256")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.cascade.message.v1~"
                    "x.test12._.sms.v1~x.test12._.short_sms.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.cascade.message.v1~"
                            "x.test12._.sms.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "payload": {
                                "type": "string",
                                "maxLength": 256
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 3 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.cascade.message.v1~"
                    "x.test12._.sms.v1~x.test12._.short_sms.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12SchemaValidation_3LevelHierarchy_InvalidCascade(
    HttpRunner
):
    """OP#12 - Schema vs Schema: 3-level where L3 exceeds L1 limit"""
    config = Config("OP#12 - 3-Level Invalid Cascade").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with max 128")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.badcascade.field.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["fieldId"],
                "properties": {
                    "fieldId": {"type": "string"},
                    "data": {"type": "string", "maxLength": 128}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register level 2 schema with max 100")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.badcascade.field.v1~"
                    "x.test12._.medium.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.test12.badcascade.field.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string", "maxLength": 100}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.badcascade.field.v1~"
                    "x.test12._.medium.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register level 3 schema with max 256")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.badcascade.field.v1~"
                    "x.test12._.medium.v1~x.test12._.bad_large.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.badcascade.field.v1~"
                            "x.test12._.medium.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string", "maxLength": 256}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.badcascade.field.v1~"
                    "x.test12._.medium.v1~x.test12._.bad_large.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
        Step(
            RunRequest("validate level 3 schema should fail")
            .post("/validate-entity")
            .with_json({
                "gts_id": (
                    "gts.x.test12.badcascade.field.v1~"
                    "x.test12._.medium.v1~x.test12._.bad_large.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_StringConstConflict(HttpRunner):
    """OP#12 - 3-level: Base string, L2 const "abc", L3 const "def"
    L3 must fail because it redefines the const value set by L2.
    """
    config = Config(
        "OP#12 - String Const Conflict"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with string field")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.strconst.item.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["itemId", "status"],
                "properties": {
                    "itemId": {"type": "string"},
                    "status": {"type": "string"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema with const abc")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.strconst.item.v1~"
                    "x.test12._.active_item.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.strconst.item.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "const": "abc"
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.strconst.item.v1~"
                    "x.test12._.active_item.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 schema with const def")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.strconst.item.v1~"
                    "x.test12._.active_item.v1~"
                    "x.test12._.bad_item.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.strconst.item.v1~"
                            "x.test12._.active_item.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "const": "def"
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.strconst.item.v1~"
                    "x.test12._.active_item.v1~"
                    "x.test12._.bad_item.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_NumericConstConflict(HttpRunner):
    """OP#12 - 3-level: Base number, L2 const 42, L3 const 99
    L3 must fail because it redefines the const value set by L2.
    """
    config = Config(
        "OP#12 - Numeric Const Conflict"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with number field")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.numconst.metric.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["metricId", "value"],
                "properties": {
                    "metricId": {"type": "string"},
                    "value": {"type": "number"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema with const 42")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.numconst.metric.v1~"
                    "x.test12._.fixed_metric.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.numconst.metric.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "number",
                                "const": 42
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.numconst.metric.v1~"
                    "x.test12._.fixed_metric.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 schema with const 99")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.numconst.metric.v1~"
                    "x.test12._.fixed_metric.v1~"
                    "x.test12._.bad_metric.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.numconst.metric.v1~"
                            "x.test12._.fixed_metric.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "number",
                                "const": 99
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.numconst.metric.v1~"
                    "x.test12._.fixed_metric.v1~"
                    "x.test12._.bad_metric.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_TypeChangeIntNumberInt(HttpRunner):
    """OP#12 - 3-level: Base integer, L2 widens to number, L3 narrows
    back to integer. L3 must fail because it narrows the type that L2
    already widened (floats valid in L2 would be rejected by L3).
    """
    config = Config(
        "OP#12 - Type Change int/number/int"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with integer field")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.typechange.score.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["scoreId", "points"],
                "properties": {
                    "scoreId": {"type": "string"},
                    "points": {"type": "integer"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema widening to number")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.typechange.score.v1~"
                    "x.test12._.float_score.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.typechange.score.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "points": {"type": "number"}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema should fail - widens type")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.typechange.score.v1~"
                    "x.test12._.float_score.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
        Step(
            RunRequest("register L3 schema narrowing back to integer")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.typechange.score.v1~"
                    "x.test12._.float_score.v1~"
                    "x.test12._.int_score.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.typechange.score.v1~"
                            "x.test12._.float_score.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "points": {"type": "integer"}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should also fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.typechange.score.v1~"
                    "x.test12._.float_score.v1~"
                    "x.test12._.int_score.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_EnumReWidening(HttpRunner):
    """OP#12 - 3-level: Base enum [a,b,c], L2 narrows to [a,b],
    L3 re-widens to [a,b,c]. L3 must fail because it reintroduces
    values that L2 explicitly removed.
    """
    config = Config(
        "OP#12 - Enum Re-Widening"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with enum field")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.enumwide.role.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["roleId", "level"],
                "properties": {
                    "roleId": {"type": "string"},
                    "level": {
                        "type": "string",
                        "enum": ["admin", "editor", "viewer"]
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema narrowing enum")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.enumwide.role.v1~"
                    "x.test12._.restricted_role.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.enumwide.role.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "level": {
                                "type": "string",
                                "enum": ["admin", "editor"]
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.enumwide.role.v1~"
                    "x.test12._.restricted_role.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 schema re-widening enum")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.enumwide.role.v1~"
                    "x.test12._.restricted_role.v1~"
                    "x.test12._.bad_role.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.enumwide.role.v1~"
                            "x.test12._.restricted_role.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "level": {
                                "type": "string",
                                "enum": [
                                    "admin",
                                    "editor",
                                    "viewer"
                                ]
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.enumwide.role.v1~"
                    "x.test12._.restricted_role.v1~"
                    "x.test12._.bad_role.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_MinLengthLoosening(HttpRunner):
    """OP#12 - 3-level: Base minLength 1, L2 tightens to minLength 5,
    L3 loosens back to minLength 3. L3 must fail because it loosens
    a constraint that L2 tightened.
    """
    config = Config(
        "OP#12 - MinLength Loosening"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with minLength 1")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.minlen.token.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["tokenId", "code"],
                "properties": {
                    "tokenId": {"type": "string"},
                    "code": {
                        "type": "string",
                        "minLength": 1
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema tightening minLength to 5")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.minlen.token.v1~"
                    "x.test12._.strict_token.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.minlen.token.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "minLength": 5
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.minlen.token.v1~"
                    "x.test12._.strict_token.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 schema loosening minLength to 3")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.minlen.token.v1~"
                    "x.test12._.strict_token.v1~"
                    "x.test12._.bad_token.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.minlen.token.v1~"
                            "x.test12._.strict_token.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "minLength": 3
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.minlen.token.v1~"
                    "x.test12._.strict_token.v1~"
                    "x.test12._.bad_token.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_TypeChangeStringToInt(HttpRunner):
    """OP#12 - 2-level: Base has string field, L2 changes type to
    integer. Must fail because type change is incompatible.
    """
    config = Config(
        "OP#12 - Type Change string to integer"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with string field")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.typebreak.record.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["recordId", "label"],
                "properties": {
                    "recordId": {"type": "string"},
                    "label": {"type": "string"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema changing string to integer")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.typebreak.record.v1~"
                    "x.test12._.bad_record.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.typebreak.record.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "label": {"type": "integer"}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.typebreak.record.v1~"
                    "x.test12._.bad_record.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_BooleanConstConflict(HttpRunner):
    """OP#12 - 3-level: Base boolean, L2 const true, L3 const false.
    L3 must fail because it redefines the const value set by L2.
    """
    config = Config(
        "OP#12 - Boolean Const Conflict"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with boolean field")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.boolconst.flag.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["flagId", "enabled"],
                "properties": {
                    "flagId": {"type": "string"},
                    "enabled": {"type": "boolean"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema with const true")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.boolconst.flag.v1~"
                    "x.test12._.on_flag.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.boolconst.flag.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "enabled": {
                                "type": "boolean",
                                "const": True
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.boolconst.flag.v1~"
                    "x.test12._.on_flag.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 schema with const false")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.boolconst.flag.v1~"
                    "x.test12._.on_flag.v1~"
                    "x.test12._.bad_flag.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.boolconst.flag.v1~"
                            "x.test12._.on_flag.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "enabled": {
                                "type": "boolean",
                                "const": False
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.boolconst.flag.v1~"
                    "x.test12._.on_flag.v1~"
                    "x.test12._.bad_flag.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_MaximumLoosening(HttpRunner):
    """OP#12 - 3-level: Base max 1000, L2 tightens to max 500,
    L3 loosens to max 800. L3 must fail because it loosens
    a constraint that L2 tightened.
    """
    config = Config(
        "OP#12 - Maximum Loosening"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with max 1000")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.maxloose.counter.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["counterId", "count"],
                "properties": {
                    "counterId": {"type": "string"},
                    "count": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 1000
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema tightening max to 500")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.maxloose.counter.v1~"
                    "x.test12._.limited_counter.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.maxloose.counter.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 500
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.maxloose.counter.v1~"
                    "x.test12._.limited_counter.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 schema loosening max to 800")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.maxloose.counter.v1~"
                    "x.test12._.limited_counter.v1~"
                    "x.test12._.bad_counter.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.maxloose.counter.v1~"
                            "x.test12._.limited_counter.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 800
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.maxloose.counter.v1~"
                    "x.test12._.limited_counter.v1~"
                    "x.test12._.bad_counter.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_StringConstIdempotent(HttpRunner):
    """OP#12 - 3-level: Base string, L2 const "abc", L3 const "abc".
    L3 must PASS because restating the same const value is valid
    (idempotent constraint restatement).
    """
    config = Config(
        "OP#12 - String Const Idempotent"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with string field")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.stridemp.item.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["itemId", "status"],
                "properties": {
                    "itemId": {"type": "string"},
                    "status": {"type": "string"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema with const abc")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.stridemp.item.v1~"
                    "x.test12._.fixed_item.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.stridemp.item.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "const": "abc"
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.stridemp.item.v1~"
                    "x.test12._.fixed_item.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 restating same const abc")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.stridemp.item.v1~"
                    "x.test12._.fixed_item.v1~"
                    "x.test12._.same_item.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.stridemp.item.v1~"
                            "x.test12._.fixed_item.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "const": "abc"
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should pass - same const")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.stridemp.item.v1~"
                    "x.test12._.fixed_item.v1~"
                    "x.test12._.same_item.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12_NumericConstIdempotent(HttpRunner):
    """OP#12 - 3-level: Base number, L2 const 42, L3 const 42.
    L3 must PASS because restating the same const value is valid.
    """
    config = Config(
        "OP#12 - Numeric Const Idempotent"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with number field")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.numidemp.metric.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["metricId", "value"],
                "properties": {
                    "metricId": {"type": "string"},
                    "value": {"type": "number"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema with const 42")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.numidemp.metric.v1~"
                    "x.test12._.fixed_metric.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.numidemp.metric.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "number",
                                "const": 42
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.numidemp.metric.v1~"
                    "x.test12._.fixed_metric.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 restating same const 42")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.numidemp.metric.v1~"
                    "x.test12._.fixed_metric.v1~"
                    "x.test12._.same_metric.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.numidemp.metric.v1~"
                            "x.test12._.fixed_metric.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "number",
                                "const": 42
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should pass - same const")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.numidemp.metric.v1~"
                    "x.test12._.fixed_metric.v1~"
                    "x.test12._.same_metric.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12_BooleanConstIdempotent(HttpRunner):
    """OP#12 - 3-level: Base boolean, L2 const true, L3 const true.
    L3 must PASS because restating the same const value is valid.
    """
    config = Config(
        "OP#12 - Boolean Const Idempotent"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with boolean field")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.boolidemp.flag.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["flagId", "active"],
                "properties": {
                    "flagId": {"type": "string"},
                    "active": {"type": "boolean"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema with const true")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.boolidemp.flag.v1~"
                    "x.test12._.on_flag.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.boolidemp.flag.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "active": {
                                "type": "boolean",
                                "const": True
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.boolidemp.flag.v1~"
                    "x.test12._.on_flag.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 restating same const true")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.boolidemp.flag.v1~"
                    "x.test12._.on_flag.v1~"
                    "x.test12._.still_on.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.boolidemp.flag.v1~"
                            "x.test12._.on_flag.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "active": {
                                "type": "boolean",
                                "const": True
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should pass - same const")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.boolidemp.flag.v1~"
                    "x.test12._.on_flag.v1~"
                    "x.test12._.still_on.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12_EnumIdenticalRestatement(HttpRunner):
    """OP#12 - 3-level: Base enum [a,b,c], L2 narrows to [a,b],
    L3 restates [a,b]. L3 must PASS because the enum set is
    identical to L2 (idempotent restatement).
    """
    config = Config(
        "OP#12 - Enum Identical Restatement"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with enum field")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.enumsame.perm.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["permId", "access"],
                "properties": {
                    "permId": {"type": "string"},
                    "access": {
                        "type": "string",
                        "enum": ["read", "write", "admin"]
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema narrowing enum")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.enumsame.perm.v1~"
                    "x.test12._.limited_perm.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.enumsame.perm.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "access": {
                                "type": "string",
                                "enum": ["read", "write"]
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.enumsame.perm.v1~"
                    "x.test12._.limited_perm.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 restating same enum")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.enumsame.perm.v1~"
                    "x.test12._.limited_perm.v1~"
                    "x.test12._.same_perm.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.enumsame.perm.v1~"
                            "x.test12._.limited_perm.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "access": {
                                "type": "string",
                                "enum": ["read", "write"]
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should pass - same enum")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.enumsame.perm.v1~"
                    "x.test12._.limited_perm.v1~"
                    "x.test12._.same_perm.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12_RequiredSubsetInOverlay(HttpRunner):
    """OP#12 - 2-level: Base requires [id, name, email], L2 overlay
    lists only [id, name] in its own required. Must PASS because
    allOf means "all of" — the base's required is still enforced
    via $ref inside allOf. The overlay listing a subset does not
    remove "email"; the effective required is the union of both.
    """
    config = Config(
        "OP#12 - Required Subset In Overlay (allOf union)"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with required fields")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.reqsub.contact.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["contactId", "name", "email"],
                "properties": {
                    "contactId": {"type": "string"},
                    "name": {"type": "string"},
                    "email": {
                        "type": "string",
                        "format": "email"
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 with subset required in overlay")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.reqsub.contact.v1~"
                    "x.test12._.slim_contact.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.reqsub.contact.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "required": ["contactId", "name"],
                        "properties": {
                            "contactId": {"type": "string"},
                            "name": {"type": "string"}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 should pass - allOf preserves base")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.reqsub.contact.v1~"
                    "x.test12._.slim_contact.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12_PatternConflict(HttpRunner):
    """OP#12 - 2-level: Base has pattern ^[a-z]+$, L2 changes
    pattern to ^[0-9]+$. Must fail because the patterns are
    incompatible (no string satisfies both simultaneously).
    """
    config = Config(
        "OP#12 - Pattern Conflict"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with alpha pattern")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.pattern.code.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["codeId", "value"],
                "properties": {
                    "codeId": {"type": "string"},
                    "value": {
                        "type": "string",
                        "pattern": "^[a-z]+$"
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 with numeric pattern")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.pattern.code.v1~"
                    "x.test12._.num_code.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.pattern.code.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "string",
                                "pattern": "^[0-9]+$"
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.pattern.code.v1~"
                    "x.test12._.num_code.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_MinItemsLoosening(HttpRunner):
    """OP#12 - 3-level: Base array minItems 1, L2 tightens to
    minItems 5, L3 loosens to minItems 2. L3 must fail because
    it loosens a constraint that L2 tightened.
    """
    config = Config(
        "OP#12 - MinItems Loosening"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with array minItems 1")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.minitems.list.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["listId", "entries"],
                "properties": {
                    "listId": {"type": "string"},
                    "entries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 tightening minItems to 5")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.minitems.list.v1~"
                    "x.test12._.strict_list.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.minitems.list.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "entries": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 5
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.minitems.list.v1~"
                    "x.test12._.strict_list.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 loosening minItems to 2")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.minitems.list.v1~"
                    "x.test12._.strict_list.v1~"
                    "x.test12._.bad_list.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.minitems.list.v1~"
                            "x.test12._.strict_list.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "entries": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.minitems.list.v1~"
                    "x.test12._.strict_list.v1~"
                    "x.test12._.bad_list.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_MinimumLoosening(HttpRunner):
    """OP#12 - 3-level: Base minimum 0, L2 tightens to minimum 10,
    L3 loosens to minimum 5. L3 must fail because it loosens
    a constraint that L2 tightened.
    """
    config = Config(
        "OP#12 - Minimum Loosening"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with minimum 0")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.minloose.temp.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["tempId", "degrees"],
                "properties": {
                    "tempId": {"type": "string"},
                    "degrees": {
                        "type": "integer",
                        "minimum": 0
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 tightening minimum to 10")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.minloose.temp.v1~"
                    "x.test12._.warm_temp.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.minloose.temp.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "degrees": {
                                "type": "integer",
                                "minimum": 10
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.minloose.temp.v1~"
                    "x.test12._.warm_temp.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 loosening minimum to 5")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.minloose.temp.v1~"
                    "x.test12._.warm_temp.v1~"
                    "x.test12._.bad_temp.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.minloose.temp.v1~"
                            "x.test12._.warm_temp.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "degrees": {
                                "type": "integer",
                                "minimum": 5
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.minloose.temp.v1~"
                    "x.test12._.warm_temp.v1~"
                    "x.test12._.bad_temp.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseTestOp12_MaxLengthIdempotent(HttpRunner):
    """OP#12 - 3-level: Base maxLength 200, L2 tightens to 100,
    L3 restates maxLength 100. L3 must PASS because restating
    the same constraint value is valid (idempotent).
    """
    config = Config(
        "OP#12 - MaxLength Idempotent"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with maxLength 200")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.mlidemp.note.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["noteId", "text"],
                "properties": {
                    "noteId": {"type": "string"},
                    "text": {
                        "type": "string",
                        "maxLength": 200
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 tightening maxLength to 100")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.mlidemp.note.v1~"
                    "x.test12._.short_note.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.mlidemp.note.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "maxLength": 100
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.mlidemp.note.v1~"
                    "x.test12._.short_note.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 restating same maxLength 100")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.mlidemp.note.v1~"
                    "x.test12._.short_note.v1~"
                    "x.test12._.same_note.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.mlidemp.note.v1~"
                            "x.test12._.short_note.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "maxLength": 100
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should pass - same value")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.mlidemp.note.v1~"
                    "x.test12._.short_note.v1~"
                    "x.test12._.same_note.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
    ]


class TestCaseTestOp12_ArrayTypeChange(HttpRunner):
    """OP#12 - 3-level: Base has array of strings, L2 narrows items
    to maxLength 50, L3 changes item type to integer.
    L3 must fail because changing array item type breaks
    compatibility with both L2 and base.
    """
    config = Config(
        "OP#12 - Array Item Type Change"
    ).base_url(get_gts_base_url())

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema with string array")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.test12.arrtype.tags.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["tagListId", "tags"],
                "properties": {
                    "tagListId": {"type": "string"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register L2 schema tightening string items")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.arrtype.tags.v1~"
                    "x.test12._.short_tags.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.arrtype.tags.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "maxLength": 50
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L2 schema")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.arrtype.tags.v1~"
                    "x.test12._.short_tags.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
        ),
        Step(
            RunRequest("register L3 schema changing items to integer")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.test12.arrtype.tags.v1~"
                    "x.test12._.short_tags.v1~"
                    "x.test12._.bad_tags.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.test12.arrtype.tags.v1~"
                            "x.test12._.short_tags.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "integer"
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate L3 schema should fail")
            .post("/validate-schema")
            .with_json({
                "schema_id": (
                    "gts.x.test12.arrtype.tags.v1~"
                    "x.test12._.short_tags.v1~"
                    "x.test12._.bad_tags.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseValidateEntity_ValidInstance(HttpRunner):
    """Validate Entity: Valid instance through unified endpoint"""
    config = Config("Validate Entity - Valid Instance").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base event schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.testentity.events.type.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["id", "type", "occurredAt"],
                "properties": {
                    "type": {"type": "string"},
                    "id": {"type": "string", "format": "uuid"},
                    "occurredAt": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "payload": {"type": "object"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived event schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.testentity.events.type.v1~"
                    "x.testentity.events.user_created.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.testentity.events.type.v1~"},
                    {
                        "type": "object",
                        "required": ["payload"],
                        "properties": {
                            "type": {
                                "const": (
                                    "gts.x.testentity.events.type.v1~"
                                    "x.testentity.events.user_created.v1~"
                                )
                            },
                            "payload": {
                                "type": "object",
                                "required": ["userId", "email"],
                                "properties": {
                                    "userId": {
                                        "type": "string",
                                        "format": "uuid"
                                    },
                                    "email": {
                                        "type": "string",
                                        "format": "email"
                                    }
                                }
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register valid instance")
            .post("/entities")
            .with_json({
                "type": (
                    "gts.x.testentity.events.type.v1~"
                    "x.testentity.events.user_created.v1~"
                ),
                "id": (
                    "gts.x.testentity.events.type.v1~"
                    "x.testentity.events.user_created.v1~"
                    "x.testentity._.event1.v1"
                ),
                "occurredAt": "2025-09-20T18:35:00Z",
                "payload": {
                    "userId": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com"
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate instance via unified endpoint")
            .post("/validate-entity")
            .with_json({
                "entity_id": (
                    "gts.x.testentity.events.type.v1~"
                    "x.testentity.events.user_created.v1~"
                    "x.testentity._.event1.v1"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.entity_type", "instance")
        ),
    ]


class TestCaseValidateEntity_InvalidInstance(HttpRunner):
    """Validate Entity: Invalid instance through unified endpoint"""
    config = Config("Validate Entity - Invalid Instance").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.testentity2.data.record.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["recordId", "value"],
                "properties": {
                    "recordId": {"type": "string"},
                    "value": {"type": "number", "minimum": 0}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register invalid instance missing required field")
            .post("/entities")
            .with_json({
                "type": "gts.x.testentity2.data.record.v1~",
                "id": (
                    "gts.x.testentity2.data.record.v1~"
                    "x.testentity2._.record1.v1"
                ),
                "recordId": "REC-001"
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate invalid instance should fail")
            .post("/validate-entity")
            .with_json({
                "entity_id": (
                    "gts.x.testentity2.data.record.v1~"
                    "x.testentity2._.record1.v1"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
            .assert_equal("body.entity_type", "instance")
        ),
    ]


class TestCaseValidateEntity_ValidSchema(HttpRunner):
    """Validate Entity: Valid derived schema through unified endpoint"""
    config = Config("Validate Entity - Valid Schema").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.testentity3.core.entity.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["entityId"],
                "properties": {
                    "entityId": {"type": "string", "format": "uuid"},
                    "description": {"type": "string", "maxLength": 200}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register valid derived schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.testentity3.core.entity.v1~"
                    "x.testentity3._.document.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.testentity3.core.entity.v1~"},
                    {
                        "type": "object",
                        "required": ["title"],
                        "properties": {
                            "title": {"type": "string", "maxLength": 100},
                            "description": {
                                "type": "string",
                                "maxLength": 150
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate schema via unified endpoint")
            .post("/validate-entity")
            .with_json({
                "entity_id": (
                    "gts.x.testentity3.core.entity.v1~"
                    "x.testentity3._.document.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.entity_type", "schema")
        ),
    ]


class TestCaseValidateEntity_InvalidSchema(HttpRunner):
    """Validate Entity: Invalid derived schema through unified endpoint"""
    config = Config("Validate Entity - Invalid Schema").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.testentity4.base.item.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["itemId"],
                "properties": {
                    "itemId": {"type": "string"},
                    "size": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100
                    }
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register invalid derived schema loosening constraints")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.testentity4.base.item.v1~"
                    "x.testentity4._.bad_item.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.testentity4.base.item.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "size": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 200
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate schema should fail")
            .post("/validate-entity")
            .with_json({
                "entity_id": (
                    "gts.x.testentity4.base.item.v1~"
                    "x.testentity4._.bad_item.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
            .assert_equal("body.entity_type", "schema")
        ),
    ]


class TestCaseValidateEntity_3LevelSchemaHierarchy(HttpRunner):
    """Validate Entity: 3-level schema hierarchy validation"""
    config = Config("Validate Entity - 3-Level Schema").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register level 1 base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.testentity5.base.message.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["msgId"],
                "properties": {
                    "msgId": {"type": "string"},
                    "content": {"type": "string", "maxLength": 1000}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register level 2 schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.testentity5.base.message.v1~"
                    "x.testentity5._.email.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.testentity5.base.message.v1~"},
                    {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "maxLength": 500}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 2 schema")
            .post("/validate-entity")
            .with_json({
                "entity_id": (
                    "gts.x.testentity5.base.message.v1~"
                    "x.testentity5._.email.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.entity_type", "schema")
        ),
        Step(
            RunRequest("register level 3 schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.testentity5.base.message.v1~"
                    "x.testentity5._.email.v1~x.testentity5._.notification.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {
                        "$$ref": (
                            "gts://gts.x.testentity5.base.message.v1~"
                            "x.testentity5._.email.v1~"
                        )
                    },
                    {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "maxLength": 200}
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate level 3 schema")
            .post("/validate-entity")
            .with_json({
                "entity_id": (
                    "gts.x.testentity5.base.message.v1~"
                    "x.testentity5._.email.v1~x.testentity5._.notification.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.entity_type", "schema")
        ),
    ]


class TestCaseValidateEntity_MixedInstanceAndSchema(HttpRunner):
    """Validate Entity: Test both instance and schema in same test"""
    config = Config(
        "Validate Entity - Mixed Instance and Schema"
    ).base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.testentity6.product.base.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["productId", "name"],
                "properties": {
                    "productId": {"type": "string"},
                    "name": {"type": "string"},
                    "price": {"type": "number", "minimum": 0}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("register derived schema")
            .post("/entities")
            .with_json({
                "$$id": (
                    "gts://gts.x.testentity6.product.base.v1~"
                    "x.testentity6._.digital.v1~"
                ),
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "allOf": [
                    {"$$ref": "gts://gts.x.testentity6.product.base.v1~"},
                    {
                        "type": "object",
                        "required": ["downloadUrl"],
                        "properties": {
                            "downloadUrl": {
                                "type": "string",
                                "format": "uri"
                            }
                        }
                    }
                ]
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate derived schema")
            .post("/validate-entity")
            .with_json({
                "entity_id": (
                    "gts.x.testentity6.product.base.v1~"
                    "x.testentity6._.digital.v1~"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.entity_type", "schema")
        ),
        Step(
            RunRequest("register instance of derived schema")
            .post("/entities")
            .with_json({
                "type": (
                    "gts.x.testentity6.product.base.v1~"
                    "x.testentity6._.digital.v1~"
                ),
                "id": (
                    "gts.x.testentity6.product.base.v1~"
                    "x.testentity6._.digital.v1~x.testentity6._.prod1.v1"
                ),
                "productId": "PROD-001",
                "name": "eBook",
                "price": 9.99,
                "downloadUrl": "https://example.com/download/ebook"
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate instance")
            .post("/validate-entity")
            .with_json({
                "entity_id": (
                    "gts.x.testentity6.product.base.v1~"
                    "x.testentity6._.digital.v1~x.testentity6._.prod1.v1"
                )
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.entity_type", "instance")
        ),
    ]


class TestCaseValidateEntity_NotFound(HttpRunner):
    """Validate Entity: Non-existent entity"""
    config = Config("Validate Entity - Not Found").base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("validate non-existent entity")
            .post("/validate-entity")
            .with_json({
                "entity_id": "gts.x.nonexistent.entity.type.v1~"
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", False)
        ),
    ]


class TestCaseValidateEntity_BaseSchemaNoParent(HttpRunner):
    """Validate Entity: Base schema with no parent (always valid)"""
    config = Config(
        "Validate Entity - Base Schema No Parent"
    ).base_url(
        get_gts_base_url()
    )

    def test_start(self):
        super().test_start()

    teststeps = [
        Step(
            RunRequest("register base schema without parent")
            .post("/entities")
            .with_json({
                "$$id": "gts://gts.x.testentity7.standalone.schema.v1~",
                "$$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["id"],
                "properties": {
                    "id": {"type": "string"}
                }
            })
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate base schema should succeed")
            .post("/validate-entity")
            .with_json({
                "entity_id": "gts.x.testentity7.standalone.schema.v1~"
            })
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.ok", True)
            .assert_equal("body.entity_type", "schema")
        ),
    ]


if __name__ == "__main__":
    TestCaseTestOp12SchemaValidation_DerivedSchemaFullyMatches().test_start()
