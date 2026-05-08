---
title: "Monorepo Detection"
description: "Per-ecosystem workspace declaration parsing rules and detection algorithm for /audit Phase 1.5. Defines parsing rules for 14 ecosystems, heuristic signals, detection algorithm pseudocode, type consistency rules, and cap policy."
version: 1.0.0
applies_to: "audit-score-v4.1.0"
---

# Monorepo Detection

This document defines deterministic monorepo classification for `/audit` Phase 1.5. Detection logic here is deterministic specification — `/audit` MUST follow these rules at runtime; LLM-runtime heuristic judgment for monorepo classification is prohibited (reproducibility + falsifiability).

## §0. Scope

**Covers**: per-ecosystem workspace declaration parsing rules (14 ecosystems), heuristic directory pattern signals, the detection algorithm pseudocode (Phase A through Phase E), type consistency rules between `project_structure.type` and `monorepo_detection.detected`, and the cap policy (display / scored / unscored counters / total filtered) applied to `package_roots[]` and `package_roots_for_scoring[]`.

**Does NOT cover**: detection authority — `/audit` Phase 1.5 invokes this document; the SKILL.md remains the runtime caller. Per-package scoring procedure — see `per-package-scoring.md`. Rollup output rendering — see `per-package-rollup.md`. PHP/Composer monorepo detection is deferred (`composer.json repositories.path` parsing is not part of this version).

## §1. Per-Ecosystem Workspace Declaration Parsing

For each ecosystem, the parser extracts a list of package root paths (relative to project root) from a formal workspace declaration field. Parser failures (malformed YAML/TOML/XML, missing field) degrade gracefully: emit a `parse_error` evidence entry and fall back to §2 heuristic signals. **Zero-root declaration fallback**: when a workspace declaration parses successfully but resolves to zero roots, append a `workspace_declaration_resolved_zero_roots` note (per-ecosystem subsections MAY override with a more specific code, e.g., `umbrella_apps_path_empty` for Elixir; sections naming an override apply that override exclusively). **Single-level resolution only**: parsers MUST NOT recursively follow nested workspace declarations (e.g., `<parent>` chains in `pom.xml`, transitive `apps_path` chains). Deeper nesting is left to the existing CLAUDE.md disclosure walk.

### §1.1 Node — `package.json workspaces`, `pnpm-workspace.yaml`

**Source**: `package.json` (root) `workspaces` field, OR `pnpm-workspace.yaml` (sibling at root). Two valid `workspaces` shapes — array (`["packages/*", "apps/*"]`) or object (`{ "packages": ["packages/*"] }`). Yarn workspaces (v1, Berry) use the same `package.json` field. Glob: `*` matches a single path segment, `**` zero or more; resolution is filesystem-real; negation patterns (`!packages/internal/*`) are respected and subtracted. If the declaration resolves to zero existing directories, emit `detected=true`, `resolved_roots=[]`, and `workspace_declaration_resolved_zero_roots`. If both sources are present, emit both as separate evidence entries with `package_roots[]` deduplicated as the union.

### §1.2 Rust — `Cargo.toml [workspace] members`

**Source**: `Cargo.toml` at project root with `[workspace]` table. Extract `members` array. Glob `*` supported (Cargo native, single-segment). `[workspace.exclude]` is respected and subtracted. Virtual workspace (`[workspace]` without top-level `[package]`) sets `detected=true`; project root itself is NOT a package root. `[workspace] resolver` and other meta fields are ignored.

### §1.3 Go — `go.work` (workspace), `go.mod` (per-package)

**Manifest role split**: `go.mod` identifies a Go package root (one per module). `go.work` is a workspace-only declaration file at project root. Parse `use ( ... )` block; only relative entries become `package_roots[]`. Single-line `use ./module` form supported. Paths are literal (no glob); `replace` directives are ignored. If `go.work` is absent but multiple `go.mod` files exist in subdirectories, emit no workspace evidence — defer to §2 heuristic signals.

