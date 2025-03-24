# models.py
import uuid
from datetime import datetime

class Tag:
    """Modelo para representar uma tag no sistema."""
    
    def __init__(self, name, color="#3498db", description=""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.color = color
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self):
        """Converte a tag para um dicionário."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma tag a partir de um dicionário."""
        tag = cls(name=data["name"], color=data.get("color", "#3498db"), 
                  description=data.get("description", ""))
        tag.id = data.get("id", tag.id)
        tag.created_at = data.get("created_at", tag.created_at)
        tag.updated_at = data.get("updated_at", tag.updated_at)
        return tag


class DocumentTag:
    """Modelo para representar a relação entre documento e tag."""
    
    def __init__(self, document_id, tag_id):
        self.id = str(uuid.uuid4())
        self.document_id = document_id
        self.tag_id = tag_id
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Converte a relação para um dicionário."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "tag_id": self.tag_id,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma relação a partir de um dicionário."""
        relation = cls(document_id=data["document_id"], tag_id=data["tag_id"])
        relation.id = data.get("id", relation.id)
        relation.created_at = data.get("created_at", relation.created_at)
        return relation