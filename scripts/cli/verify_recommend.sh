#!/usr/bin/env bash
set -euo pipefail

base_ref="${1:-origin/master}"
if ! git rev-parse --verify "${base_ref}" >/dev/null 2>&1; then
  base_ref="master"
fi

merge_base="$(git merge-base HEAD "${base_ref}" 2>/dev/null || true)"
if [[ -z "${merge_base}" ]]; then
  merge_base="${base_ref}"
fi

mapfile -t files < <(git diff --name-only "${merge_base}...HEAD" || true)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "No changes detected vs ${base_ref}."
  exit 0
fi

touches_verification=0
touches_infra=0
touches_core=0
touches_only_docs=1

for f in "${files[@]}"; do
  case "${f}" in
    docs/**|README.md|**/*.md) ;;
    *) touches_only_docs=0 ;;
  esac

  case "${f}" in
    backend/scripts/verification/**|frontend/src/middleware.ts|Makefile)
      touches_verification=1
      ;;
  esac

  case "${f}" in
    railway.toml|backend/railway.toml|frontend/railway.toml|.github/workflows/**|scripts/railway-*|scripts/ci/**)
      touches_infra=1
      ;;
  esac

  case "${f}" in
    backend/db/**|backend/services/**|backend/routers/**|frontend/src/**)
      touches_core=1
      ;;
  esac
done

echo "Changed files: ${#files[@]}"

if [[ ${touches_only_docs} -eq 1 ]]; then
  echo "Recommended: make ci-lite   (docs-only)"
  exit 0
fi

if [[ ${touches_verification} -eq 1 || ${touches_infra} -eq 1 ]]; then
  echo "Recommended: make verify-pr PR=<N>   (verification/infra wiring touched)"
  exit 0
fi

if [[ ${#files[@]} -gt 25 ]]; then
  echo "Recommended: make verify-pr PR=<N>   (large PR)"
  exit 0
fi

if [[ ${touches_core} -eq 1 && ${#files[@]} -gt 8 ]]; then
  echo "Recommended: make verify-pr-lite  +  make ci-lite   (moderate core changes)"
  exit 0
fi

echo "Recommended: make ci-lite   (small/moderate change)"