### §1.4 Python — `pyproject.toml` workspace, legacy `setup.py`/`setup.cfg`

**Source**: `pyproject.toml` workspace tables, or fallback to `setup.py`/`setup.cfg` (single-package indicator only). Recognized tables: `[tool.uv.workspace] members` (glob; `exclude` respected), `[tool.hatch.workspace] members` (glob), `[tool.rye.workspace] members` (glob; if `members` absent, Rye treats discovered subfolder Python projects as workspace members). With no workspace table, `pyproject.toml` is single-package. If both `pyproject.toml` (with workspace) and `setup.py` are present, prefer `pyproject.toml`.

### §1.5 Java/Maven — `pom.xml <modules>`

**Source**: `pom.xml` at project root, typically with `<packaging>pom</packaging>`. Extract `<modules><module>...</module></modules>` values; each is a relative path to a child directory containing its own `pom.xml`. Profile-conditional `<modules>` are NOT evaluated (parse base only). Property-substituted module names emit raw value; resolution is filesystem-real (skip nonexistent directories).

### §1.6 Java/Gradle — `settings.gradle[.kts] include`

**Source**: `settings.gradle` or `settings.gradle.kts` at project root. Extract `include 'subproject'` (Groovy) or `include("subproject")` (Kotlin); multi-arg form supported. Subproject names may use `:` as path separator (`:lib:core` → `lib/core`). `includeBuild('other-project')` is emitted as `composite_build` evidence and is NOT in `package_roots[]`. Programmatic enumeration is SKIPPED with a `parse_error` entry noting manual review required.

### §1.7 .NET — `*.sln Project()` entries

**Source**: `*.sln` at project root. Parse `Project("{type-guid}") = "Name", "Path/Project.csproj", "{project-guid}"` lines; path is relative to the solution file. Solution folder entries (type-guid `2150E333-8FDC-42A3-9474-1A3956D46DE8`) SKIPPED. Multiple `*.sln` at root → pick lexicographically first, emit warning evidence. No `*.sln` but multiple `*.csproj`/`*.fsproj` → each parent dir is a low-confidence candidate (defer to §2).

### §1.8 Elixir — `mix.exs` umbrella + `apps/`

**Source**: `mix.exs` at project root. Parse Mix project tuple for `apps_path: "apps"` (or another path). When present, the project is an umbrella — enumerate immediate subdirectories of `apps_path/` containing their own `mix.exs`. Absent → not an umbrella. Set but empty/missing → emit `detected=true`, `resolved_roots=[]`, with note code `umbrella_apps_path_empty` (Elixir-specific override of the generic zero-root code). Custom `apps_path` respected literally.

### §1.9 Swift — `Package.swift`, nested-package convention

**Source**: `Package.swift` at project root. SwiftPM's `targets:` array declares multiple targets, but **multiple targets in a single `Package.swift` are NOT a monorepo** — single-package, multi-target layout. Emit `detected=true` only when nested `Package.swift` files exist below project root (`<sub>/Package.swift` for one or more `<sub>`); nested manifests are a high-confidence multi-package signal; `package_roots[]` are the parent directories of nested manifests.

### §1.10 Ruby — convention-only

**Source**: `Gemfile` (root) + `*.gemspec` (per-gem directory). Ruby has no native workspace declaration syntax — detection is convention-only: multiple `*.gemspec` in distinct subdirectories AND a root `Gemfile` referencing them via `gemspec path: "..."` lines → monorepo-by-convention. Emit `evidence` of type `convention` (NOT `workspace_declaration`) to flag lower confidence; `resolved_roots` are the parent directories of subdirectory `*.gemspec` referenced by root `Gemfile gemspec path:` entries; §5 Evidence Cap metadata applies.

### §1.11 C/C++ — CMake, Bazel, Conan, Meson

