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
            "Obtain VirtualBox extension pack Debian package download link "
            "from VirtualBox extension pack official download page"
        )
    )

    p.add_argument(
        "--homepage",
        help=(
            "VirtualBox extension pack official download page " "(default: %(default)s)"
        ),
        default="https://www.virtualbox.org/wiki/Downloads",
        type=_url,
    )

    return p


def _find_extpack_version(soup):
    P = re.compile(r"^VirtualBox (\d+\.\d+\.\d+) Extension Pack$")
    ext_version = None

    for span in soup.find_all("span"):
        if not span.text:
            continue

        m = P.match(span.text)
        if m is None:
            continue

        ext_version = m.group(1)
        break

    return ext_version


def _find_extpack_link(soup):
    ext_link = None

    anchors = soup.find_all("a")
    for a in anchors:
        a_text = a.text.upper()

        if "Accept and download".upper() in a_text:
            ext_link = a.get("href")

    return ext_link


def _find_extpack_sha256_link(soup, homepage):
    ext_sha256_link = None

    anchors = soup.find_all("a")
    for a in anchors:
        a_text = a.text.upper()

        if "SHA256 checksums".upper() in a_text:
            # The SHA256 download link is relative.
            ext_sha256_link = urllib.parse.urljoin(homepage, a.get("href"))

    return ext_sha256_link


def get_vb_extpack_download_link(*, homepage):
    page_html = requests.get(homepage).text
    soup = bs4.BeautifulSoup(page_html, "html.parser")

    ext_version = _find_extpack_version(soup)
    if ext_version is None:
        raise ValueError("Cannot find VirtualBox extension pack version.")

    ext_link = _find_extpack_link(soup)
    if ext_link is None:
        raise ValueError(
            "Cannot find the link to VirtualBox extension pack "
            "{ext_version}.".format(ext_version=ext_version)
        )

    ext_sha256_link = _find_extpack_sha256_link(soup, homepage)
    if ext_sha256_link is None:
        raise ValueError(
            "Cannot find the SHA256 link to VirtualBox extension pack "
            "{ext_version}.".format(ext_version=ext_version)
        )

    return ext_version, ext_link, ext_sha256_link


def main(*, homepage):
    ext_version, ext_link, ext_sha256_link = get_vb_extpack_download_link(
        homepage=homepage
    )
    print(f"    ext_version: {ext_version}")
    print(f"       ext_link: {ext_link}")
    print(f"ext_sha256_link: {ext_sha256_link}")


if __name__ == "__main__":
    main(**vars(_syntax().parse_args()))
