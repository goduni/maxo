
from collections import defaultdict
from collections.abc import MutableMapping, MutableSequence
from typing import Any

from maxo.routing.interfaces.middleware import BaseMiddleware
from maxo.routing.interfaces.router import BaseRouter
from maxo.routing.updates.base import BaseUpdate


def _resolving_middlewares(
    router: BaseRouter,
    outer_middlewares: MutableMapping[
        type[BaseUpdate],
        MutableSequence[BaseMiddleware[Any]],
    ],
    inner_middlewares: MutableMapping[
        type[BaseUpdate],
        MutableSequence[BaseMiddleware[Any]],
    ],
) -> None:
    for update_tp, observer in router.observers.items():
        new_outers = (*outer_middlewares[update_tp],)
        current_outers = (*observer.middleware.outer.middlewares,)

        observer.middleware.outer.middlewares.extend(new_outers)
        outer_middlewares[update_tp].extend(current_outers)

        new_inners = (*inner_middlewares[update_tp],)
        current_inners = (*observer.middleware.inner.middlewares,)

        observer.middleware.inner.middlewares.extend(new_inners)
        inner_middlewares[update_tp].extend(current_inners)


def _resolving_outer_middlewares(
    router: BaseRouter,
    middlewares_map: MutableMapping[
        type[BaseUpdate],
        MutableSequence[BaseMiddleware[Any]],
    ],
) -> None:
    for update_tp, observer in router.observers.items():
        new_middlewares = (*middlewares_map[update_tp],)
        current_middlewares = (*observer.middleware.outer.middlewares,)

        observer.middleware.outer.middlewares.extend(new_middlewares)
        middlewares_map[update_tp].extend(current_middlewares)


def resolve_middlewares(
    router: BaseRouter,
    outer_middlewares: (
        MutableMapping[type[BaseUpdate], MutableSequence[BaseMiddleware[Any]]] | None
    ) = None,
    inner_middlewares: (
        MutableMapping[type[BaseUpdate], MutableSequence[BaseMiddleware[Any]]] | None
    ) = None,
) -> None:
    if outer_middlewares is None:
        outer_middlewares = defaultdict(list)
    if inner_middlewares is None:
        inner_middlewares = defaultdict(list)

    _resolving_middlewares(router, outer_middlewares, inner_middlewares)

    for children_router in router.children_routers:
        resolve_middlewares(
            children_router,
            {**outer_middlewares},
            {**inner_middlewares},
        )