**Sources**: CMake (`CMakeLists.txt` root + `add_subdirectory(name)`), Bazel (`WORKSPACE` or `MODULE.bazel` root + `BUILD.bazel`/`BUILD` subdirs), Meson (`meson.build` root + `subdir('name')`), Conan (`conanfile.txt`/`conanfile.py` root + per-package). CMake `add_subdirectory(name)` — each `name` is a package root relative to its `CMakeLists.txt`; parser stops after first level (single-level resolution); deeper subdirs still discoverable via the CLAUDE.md disclosure walk. Bazel — enumerate all dirs with `BUILD.bazel`/`BUILD` (subject to §5 cap policy — Bazel can have hundreds). Meson `subdir('name')` analogous to CMake. `add_subdirectory(name EXCLUDE_FROM_ALL)` still counts. Conditional inclusion NOT evaluated.

### §1.12 Dart/Flutter — `melos.yaml`

**Source**: `melos.yaml` at project root with `packages:` array (glob `*` supported). Present without `packages:` → malformed, emit `parse_error` and fall back to §2. Single `pubspec.yaml` at root with no `melos.yaml` → single-package.

### §1.13 Erlang — `rebar.config` + `apps/`

**Source**: `rebar.config` at project root. Enumerate `apps/` subdirectories with their own `rebar.config` or `<name>.app.src`. Custom directory respected via `{project_app_dirs, ["lib/*"]}`. No `apps/` and no `project_app_dirs` → single-app. `project_app_dirs` glob entries are glob-expanded and filtered to directories with `rebar.config` or `*.app.src`.

### §1.14 Haskell — `cabal.project`, `stack.yaml`

**Sources**: `cabal.project` (`packages:` field with paths/globs; split on whitespace, glob-expand) and `stack.yaml` (`packages:` array; YAML array, glob-expand). Single root `*.cabal` with no `cabal.project` → single-package. Both files present → emit both as evidence with `package_roots[]` as the union.

## §2. Heuristic Signals

When workspace declaration parsing returns zero workspace evidence but the project structure suggests monorepo layout, heuristic directory pattern matching may tip the classification. Heuristic signals also supplement workspace declarations.

| Pattern | Confidence | Typical Ecosystem |
|---|---|---|
| `packages/<name>/` | High | Node (yarn workspaces), Dart (melos) |
| `apps/<name>/` | High | Node, Elixir umbrella, Nx |
| `crates/<name>/` | High | Rust |
| `services/<name>/` | Medium | Node (microservices), Go |
| `libs/<name>/` | Medium | Generic |
| `modules/<name>/` | Low | Generic |
| `subprojects/<name>/` | Low | Meson, Gradle |

**Confidence semantics and gating**:
- **High** — pattern is a near-exclusive monorepo signal. Sufficient to set `detected=true` even without a §1 workspace declaration, provided ≥1 manifest-bearing subdirectory exists.
- **Medium** — pattern correlates with monorepos but also appears in single-package projects. Requires either ≥2 manifest-bearing subdirectories OR co-occurrence with another medium/high-confidence signal in `evidence[]`.
- **Low** — pattern is too generic. Requires both ≥2 manifest-bearing subdirectories AND co-occurrence with a higher-confidence signal in `evidence[]`.

**Heuristic-only detection**: a project with no §1 declaration but ≥1 high-confidence pattern with ≥1 manifest-bearing subdirectory emits `detected=true` with `evidence: [{type: "heuristic_signal", pattern: "...", confidence: "high", manifest_bearing_subdirs: N}]`. A project with only medium/low patterns failing the gate emits `detected=false` and records the patterns in `monorepo_detection.notes` (NOT `evidence[]`, since `evidence[]` semantics is "supports `detected=true`").

## §3. Detection Algorithm

The algorithm proceeds in five phases. Phase A iterates ecosystems in deterministic order parsing each workspace declaration; all ecosystems are checked (early exit is forbidden because polyglot monorepos may have multiple declarations). Phase B runs regardless of Phase A — heuristic evidence supplements declarations. Phase B.5 includes every disclosed subpackage CLAUDE.md parent directory in the uncapped candidate root set before filtering. Phase C applies the 4-layer filter (Layer 1 root exclusion implicit; Layer 3 defensive sanity check). Phase D sets `detected` from filtered roots, declarations, or high-confidence heuristics. Phase E applies caps and emits the result.

