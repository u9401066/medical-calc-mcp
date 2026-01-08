# Psychiatry Calculators

Validated screening and assessment tools for mental health conditions.

!!! warning "Clinical Use"
    These tools are for screening purposes. Clinical diagnosis requires comprehensive psychiatric evaluation.

## Depression

### PHQ-9 (Patient Health Questionnaire-9)

Depression screening and severity assessment.

**Tool ID**: `phq9`

**9 Questions** rated 0-3 (Not at all → Nearly every day):
1. Little interest or pleasure
2. Feeling down, depressed, hopeless
3. Sleep problems
4. Feeling tired
5. Appetite changes
6. Feeling bad about yourself
7. Trouble concentrating
8. Moving/speaking slowly or restlessly
9. Thoughts of self-harm

**Severity**:

| Score | Severity | Action |
|-------|----------|--------|
| 0-4 | Minimal | Monitor |
| 5-9 | Mild | Watchful waiting |
| 10-14 | Moderate | Treatment plan |
| 15-19 | Moderately severe | Active treatment |
| 20-27 | Severe | Immediate intervention |

!!! danger "Question 9"
    Always assess suicide risk if Q9 > 0

---

### HAM-D (Hamilton Depression Rating Scale)

Clinician-administered depression severity assessment.

**Tool ID**: `hamd`

**17-item version** assessing:
- Depressed mood
- Guilt
- Suicide
- Insomnia (early, middle, late)
- Work and activities
- Retardation
- Agitation
- Anxiety (psychic, somatic)
- Somatic symptoms
- Hypochondriasis
- Weight loss
- Insight

---

### MADRS (Montgomery-Åsberg Depression Rating Scale)

**Tool ID**: `madrs`

10-item scale particularly sensitive to treatment changes.

---

## Anxiety

### GAD-7 (Generalized Anxiety Disorder-7)

**Tool ID**: `gad7`

**7 Questions** rated 0-3:
1. Feeling nervous, anxious
2. Not being able to stop worrying
3. Worrying too much
4. Trouble relaxing
5. Being restless
6. Easily annoyed
7. Feeling afraid

| Score | Severity |
|-------|----------|
| 0-4 | Minimal |
| 5-9 | Mild |
| 10-14 | Moderate |
| 15-21 | Severe |

---

### HAM-A (Hamilton Anxiety Rating Scale)

**Tool ID**: `hama`

14-item clinician-administered anxiety assessment.

---

## Trauma & PTSD

### PCL-5 (PTSD Checklist for DSM-5)

**Tool ID**: `pcl5`

20-item self-report for PTSD symptoms.

**Clusters**:
- Intrusion (items 1-5)
- Avoidance (items 6-7)
- Negative cognition/mood (items 8-14)
- Arousal/reactivity (items 15-20)

**Cutoff**: Score ≥31-33 suggests probable PTSD

---

### CAPS-5 (Clinician-Administered PTSD Scale)

**Tool ID**: `caps5`

Gold standard structured interview for PTSD diagnosis.

**30 Items** assessing:
- Criterion A: Trauma exposure
- Criterion B: Intrusion symptoms
- Criterion C: Avoidance
- Criterion D: Negative alterations
- Criterion E: Arousal/reactivity
- Criterion F: Duration
- Criterion G: Functional impairment
