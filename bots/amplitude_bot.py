from concurrent.futures import ThreadPoolExecutor

from amplitude import Amplitude, BaseEvent

from core.settings import settings

executor = ThreadPoolExecutor(max_workers=4)

class AmplitudeBot:
    def __init__(self, api_key):
        self._client = Amplitude(api_key=api_key)

    def track_event(self, user_id: int, event_type: str, event_properties: dict = None):
        """Отслеживание ивента"""
        event = BaseEvent(event_type=event_type, user_id=str(user_id), event_properties=event_properties or {})
        executor.submit(self._client.track, event)
        print(f'Отработал ивент: {event_type}')

amplitude_bot = AmplitudeBot(settings.amplitude_api_key)