```
function detect_monorepo(project_root):
    evidence, candidate_roots, notes = [], set(), []

    # Phase A: workspace declaration parse (§1)
    for eco in ECOSYSTEMS_ORDERED:
        manifest_path = find_manifest(project_root, eco)
        if not manifest_path: continue
        try:
            decl = parse_workspace_declaration(eco, manifest_path)
        except ParseError as e:
            evidence.append({"type": "parse_error", "ecosystem": eco,
                             "manifest": manifest_path, "error": str(e)})
            continue
        if decl is None: continue
        roots = resolve_glob(decl.raw_value, project_root, eco)
        if len(roots) == 0:
            code = ("umbrella_apps_path_empty" if eco == "elixir"
                    else "workspace_declaration_resolved_zero_roots")
            notes.append({"code": code, "ecosystem": eco,
                          "details": f"manifest: {manifest_path}"})
        roots_truncated = len(roots) > scored_cap
        evidence.append({
            "type": "workspace_declaration", "ecosystem": eco,
            "manifest": manifest_path, "field": decl.field,
            "raw_value": decl.raw_value,
            "resolved_roots": roots[:scored_cap] if roots_truncated else roots,
            "resolved_roots_total": len(roots),
            "resolved_roots_truncated": roots_truncated,
        })
        candidate_roots.update(roots)

    # Phase B: heuristic signals (§2)
    for pattern, confidence in HEURISTIC_PATTERNS:
        if not directory_exists(project_root / pattern): continue
        subdirs = enumerate_manifest_bearing_subdirs(project_root / pattern)
        if not subdirs: continue
        if confidence == "low" and not (
            len(subdirs) >= 2 and has_higher_confidence_evidence(evidence)
        ):
            notes.append({"code": "heuristic_low_confidence_gate_rejected",
                          "details": f"{pattern}: {len(subdirs)} subdirs"})
            continue
        if confidence == "medium" and not (
            len(subdirs) >= 2 or has_higher_confidence_evidence(evidence)
        ):
            notes.append({"code": "heuristic_medium_confidence_gate_rejected",
                          "details": f"{pattern}: {len(subdirs)} subdirs"})
            continue
        evidence.append({"type": "heuristic_signal", "pattern": pattern,
                         "confidence": confidence,
                         "manifest_bearing_subdirs": len(subdirs)})
        candidate_roots.update(subdirs)

    # Phase B.5: disclosure walk inclusion (subset invariant)
    for claude_md_path in phase_1_5_disclosure_walk(project_root):
        candidate_roots.add(parent_dir(claude_md_path))

    # Phase C: 4-layer filter
    filtered_roots = []
    for root in candidate_roots:
        if matches_build_cache_exclusion(root): continue        # Layer 2
        if not has_manifest_in(root, MANIFEST_LIST): continue   # Layer 3
        if git_check_ignore(root) == 0: continue                # Layer 4
        filtered_roots.append(repo_relative(root))

    # Phase D: type-consistency-aware detected flag (§4)
    detected = (
        len(filtered_roots) > 0
        or any_workspace_declaration_in(evidence)
        or any_high_confidence_heuristic_in(evidence)
    )

    # Phase E: cap policy (§5)
    sorted_roots = sorted(filtered_roots)
    display_cap, scored_cap = 20, 50
    return {
        "detected": detected, "evidence": evidence,
        "package_roots": sorted_roots[:display_cap],
        "package_roots_for_scoring": sorted_roots[:scored_cap],
        "package_root_caps": {
            "display": display_cap, "scored": scored_cap,
            "unscored_count_in_view": max(0, len(sorted_roots) - display_cap),
            "total_filtered": len(sorted_roots),
        },
        "notes": notes,
    }
```

