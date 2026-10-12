"""One-time OAuth login for the Business Profile API + token refresh helper.

First run (opens a browser; sign in with an OWNER/MANAGER of the profiles)::

    python scripts/gbp_auth.py login --client-secrets client_secret.json

This stores a refresh token in ``.gbp_token.json`` (git-ignored). Later runs
of ``run_pilot_audit.py --client-source gbp-api`` refresh the access token
silently. To list what the token can see::

    python scripts/gbp_auth.py accounts
    python scripts/gbp_auth.py locations --account 1234567890

Requires: ``pip install google-auth google-auth-oauthlib requests``.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import settings  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/business.manage"]


def token_provider_from_file(token_file: str | Path = "") -> "callable[[], str]":
    """Return a callable that yields a fresh access token from the stored refresh token."""
    from google.auth.transport.requests import Request  # lazy: optional dependency
    from google.oauth2.credentials import Credentials

    path = Path(token_file or settings.GBP_TOKEN_FILE)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found - run `python scripts/gbp_auth.py login` first")
    creds = Credentials.from_authorized_user_file(str(path), SCOPES)

    def _token() -> str:
        if not creds.valid or creds.expired:
            creds.refresh(Request())
            path.write_text(creds.to_json(), encoding="utf-8")
        return str(creds.token)

    return _token


def login(client_secrets: str, token_file: str) -> None:
    from google_auth_oauthlib.flow import InstalledAppFlow  # lazy: optional dependency

    flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    Path(token_file).write_text(creds.to_json(), encoding="utf-8")
    print(f"saved refresh token to {token_file}")  # noqa: T201


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_login = sub.add_parser("login")
    p_login.add_argument("--client-secrets", default=settings.GBP_CLIENT_SECRETS_FILE)
    p_login.add_argument("--token-file", default=settings.GBP_TOKEN_FILE)
    sub.add_parser("accounts")
    p_loc = sub.add_parser("locations")
    p_loc.add_argument("--account", required=True)
    args = parser.parse_args(argv)

    if args.cmd == "login":
        login(args.client_secrets, args.token_file)
        return 0

    import requests

    from core.adapters.gbp_api_adapter import GBPApiAdapter

    adapter = GBPApiAdapter(requests.Session(), token_provider_from_file())
    if args.cmd == "accounts":
        print(json.dumps(adapter.list_accounts(), indent=2))  # noqa: T201
    else:
        for loc in adapter.list_locations(args.account):
            print(f"{loc.location_id:>22}  {loc.title:45}  {loc.address}")  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main())
