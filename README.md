## Global Type System (GTS) Specification

This document defines GTS — a simple, human-readable, globally unique identifier and referencing system for data type definitions (e.g., JSON Schemas) and data instances (e.g., JSON objects). It is specification-first, language-agnostic, and intentionally minimal, with primary focus on JSON and JSON Schema.


### Table of Contents

- [Global Type System (GTS) Specification](#global-type-system-gts-specification)
- [1. Motivation](#1-motivation)
- [2. Identifier Format](#2-identifier-format)
  - [2.1 Canonical form](#21-canonical-form)
  - [2.2 Chained identifiers](#22-chained-identifiers)
  - [2.3 Formal Grammar (EBNF)](#23-formal-grammar-ebnf)
- [3. Semantics and Capabilities](#3-semantics-and-capabilities)
  - [3.1 JSON and JSON Schema examples](#31-json-and-json-schema-examples)
  - [3.2 Minor Version compatibility](#32-minor-version-compatibility)
  - [3.3 Access control with wildcards](#33-access-control-with-wildcards)
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
- [9. Collecting Identifiers with Wildcards](#9-collecting-identifiers-with-wildcards)
- [10. JSON and JSON Schema Conventions](#10-json-and-json-schema-conventions)
- [11. Notes and Best Practices](#11-notes-and-best-practices)
- [12. Registered Vendors](#12-registered-vendors)


### Document Version

| Document Version | Status                              |
|------------------|-------------------------------------|
| 0.1              | Initial Draft, Request for Comments |



### 1. Motivation

- There is a practical need to identify both data type schemas and data instances globally in a unique, human-readable way.
- Such identifiers should support versioning, inheritance/extension, validation, and coarse-grained access control.
- JSON and JSON Schema are the first-class target formats in this specification, however it is compatible with RAML, OpenAPI, and practically any other data type modelling specifications as GTS identifiers are just strings

### 2. Identifier Format

GTS identifiers name either a schema (type) or an instance (object). A single GTS identifier may also chain multiple identifiers to express inheritance/compatibility and an instance’s conformance lineage.

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

Use `_` as a placeholder when a slot is not applicable:

- `gts.x.idp.users._.user.v1.0~`
- `gts.x.mq.messages._.contact_created.v1`

Segments must be lowercase ASCII letters, digits, and underscores; they must start with a letter or underscore: `[a-z_][a-z0-9_]*`.

Versioning uses semantic versioning constrained to major and optional minor: `v<MAJOR>[.<MINOR>]` where `<MAJOR>` and `<MINOR>` are non-negative integers, for example:
- `gts.x.core.events.event.v1~` - defines a base event type in the system
- `gts.x.core.events.event.v1.2~` - defines a specific edition v1.2 of the base event type


#### 2.2 Chained identifiers

Multiple GTS identifiers can be chained with `~` to express derivation and conformance. The chain follows **left-to-right inheritance** semantics:

- Pattern: `gts.<gtx1>~<gtx2>~<gtx3>`
- Where **GTX** (Global Type Extension) stands for a single type segment:
  - `<gtx1>` is a **base type** (schema ID ending with `~`)
  - `<gtx2>` is a **derived/refined type** (schema ID ending with `~`) that extends `<gtx1>` with additional constraints or implementation-specific details. It MUST be compatible with `<gtx1>`.
  - `<gtx3>` is an **instance identifier** (no trailing `~`) that conforms to `<gtx2>`. By transitivity, it also conforms to `<gtx1>`.

**Important:** Each type in the chain inherits from its immediate predecessor (left neighbor) and MUST maintain compatibility.

**Chaining rules:**
1. All elements except the rightmost MUST be type identifiers (conceptually ending with `~`).
2. The rightmost element determines the identifier's nature:
   - Ends with `~` → the whole identifier represents a **type/schema**.
   - No trailing `~` → the whole identifier represents an **instance/object**.
3. The `gts.` prefix appears **only once** at the very beginning of the identifier string.
4. Segments after the first are considered relative identifiers and do not repeat the `gts.` prefix. (e.g., `gts.x.some.base.type.v1~vendor.app.some.derived.v1~`).

**Examples with explanations:**

- `gts.x.core.events.event.v1~`
  → Base type only (standalone schema)

- `gts.x.core.events.event.v1~ven.app._.custom_event.v1~`
  → Type `ven.app._.custom_event.v1` derives from base type `gts.x.core.events.event.v1`. Both are schemas (trailing `~`).

- `gts.x.core.events.topic.v1~ven.app._.custom_event_topic.v1.2`
  → Instance `ven.app._.custom_event_topic.v1.2` (no trailing `~`) conforms to type `gts.x.core.events.topic.v1`. The identifier shows the full inheritance chain.

#### 2.3 Formal Grammar (EBNF)

The complete GTS identifier syntax in Extended Backus-Naur Form (EBNF):

```ebnf
(* Top-level identifier *)
gts-identifier = "gts." , gtx-segment , [ chain-suffix ] ;

(* Chain of type extensions *)
chain-suffix   = { "~" , gtx-segment } , [ final-tilde ] ;
final-tilde    = "~" ;  (* present for type IDs, absent for instance IDs *)

(* Single GTX segment *)
gtx-segment    = vendor , "." , package , "." , namespace , "." , type , "." , version ;

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

2. **Chain interpretation**: In a chained identifier `gts.<gtx1>~<gtx2>~<gtx3>`, each `~` acts as a separator. All segments before the final segment MUST be types (conceptually ending with `~`). The final segment determines whether the entire identifier is a type or instance.

3. **Placeholder rule**: Use `_` (underscore) as a segment value when a component (vendor, package, namespace, or type) is not applicable.

4. **Normalization**: GTS identifiers are case-sensitive and must be lowercase. Leading/trailing whitespace is not permitted. Canonical form has no optional spacing.

5. **Reserved prefix**: The `gts.` prefix is mandatory and reserved. Future versions may introduce alternative prefixes but will maintain backward compatibility.


### 3. Semantics and Capabilities

GTS identifiers enable the following operations and use cases:

**Core Operations:**

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

5. **Extensible Type Systems**: Enable platforms where:
   - Base system types are defined by a core vendor
   - Third-party vendors extend base types with additional constraints
   - All validation guarantees are preserved through the inheritance chain
   - Type evolution is tracked explicitly through versioning

#### 3.1 JSON and JSON Schema examples

**Practical scenario:**

Vendor `X` operates an event manager platform. Each event must include a `gtsId` field. The platform processes events as follows:

1. **Schema Resolution**: Parse `gtsId` to extract the rightmost type (e.g., from `gts.x.core.events.event.v1~abc.app._.custom_event.v1~abc.app._.custom_event.v1.2`, extract `abc.app._.custom_event.v1~`)

2. **Validation**: Load the JSON Schema for `gts.x.core.events.event.v1~abc.app._.custom_event.v1~` and validate the event payload

3. **Authorization** (optional, implementation-defined): Check if the producer is authorized to emit events of type `abc.app._.custom_event.v1`

4. **Routing & Auditing**: Use the chain to route events to appropriate handlers and create audit trails per vendor/application

This approach allows vendor `ABC` to define custom event types while maintaining compatibility with the base `gts.x.core.events.event.v1~` schema.

Base event schema (system type) defined by vendor `X`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gts.x.core.events.event.v1~",
  "title": "Base Event",
  "type": "object",
  "properties": {
    "gtsId": { "type": "string", "$comment": "This field serves as the unique identifier for the event schema" },
    "topic_id": { "type": "string" },
    "payload": { "type": "object", "additionalProperties": true }
  },
  "required": ["gtsId", "payload"],
  "additionalProperties": false
}
```

The derived event schema is registered by vendor `ABC` within the `App` application, which is part of vendor `X`'s event manager. Vendor `ABC` enhances the base payload object with a specific schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gts.x.core.events.event.v1~abc.app._.custom_event.v1~",
  "title": "Vendor ABC Custom Event",
  "allOf": [
    { "$ref": "gts.x.core.events.event.v1~" },
    {
      "type": "object",
      "properties": {
        "payload": {
          "type": "object",
          "properties": {
            "id": { "type": "string" },
            "amount": { "type": "number" },
            "currency": { "type": "string" },
            "metadata": { "type": "object", "additionalProperties": true }
          },
          "required": ["id", "amount", "currency"],
          "additionalProperties": false
        }
      },
      "required": ["payload"]
    }
  ]
}
```

Example JSON instance implementing the derived schema — the `gtsId` shows the chain and the instance identifier as the right-most element:

```json
{
  "gtsId": "gts.x.core.events.event.v1~abc.app._.custom_event.v1~abc.app._.custom_event.v1.2",
  "topic_id": "gts.x.core.events.topic.v1.0",
  "payload": {
    "id": "evt-123",
    "amount": 99.95,
    "currency": "USD",
    "metadata": { "campaign": "fall-sale" }
  }
}
```

#### 3.2 Minor Version Compatibility

**Semantic Versioning Rules for GTS:**

MINOR version increments (e.g., v1.2 → v1.3) within the same MAJOR version MUST maintain backward compatibility:

**Allowed changes (backward compatible):**
- Adding new optional properties
- Relaxing constraints (e.g., making a field less restrictive)
- Adding new enum values (with caution)
- Clarifying documentation or examples

**Prohibited changes (breaking):**
- Removing required properties
- Adding new required properties
- Changing property types incompatibly
- Tightening constraints on existing fields
- Removing enum values

**Chain Compatibility:**
- In a chain `gts.A~B~C`, type `B` MUST be compatible with `A`, and type `C` MUST be compatible with `B`
- Compatibility is verified left-to-right: each type must accept all valid instances of its predecessor
- Use MAJOR version increment for any breaking change

**Practical implication:** A consumer expecting v1.2 can safely process objects validated against v1.3 of the same schema.

#### 3.3 Access control with wildcards

See section 9 (Collecting Identifiers with Wildcards) for the wildcard pattern semantics used to collect or authorize groups of identifiers.


### 4. Typical Uses

- API custom payload schema definitions
- Event schema definitions
- Configuration settings schema definitions
- Database schema definitions
- Data warehouse object schema definitions

See some definitions in the [examples folder](./examples/)


### 5. Implementation-defined and Non-goals

This specification intentionally does not enforce several operational or governance choices. It is up to the implementation vendor to define policies and behavior for:

1. Whether a defined type is exported and available for cross-vendor use via APIs or an event bus.
2. Whether a given JSON/JSON Schema definition is mutable or immutable (e.g., handling an incompatible change without changing the minor or major version).
3. How to implement access checks based on the GTS query mini-language.
4. When to introduce a new minor version versus a new major version.
5. GTS identifiers renaming and aliasing

Non-goals reminder: GTS is not an eventing framework, transport, or workflow. It standardizes identifiers and basic validation/casting semantics around JSON and JSON Schema.


### 6. Comparison with other identifiers

- JSONSchema $schema url: While JSONSchema provides a robust framework for defining the structure of JSON data, GTS extends this by offering clear vendor, package and namespace notation and chaining making it easier to track and validate data instances across different systems and versions.
- UUID: Opaque and globally unique. GTS is meaningful to humans and machines; UUIDs can be derived from GTS deterministically when opaque IDs are required.
- Apple UTI: Human-readable, reverse-DNS-like. GTS is similar in readability but adds explicit versioning, vendors/apps support, chaining, and schema/instance distinction suitable for JSON Schema-based validation.
- Amazon ARN: Global and structured, but cloud-service-specific. GTS is vendor-neutral and domain-agnostic, focused on data schemas and instances.


### 7. Parsing and Validation

#### 7.1 Single-segment regex (type or instance)

Single-line variant:

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


### 8. Reference Operators (Python)

The following reference implementations target Python. Other languages can mirror the semantics in dedicated repositories.

> Requirements: `jsonschema>=4`, `uuid` from the standard library.

#### 8.1 Normalize, validate, and parse

```python
import re
from dataclasses import dataclass
from typing import Optional, List

# Absolute first segment: includes the 'gts.' prefix
ABSOLUTE_SEGMENT_PATTERN = re.compile(r"^gts\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.v(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?(~)?$")

# Relative chained segment: no 'gts.' prefix
RELATIVE_SEGMENT_PATTERN = re.compile(r"^([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\.v(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?(~)?$")


@dataclass(frozen=True)
class Gtx:
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


def parse_absolute(segment: str) -> Gtx:
    m = ABSOLUTE_SEGMENT_PATTERN.fullmatch(segment)
    if not m:
        raise ValueError(f"Invalid absolute GTS segment: {segment}")
    vendor, package, namespace, type_, major, minor, is_type = m.groups()
    return Gtx(
        vendor=vendor,
        package=package,
        namespace=namespace,
        type=type_,
        major=int(major),
        minor=int(minor) if minor is not None else None,
        is_type=is_type == "~",
    )


def parse_relative(segment: str) -> Gtx:
    m = RELATIVE_SEGMENT_PATTERN.fullmatch(segment)
    if not m:
        raise ValueError(f"Invalid relative GTS segment: {segment}")
    vendor, package, namespace, type_, major, minor, is_type = m.groups()
    return Gtx(
        vendor=vendor,
        package=package,
        namespace=namespace,
        type=type_,
        major=int(major),
        minor=int(minor) if minor is not None else None,
        is_type=is_type == "~",
    )


def parse_single(segment: str) -> Gtx:
    """
    Parse a single GTS segment (absolute or relative) into structured components.

    Args:
        segment: A GTS segment (e.g., 'gts.x.core.events.event.v1~' or 'x.app._.custom.v1.2')

    Returns:
        Gtx object with parsed vendor, package, namespace, type, version, and type flag

    Raises:
        ValueError: If the segment doesn't match either pattern
    """
    try:
        return parse_absolute(segment)
    except ValueError:
        return parse_relative(segment)


def split_chain(gts_id: str) -> List[Gtx]:
    """
    Parse a GTS identifier (single or chained) into a list of GTX segments.

    The first segment must be absolute (with 'gts.' prefix). Subsequent segments
    are relative (without 'gts.'). All but the last segment MUST be types.

    Args:
        gts_id: Full GTS identifier (e.g., 'gts.x.base.v1~vendor.derived.v1.2')

    Returns:
        List of Gtx objects representing the chain

    Raises:
        ValueError: If the identifier is malformed or violates chaining rules
    """
    raw_parts = gts_id.split("~")
    parts = [p for p in raw_parts if p != ""]
    if not parts:
        raise ValueError("Empty GTS identifier")

    # First segment: absolute
    segments: List[Gtx] = [parse_absolute(parts[0])]

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

#### 8.2 Validate object against schema

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


def rightmost_type_id(chain: List[Gtx]) -> str:
    """
    Extract the rightmost type ID from a GTS chain.

    Rules:
    - If the last segment is a type (ends with ~), return it
    - If the last segment is an instance, return the previous segment (which must be a type)
    - A standalone instance without a chain is invalid

    Args:
        chain: List of parsed GTX segments

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

#### 8.3 Minor version casting (downcast/upcast)

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

#### 8.4 Type compatibility across minor versions

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

#### 8.5 Mapping GTS to UUIDs

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


def _strip_minor(gtx: Gtx) -> Gtx:
    return Gtx(
        vendor=gtx.vendor,
        package=gtx.package,
        namespace=gtx.namespace,
        type=gtx.type,
        major=gtx.major,
        minor=None,
        is_type=gtx.is_type,
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

#### 8.6 GTS Query mini-language

**Purpose:** Enable filtering and querying object collections based on GTS identifiers and attributes.

**Syntax:** `<gts-type-prefix>[ <attribute>="<value>" <attribute>="<value>" ... ]`

**Examples:**
- `gts.x.core.events.event.v1.0` - Match all instances of this type (prefix match)
- `gts.x.core.events.event.v1.0[ topic_id="gts.x.core.events.topic.v1.0" ]` - Match events with specific topic_id
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

#### 8.7 Attribute Selector (`@`)

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


### 9. Collecting Identifiers with Wildcards

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


### 10. JSON and JSON Schema Conventions

It is advisable to include instance GTS identifiers in a top-level field, such as `gtsId`. However, the choice of the specific field name is left to the discretion of the implementation and can vary from service to service. Example:

```json
{
  "gtsId": "gts.x.core.events.event.v1~gts.x.core.events.event.v1~gts.vendorA.app._.custom_event.v1.3",
  "topic_id": "gts.x.core.events.topic.v1.0",
  "payload": { "id": "123", "value": 42 }
}
```

Schemas SHOULD include `$id` equal to the type identifier (ending with `~`). Example schema `$id`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gts.x.core.events.event.v1~",
  "type": "object",
  "properties": {
    "gtsId": { "type": "string" },
    "topic_id": { "type": "string" },
    "payload": { "type": "object" }
  },
  "required": ["gtsId", "payload"]
}
```


### 11. Notes and Best Practices

- Prefer chains where the base system type is first, followed by vendor-specific refinements, and finally the instance.
- Favor additive changes in MINOR versions. Use a new MAJOR for breaking changes.
- Keep types small and cohesive; use `namespace` to group related types within a package.


### 12. Registered Vendors

The GTS specification does not require vendors to publish their types publicly, but we encourage them to submit their vendor codes to prevent future conflicts.

Currently registered vendors:

| Vendor | Description       |
|--------|-------------------|
| x      | example vendor    |
