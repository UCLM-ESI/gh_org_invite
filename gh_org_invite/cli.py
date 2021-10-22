"""
Module containing the CLI handlers.

Take a look into project setup.cfg to see the correspondance between
CLI commands and methods in this module.
"""

import argparse
import json
import logging
import sys

from gh_org_invite.github_info import GHOrgClient


DEFAULT_ORG_NAME = "SSDD-2021-2022"


def org_invite() -> None:
    """Method handling the org-invite command."""
    
    parser = argparse.ArgumentParser(
        description="Invite users from input file to a GitHub organization",
        epilog="Too lazy to type aaaaaaall their names",
    )
    parser.add_argument(
        "--dry-run",
        help=(
            "Show the users to invite and the organization info, but doesn't"
            " perform any action"
            ),
        action="store_true",
    )
    parser.add_argument(
        "--org-name",
        help="The organization name where the users has to be invited",
        type=str,
        default=DEFAULT_ORG_NAME,
    )
    parser.add_argument(
        "-t", "--token",
        help="A GitHub user token from the organization admin",
        type=str,
        required=True,
    )
    
    parser.add_argument("input_file", type=argparse.FileType('r'))
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)

    users = json.load(args.input_file)
    args.input_file.close()

    # Users, as they come from Moodle, are in a list with only one element
    # That list contains one element per user
    # each user is a 5-element list in this form
    # ['Real name', 'Lab group', 'e-mail@address.com', 'spanish timestamp of the answer', 'GH username']
    users = users[0]  # avoiding the unnecessary list nesting
    
    usernames = [user[4] for user in users]
    logging.info(usernames)

    if args.dry_run:
        logging.info("Running with --dry-run, no real actions will be performed")
    
    client = GHOrgClient(args.token, args.org_name, args.dry_run)
    client.invite_users(usernames)
    
    logging.info("Bye")