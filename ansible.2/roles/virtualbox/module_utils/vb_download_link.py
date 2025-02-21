import argparse
import bs4
import re
import requests
import urllib.parse


def _url(v):
    if not v:
        raise ValueError("given URL is empty")

    parsed = urllib.parse.urlparse(v)
    # `urllib.parse.urlparse` doesn't raise errors on invalid URLs so we need
    # to check that by ourselves.
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"invalid URL: {v}")

    return v


def _syntax():
    p = argparse.ArgumentParser(
        description=(
            "Obtain VirtualBox Debian package download link "
            "from VirtualBox official download page"
        )
    )

    p.add_argument(
        "--homepage",
        help="VirtualBox's official download page (default: %(default)s)",
        default="https://www.virtualbox.org/wiki/Linux_Downloads",
        type=_url,
    )

    p.add_argument(
        "--os-name",
        help=(
            "Name of the target operating system, case-insensitive "
            "(default: %(default)s)"
        ),
        default="ubuntu",
    )

    p.add_argument(
        "--os-version",
        help="Version of the target operating system (default: %(default)s)",
        default="24.04",
    )

    return p


def _find_pkg_version(soup):
    P = re.compile(r"^VirtualBox (\d+\.\d+\.\d+) for Linux$")
    pkg_version = None

    for span in soup.find_all("span"):
        if not span.text:
            continue

        m = P.match(span.text)
        if m is None:
            continue

        pkg_version = m.group(1)
        break

    return pkg_version


def _find_pkg_link(soup, os_name, os_version):
    pkg_link = None

    litems = soup.find_all("li")
    for i in litems:
        os_text = i.text.upper()

        if os_name.upper() in os_text and os_version.upper() in os_text:
            for c in i.children:
                if c is None:
                    continue

                if c.name == "a":
                    pkg_link = c.get("href")

    return pkg_link


def get_vb_download_link(*, homepage, os_name, os_version):
    page_html = requests.get(homepage).text
    soup = bs4.BeautifulSoup(page_html, "html.parser")

    pkg_version = _find_pkg_version(soup)
    if pkg_version is None:
        raise ValueError("Cannot find VirtualBox package version.")

    pkg_link = _find_pkg_link(soup, os_name, os_version)
    if pkg_link is None:
        raise ValueError(
            "Cannot find the link to VirtualBox package "
            "{pkg_version}.".format(pkg_version=pkg_version)
        )

    return pkg_version, pkg_link


def main(*, homepage, os_name, os_version):
    pkg_version, pkg_link = get_vb_download_link(
        homepage=homepage, os_name=os_name, os_version=os_version
    )
    print(f"pkg_version: {pkg_version}")
    print(f"   pkg_link: {pkg_link}")


if __name__ == "__main__":
    main(**vars(_syntax().parse_args()))
