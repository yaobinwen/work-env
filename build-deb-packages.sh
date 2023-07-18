#!/bin/bash

_banner() {
    local PKG_PATH

    PKG_PATH=$1

    WIDTH=$2
    test -z "$WIDTH" && WIDTH=30

    printf -- =%.0s $(seq 1 $WIDTH) && echo
    echo "Building '$PKG_PATH'"
    printf -- =%.0s $(seq 1 $WIDTH) && echo
}

_build_pkg() {
    local TMP_DIR PKG_PATH CHANGELOG PKG_NAME PKG_VERSION TARBALL_FNAME OUTPUT_DIR

    PKG_PATH="$1"
    _banner "$PKG_PATH"

    OUTPUT_DIR="$2"
    echo "OUTPUT_DIR=$OUTPUT_DIR"

    # Create temporary storage.
    TMP_DIR="$(mktemp -d)" || return
    echo "TMP_DIR=$TMP_DIR"

    # Check if `changelog` exists.
    CHANGELOG="$PKG_PATH/debian/changelog"
    echo "CHANGELOG=$CHANGELOG"
    test -f "$CHANGELOG" || {
        echo "ERROR: '$CHANGELOG' is not a regular file."
        return
    }

    # Figure out package name.
    PKG_NAME=$(
        dpkg-parsechangelog \
            --file "$PKG_PATH/debian/changelog" \
            --show-field Source
    )
    echo "PKG_NAME=$PKG_NAME"
    test -n "$PKG_NAME" || {
        echo "ERROR: Cannot find the field 'Source' in '$CHANGELOG'."
        return
    }

    # Figure out package version.
    dpkg-parsechangelog \
        --file "$PKG_PATH/debian/changelog" \
        --show-field Version >"$TMP_DIR/pkg_full_version" || return
    PKG_FULL_VERSION=$(cat "$TMP_DIR/pkg_full_version")
    echo "PKG_FULL_VERSION=$PKG_FULL_VERSION"
    grep "-" <"$TMP_DIR/pkg_full_version" || {
        echo "ERROR: Cannot find '-' in version string 'PKG_FULL_VERSION'."
        return
    }
    PKG_VERSION=$(
        cut -d "-" -f 1 <"$TMP_DIR/pkg_full_version"
    )
    echo "PKG_VERSION=$PKG_VERSION"
    test -n "$PKG_VERSION" || {
        echo "ERROR: Cannot find the field 'Version' in '$CHANGELOG'."
        return
    }

    # Copy the source files.
    rsync -r -v "$PKG_PATH" "$TMP_DIR" || return

    # Create the tarball.
    TARBALL_FNAME="${PKG_NAME}_${PKG_VERSION}.orig.tar.xz"
    echo "TARBALL_FNAME=$TARBALL_FNAME"
    (
        cd "$TMP_DIR" &&
            tar --exclude=debian -cJf "$TARBALL_FNAME" "$PKG_NAME"
    ) || return

    # Build the package.
    (
        cd "$TMP_DIR/$PKG_NAME" &&
            debuild -us -uc
    ) || return

    # Copy the built artifacts to the output directory.
    (
        cd "$TMP_DIR" &&
            cp -v ./*.deb "$OUTPUT_DIR" &&
            cp -v ./*.build "$OUTPUT_DIR" &&
            cp -v ./*.buildinfo "$OUTPUT_DIR" &&
            cp -v ./*.changes "$OUTPUT_DIR" &&
            cp -v ./*.debian.tar.xz "$OUTPUT_DIR" &&
            cp -v ./*.dsc "$OUTPUT_DIR" &&
            cp -v ./*.orig.tar.xz "$OUTPUT_DIR"
    ) || return

    # Remove the temporary storage on success. We don't remove the temporary
    # storage on failure so we can debug the code.
    rm -rf "$TMP_DIR" || return
}

_build_packages() {
    local PKG_PATHS

    PKG_PATHS=$1

    for PKG_PATH in $PKG_PATHS; do
        # Create the output directory.
        mkdir -p "$PWD/build/$PKG_PATH" || return

        _build_pkg "$PWD/$PKG_PATH" "$PWD/build/$PKG_PATH" || return
    done
}

PKG_PATHS="
    python/ywen
    python/secret-file
    python/tex-pkg
    openvpn-utils
    pyinterpreter
"

_build_packages "$PKG_PATHS" || {
    echo "Build failed!"
    exit
}
echo "Build succeeded!"
