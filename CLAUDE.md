# CLAUDE.md — Products.MeetingCharleroi

## What is this project?

Products.MeetingCharleroi is a **PloneMeeting extension** that customizes meeting management for the **City of Charleroi** (Belgium). It extends Products.MeetingCommunes with Charleroi-specific workflows, financial advice handling, police zone integration, and document generation overrides for both the College (executive) and Council (legislative body).

It does **not** define its own content types — it customizes Products.PloneMeeting and Products.MeetingCommunes objects through **Zope adapters**, **event handlers**, and **GenericSetup profiles**.

Part of the **iMio** ecosystem, commercially known as **iA.Delib**.

### Inheritance chain

```
Products.PloneMeeting          (core framework)
  └─ Products.MeetingCommunes  (Belgian municipalities base)
       └─ Products.MeetingCharleroi  (this package — Charleroi-specific)
```

## Tech stack

Same as Products.PloneMeeting:

- **Python 2.7** on **Plone 4.3** (Zope 2)
- Build system: **zc.buildout** (extends `buildout.pm`)
- Document generation: **appy** (ODT/POD templates)
- Search/dashboard: **eea.facetednavigation** + `collective.eeafaceted.dashboard`
- CI: GitHub Actions (`.github/workflows/`)

Dependencies: `Products.MeetingCommunes`, `Products.PloneMeeting`, `Products.CMFPlone`, `Pillow`

## Repository layout

```
src/Products/MeetingCharleroi/
  config.py               # Constants: validation levels, finance groups, legal texts, advice categories
  interfaces.py           # Workflow interfaces, browser layer (IMeetingCharleroiLayer)
  adapters.py             # Core: Custom* adapters + workflow adapters (~1000 lines)
  meeting.py              # Dexterity schema extensions (assembly_police, assembly_privacy_secret_absents)
  utils.py                # finance_group_uid() helper
  vocabularies.py         # Advice category vocabularies (14 finance + 9 motivation categories)
  events.py               # Event handlers (finance advice transitions, item duplication)
  indexes.py              # financesAdviceCategory catalog indexer
  setuphandlers.py        # GenericSetup import handlers
  testing.py              # Test layers (MCH_TESTING_PROFILE_FUNCTIONAL, etc.)
  browser/
    overrides.py          # Document generation helpers (MCHItem/MeetingDocumentGenerationHelperView)
    configure.zcml        # Browser view registrations on IMeetingCharleroiLayer
  model/
    pm_updates.py         # Schema extensions (bourgmestreObservations, assemblyPolice, etc.)
  migrations/             # Upgrade steps (migrate_to_4_1, migrate_to_4200, migrate_to_4201)
  profiles/
    default/              # Base profile (version 4201, depends on MeetingCommunes:financesadvice)
    testing/              # Test configuration with sample data
    zcharleroi/           # Production profile with real city data
  skins/
    meetingcharleroi_templates/  # TAL page template overrides (item view/edit, meeting edit)
  tests/                  # ~47 test modules
  Extensions/             # Legacy Zope External Methods
```

## Architecture: adapter pattern

All customization goes through Zope adapters registered in `configure.zcml`. No PloneMeeting code is patched.

**Model adapters** (in `adapters.py`):
- `CustomCharleroiMeeting` → `IMeetingCustom` — assembly fields (police, secret absents), item sorting
- `CustomCharleroiMeetingItem` → `IMeetingItemCustom` — late item detection, finance advice delays, duplication logic
- `CustomCharleroiMeetingConfig` → `IMeetingConfigCustom` — inserting methods, default categories
- `CustomCharleroiToolPloneMeeting` → `IToolPloneMeetingCustom` — police group discovery

**Workflow adapters** (8 classes, implement custom transitions/guards):
- `MeetingCharleroiCollege/CouncilWorkflowActions/Conditions` (for `IMeeting`)
- `MeetingItemCharleroiCollege/CouncilWorkflowActions/Conditions` (for `IMeetingItem`)

All workflow adapters inherit from MeetingCommunes base classes.

## Key Charleroi-specific features

