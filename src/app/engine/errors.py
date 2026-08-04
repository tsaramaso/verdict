# src/app/engine/errors.py


class IllegalAction(Exception):
    """
    Raised whenever a command doesn't match a legal edge in
    game_flow.mermaid for the current phase/actor — e.g. acting out of
    turn, pressing a button that isn't legal in the current window,
    targeting an already-emptied slot. Callers (sockets.py) catch this
    and send the acting client an error, without mutating state or
    emitting any event.
    """
