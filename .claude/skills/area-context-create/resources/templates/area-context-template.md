---
name: context-{{AREA_NAME}}
description: |
  {{DESCRIPTION}}. Use when working with {{AREA_NAME}} code, files, or integration. Invoke when navigating {{AREA_NAME}} codebase, searching for {{AREA_NAME}} files, debugging {{AREA_NAME}} errors, or discussing {{AREA_NAME}} patterns. Keywords: {{AREA_NAME}}, {{KEYWORDS}}
tags: {{TAGS}}
---

# {{AREA_NAME}} Context

**Files:** {{TOTAL_FILES}} files, {{TOTAL_LOC}} LOC

Quick navigation for {{AREA_NAME}} area. Indexed {{CREATED_DATE}}.

## Quick Navigation

{{ACTIVE_FILES}}

{{DEPRECATED_FILES}}

{{TEST_FILES}}

## How to Use This Skill

**When navigating {{AREA_NAME}} code:**
- Use file paths with line numbers for precise navigation
- Check "CURRENT" markers for actively maintained files
- Avoid "DO NOT EDIT" files (backups, deprecated)
- Look for entry points (classes, main functions)

**Common tasks:**
- Find API endpoints: Look for `*_api.py:*` files
- Find business logic: Look for `*_service*.py` or engine classes
- Find data models: Look for `*_models.py` or schema definitions
- Find tests: Check "Tests" section

## Serena Quick Commands

```python
# Get symbol overview for a file
mcp__serena__get_symbols_overview(
  relative_path="<file_path_from_above>"
)

# Find specific symbol
mcp__serena__find_symbol(
  name_path="ClassName.method_name",
  relative_path="<file_path>",
  include_body=True
)

# Search for pattern
mcp__serena__search_for_pattern(
  substring_pattern="search_term",
  relative_path="<directory>"
)
```

## Maintenance

**Regenerate this skill:**
```bash
scripts/area-context-update {{AREA_NAME}}
```

**Edit area definition:**
```bash
# Edit .context/area-config.yml
# Then regenerate
scripts/area-context-update {{AREA_NAME}}
```

---

**Area:** {{AREA_NAME}}
**Last Updated:** {{CREATED_DATE}}
**Maintenance:** Manual (regenerate as needed)
**Auto-activation:** Triggers on "{{AREA_NAME}}", "navigate {{AREA_NAME}}", "{{AREA_NAME}} files"
