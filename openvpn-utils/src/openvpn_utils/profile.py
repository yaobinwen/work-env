# standard
import pathlib
import typing

# 3rd-party
from ywen import (
    args_helpers,
    encoding,
)


_PROFILE_TEMPLATE = """
# Automatically generated OpenVPN client profile

{client_config_content}

<ca>
{ca_crt_content}
</ca>

<cert>
{client_crt_content}
</cert>

<key>
{client_key_content}
</key>

<tls-crypt>
{tls_auth_key_content}
</tls-crypt>

""".strip()


def _read_client_config(
    client_config_file: pathlib.Path,
    excluded_keys: typing.Set[str] = None,
) -> typing.Dict[str, str]:
    config = {}

    raw_content = client_config_file.read_text(
        encoding=encoding.PREFERRED_ENCODING,
    )
    lines = raw_content.split("\n")
    for line in lines:
        if line.startswith("#") or line.startswith(";"):
            # A comment line. Skip.
            continue

        pos = line.find(" ")
        if pos == -1:
            # This line is a single key.
            key = line
            value = None
        else:
            key = line[:pos]
            value = line[pos+1:]

        if key in excluded_keys:
            continue

        config[key] = value

    return config


def _form_client_config_content(
    client_config: typing.Dict[str, str],
) -> str:
    lines = []
    for k, v in client_config.items():
        if v is None:
            lines.append(k)
        else:
            lines.append(f"{k} {v}")

    return "\n".join(lines)


def _do_subcmd_profile(
    logger,
    subcmd: str,
    client_config_file: pathlib.Path,
    client_bundle_dir: pathlib.Path,
    ca_crt: str,
    client_crt: str,
    client_key: str,
    crl_pem: str,
    tls_auth_key: str,
    output: pathlib.Path,
):
    client_config = _read_client_config(
        client_config_file=client_config_file,
        excluded_keys=set([
            "ca",
            "cert",
            "key",
            "tls-auth",
            "up",
            "down",
        ]),
    )
    client_config_content = _form_client_config_content(client_config)

    ca_crt_fpath = client_bundle_dir / ca_crt
    ca_crt_content = ca_crt_fpath.read_text(
        encoding=encoding.PREFERRED_ENCODING,
    ).strip()

    client_crt_fpath = client_bundle_dir / client_crt
    client_crt_content = client_crt_fpath.read_text(
        encoding=encoding.PREFERRED_ENCODING,
    ).strip()

    client_key_fpath = client_bundle_dir / client_key
    client_key_content = client_key_fpath.read_text(
        encoding=encoding.PREFERRED_ENCODING,
    ).strip()

    tls_auth_key_fpath = client_bundle_dir / tls_auth_key
    tls_auth_key_content = tls_auth_key_fpath.read_text(
        encoding=encoding.PREFERRED_ENCODING,
    ).strip()

    profile_content = _PROFILE_TEMPLATE.format(
        client_config_content=client_config_content,
        ca_crt_content=ca_crt_content,
        client_crt_content=client_crt_content,
        client_key_content=client_key_content,
        tls_auth_key_content=tls_auth_key_content,
    )

    output.write_text(
        data=profile_content,
        encoding=encoding.PREFERRED_ENCODING,
    )


def syntax_subcmd_profile(subcmds):
    desc = "Create a client profile"
    subcmd = subcmds.add_parser("profile", description=desc, help=desc)
    subcmd.set_defaults(func=_do_subcmd_profile)

    subcmd.add_argument(
        "--client-config-file",
        metavar="PATH",
        help="Path of the OpenVPN client configuration file",
        type=pathlib.Path,
        required=True,
    )

    subcmd.add_argument(
        "--client-bundle-dir",
        metavar="PATH",
        help="Path of the OpenVPN client bundle",
        type=pathlib.Path,
        required=True,
    )

    d = "ca.crt"
    subcmd.add_argument(
        "--ca-crt",
        metavar="FILENAME",
        help=args_helpers.arg_help_with_default(
            help="Filename of OpenVPN CA certificate",
            default=d,
        ),
        default=d,
    )

    d = "client.crt"
    subcmd.add_argument(
        "--client-crt",
        metavar="FILENAME",
        help=args_helpers.arg_help_with_default(
            help="Filename of OpenVPN client certificate",
            default=d,
        ),
        default=d,
    )

    d = "client.key"
    subcmd.add_argument(
        "--client-key",
        metavar="FILENAME",
        help=args_helpers.arg_help_with_default(
            help="Filename of OpenVPN client key",
            default=d,
        ),
        default=d,
    )

    d = "crl.pem"
    subcmd.add_argument(
        "--crl-pem",
        metavar="FILENAME",
        help=args_helpers.arg_help_with_default(
            help="Filename of Certificate Revocation List (CRL)",
            default=d,
        ),
        default=d,
    )

    d = "ta.key"
    subcmd.add_argument(
        "--tls-auth-key",
        metavar="FILENAME",
        help=args_helpers.arg_help_with_default(
            help="Filename of TLS authentication key",
            default=d,
        ),
        default=d,
    )

    subcmd.add_argument(
        "--output",
        metavar="PATH",
        help="Path of the output OpenVPN client profile file",
        type=pathlib.Path,
        required=True,
    )
