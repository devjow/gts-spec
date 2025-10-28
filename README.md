> **VERSION**: GTS early draft, version 0.2

# Global Type System (GTS) Specification

This document defines GTS — a simple, human-readable, globally unique identifier and referencing system for data type definitions (e.g., JSON Schemas) and data instances (e.g., JSON objects). It is specification-first, language-agnostic, and intentionally minimal, with primary focus on JSON and JSON Schema.

The GTS identifiers are strings in a format like:

```
gts.<vendor>.<package>.<namespace>.<type>.v<MAJOR>[.<MINOR>]
```

They can be used instead of UUID, ULID, URN, JSON Schema URL, XML Namespace URI, or other notations for identification of various objects and schema definitions like:

- API data types and typed payloads (e.g. custom resource attributes)
- RPC contracts schemas
- API errors, headers and various semantics definitions
- Event catalogs, messages and stream topics
- Workflow categories and instances
- FaaS functions or actions contract definitions
- Policy objects (RBAC/ABAC/IAM)
- UI elements, schemas and forms
- Observability payloads (e.g. log formats)
- IoT/Edge telemetry data (e.g. device message formats)
- Warehouse/lake schemas
- Enumerations and references (e.g. enum id + description)
- ML/AI artifacts (e.g. model metadata or MCP tools declarations)
- Configuration-as-data templates and config instances
- Testing artifacts (e.g. golden records and fixtures)
- Database schemas
- Compliance and audit objects

See detailed description and examples below.

## Table of Contents

