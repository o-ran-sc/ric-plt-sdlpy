from dataclasses import dataclass


@dataclass(frozen=True)
class SDLNamespaces:
    E2_MANAGER = "e2Manager"


sdl_ns = SDLNamespaces()
