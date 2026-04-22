try:
    import fcntl
except ImportError:
    fcntl = None

import json
import os
from typing import List, Type, TypeVar, Optional, Any
from pydantic import BaseModel, TypeAdapter

T = TypeVar("T", bound=BaseModel)

class JSONDatabase:
    def __init__(self):
        # Ensure default directory exists on first init
        os.makedirs(self.data_dir, exist_ok=True)

    @property
    def data_dir(self) -> str:
        return os.getenv("ONEBRIDGE_DATA_DIR", "data")

    def _get_path(self, model_type: Type[T]) -> str:
        # Map model name (e.g. StudentProfile) to filename (students.json)
        # Standard mapping for OneBridge
        mapping = {
            "StudentProfile": "students.json",
            "SupportTicket": "tickets.json",
            "Opportunity": "opportunities.json",
            "FacilityBooking": "facility_bookings.json",
            "Notification": "notifications.json",
            "KnowledgeBaseArticle": "knowledge_base.json",
            "ChatConversation": "chat_conversations.json",
            "ChatMessage": "chat_messages.json",
            "ScholarshipScheme": "scholarships.json",
            "ApplicationRecord": "applications.json",
            "SecurityEvent": "security_events.json"
        }
        filename = mapping.get(model_type.__name__, f"{model_type.__name__.lower()}s.json")
        return os.path.join(self.data_dir, filename)

    def _load_raw(self, path: str) -> List[dict]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                # Use flock for thread/process safety (Unix-like systems)
                try:
                    fcntl.flock(f, fcntl.LOCK_SH)
                    data = json.load(f)
                    fcntl.flock(f, fcntl.LOCK_UN)
                    return data
                except (IOError, AttributeError):
                    # Fallback for systems without fcntl (Windows)
                    return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []

    def _save_raw(self, path: str, data: List[dict]):
        with open(path, "w", encoding="utf-8") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(data, f, indent=2, default=str)
                fcntl.flock(f, fcntl.LOCK_UN)
            except (IOError, AttributeError):
                # Fallback for systems without fcntl
                json.dump(data, f, indent=2, default=str)

    def get_all(self, model_type: Type[T]) -> List[T]:
        path = self._get_path(model_type)
        raw_data = self._load_raw(path)
        adapter = TypeAdapter(List[model_type])
        return adapter.validate_python(raw_data)

    def get_by_id(self, model_type: Type[T], obj_id: int) -> Optional[T]:
        items = self.get_all(model_type)
        return next((item for item in items if getattr(item, 'id') == obj_id), None)

    def find_one(self, model_type: Type[T], **filters) -> Optional[T]:
        items = self.get_all(model_type)
        for item in items:
            if all(getattr(item, k, None) == v for k, v in filters.items()):
                return item
        return None

    def find_many(self, model_type: Type[T], **filters) -> List[T]:
        items = self.get_all(model_type)
        results = []
        for item in items:
            if all(getattr(item, k, None) == v for k, v in filters.items()):
                results.append(item)
        return results

    def insert(self, model_instance: T) -> T:
        model_type = type(model_instance)
        path = self._get_path(model_type)
        items = self._load_raw(path)
        
        # Auto-increment ID if needed
        if model_instance.id <= 0:
            max_id = max([item.get('id', 0) for item in items], default=0)
            model_instance.id = max_id + 1
            
        items.append(model_instance.model_dump(mode='json'))
        self._save_raw(path, items)
        return model_instance

    def update(self, model_type: Type[T], obj_id: int, **updates) -> Optional[T]:
        path = self._get_path(model_type)
        items = self._load_raw(path)
        
        updated_item = None
        for item in items:
            if item.get('id') == obj_id:
                item.update(updates)
                updated_item = model_type.model_validate(item)
                break
        
        if updated_item:
            self._save_raw(path, items)
        return updated_item

    def delete(self, model_type: Type[T], obj_id: int) -> bool:
        path = self._get_path(model_type)
        items = self._load_raw(path)
        new_items = [item for item in items if item.get('id') != obj_id]
        if len(new_items) < len(items):
            self._save_raw(path, new_items)
            return True
        return False

# Global instance for the platform
db = JSONDatabase()