- [Global Type System (GTS) Specification](#global-type-system-gts-specification)
- [1. Motivation](#1-motivation)
- [2. Identifier Format](#2-identifier-format)
  - [2.1 Canonical form](#21-canonical-form)
  - [2.2 Chained identifiers](#22-chained-identifiers)
  - [2.3 Formal Grammar (EBNF)](#23-formal-grammar-ebnf)
- [3. Semantics and Capabilities](#3-semantics-and-capabilities)
  - [3.1 Core Operations](#31-core-operations)
  - [3.2 Minor Version Compatibility](#32-minor-version-compatibility)
  - [3.3 Query Language](#33-query-language)
  - [3.4 Attribute selector](#34-attribute-selector)
  - [3.5 Access control with wildcards](#35-access-control-with-wildcards)
  - [3.6 Access Control Implementation Notes](#36-access-control-implementation-notes)
- [4. Typical Uses](#4-typical-uses)
- [5. Implementation-defined and Non-goals](#5-implementation-defined-and-non-goals)
- [6. Comparison with other identifiers](#6-comparison-with-other-identifiers)
- [7. Parsing and Validation](#7-parsing-and-validation)
  - [7.1 Single-segment regex (type or instance)](#71-single-segment-regex-type-or-instance)
  - [7.2 Chained identifier regex](#72-chained-identifier-regex)
- [8. Reference Operators (Python)](#8-reference-operators-python)
  - [8.1 Normalize, validate, and parse](#81-normalize-validate-and-parse)
  - [8.2 Validate object against schema](#82-validate-object-against-schema)
  - [8.3 Minor version casting (downcast/upcast)](#83-minor-version-casting-downcastupcast)
  - [8.4 Type compatibility across minor versions](#84-type-compatibility-across-minor-versions)
  - [8.5 Mapping GTS to UUIDs](#85-mapping-gts-to-uuids)
  - [8.6 GTS Query mini-language](#86-gts-query-mini-language)
  - [8.7 Attribute Selector (`@`)](#87-attribute-selector-)
  - [8.8 Identifier extraction (instances and schemas)](#88-identifier-extraction-instances-and-schemas)
  - [8.9 Pattern matching (wildcards)](#89-pattern-matching-wildcards)
  - [8.10 Relationship resolution (schemas and refs)](#810-relationship-resolution-schemas-and-refs)
- [9. Collecting Identifiers with Wildcards](#9-collecting-identifiers-with-wildcards)
- [10. JSON and JSON Schema Conventions](#10-json-and-json-schema-conventions)
- [11. Notes and Best Practices](#11-notes-and-best-practices)
- [12. Registered Vendors](#12-registered-vendors)


## Document Version

| Document Version | Status                                                                                        |
|------------------|-----------------------------------------------------------------------------------------------|
| 0.1              | Initial Draft, Request for Comments                                                           |
| 0.2              | Semantics and Capabilities refined - access control notes, query language, attribute selector |


## 1. Motivation

The proliferation of distributed systems, microservices, and event-driven architectures has created a significant challenge in maintaining **data integrity**, **system interoperability**, and **type governance** across organizational boundaries and technology stacks.

Existing identification methods—such as opaque UUIDs, simple URLs (e.g. JSON Schema URLs), or proprietary naming conventions—fail to address the full spectrum of modern data management requirements. The **Global Type System (GTS)** is designed to solve these systemic issues by providing a simple, structured, and self-describing mechanism for identifying and referencing data types (schemas) and data instances (objects).

The primary value of GTS is to provide a single, universal identifier that is immediately useful for:

### 1.1 Unifying Data Governance and Interoperability

**Human- and Machine-Readable**: GTS identifiers are semantically meaningful, incorporating vendor, package, namespace, and version information directly into the ID. This makes them instantly comprehensible to developers, architects, and automated systems for logging, tracing, and debugging.

**Vendor and Domain Agnostic**: By supporting explicit vendor registration, GTS facilitates safe, cross-vendor data exchange (e.g., in event buses or plugin systems) while preventing naming collisions and ensuring the origin of a definition is clear.

#### 1.2 Enforcing Type Safety and Extensibility

**Explicit Schema/Instance Distinction**: The GTS naming format clearly separates a type definition (schema) from a concrete data instance, enabling unambiguous schema resolution and validation.

**Inheritance and Conformance Lineage**: The chained identifier system provides a robust, first-class mechanism for expressing type derivation and instance conformance. This is critical for ecosystems where third-parties must safely extend core types while guaranteeing compatibility with the base schema.

**Built-in Version Compatibility**: By adopting a constrained Semantic Versioning model, GTS inherently supports automated compatibility checking across minor versions. This simplifies data casting (upcast/downcast), allowing consumers to safely process data from newer schema versions without breaking.

#### 1.3 Simplifying Policy and Tooling

**Granular Access Control**: The structured nature of the identifier enables the creation of coarse-grained access control policies using wildcard matching (e.g., granting a service permission to process all events from a specific vendor/package: gts.myvendor.accounting.*).

**Deterministic Opaque IDs**: GTS supports the deterministic derivation of UUIDs (v5), providing a stable, fixed-length key for database indexing and external system APIs where human-readability is not required, while maintaining a clear, auditable link back to the source type.

**Specification-First**: As a language- and format-agnostic specification (though prioritizing JSON/JSON Schema), GTS provides a stable foundation upon which robust, interchangeable validation and parsing tools can be built across any ecosystem.


## 2. Identifier Format

GTS identifiers name either a schema (type) or an instance (object). A single GTS identifier may also chain multiple identifiers to express inheritance/compatibility and an instance’s conformance lineage.

The GTS identifier is a string with total length of 1024 characters maximum.

#### 2.1 Canonical form

- A single type identifier (schema):
  - `gts.<vendor>.<package>.<namespace>.<type>.v<MAJOR>[.<MINOR>]~`
  - Note the trailing `~` to denote a type (schema) identifier.
- A single instance identifier (object):
  - `gts.<vendor>.<package>.<namespace>.<type>.v<MAJOR>[.<MINOR>]`
  - Note: no trailing `~` for instances. The identifier ends with an integer (the last version component).

The `<vendor>` refers to a string code that indicates the origin of a given schema or instance definition. This can be valuable in systems that support cross-vendor data exchange, such as events or configuration files, especially in environments with deployable applications or plugins.

The `<package>` notation defines a module, plugin, or application provided by the vendor that contains the specified GTS definition.

The `<namespace>` specifies a category of GTS definitions within the package, and finally, the `<type>` defines the specific object type.

Segments must be lowercase ASCII letters, digits, and underscores; they must start with a letter or underscore: `[a-z_][a-z0-9_]*`. The single underscore `_` is reserved as a placeholder and may only be used for the `<namespace>` segment.

Versioning uses semantic versioning constrained to major and optional minor: `v<MAJOR>[.<MINOR>]` where `<MAJOR>` and `<MINOR>` are non-negative integers, for example:
- `gts.x.core.events.event.v1~` - defines a base event type in the system
- `gts.x.core.events.event.v1.2~` - defines a specific edition v1.2 of the base event type

**Examples** - The GTS identifier can be used for instance or type identifiers:
```bash
gts.x.idp.users.user.v1.0~ # defines ID of a schema of the user objects provided by vendor 'x' in scope of the package 'idp'
gts.x.mq.events.topic.v1~ # defines ID of a schema of the MQ topic stream provided by vendor 'x' in scope of the 'mq' (message queue) package

```

### 2.2 Chained identifiers

Multiple GTS identifiers can be chained with `~` to express derivation and conformance. The chain follows **left-to-right inheritance** semantics:

- Pattern: `gts.<segment1>~<segment2>~<segment3>`
- Where **<segment>** is a single GTS identifier segment: `<vendor>.<package>.<namespace>.<type>.v<MAJOR>[.<MINOR>]`
  - `<segment1>` is a **base type** (schema ID ending with `~`)
  - `<segment2>` is a **derived/refined type** (schema ID ending with `~`) that extends `<segment1>` with additional constraints or implementation-specific details. It MUST be compatible with `<segment1>`.
  - `<segment3>` is an **instance identifier** (no trailing `~`) that conforms to `<segment2>`. By transitivity, it also conforms to `<segment1>`.

**Important:** Each type in the chain inherits from its immediate predecessor (left neighbor) and MUST maintain compatibility.

**Chaining rules:**
1. All elements except the rightmost MUST be type identifiers (conceptually ending with `~`).
2. The rightmost element determines the identifier's nature:
   - Ends with `~` → the whole identifier represents a **type/schema**.
   - No trailing `~` → the whole identifier represents an **instance/object**.
3. The `gts.` prefix appears **only once** at the very beginning of the identifier string.
4. Segments after the first are considered relative identifiers and do not repeat the `gts.` prefix. (e.g., `gts.x.some.base.type.v1~vendor.app.some.derived.v1~`).
5. Use `_` as a placeholder when the namespace is not applicable

**Examples with explanations:**

``` bash
# Base type only (standalone schema)
gts.x.core.events.event.v1~

# Type `ven.app._.custom_event.v1` derives from base type `gts.x.core.events.event.v1`. Both are schemas (trailing `~`).
gts.x.core.events.event.v1~ven.app._.custom_event.v1~

# Instance `ven.app._.custom_event_topic.v1.2` (no trailing `~`) conforms to type `gts.x.core.events.topic.v1`. The identifier shows the full inheritance chain.
gts.x.core.events.topic.v1~ven.app._.custom_event_topic.v1.2
```

### 2.3 Formal Grammar (EBNF)

The complete GTS identifier syntax in Extended Backus-Naur Form (EBNF):

```ebnf
(* Top-level identifier *)
gts-identifier = "gts." , gts-segment , [ chain-suffix ] ;

(* Chain of type extensions *)
chain-suffix   = { "~" , gts-segment } , [ final-tilde ] ;
final-tilde    = "~" ;  (* present for type IDs, absent for instance IDs *)

(* Single GTS ID segment *)
gts-segment    = vendor , "." , package , "." , namespace , "." , type , "." , version ;

vendor         = segment ;
package        = segment ;
namespace      = segment ;
type           = segment ;

(* Segment: lowercase letters, digits, underscores; starts with letter or underscore *)
segment        = ( letter | "_" ) , { letter | digit | "_" } ;

(* Version: major.minor or major only *)
version        = "v" , major , [ "." , minor ] ;
major          = "0" | positive-integer ;
minor          = "0" | positive-integer ;

(* Primitives *)
positive-integer = non-zero-digit , { digit } ;
letter           = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j"
                 | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t"
                 | "u" | "v" | "w" | "x" | "y" | "z" ;
digit            = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
non-zero-digit   = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

**Grammar notes:**

1. **Type vs Instance distinction**: A GTS identifier ending with `~` (final-tilde present) denotes a type/schema. Without the trailing `~`, it denotes an instance.

2. **Chain interpretation**: In a chained identifier `gts.<gts-segment1>~<gts-segment2>~<gts-segment3>`, each `~` acts as a separator. All segments before the final segment MUST be types (conceptually ending with `~`). The final segment determines whether the entire identifier is a type or instance.

3. **Placeholder rule**: Use `_` (underscore) as a segment value when the namespace is not applicable. It is recommended to use the placeholder only for the `<namespace>` segment.

4. **Normalization**: GTS identifiers must be lowercase. Leading/trailing whitespace is not permitted. Canonical form has no optional spacing.

5. **Reserved prefix**: The `gts.` prefix is mandatory and reserved. Future versions may introduce alternative prefixes but will maintain backward compatibility.


## 3. Semantics and Capabilities

GTS identifiers enable the following operations and use cases:

### 3.1 Core Operations

1. **Global Identification**: Uniquely identify data types (JSON Schemas) and data instances (JSON objects) in a human-readable format across systems and vendors.

2. **Schema Resolution and Validation**:
   - For a type identifier (ending with `~`): resolve to the JSON Schema definition
   - For an instance identifier: extract the rightmost type from the chain and validate the object against that schema
   - Chain validation: optionally verify that each type in the chain is compatible with its predecessor

3. **Version Compatibility Checking**: Automatically determine if schemas with different MINOR versions are compatible (see section 3.2).

4. **Access Control Policies**: Build fine-grained or coarse-grained authorization rules using:
   - Exact identifier matching
   - Wildcard patterns (e.g., `gts.vendor.package.*`)
   - Chain-based isolation (e.g., restrict access to specific vendor's extensions)
   - See also ABAC use-cases in sections 3.2 and 3.3 below

5. **Extensible Type Systems**: Enable platforms where:
   - Base system types are defined by a core vendor
   - Third-party vendors extend base types with additional constraints
   - All validation guarantees are preserved through the inheritance chain
   - Type evolution is tracked explicitly through versioning

### 3.2 Minor Version Compatibility

**Semantic Versioning Rules for GTS:**

MINOR version increments (e.g., v1.2 → v1.3) within the same MAJOR version MUST maintain backward compatibility:

**Allowed changes (backward compatible):**
- Adding new optional properties with default value
- Clarifying documentation or examples

**Prohibited changes (breaking):**
- Removing required properties
- Adding new required properties
- Changing property types incompatibly
- Tightening constraints on existing fields
- Removing enum values
- Adding new enum values (prohibited to catch problems with if/else/switch and version downcast, instead define enums as gts instances of a base enum type)
- Relaxing constraints (e.g., v1.0 has field with max length 128, in v1.1 length changed to 256, v1.1 -> v1.0 cast would need to cut off some data)

**Chain Compatibility:**
- In a chain `gts.A~B~C`, type `B` MUST be compatible with `A`, and type `C` MUST be compatible with `B`
- Compatibility is verified left-to-right: each type must accept all valid instances of its predecessor
- Use MAJOR version increment for any breaking change

**Practical implication:** A consumer expecting v1.2 can safely process objects validated against v1.3 of the same schema.

### 3.3 Query Language

A compact predicate syntax, inspired by XPath/JSONPath, lets you constrain results by attributes. Attach a square-bracket clause to a GTS identifier with comma-separated name="value" pairs. Example form: <gts>[ attr="value", other="value2" ].

Predicates can reference plain literals or GTS-formatted values, e.g.:

```bash
# filter all events that are published to the topic "some_topic" by the vendor "z"
gts.x.core.events.event.v1.0[type_id="gts.x.core.events.topic.v1~z.app._.some_topic.v1"]
# filter all user settings that were defined for users if type is z-vendor app_admin
gts.x.core.acm.user_setting.v1[user_type="gts.x.core.acm.user.v1~z.app._.app_admin.v1"]
```

Multiple parameters are combined with logical AND to further restrict the result set:

```bash
gts.x.z.z.type.v1[foo="bar", id="ef275d2b-9f21-4856-8c3b-5b5445dba17d"]
```

### 3.4 Attribute selector

GTS includes a lightweight attribute accessor, akin to JSONPath dot notation, to read a single value from a bound instance. Append `@` to the identifier and provide a property path, e.g., <gts>@<root>.<nested>.

The selector always resolves from the instance root and returns one attribute per query. For example:

```bash
# refer to the value of the message identifier
gts.x.y.z.message.v1@id
```

Nested attributes also can be accessed within the instance's structure. For example:
```bash
# refer to the value of the 'bar' item property from the 'foo' field
gts.x.y.z.message.v1.0@foo.bar
```

### 3.5 Access control with wildcards

Wildcards (`*`) enable policy scopes that cover families of identifiers (e.g., entire vendor/package trees) rather than single, exact instance or schema IDs. This is useful in RBAC/ABAC style engines and relationship-based systems (e.g., Zanzibar-like models) where permissions are expressed over sets of resources.

```bash
# grants access to all the audit events category defined by the vendor 'xyz'
gts.x.core.events.event.v1~x.core._.audit_event.v1~xyz.*
# grants access to all the menu items referring screens of the vendor 'abc'
gts.x.ui.left_menu.menu_item.v1[screen_type="gts.x.ui.core_ui.screens.v1~abc.*"]
```

### 3.6 Access Control Implementation Notes

> **Scope disclaimer:** GTS-based access control implementation is outside the scope of this specification and will vary across systems. GTS provides the syntax to express authorization rules; however, different policy engines may apply different evaluation strategies or may not support attribute-based or wildcard-based access control at all.

The following guidance is provided for implementers building GTS-aware policy engines:

**Policy management domain model:**
- **Principal**: Users, services, or groups (outside the scope of GTS) mapped to roles.
- **Resource**: GTS identifiers or patterns (with wildcards and, optionally, attribute predicates) that denote types or instances.
- **Action**: Verbs such as `read`, `write`, `emit`, `subscribe`, `admin` defined by the platform.

**Example policy shapes:**
- **RBAC-style allow**: Role `xyz_auditor` → allow `read` on `gts.x.core.events.event.v1~x.core._.audit_event.v1~xyz.*`
- **ABAC refinement**: Attach predicate filters like `[screen_type="..."]` to restrict by referenced type.
- **Derived-type envelopes**: Grant access at the base type (e.g., `gts.x.core.events.event.v1~`) so that derived schemas remain covered if they conform by chain rules.

**Matching semantics options:**
- **Segment-wise prefixing**: The `*` wildcard can match any valid content of the target segment and its suffix hierarchy, enabling vendor/package/namespace/type grouping.
- **Chain awareness**: Patterns may target the base segment, derived segments, or instance tail; evaluation should consider the entire chain when present.
- **Attribute filters**: Optional `[name="value", ...]` predicates further constrain matches (e.g., only instances referencing a specific `screen_type`).

**Evaluation guidelines:**
- **Deny-over-allow (recommended)**: If your engine supports explicit denies, process them before allows to prevent privilege escalation.
- **Most-specific wins**: Prefer the most specific matching rule (longest concrete prefix, fewest wildcards, most predicates).
- **Version safety**: Consider pinning MAJOR and, optionally, MINOR versions in sensitive paths; otherwise rely on minor-version compatibility guarantees (see section 3.2).
- **Tenant isolation**: Use vendor/package scoping to isolate tenants and applications; avoid cross-vendor wildcards unless explicitly required.

**Performance guidelines:**
- **Indexing**: Normalize and index rules by canonical GTS prefix to avoid expensive pattern-matching scans.
- **Caching**: Cache resolution results for common patterns and predicate evaluations; invalidate caches on schema or policy changes.
- **Auditing**: Log the concrete identifier and the matched rule (pattern + predicates) for traceability and compliance.


## 4. Typical Uses

### 4.1 Use-cases

- API custom payload schema definitions
- Event schema definitions
- Configuration settings schema definitions
- Database schema definitions
- Data warehouse object schema definitions

See some definitions in the [examples folder](./examples/)

#### 4.2 JSON and JSON Schema examples

**Practical Scenario:**

Consider a vendor, `X`, who operates a multi-tenant event management platform. This platform acts as a broker, receiving events from various producers (e.g., third-party applications) and routing them to the correct handlers. According to the platform's specification, every event must contain a `gtsId` field that references a registered event schema. This allows the platform to validate, authorize, and route events of different kinds, such as general-purpose events, audit logs, and custom messages.

Now, imagine a second vendor, `ABC`, develops an application named `APP` that runs on vendor `X`'s platform. When a customer makes an online purchase within `APP`, the application needs to emit a `store.purchase_audit_event` to the event manager.

In this scenario, vendor `X`'s platform must be able to:
1.  **Authorize** the incoming event, ensuring that vendor `ABC` is permitted to emit it.
2.  **Validate** the event's structure against the correct schema.
3.  **Ensure data isolation**, making the event visible only to authorized parties (e.g., vendor `ABC`'s `APP` administrators) and not to other tenants.

Let's define the schemas required to implement this.

First, let's define the base event schema for vendor `X` event manager:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gts.x.core.events.event.v1~",
  "title": "Base Event",
  "type": "object",
  "properties": {
    "gtsId": { "type": "string", "$comment": "This field serves as the unique identifier for the event schema" },
    "id": { "type": "string", "$comment": "This field serves as the unique identifier for the event instance" },
    "timestamp": { "type": "integer", "$comment": "timestamp in seconds since epoch" },
    "payload": { "type": "object", "additionalProperties": true, "$comment": "Event payload... can be anything" }
  },
  "required": ["gtsId", "id", "timestamp", "payload"],
  "additionalProperties": false
}
```

Now, let's define the audit event schema for vendor `X` event manager:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gts.x.core.events.event.v1~x.core.audit.event.v1~",
  "title": "Audit Event, derived from Base Event",
  "type": "object",
  "allOf": [
    { "$ref": "gts.x.core.events.event.v1~" },
    {
      "type": "object",
      "properties": {
        "payload": {
          "type": "object",
          "properties": {
            "user_id": { "type": "string", "$comment": "User ID" },
            "user_agent": { "type": "string", "$comment": "User agent" },
            "ip_address": { "type": "string", "$comment": "IP address" },
            "data": { "type": "object", "additionalProperties": true, "$comment": "Audit event custom data... can be anything" }
          },
          "required": ["user_id", "user_agent", "ip_address", "data"],
          "additionalProperties": false
        }
      },
      "required": ["payload"]
    }
  ],
}
```

Then, let's define the schema of specific audit event registered by vendor `ABC` application `APP`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gts.x.core.events.event.v1~x.core.audit.event.v1~abc.app.store.purchase_audit_event.v1.2~",
  "title": "Vendor ABC Custom Purchase Audit Event from app APP",
  "type": "object",
  "allOf": [
    { "$ref": "gts.x.core.events.event.v1~x.core.audit.event.v1~" },
    {
      "type": "object",
      "properties": {
        "payload": {
          "type": "object",
          "properties": {
            "data": {
              "type": "object",
              "properties": {
                "purchase_id": { "type": "string" },
                "amount": { "type": "number" },
                "currency": { "type": "string" },
                "price": { "type": "number" }
              },
              "required": ["purchase_id", "amount", "currency", "price"],
              "additionalProperties": false
            }
          },
        }
      },
      "required": ["payload"]
    }
  ],
}
```

Finally, when the producer (the application `APP` of vendor `ABC`) emits the event, it uses the `gtsId` to identify the event schema and provide required payload:

```json
{
  "gtsId": "gts.x.core.events.event.v1~x.core.audit.event.v1~abc.app.store.purchase_audit_event.v1.2~",
  "id": "e81307e5-5ee8-4c0a-8d1f-bd98a65c517e",
  "timestamp": 1743466200000000000,
  "payload": {
    "user_id": "9c905ae1-f0f3-4cfb-aa07-5d9a86219abe",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "ip_address": "127.0.0.1",
    "data": {
      "purchase_id": "cats_drinking_bowl_42",
      "amount": 2,
      "currency": "USD",
      "price": 19.95
    }
  }
}
```

When the event manager receives the event it processes it as follows:

1. **Schema Resolution**: Parse the `gtsId` to identify the full chain. The event manager can see that this instance conforms to `gts.x.core.events.event.v1~`, `...~x.core.audit.event.v1~`, and finally `...~abc.app.store.purchase_audit_event.v1.2~`.

2. **Validation**: Load the most specific JSON Schema (`...~abc.app.store.purchase_audit_event.v1.2~`) and validate the event object against it. It would automatically mean the event body is validated against any other schema in the chain (e.g., the base event and the base audit event).

3. **Authorization**: Check if the producer is authorized to emit events matching the pattern `gts.x.core.audit.event.v1~x.core.audit.event.v1~abc.app.*` or a broader pattern like `gts.x.core.audit.event.v1~x.core.audit.event.v1~abc.app.*`.

4. **Routing & Auditing**: Use the chain to route events to appropriate handlers or storage if needed.

> **Note**: use the [GTS Kit](https://github.com/globaltypesystem/gts-kit) for visualization of the entities relationship and validation


## 5. Implementation-defined and Non-goals

This specification intentionally does not enforce several operational or governance choices. It is up to the implementation vendor to define policies and behavior for:

1. Whether a defined type is exported and available for cross-vendor use via APIs or an event bus.
2. Whether a given JSON/JSON Schema definition is mutable or immutable (e.g., handling an incompatible change without changing the minor or major version).
3. How to implement access policies and access checks based on the GTS query and attribute access languages.
4. When to introduce a new minor version versus a new major version.
5. GTS identifiers renaming and aliasing

> **Non-goals reminder**: GTS is not an eventing framework, transport, or workflow. It standardizes identifiers and basic validation/casting semantics around JSON and JSON Schema.


## 6. Comparison with other identifiers

- JSONSchema $schema url: While JSONSchema provides a robust framework for defining the structure of JSON data, GTS extends this by offering clear vendor, package and namespace notation and chaining making it easier to track and validate data instances across different systems and versions.
- UUID: Opaque and globally unique. GTS is meaningful to humans and machines; UUIDs can be derived from GTS deterministically when opaque IDs are required.
- Apple UTI: Human-readable, reverse-DNS-like. GTS is similar in readability but adds explicit versioning, vendors/apps support, chaining, and schema/instance distinction suitable for JSON Schema-based validation.
- Amazon ARN: Global and structured, but cloud-service-specific. GTS is vendor-neutral and domain-agnostic, focused on data schemas and instances.


## 7. Parsing and Validation

### 7.1 Single-segment regex (type or instance)

Single-chain variant:

```regex
^gts\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.v(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?~?$
```

Verbose, named groups (Python `re.VERBOSE`):

```regex
^\s*
gts\.
(?P<vendor>[a-z_][a-z0-9_]*)\.
(?P<package>[a-z_][a-z0-9_]*)\.
(?P<namespace>[a-z_][a-z0-9_]*)\.
(?P<type>[a-z_][a-z0-9_]*)
\.v(?P<major>0|[1-9]\d*)
(?:\.(?P<minor>0|[1-9]\d*))?
(?P<is_type>~)?
\s*$
```

`is_type` captures the optional trailing `~` (present for type IDs, absent for instance IDs).

#### 7.2 Chained identifier regex

For chained identifiers, the pattern enforces that all segments except the last are type IDs (with `~` separators):

```regex
^\s*gts\.[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\.v(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?(?:~[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\.v(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?)*~?\s*$
```

**Pattern explanation:**
- Starts with a single absolute segment (`gts.` prefix)
- Followed by zero or more relative segments, each prefixed by `~`
- The final `~` is optional: present for a type, absent for an instance

**Validation rules:**
1. Standalone type identifier: MUST end with `~`
2. In a chain, all segments except the rightmost MUST be types (end with `~` in the original string)
3. Only the first segment uses the `gts.` prefix; chained segments are relative (no `gts.`)

**Parsing strategy:**
- Split on `~` to get raw segments; the first is absolute, the rest are relative
- Parse the first using the absolute pattern, the rest using the relative pattern
- Validate that all segments except possibly the last are types


## 8. Reference Operators (Python)

GTS implementations provide several core operations for working with identifiers:

- **OP#1 - ID Validation**: Verify identifier syntax using regex patterns
- **OP#2 - ID Extraction**: Fetch identifiers from JSON objects or JSON Schema documents
- **OP#3 - ID Parsing**: Decompose identifiers into constituent parts (vendor, package, namespace, type, version, etc.)
- **OP#4 - ID Pattern Matching**: Match identifiers against patterns containing wildcards
- **OP#5 - ID to UUID Mapping**: Generate deterministic UUIDs from GTS identifiers
- **OP#6 - Schema Validation**: Validate object instances against their corresponding schemas
- **OP#7 - Relationship Resolution**: Load all schemas and instances, resolve inter-dependencies, and detect broken references
- **OP#8 - Compatibility Checking**: Verify that schemas with different MINOR versions are compatible
- **OP#9 - Version Casting**: Transform instances between compatible MINOR versions
- **OP#10 - Query Execution**: Filter identifier collections using the GTS query language
- **OP#11 - Attribute Access**: Retrieve property values and metadata using the attribute selector (`@`)

The following sections provide reference implementations in Python. Implementations in other languages should mirror these semantics and are maintained in dedicated repositories.

### 8.1 Normalize, validate, and parse

```python
import re
from dataclasses import dataclass
from typing import Optional, List

# Absolute first segment: includes the 'gts.' prefix
ABSOLUTE_SEGMENT_PATTERN = re.compile(r"^gts\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.v(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?(~)?$")

# Relative chained segment: no 'gts.' prefix
RELATIVE_SEGMENT_PATTERN = re.compile(r"^([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.v(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?(~)?$")


@dataclass(frozen=True)
class GtsIdSegment:
    vendor: str
    package: str
    namespace: str
    type: str
    major: int
    minor: Optional[int]
    is_type: bool  # True if ends with '~'

    def short(self) -> str:
        v = f"v{self.major}" + (f".{self.minor}" if self.minor is not None else "")
        suffix = "~" if self.is_type else ""
        return f"gts.{self.vendor}.{self.package}.{self.namespace}.{self.type}.{v}{suffix}"


def parse_absolute(segment: str) -> GtsIdSegment:
    m = ABSOLUTE_SEGMENT_PATTERN.fullmatch(segment)
    if not m:
        raise ValueError(f"Invalid absolute GTS segment: {segment}")
    vendor, package, namespace, type_, major, minor, is_type = m.groups()
    return GtsIdSegment(
        vendor=vendor,
        package=package,
        namespace=namespace,
        type=type_,
        major=int(major),
        minor=int(minor) if minor is not None else None,
        is_type=is_type == "~",
    )


def parse_relative(segment: str) -> GtsIdSegment:
    m = RELATIVE_SEGMENT_PATTERN.fullmatch(segment)
    if not m:
        raise ValueError(f"Invalid relative GTS segment: {segment}")
    vendor, package, namespace, type_, major, minor, is_type = m.groups()
    return GtsIdSegment(
        vendor=vendor,
        package=package,
        namespace=namespace,
        type=type_,
        major=int(major),
        minor=int(minor) if minor is not None else None,
        is_type=is_type == "~",
    )


def parse_single(segment: str) -> GtsIdSegment:
    """
    Parse a single GTS segment (absolute or relative) into structured components.

    Args:
        segment: A GTS segment (e.g., 'gts.x.core.events.event.v1~' or 'x.app._.custom.v1.2')

    Returns:
        GtsIdSegment object with parsed vendor, package, namespace, type, version, and type flag

    Raises:
        ValueError: If the segment doesn't match either pattern
    """
    try:
        return parse_absolute(segment)
    except ValueError:
        return parse_relative(segment)


def split_chain(gts_id: str) -> List[GtsIdSegment]:
    """
    Parse a GTS identifier (single or chained) into a list of GtsIdSegment segments.

    The first segment must be absolute (with 'gts.' prefix). Subsequent segments
    are relative (without 'gts.'). All but the last segment MUST be types.

    Args:
        gts_id: Full GTS identifier (e.g., 'gts.x.base.v1~vendor.derived.v1.2')

    Returns:
        List of GtsIdSegment objects representing the chain

    Raises:
        ValueError: If the identifier is malformed or violates chaining rules
    """
    raw_parts = gts_id.split("~")
    parts = [p for p in raw_parts if p != ""]
    if not parts:
        raise ValueError("Empty GTS identifier")

    # First segment: absolute
    segments: List[GtsIdSegment] = [parse_absolute(parts[0])]

    # Remaining: relative
    for p in parts[1:]:
        segments.append(parse_relative(p))

    # Enforce: all but last must be types
    for seg in segments[:-1]:
        if not seg.is_type:
            raise ValueError("All segments except the last must be type identifiers (end with '~')")

    # If there was a trailing '~' in the original, then the last should be a type
    if gts_id.endswith("~") and not segments[-1].is_type:
        raise ValueError("Identifier ends with '~' but last segment is not marked as type")

    return segments
```

Validation helpers (OP#1)

```python
def is_valid_gts_segment(s: str) -> bool:
    """Check if a single segment (absolute or relative) is syntactically valid."""
    return bool(ABSOLUTE_SEGMENT_PATTERN.fullmatch(s) or RELATIVE_SEGMENT_PATTERN.fullmatch(s))


def is_valid_gts_id(s: str) -> bool:
    """Check if a full GTS identifier (single or chained) is valid by parsing it."""
    try:
        _ = split_chain(s)
        return True
    except Exception:
        return False
```

### 8.2 Validate object against schema

**Validation algorithm:**

1. Parse the instance's `gtsId` to extract all segments in the chain
2. Identify the rightmost **type** segment (the one immediately before the final instance segment, or the final segment if it ends with `~`)
3. Load the JSON Schema associated with that type identifier
4. Validate the object against the loaded schema
5. Optionally, verify compatibility across the entire chain

**Implementation notes:**
- Store schemas indexed by their type identifiers (ending with `~`)
- The instance identifier should match the schema's vendor, package, namespace, type, and MAJOR.MINOR version
- For chained types, the final type in the chain is the most specific and should be used for validation

```python
from jsonschema import validate as js_validate

class SchemaStore:
    def __init__(self):
        self._by_id = {}  # key: type-id (ending with ~), value: JSON Schema dict

    def register(self, type_id: str, schema: dict) -> None:
        if not type_id.endswith("~"):
            raise ValueError("Schema type_id must end with '~'")
        # sanity check
        parse_single(type_id)
        self._by_id[type_id] = schema

    def get(self, type_id: str) -> dict:
        return self._by_id[type_id]


def rightmost_type_id(chain: List[GtsIdSegment]) -> str:
    """
    Extract the rightmost type ID from a GTS chain.

    Rules:
    - If the last segment is a type (ends with ~), return it
    - If the last segment is an instance, return the previous segment (which must be a type)
    - A standalone instance without a chain is invalid

    Args:
        chain: List of parsed GtsIdSegment segments

    Returns:
        The type identifier string (ending with ~)

    Raises:
        ValueError: If the chain doesn't contain a valid type for validation
    """
    if len(chain) == 1 and not chain[0].is_type:
        raise ValueError("Standalone instances must include their type in a chain")
    last = chain[-1]
    if last.is_type:
        return last.short()
    # Last is instance, use second-to-last (which must be a type)
    return chain[-2].short()


def validate_instance(obj: dict, gts_id: str, store: SchemaStore) -> None:
    chain = split_chain(gts_id)
    type_id = rightmost_type_id(chain)
    schema = store.get(type_id)
    js_validate(instance=obj, schema=schema)
```

### 8.3 Minor version casting (downcast/upcast)

**Casting between minor versions** allows transformation of objects between compatible schema versions.

**Downcast (v1.3 → v1.2):** Remove properties that were added in newer minor versions
- Use case: Send data to a consumer that only understands an older schema version
- Safe operation: Only removes properties unknown to the target version

**Upcast (v1.2 → v1.3):** Add default values for new optional properties
- Use case: Normalize data to the latest schema version
- Requires: Default values defined in the target schema for new fields

**Note:** Both operations require access to both schema versions for accurate field mapping.

```python
def downcast(obj: dict, from_schema: dict, to_schema: dict) -> dict:
    """
    Downcast an object to an older minor version by removing unknown properties.

    Args:
        obj: The object to downcast
        from_schema: The current (newer) schema
        to_schema: The target (older) schema

    Returns:
        A new dict with only properties known to the target schema
    """
    allowed = set(to_schema.get("properties", {}).keys())
    return {k: v for k, v in obj.items() if k in allowed}


def upcast(obj: dict, from_schema: dict, to_schema: dict) -> dict:
    """
    Upcast an object to a newer minor version by adding default values.

    Args:
        obj: The object to upcast
        from_schema: The current (older) schema
        to_schema: The target (newer) schema

    Returns:
        A new dict with default values for new optional properties

    Note:
        If a new required property lacks a default, the result will fail validation.
        This is intentional - it signals an incompatible schema change.
    """
    result = dict(obj)
    props = to_schema.get("properties", {})
    required = set(to_schema.get("required", []))
    for k, v in props.items():
        if k not in result:
            if "default" in v:
                result[k] = v["default"]
            elif k in required:
                # Cannot upcast without a value; leave as-is for validator to catch
                pass
    return result
```

### 8.4 Type compatibility across minor versions

Basic check: required fields cannot be removed; properties should be a superset; types must not widen incompatibly.

```python
def is_minor_compatible(old_schema: dict, new_schema: dict) -> bool:
    old_props = old_schema.get("properties", {})
    new_props = new_schema.get("properties", {})
    old_req = set(old_schema.get("required", []))
    new_req = set(new_schema.get("required", []))

    # required of old must be subset of required of new plus possibly optional
    if not old_req.issubset(new_req.union(set())):
        return False

    # new props must include all old props
    if not set(old_props.keys()).issubset(set(new_props.keys())):
        return False

    # primitive type check (very simplified)
    for k in old_props.keys():
        old_t = old_props[k].get("type")
        new_t = new_props[k].get("type")
        if old_t != new_t:
            return False
    return True
```

### 8.5 Mapping GTS to UUIDs

**Use case:** Systems often need opaque, fixed-length identifiers for database keys, indexing, or external APIs while maintaining human-readable GTS identifiers for logs and debugging.

**Approach:** Generate stable UUIDv5 values deterministically from GTS identifiers. Two scopes are supported:

1. **Major-version UUID**: Same UUID for all minor versions within a major version (e.g., `v1.0`, `v1.1`, `v1.2` → same UUID)
   - Use case: Join tables on major version, allowing minor version flexibility

2. **Full-version UUID**: Unique UUID for each major.minor combination
   - Use case: Precise version tracking in databases

**Properties:**
- Deterministic: Same GTS identifier always produces the same UUID
- Collision-resistant: UUIDv5 uses cryptographic hashing
- Reversible reference: Store GTS alongside UUID for human-readable lookups

```python
import uuid

MAJOR_NS = uuid.uuid5(uuid.NAMESPACE_URL, "gts:major")
FULL_NS = uuid.uuid5(uuid.NAMESPACE_URL, "gts:full")


def _strip_minor(gts_id_segment: GtsIdSegment) -> GtsIdSegment:
    return GtsIdSegment(
        vendor=gts_id_segment.vendor,
        package=gts_id_segment.package,
        namespace=gts_id_segment.namespace,
        type=gts_id_segment.type,
        major=gts_id_segment.major,
        minor=None,
        is_type=gts_id_segment.is_type,
    )


def gts_uuid_major(gts_id: str) -> uuid.UUID:
    parts = split_chain(gts_id)
    # UUIDs are derived from the right-most element
    g = parts[-1]
    return uuid.uuid5(MAJOR_NS, _strip_minor(g).short())


def gts_uuid_full(gts_id: str) -> uuid.UUID:
    parts = split_chain(gts_id)
    g = parts[-1]
    return uuid.uuid5(FULL_NS, g.short())
```

### 8.6 GTS Query mini-language

**Purpose:** Enable filtering and querying object collections based on GTS identifiers and attributes.

**Syntax:** `<gts-type-prefix>[ <attribute>="<value>" <attribute>="<value>" ... ]`

**Examples:**
- `gts.x.core.events.event.v1.0` - Match all instances of this type (prefix match)
- `gts.x.core.events.event.v1.0[ topic_id="gts.x.core.events.topic.v1.0~x.core.idp._.contacts.v1.0" ]` - Match events with specific `contacts` topic_id
- `gts.x.core.events.event.v1[ status="active" priority="high" ]` - Multiple attribute filters

**Matching rules:**
1. GTS prefix match: The object's `gtsId` must start with the query's type prefix
2. Attribute filters: All specified attributes must match exactly (string comparison)
3. Attribute values are compared as strings (cast if needed)

```python
import shlex
from typing import Iterable, Callable

def parse_query(expr: str) -> tuple[str, dict]:
    base, _, filt = expr.partition("[")
    gts_base = base.strip()
    conditions = {}
    if filt:
        filt = filt.rsplit("]", 1)[0]
        # very simple tokenizer: key="value" pairs separated by spaces
        tokens = shlex.split(filt)
        for tok in tokens:
            if "=" in tok:
                k, v = tok.split("=", 1)
                conditions[k.strip()] = v.strip().strip('"')
    return gts_base, conditions


def match_query(obj: dict, gts_field: str, expr: str) -> bool:
    gts_base, cond = parse_query(expr)
    # type prefix match
    if not obj.get(gts_field, "").startswith(gts_base):
        return False
    for k, v in cond.items():
        if str(obj.get(k)) != v:
            return False
    return True
```

### 8.7 Attribute Selector (`@`)

**Purpose:** Access a specific attribute value from a GTS-identified instance using a simple path. An identifier with an attribute selector cannot be used as a type or instance identifier; it is only for data retrieval.

**Syntax:** `<gts-identifier>@<attribute-path>`

**Path Format:**
- A dot-separated (`.`) path to a nested attribute.
- The path always starts from the root of the instance.
- Array elements can be accessed by their index.

**Valid Examples:**
- `gts.x.llm.chat.message.v1.0@id` - Get the value of the `id` field from the root of the message object.
- `gts.x.llm.chat.message.v1.0@data.item` - Get the `item` property from the `data` object.
- `gts.x.core.idp.user.v1@addresses.0.city` - Get the `city` from the first element in the `addresses` array.

**Invalid Examples:**
- `gts.x.llm.chat.message.v1.0~@id` - Cannot be used on a type identifier.
- `gts.x.llm.chat.message.v1.0@` - Path cannot be empty.

```python
def split_at_path(gts_with_path: str) -> tuple[str, Optional[str]]:
    if "@" not in gts_with_path:
        return gts_with_path, None
    gts, path = gts_with_path.split("@", 1)
    if not path:
        raise ValueError("Attribute path cannot be empty")
    return gts, path


def resolve_path(obj: object, path: str) -> object:
    """
    Resolve a dot-separated attribute path against an object.
    """
    parts = path.split('.')
    cur = obj
    for p in parts:
        try:
            if isinstance(cur, list):
                idx = int(p)
                cur = cur[idx]
            elif isinstance(cur, dict):
                cur = cur[p]
            else:
                raise KeyError(f"Cannot descend into {type(cur)} with segment '{p}'")
        except (KeyError, IndexError, ValueError):
            raise KeyError(f"Path segment '{p}' not found in path '{path}'")
    return cur
```

### 8.8 Identifier extraction (instances and schemas)

OP#2 extracts GTS identifiers from JSON instances and JSON Schema documents.

```python
from typing import Iterable, Set


def _walk_json(o: object) -> Iterable[object]:
    if isinstance(o, dict):
        for v in o.values():
            yield from _walk_json(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk_json(v)
    else:
        yield o


def extract_identifiers_from_instance(obj: dict, fields: tuple[str, ...] = ("gtsId", "$id")) -> Set[str]:
    """Collect all strings in the object that look like valid GTS identifiers.

    Heuristic: prefer known fields like 'gtsId' or '$id', but also scan all string values.
    """
    found: Set[str] = set()
    # Preferred fields
    for f in fields:
        v = obj.get(f)
        if isinstance(v, str) and is_valid_gts_id(v):
            found.add(v)
    # Fallback: scan all strings
    for v in _walk_json(obj):
        if isinstance(v, str) and is_valid_gts_id(v):
            found.add(v)
    return found


def extract_identifiers_from_schema(schema: dict) -> Set[str]:
    """Collect type identifiers from a JSON Schema: $id and any $ref values that are GTS strings."""
    found: Set[str] = set()
    # $id
    sid = schema.get("$id")
    if isinstance(sid, str) and is_valid_gts_id(sid):
        found.add(sid)
    # $ref occurrences
    for v in _walk_json(schema):
        if isinstance(v, dict) and "$ref" in v:
            ref = v.get("$ref")
            if isinstance(ref, str) and is_valid_gts_id(ref):
                found.add(ref)
        elif isinstance(v, str) and is_valid_gts_id(v):
            # in case refs are represented as plain strings in arrays
            found.add(v)
    return found
```

### 8.9 Pattern matching (wildcards)

OP#8 matches identifiers against greedy end-of-string wildcard patterns.

```python
def wildcard_match(pattern: str, candidate: str) -> bool:
    """
    Matches a candidate identifier against a greedy, end-of-string wildcard pattern.

    Rules:
    - Only one '*' is allowed
    - '*' must be the last character
    """
    if '*' not in pattern:
        return pattern == candidate

    if pattern.count('*') > 1:
        return False

    if not pattern.endswith('*'):
        return False

    prefix = pattern[:-1]
    return candidate.startswith(prefix)
```

### 8.10 Relationship resolution (schemas and refs)

OP#5 loads schemas, resolves inter-dependencies via $ref, and detects broken references.

```python
from collections import defaultdict
from typing import Dict, Set, Tuple, List


def _extract_type_refs(schema: dict) -> Set[str]:
    refs: Set[str] = set()
    for v in _walk_json(schema):
        if isinstance(v, dict) and "$ref" in v and isinstance(v["$ref"], str):
            ref = v["$ref"]
            if is_valid_gts_id(ref) and ref.endswith("~"):
                refs.add(ref)
    return refs


def build_schema_graph(store: SchemaStore) -> Tuple[Dict[str, Set[str]], List[str]]:
    """Return adjacency graph and list of missing referenced type IDs."""
    graph: Dict[str, Set[str]] = {}
    missing: Set[str] = set()
    for type_id, schema in store._by_id.items():  # simple access for illustration
        refs = _extract_type_refs(schema) - {type_id}
        graph[type_id] = refs
        for r in refs:
            if r not in store._by_id:
                missing.add(r)
    return graph, sorted(missing)


def detect_cycles(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Detect cycles in the dependency graph using DFS."""
    cycles: List[List[str]] = []
    temp: Set[str] = set()
    perm: Set[str] = set()
    stack: list[str] = []

    def visit(n: str):
        if n in perm:
            return
        if n in temp:
            # cycle found
            if n in stack:
                i = stack.index(n)
                cycles.append(stack[i:] + [n])
            return
        temp.add(n)
        stack.append(n)
        for m in graph.get(n, ()): visit(m)
        stack.pop()
        temp.remove(n)
        perm.add(n)

    for node in graph.keys():
        if node not in perm:
            visit(node)
    return cycles
```


## 9. Collecting Identifiers with Wildcards

**Important:** An identifier containing a wildcard (`*`) is a **pattern for matching** and may not serve as a canonical identifier for a type or instance.

A single wildcard (`*`) character can be used to find all identifiers matching a given prefix. The wildcard is a greedy operator that matches any sequence of characters after it, including the `~` chain separator.

**Rules for using wildcards:**
1. The wildcard (`*`) must be used only **once**.
2. The wildcard must appear at the **end** of the pattern.
3. The wildcard must not be used in combination with an attribute selector (`@`) or query (`[]`).
4. The pattern must start at the beginning of a valid segment. For example, `gts.x.llm.chat.msg*` is invalid if `msg` is not a complete segment. `gts.x.llm.chat.message.v*` is valid because `v` is the start of the version segment.

**Valid Examples:**

Given the following identifiers:
```
gts.x.llm.chat.message.v1.0~
gts.x.llm.chat.message.v1.0~x.llm.system_message.v1.0~
gts.x.llm.chat.message.v1.0~x.llm.user_message.v1.1~
gts.x.llm.chat.message.v1.1~
```

- **Pattern:** `gts.x.llm.chat.message.v1.0~*` - Find all derived types (schemas) down the chain
  - **Result:** `gts.x.llm.chat.message.v1.0~x.llm.system_message.v1.0~`, `gts.x.llm.chat.message.v1.0~x.llm.user_message.v1.1~`

- **Pattern:** `gts.x.llm.chat.message.v*` - Find all schemas versions and their derived schemas
  - **Result:** All four identifiers listed above.

**Invalid Examples:**
- `gts.x.llm.chat.msg*` - Invalid if `msg` is not a complete segment.
- `gts.x.llm.chat.message.v*~*` - Multiple wildcards are used.

```python
def wildcard_match(pattern: str, candidate: str) -> bool:
    """
    Matches a candidate identifier against a greedy, end-of-string wildcard pattern.

    Args:
        pattern: The wildcard pattern (e.g., 'gts.x.llm.chat.message.v*').
        candidate: The GTS identifier to check.

    Returns:
        True if the candidate matches the pattern.
    """
    if '*' not in pattern:
        return pattern == candidate

    if pattern.count('*') > 1:
        # Rule: Wildcard must be used only once.
        return False

    if not pattern.endswith('*'):
        # Rule: Wildcard must be at the end.
        return False

    prefix = pattern[:-1]
    return candidate.startswith(prefix)
```


## 10. JSON and JSON Schema Conventions

It is advisable to include instance GTS identifiers in a top-level field, such as `gtsId`. However, the choice of the specific field name is left to the discretion of the implementation and can vary from service to service.

**Example #1**: **instance definition** of an object instance (event topic) that has a `gtsId` field that encodes the object type (`gts.x.core.events.topic.v1~`) and identifies the object itself (`x.core.idp.events.v1`). In the example below it makes no sense to add an additional `id` field because the `gtsId` is already unique and there are no other event topics with the given id in the system:

```json
{
  "gtsId": "gts.x.core.events.topic.v1~x.core.idp.events.v1",
  "description": "User-related events (creation, profile changes, etc.)",
  "retention": "P30D",
  "ordering": "by-partition-key",
}
```

**Example #2**: **instance definition** of an object that has a `gtsId` field that encodes the object type, but also its own integer identifier of the object:

```json
[{
    "gtsId": "gts.x.core.events.event.v1~x.core.idp.events.v1~",
    "id": "123",
    "payload": { "foo": "123", "bar": 42 }
},
{
    "gtsId": "gts.x.core.events.event.v1~x.core.idp.events.v1~",
    "id": "125",
    "payload": { "foo": "xyz", "bar": 123 }
}]
```

**Example #3**: **schema definition** of an event type with the `$id` field equal to the type identifier (ending with `~`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gts.x.core.events.event.v1~",
  "type": "object",
  "properties": {
    "gtsId": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "payload": { "type": "object" }
  },
  "required": ["gtsId", "payload"]
}
```


## 11. Notes and Best Practices

- Prefer chains where the base system type is first, followed by vendor-specific refinements, and finally the instance.
- Favor additive changes in MINOR versions. Use a new MAJOR for breaking changes.
- Keep types small and cohesive; use `namespace` to group related types within a package.


## 12. Registered Vendors

The GTS specification does not require vendors to publish their types publicly, but we encourage them to submit their vendor codes to prevent future conflicts.

Currently registered vendors:

| Vendor | Description       |
|--------|-------------------|
| x      | example vendor    |
