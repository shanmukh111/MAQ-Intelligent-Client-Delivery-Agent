from dataclasses import dataclass


@dataclass(frozen=True)
class UserAccess:
    user_id: str
    role: str
    can_view_portfolio: bool
    can_view_engineering: bool
    can_view_timesheets: bool


# ---------------------------------------------------------
# Demo authorization map
#
# Production replacement:
# Microsoft Entra ID claims / groups / app roles.
# ---------------------------------------------------------

AUTHORIZED_USERS = {
    "manager01": UserAccess(
        user_id="manager01",
        role="DeliveryManager",
        can_view_portfolio=True,
        can_view_engineering=True,
        can_view_timesheets=True,
    ),

    "engineering01": UserAccess(
        user_id="engineering01",
        role="EngineeringLead",
        can_view_portfolio=False,
        can_view_engineering=True,
        can_view_timesheets=False,
    ),

    "portfolio01": UserAccess(
        user_id="portfolio01",
        role="PortfolioLead",
        can_view_portfolio=True,
        can_view_engineering=False,
        can_view_timesheets=True,
    ),
}


class AuthorizationError(Exception):
    """
    Raised when a user is unknown or is not permitted
    to access the requested evidence domain.
    """


def get_user_access(
    user_id: str,
) -> UserAccess:
    """
    Returns the access profile for a known demo user.
    """

    normalized_user_id = (
        user_id.strip().lower()
    )

    access = AUTHORIZED_USERS.get(
        normalized_user_id
    )

    if access is None:
        raise AuthorizationError(
            "User is not authorized."
        )

    return access


def authorize_route(
    *,
    user_id: str,
    routing: dict,
) -> UserAccess:
    """
    Validates whether the user can access the
    evidence domains required by the routing decision.
    """

    access = get_user_access(
        user_id
    )

    if (
        routing.get("portfolio")
        and not access.can_view_portfolio
    ):
        raise AuthorizationError(
            "User is not authorized "
            "for portfolio evidence."
        )

    if (
        routing.get("engineering")
        and not access.can_view_engineering
    ):
        raise AuthorizationError(
            "User is not authorized "
            "for engineering evidence."
        )

    return access