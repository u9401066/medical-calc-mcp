# Specialty Coverage Gap Analysis

> Generated from the live calculator registry. Do not edit manually.
> Regenerate with `uv run python scripts/generate_specialty_coverage_gap_analysis.py` (v1.6.2).

## Current Status

- Specialty enum total: 76
- Specialties with at least one calculator: 44
- Specialties with no calculators: 32
- Established coverage (>=5 tools): 27
- Developing coverage (3-4 tools): 7
- Thin coverage (1-2 tools): 10
- Current coverage tracks **65/65** guideline-recommended tools across **16** clinical domains.

## Interpretation

- This report measures breadth across specialty labels, not just guideline-recommended tools.
- The guideline program is currently complete, but broad specialty coverage is not.
- Several specialties from older planning notes are now implemented and should no longer be treated as missing.

## Established Coverage

| Specialty | Tool Count | Example Tool IDs |
|-----------|-----------:|------------------|
| Internal Medicine | 83 | 4ts_hit, aa_gradient, abcd2, aims65, anion_gap |
| Critical Care | 72 | 4ts_hit, aa_gradient, acef_ii, aims65, aldrete_score |
| Emergency Medicine | 61 | aa_gradient, abcd2, aims65, anion_gap, apache_ii |
| Anesthesiology | 36 | aa_gradient, acef_ii, aldrete_score, anion_gap, apache_ii |
| Geriatrics | 29 | barthel_index, braden_scale, cfs, charlson_comorbidity_index, cockcroft_gault |
| Surgery | 26 | 4ts_hit, acef_ii, aldrete_score, apfel_ponv, asa_physical_status |
| Neurology | 23 | abcd2, barthel_index, cam_icu, chads2_va, chads2_vasc |
| Family Medicine | 21 | athens_insomnia_scale, audit, audit_c, berlin_questionnaire, cage |
| Psychiatry | 21 | athens_insomnia_scale, audit, audit_c, cage, cam_icu |
| Pulmonology | 21 | aa_gradient, apache_ii, berlin_questionnaire, cpis, curb65 |
| Cardiology | 18 | 4ts_hit, acef_ii, body_surface_area, chads2_va, chads2_vasc |
| Nephrology | 14 | anion_gap, bosniak, charlson_comorbidity_index, ckd_epi_2021, cockcroft_gault |
| Pediatrics | 12 | apgar_score, ballard_score, body_surface_area, centor_score, parkland_formula |
| Oncology | 10 | body_surface_area, charlson_comorbidity_index, corrected_calcium, ecog_performance_status, karnofsky_performance_scale |
| Gastroenterology | 9 | aims65, child_pugh, fib4_index, glasgow_blatchford, lille_model |
| Endocrinology | 8 | cas_graves, corrected_calcium, corrected_sodium, cushingoid_score, findrisc |
| Hematology | 8 | 4ts_hit, caprini_vte, has_bled, mabl, mascc_score |
| Infectious Disease | 8 | centor_score, cockcroft_gault, cpis, curb65, mascc_score |
| Physical Medicine | 7 | barthel_index, braden_scale, frail_scale, katz_adl, lawton_iadl |
| Hepatology | 6 | child_pugh, corrected_calcium, fib4_index, lille_model, maddrey_df |
| Dermatology | 5 | bsa_dermatology, dlqi, pasi, salt_score, scorad |
| Nursing | 5 | braden_scale, katz_adl, lawton_iadl, mst, pews |
| Nutrition Medicine | 5 | conut, gnri, mst, sarc_f, scoff |
| Rheumatology | 5 | bsa_dermatology, das28, dlqi, frax, pasi |
| Sleep Medicine | 5 | athens_insomnia_scale, berlin_questionnaire, epworth_sleepiness_scale, insomnia_severity_index, no_sas_score |
| Trauma | 5 | iss, pediatric_gcs, rts, tbsa, triss |
| Urology | 5 | bosniak, iciq_sf, ipss, pop_q, stone_score |

## Developing Coverage

| Specialty | Tool Count | Tool IDs |
|-----------|-----------:|----------|
| Gynecology | 4 | epds, iciq_sf, pop_q, sflt_plgf_ratio |
| Neurosurgery | 4 | fisher_grade, four_score, hunt_hess, ich_score |
| Obstetrics | 4 | apgar_score, ballard_score, bishop_score, shock_index |
| Addiction Medicine | 3 | audit, audit_c, cage |
| Cardiac Anesthesia | 3 | euroscore_ii, mabl, rcri |
| Orthopedics | 3 | caprini_vte, frax, tug |
| Pediatric Anesthesia | 3 | mabl, pediatric_dosing, transfusion_calc |

## Thin Coverage

| Specialty | Tool Count | Tool IDs |
|-----------|-----------:|----------|
| Ent | 1 | mallampati_score |
| Obstetric Anesthesia | 1 | bishop_score |
| Ophthalmology | 1 | cas_graves |
| Pain Medicine | 1 | mme_calculator |
| Allergy Immunology | 2 | dlqi, scorad |
| Neonatology | 2 | apgar_score, ballard_score |
| Palliative Care | 2 | palliative_performance_scale, palliative_prognostic_index |
| Pediatric Critical Care | 2 | pediatric_sofa, pim3 |
| Radiology | 2 | bosniak, fisher_grade |
| Toxicology | 2 | osmolar_gap, serum_osmolality |

## Uncovered Specialties

These specialty enums currently have zero calculators mapped to them and are the primary candidates for future PubMed/guideline expansion.

| Specialty | Coverage Bucket |
|-----------|-----------------|
| Burn Care | uncovered |
| Cardiac Critical Care | uncovered |
| Cardiac Surgery | uncovered |
| Colorectal Surgery | uncovered |
| Dentistry | uncovered |
| Echocardiography | uncovered |
| Electrophysiology | uncovered |
| Gynecologic Oncology | uncovered |
| Heart Failure | uncovered |
| Interventional Cardiology | uncovered |
| Interventional Radiology | uncovered |
| Maternal Fetal Medicine | uncovered |
| Neuro Critical Care | uncovered |
| Neuroanesthesia | uncovered |
| Nuclear Medicine | uncovered |
| Obstetrics Gynecology | uncovered |
| Occupational Medicine | uncovered |
| Oral Surgery | uncovered |
| Other | uncovered |
| Pathology | uncovered |
| Pediatric Surgery | uncovered |
| Plastic Surgery | uncovered |
| Preventive Medicine | uncovered |
| Public Health | uncovered |
| Regional Anesthesia | uncovered |
| Reproductive Medicine | uncovered |
| Sports Medicine | uncovered |
| Surgical Critical Care | uncovered |
| Thoracic Surgery | uncovered |
| Transplant Surgery | uncovered |
| Vascular Surgery | uncovered |
| Wound Care | uncovered |

## Recommended Next Pass

1. Prioritize uncovered primary specialties before subspecialties that mostly re-label existing internal medicine or surgery tools.
2. For each target specialty, confirm a stable, literature-backed score with clear clinical adoption before implementation.
3. Add PubMed/guideline evidence, tests, MCP handler wiring, and provenance metadata together as one unit.
4. Regenerate this report after each batch so the backlog stays live instead of drifting.

## Priority Research Queue

The following uncovered specialties are likely higher-yield than niche subspecialties and should be researched first:

- Palliative Care
- Dentistry
- Public Health
- Preventive Medicine
- Sleep Medicine
- Pathology
- Nuclear Medicine
- Cardiac Surgery
- Thoracic Surgery
- Vascular Surgery
