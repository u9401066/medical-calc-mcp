from typing import Any

from src.shared.formula_provenance import ALLOWED_FORMULA_SOURCE_TYPES, validate_formula_provenance_manifest, validate_reference_metadata


def test_formula_provenance_manifest_covers_full_registry(registry: Any) -> None:
    tool_ids = set(registry.list_all_ids())

    assert validate_formula_provenance_manifest(tool_ids) == []


def test_all_calculators_have_identifier_backed_references(registry: Any) -> None:
    for metadata in registry.list_all():
        assert metadata.formula_source_type in ALLOWED_FORMULA_SOURCE_TYPES
        assert len(metadata.references) >= 1, metadata.tool_id
        assert any(ref.pmid or ref.doi for ref in metadata.references), metadata.tool_id


def test_all_reference_metadata_fields_are_well_formed(registry: Any) -> None:
    issues: list[str] = []

    for metadata in registry.list_all():
        for index, reference in enumerate(metadata.references, start=1):
            issues.extend(validate_reference_metadata(reference, context=f"{metadata.tool_id} reference #{index}"))

    assert issues == []
