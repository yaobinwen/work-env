#!/bin/sh

set -x

# Set up temporary storage.
TMP="$(mktemp -d)" || exit

cleanup() {
    rm -fr "$TMP" || echo "WARNING: cleanup() failed" >&2
}
trap cleanup EXIT INT TERM

FNAME="sandbox.sh"

./generate_script.py --script-dir "$TMP" --script-file-name "$FNAME" "$@" || exit

# Print for debugging purpose.
cat "$TMP/$FNAME" || exit
"$TMP/$FNAME" || exit
