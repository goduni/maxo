from collections.abc import Sequence

from maxo.enums import UpdateType
from maxo.routing.interfaces.router import BaseRouter
from maxo.routing.updates.base import MaxUpdate


def collect_used_updates(
    router: BaseRouter,
    used_updates: set[UpdateType] | None = None,
) -> Sequence[str]:
    if used_updates is None:
        used_updates = set()

    used_updates |= _collect_used_updates_type(router)

    for children_router in router.children_routers:
        collect_used_updates(children_router, used_updates)

    return tuple(used_updates)


def _collect_used_updates_type(router: BaseRouter) -> set[UpdateType]:
    used_updates = set()
    for update_tp, observer in router.observers.items():
        if (
            issubclass(update_tp, MaxUpdate)
            and observer.handlers
            and update_tp.type is not None
        ):
            used_updates.add(update_tp.type)

    return used_updates