**Dual-track meetings** — College (4-stage item validation: creators → serviceheads → prereviewers → reviewers) and Council (3-stage: creators → prereviewers → reviewers), configured via `CHARLEROI_COLLEGE/COUNCIL_ITEM_WF_VALIDATION_LEVELS` in `config.py`.

**Financial advice** — Custom `meetingadvicefinances` advice type with dedicated workflow (`dirfin` group). Auto-validates items on positive finance advice, sends back on negative. Finance advice categories and motivations defined in `vocabularies.py`.

**Police zone integration** — Groups prefixed `zone-de-police` get special treatment in assembly fields and document generation.

**College → Council duplication** — When items are sent from College to Council, `onItemDuplicatedToOtherMC` auto-sets categories, preserves poll type, and presents to the next meeting.

## Building & running

From the buildout root (`pm42_dev/`):

```bash
bin/buildout              # Build/install
bin/instance1 fg          # Run Plone in foreground
```

## Running tests

From the buildout root (`pm42_dev/`):

```bash
bin/testcharleroi                                      # All MeetingCharleroi tests
bin/testcharleroi -t testCustomMeetingItem             # Single test module
bin/testcharleroi -t testCustomMeetingItem.test_method # Single test method
```

Some tests require LibreOffice for document generation (`OO_SERVER=localhost OO_PORT=2002`).

### Test architecture

- Base class: `MeetingCharleroiTestCase` (extends `MeetingCommunesTestCase` + `MeetingCharleroiTestingHelpers`)
- Layer: `MCH_TESTING_PROFILE_FUNCTIONAL`
- Test profile: `Products.MeetingCharleroi:testing`
- Meeting configs in tests: `meeting-config-college`, `meeting-config-council`
- Ignored test files: `test_robot.py`, `testPerformances.py`, `testVotes.py`

Test modules follow PloneMeeting's pattern — most inherit from MeetingCommunes test classes and override with Charleroi-specific behavior.

## Linting

From the buildout root (`pm42_dev/`):

```bash
bin/code-analysis                   # All checks
bin/code-analysis-flake8            # PEP8
bin/code-analysis-isort             # Import sorting
```

## Code style & conventions

Follows Products.PloneMeeting conventions:

- **Encoding header**: `# -*- coding: utf-8 -*-` on every `.py` file
- **License header**: GPL block at top of every file
- **Imports**: single-line, alphabetically sorted (`isort` with `force_single_line = True`)
- **Line length**: 200 characters max
- **Naming**: `PascalCase` classes, `snake_case` functions, `UPPER_SNAKE_CASE` constants
- **Security**: `AccessControl.ClassSecurityInfo` declarations on class methods
- **i18n**: `from Products.PloneMeeting.config import PMMessageFactory as _` — wrap translatable strings with `_()`
- **Python 3 compat**: write compatible code where possible (`from __future__ import`, use `six`)

## Commit message style

Short imperative sentence. Examples from recent history:

```
Removed overrides of `MeetingItem._advicePortalTypeForAdviser` and `MeetingItem._adviceTypesForAdviser` as we use `ToolPloneMeeting.get_extra_adviser_infos` now.
Update meetingitem_view.pt
```

## Changelog

Update `CHANGES.rst` for every user-facing change. Format:

```rst
- Description of change with `backtick-quoted` code references.
  [author_shortname]
```

## Migrations

Upgrade steps live in `migrations/migrate_to_*.py`. Each file corresponds to a profile version. The migration base class comes from `Products.PloneMeeting.migrations.Migrator`. Current profile version: **4201**.

## Important constants (config.py)

- `FINANCE_GROUP_ID = 'dirfin'` — Finance Director organization
- `POLICE_GROUP_PREFIX = 'zone-de-police'` — Police zone group prefix
- `COUNCIL_SPECIAL_CATEGORIES` — Categories exempt from "late item" rules
- `FINANCE_ADVICE_LEGAL_TEXT_*` — Legal texts for financial opinions (French)
- Monkeypatches `PMconfig.ADVICE_STATES_ALIVE` and `PMconfig.EXTRA_GROUP_SUFFIXES`
