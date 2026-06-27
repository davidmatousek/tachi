#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
usage: llvm-cov.sh [cargo-llvm-cov-args...]

Runs cargo llvm-cov with LLVM_COV and LLVM_PROFDATA resolved from the active
Rust toolchain.
EOF
}

if [[ ${1:-} == "--help" || ${1:-} == "-h" ]]; then
  usage
  exit 0
fi

HOST_TRIPLE=""
while IFS= read -r line; do
  case "$line" in
    host:\ *)
      HOST_TRIPLE="${line#host: }"
      break
      ;;
  esac
done < <(rustc -Vv)

if [[ -z "$HOST_TRIPLE" ]]; then
  echo "unable to determine host triple from rustc -Vv" >&2
  exit 1
fi

TOOLCHAIN="${RUSTUP_TOOLCHAIN:-}"
if [[ -z "$TOOLCHAIN" ]]; then
  TOOLCHAIN="$(rustup show active-toolchain 2>/dev/null | awk 'NR == 1 { print $1 }')"
fi

LLVM_BIN_DIR=""
if [[ -n "$TOOLCHAIN" ]]; then
  RUSTUP_HOME_DIR="${RUSTUP_HOME:-$HOME/.rustup}"
  CANDIDATE_DIR="$RUSTUP_HOME_DIR/toolchains/$TOOLCHAIN/lib/rustlib/$HOST_TRIPLE/bin"
  if [[ -x "$CANDIDATE_DIR/llvm-cov" && -x "$CANDIDATE_DIR/llvm-profdata" ]]; then
    LLVM_BIN_DIR="$CANDIDATE_DIR"
  fi
fi

if [[ -z "$LLVM_BIN_DIR" ]]; then
  SYSROOT="$(rustc --print sysroot)"
  CANDIDATE_DIR="$SYSROOT/lib/rustlib/$HOST_TRIPLE/bin"
  if [[ -x "$CANDIDATE_DIR/llvm-cov" && -x "$CANDIDATE_DIR/llvm-profdata" ]]; then
    LLVM_BIN_DIR="$CANDIDATE_DIR"
  fi
fi

if [[ -z "$LLVM_BIN_DIR" ]]; then
  echo "missing llvm-cov tools in active toolchain" >&2
  exit 1
fi

LLVM_COV="$LLVM_BIN_DIR/llvm-cov"
LLVM_PROFDATA="$LLVM_BIN_DIR/llvm-profdata"

if [[ $# -eq 0 ]]; then
  set -- --workspace --summary-only --fail-under-lines 85 --ignore-filename-regex 'target/|tests/'
fi

exec env LLVM_COV="$LLVM_COV" LLVM_PROFDATA="$LLVM_PROFDATA" cargo llvm-cov "$@"
