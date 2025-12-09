# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-12-09

### Added
- **Comprehensive E2E Test Suite**: 697 E2E tests covering all 75 medical calculators
  - 77 test files in `tests/e2e/` directory
  - One test file per calculator with multiple clinical scenarios
  - Tests cover normal cases, edge cases, and error handling
  - Full coverage of parameter validation

### Changed
- **Test Count**: 1639 total tests (was ~940)
  - E2E tests: 697 (new)
  - Unit tests: 940 (existing)
- **Test Coverage**: Comprehensive REST API endpoint testing

### Fixed
- Multiple E2E test parameter fixes to match actual calculator implementations:
  - `tbsa`: Corrected body region parameters (chest, abdomen, thigh vs anterior_trunk)
  - `timi_stemi`: Fixed parameter names and types (age_years, killip_class, booleans)
  - `news2_score`: Fixed consciousness AVPU values ("A", "C" vs "alert", "confusion")
  - `transfusion_calc`: Corrected assertion for mL output
  - And 20+ other calculators with parameter/assertion fixes

## [1.0.0] - 2025-12-03

### Added
- **75 Medical Calculators** across 12 specialties
- **MCP Server** with FastMCP SDK integration
- **REST API** with Starlette/Uvicorn
- **Docker Support** with docker-compose.yml and HTTPS configuration
- **Security Features**: Optional rate limiting and API key authentication
- **Tool Discovery**: Two-level key system (Low/High Level) for AI tool selection
- **DDD Architecture**: Clean onion architecture with domain-driven design

### Specialties Covered
- Anesthesiology/Preoperative (ASA-PS, Mallampati, STOP-BANG, Aldrete, etc.)
- Critical Care/ICU (APACHE II, SOFA, qSOFA, SAPS II, etc.)
- Pediatrics (Pediatric GCS, PEWS, PIM3, APGAR, etc.)
- Nephrology (eGFR-CKD-EPI, Cockcroft-Gault, KDIGO-AKI, etc.)
- Pulmonology (A-a Gradient, CURB-65, PSI/PORT, ROX Index, etc.)
- Cardiology (CHA₂DS₂-VASc, HAS-BLED, HEART Score, TIMI, etc.)
- Hematology (4Ts HIT, PLASMIC, DIC Score, Transfusion Calc)
- Emergency Medicine (Wells DVT/PE, Canadian C-Spine, etc.)
- Hepatology (Child-Pugh, MELD, MELD-Na, etc.)
- Acid-Base/Metabolic (Anion Gap, Osmolar Gap, Winters Formula, etc.)
- Neurology (GCS, NIHSS, Hunt & Hess, Fisher Grade, ICH Score)
- Trauma/Surgery (ISS, TBSA, Parkland Formula, MABL)

### Technical Features
- 940 unit tests with 88% code coverage
- Type-safe Python with dataclass entities
- Evidence-based formulas with paper citations (Vancouver style)
- Bilingual documentation (English/Chinese)

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.1.0 | 2025-12-09 | 697 E2E tests, comprehensive API testing |
| 1.0.0 | 2025-12-03 | Initial release, 75 calculators |

---

[Unreleased]: https://github.com/u9401066/medical-calc-mcp/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/u9401066/medical-calc-mcp/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/u9401066/medical-calc-mcp/releases/tag/v1.0.0
