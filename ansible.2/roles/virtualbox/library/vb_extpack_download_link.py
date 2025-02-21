from ansible.module_utils.basic import *
from ansible.module_utils.vb_extpack_download_link import get_vb_extpack_download_link


def _exception_msg(e):
    return "{type}: {msg}".format(type=type(e).__name__, msg=str(e))


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
        ext_version, ext_link, ext_sha256_link = get_vb_extpack_download_link(
            homepage=homepage
        )
    except ValueError as e:
        module.fail_json(msg=_exception_msg(e))

    module.exit_json(
        changed=changed,
        link=ext_link,
        sha256_link=ext_sha256_link,
        version=ext_version,
    )


main()
