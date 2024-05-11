from __future__ import absolute_import, print_function, unicode_literals

import re
import requests
from bs4 import BeautifulSoup


def _exception_msg(e):
    return "{type}: {msg}".format(type=type(e).__name__, msg=str(e))


def _find_pkg_version(soup):
    P = re.compile(r"^VirtualBox(\d+\.\d+\.\d+)forLinux$")
    pkg_version = None

    for h3 in soup.find_all("h3"):
        h3_id = h3.get("id")
        if h3_id is None:
            continue

        m = P.match(h3_id)
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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            homepage=dict(
                type="str",
                default="https://www.virtualbox.org/wiki/Linux_Downloads",
            ),
            os_name=dict(
                type="str",
                default="ubuntu",
            ),
            os_version=dict(
                type="str",
                default="18.04",
            ),
        ),
        supports_check_mode=True,
    )

    homepage = module.params["homepage"]
    os_name = module.params["os_name"]
    os_version = module.params["os_version"]

    changed = False

    try:
        page_html = requests.get(homepage).text
        soup = BeautifulSoup(page_html, "html.parser")

        pkg_version = _find_pkg_version(soup)
        if pkg_version is None:
            raise ValueError("Cannot find VirtualBox package version.")

        pkg_link = _find_pkg_link(soup, os_name, os_version)
        if pkg_link is None:
            raise ValueError(
                "Cannot find the link to VirtualBox package "
                "{pkg_version}.".format(pkg_version=pkg_version)
            )
    except ValueError as e:
        module.fail_json(msg=_exception_msg(e))

    module.exit_json(
        changed=changed,
        link=pkg_link,
        version=pkg_version,
    )


from ansible.module_utils.basic import *

main()
