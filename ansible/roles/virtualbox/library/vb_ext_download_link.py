from __future__ import absolute_import, print_function, unicode_literals

import re
import requests
from bs4 import BeautifulSoup


def _exception_msg(e):
    return "{type}: {msg}".format(type=type(e).__name__, msg=str(e))


def _find_ext_version(soup):
    P = re.compile(r"^VirtualBox(\d+\.\d+\.\d+)OracleVMVirtualBoxExtensionPack$")
    ext_version = None

    for h3 in soup.find_all("h3"):
        h3_id = h3.get("id")
        if h3_id is None:
            continue

        m = P.match(h3_id)
        if m is None:
            continue

        ext_version = m.group(1)
        break

    return ext_version


def _find_ext_link(soup):
    ext_link = None

    litems = soup.find_all("li")
    for i in litems:
        os_text = i.text.upper()

        if "All supported platforms".upper() in os_text:
            for c in i.children:
                if c is None:
                    continue

                if c.name == "a":
                    ext_link = c.get("href")

    return ext_link


def _find_ext_sha256_link(soup):
    ext_sha256_link = None

    litems = soup.find_all("li")
    for i in litems:
        os_text = i.text.upper()

        if "SHA256 checksums".upper() in os_text:
            for c in i.children:
                if c is None:
                    continue

                if c.name == "a":
                    ext_sha256_link = c.get("href")

    return ext_sha256_link


def main():
    module = AnsibleModule(
        argument_spec=dict(
            homepage=dict(
                type="str",
                default="https://www.virtualbox.org/wiki/Downloads",
            ),
        ),
        supports_check_mode=True,
    )

    homepage = module.params["homepage"]

    changed = False

    try:
        page_html = requests.get(homepage).text
        soup = BeautifulSoup(page_html, "html.parser")

        ext_version = _find_ext_version(soup)
        if ext_version is None:
            raise ValueError("Cannot find VirtualBox extension pack version.")

        ext_link = _find_ext_link(soup)
        if ext_link is None:
            raise ValueError(
                "Cannot find the link to VirtualBox extension pack "
                "{ext_version}.".format(ext_version=ext_version)
            )

        ext_sha256_link = _find_ext_sha256_link(soup)
        if ext_sha256_link is None:
            raise ValueError(
                "Cannot find the SHA256 link to VirtualBox extension pack "
                "{ext_version}.".format(ext_version=ext_version)
            )

    except ValueError as e:
        module.fail_json(msg=_exception_msg(e))

    module.exit_json(
        changed=changed,
        link=ext_link,
        sha256_link=ext_sha256_link,
        version=ext_version,
    )


from ansible.module_utils.basic import *

main()
