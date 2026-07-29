from modules.logger import log

_INTERVAL_MS = 150


class AnimationQueue:
    """Drives hover animations from a Tk timer that only runs when needed.

    The timer is armed when a widget starts hovering and disarmed as soon as the
    last one stops, so an idle window schedules no work at all. Running frames
    off a background thread (the previous design) meant touching Tk from a
    non-main thread, which pegs a core on macOS.
    """

    isInit: bool = False
    _active: set = set()
    _master = None
    _timer = None

    @classmethod
    def Initialize(cls, master):
        log.warning("Initialize AnimationQueue")
        if cls.isInit:
            raise RuntimeError("Already Initialized.")
        cls._master = master
        cls.isInit = True

    @classmethod
    def AddToQueue(cls, func):
        """Kept for callers that register an animation up front; a registered
        animation costs nothing until it is activated."""
        return

    @classmethod
    def Activate(cls, func):
        cls._active.add(func)
        if cls._timer is None and cls._master is not None:
            cls._schedule()

    @classmethod
    def Deactivate(cls, func):
        cls._active.discard(func)

    @classmethod
    def _schedule(cls):
        cls._timer = cls._master.after(_INTERVAL_MS, cls._tick)

    @classmethod
    def _tick(cls):
        cls._timer = None

        # snapshot, a callback may activate or deactivate animations while we run
        for func in tuple(cls._active):
            try:
                func()
            except Exception:
                log.exception("Animation callback failed")

        # re-arm only while something is still animating
        if cls._active:
            cls._schedule()
