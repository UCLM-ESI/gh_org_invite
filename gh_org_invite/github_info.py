"""Contains a set of functions to interact with GitHub API."""

import logging

from github import Github
from github.Organization import Organization
from github.GithubException import UnknownObjectException


class GHOrgClient:
    """Class to interact with Github thourgh the library."""
    logger = logging.getLogger("GHOrgClient")

    def __init__(self, token: str, org_name:str, dry_run:bool=False) -> None:
        """Initialize a GHClient object."""
        self.gh = Github(token)
        self.org = self.gh.get_organization(org_name)
        self.dry_run = dry_run

    def invite_users(self, new_users:list) -> None:
        """Send invites to users from the list that doesn't belong to the organization."""
        current_members = self._get_current_members()
        pending_invitations = self._get_pending_invitations()
        
        invite_to = self._named_users_from_logins(
            [
                user for user in new_users
                if user not in current_members and user not in pending_invitations
            ]
        )

        for named_user in invite_to:
            self.logger.info("Inviting user: %s", named_user.login)
            if not self.dry_run:
                self.org.invite_user(named_user)

    def _get_current_members(self) -> set:
        """Returns a set with the username of the current members of the org."""
        members = set()
        members_pager = self.org.get_members()

        page_index = 0
        
        while True:
            page_members = members_pager.get_page(page_index)
            if not page_members:
                break

            
            members = members.union(
                [member.login for member in page_members],
            )
            
            page_index += 1
        
        return members
    
    def _get_pending_invitations(self) -> set:
        """Returns a set of already invited usernames."""
        pending = set()
        invitations_pager = self.org.invitations()

        page_index = 0

        while True:
            page_invitations = invitations_pager.get_page(page_index)

            if not page_invitations:
                break

            pending = pending.union(
                [invited.login for invited in page_invitations]
            )
            page_index += 1
        
        return pending

    def _named_users_from_logins(self, login_names:list) -> list:
        """Generates a list of `NamedUser` from a list of user names."""
        named_users = set()

        for username in login_names:
            try:
                named_user = self.gh.get_user(username)
                named_users.add(named_user)
            except UnknownObjectException as ex:
                self.logger.error("Username %s cannot be retrieved", username)
        
        return named_users