**Phase 1.5 mapping**: candidate roots are the deduplicated union of three sources — workspace-declaration roots (Phase A), accepted heuristic roots (Phase B), and CLAUDE.md disclosure walk parents (Phase B.5). The uncapped filtered root set (Phase C output) MUST include every disclosed subpackage CLAUDE.md parent that passes Layer 2/3/4. `package_roots_for_scoring[]` is the `scored=50` capped prefix; truncation past the cap MUST be surfaced through `package_root_caps` and `notes`. `package_roots[]` is the display-capped prefix of `package_roots_for_scoring[]`.

## §4. Type Consistency Rules

Schema 1.2.0 enforces these invariants at validation time. Runtime detection always co-emits the consistent pair; the schema invariants are a defensive guard against fixture/integration drift.

1. **`single_project + detected:true` rejected**: `project_structure.type=="single_project"` AND `monorepo_detection.detected==true` is invalid. The two fields co-vary; a project cannot be classified `single_project` while detection reports a monorepo.
2. **`monorepo` requires `detected:true`**: `project_structure.type=="monorepo"` MUST have `monorepo_detection.detected==true`. The reverse is also required: `detected==true` MUST imply `type=="monorepo"`.
3. **`null` fallback only with absent or null detection**: `project_structure.type==null` MUST have `monorepo_detection==null` or `monorepo_detection.detected==null`. The `null` fallback is the no-decision state (e.g., audit ran in degraded mode without filesystem access).

## §5. Cap Policy

| Cap | Value | Applied To | Rationale |
|---|---|---|---|
| `display` | 20 | `package_roots[]` rendered in audit output | Token budget — Phase 1.5 disclosure cap inherited. |
| `scored` | 50 | `package_roots_for_scoring[]` evaluated by Phase 3.6 LAV | Audit runtime budget — per-package LAV is roughly 5× a single root LAV; 50 subpackages bound total Phase 3.6 budget within timeout envelope. |
| `unscored_count_in_view` | computed | Reported in audit output as "(+N more not shown)" | Visibility into truncation. |
| `total_filtered` | computed | Total count after Phase C 4-layer filter, before any cap | Surface absolute size for users with very large monorepos. |

**Interaction**: invariant `display ≤ scored` — scoring rows that are not rendered is permitted; rendering rows outside the scored/display-selected set is not. When `total_filtered > scored`: rendering shows the first 20; the audit emits a Recommendation noting `(total_filtered - scored)` subpackages were neither shown nor scored. When `display < total_filtered ≤ scored`: rendering shows 20 with `(+N more not shown)`; all `total_filtered` are scored, only the top 20 visible. When `total_filtered ≤ display`: full list, no truncation notice.

**Selection order**: when `total_filtered > display`, the first 20 shown are sorted ascending by repo-relative path (deterministic, ecosystem-agnostic). No prioritization heuristic is applied.

**Evidence cap**: evidence entries that carry root lists (`workspace_declaration.resolved_roots`, `convention.resolved_roots`, or any future evidence type adding a path-list field) MUST cap those lists at `scored_cap=50` and emit `resolved_roots_total` (integer ≥ 0) and `resolved_roots_truncated` (bool, true iff total > cap and the list was sliced). Rationale: a single Bazel `workspace_declaration` could otherwise carry hundreds to thousands of resolved roots, ballooning `profile.json` size and downstream schema validation cost. `heuristic_signal` evidence is aggregated **per pattern** (one entry per recognized §2 pattern, NOT one per discovered package); bounded by 7 patterns × 14 ecosystems ≈ 98 max, no path-list cap needed. `parse_error` and `composite_build` entries are not path-list-bearing.

**Stateless mode**: in stateless mode (`local/` unwritable), `monorepo_detection` is computed in memory and rendered to terminal output only; it MUST NOT be persisted to `local/profile.json`, `state-summary.md`, or any other state file. Each stateless `/audit` run re-walks and re-detects. Cap policy is identical between stateful and stateless runs.
