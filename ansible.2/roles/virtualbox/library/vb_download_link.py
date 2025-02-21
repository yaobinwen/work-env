from ansible.module_utils.basic import *
from ansible.module_utils.vb_download_link import get_vb_download_link


def _exception_msg(e):
    return "{type}: {msg}".format(type=type(e).__name__, msg=str(e))


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
                default="24.04",
            ),
        ),
        supports_check_mode=True,
    )

    homepage = module.params["homepage"]
    os_name = module.params["os_name"]
    os_version = module.params["os_version"]

    changed = False

    try:
        pkg_version, pkg_link = get_vb_download_link(
            homepage=homepage, os_name=os_name, os_version=os_version
        )
    except ValueError as e:
        module.fail_json(msg=_exception_msg(e))

    module.exit_json(
        changed=changed,
        version=pkg_version,
        link=pkg_link,
    )


main()
