# tag_service.py
import json
import os
from models import Tag, DocumentTag

# Caminhos para os arquivos JSON (simulando um banco de dados)
TAGS_FILE = "data/tags.json"
DOCUMENT_TAGS_FILE = "data/document_tags.json"

# Garantir que os diretórios existam
os.makedirs(os.path.dirname(TAGS_FILE), exist_ok=True)
os.makedirs(os.path.dirname(DOCUMENT_TAGS_FILE), exist_ok=True)

def _load_tags():
    """Carrega todas as tags do arquivo JSON."""
    if not os.path.exists(TAGS_FILE):
        return []
    
    try:
        with open(TAGS_FILE, 'r', encoding='utf-8') as f:
            tags_data = json.load(f)
            return [Tag.from_dict(tag_data) for tag_data in tags_data]
    except Exception as e:
        print(f"Erro ao carregar tags: {e}")
        return []

def _save_tags(tags):
    """Salva todas as tags no arquivo JSON."""
    tags_data = [tag.to_dict() for tag in tags]
    with open(TAGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tags_data, f, indent=2)

def _load_document_tags():
    """Carrega todas as relações documento-tag do arquivo JSON."""
    if not os.path.exists(DOCUMENT_TAGS_FILE):
        return []
    
    try:
        with open(DOCUMENT_TAGS_FILE, 'r', encoding='utf-8') as f:
            relations_data = json.load(f)
            return [DocumentTag.from_dict(rel_data) for rel_data in relations_data]
    except Exception as e:
        print(f"Erro ao carregar relações documento-tag: {e}")
        return []

def _save_document_tags(relations):
    """Salva todas as relações documento-tag no arquivo JSON."""
    relations_data = [relation.to_dict() for relation in relations]
    with open(DOCUMENT_TAGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(relations_data, f, indent=2)

def get_all_tags():
    """Retorna todas as tags cadastradas."""
    return _load_tags()

def get_tag_by_id(tag_id):
    """Busca uma tag pelo ID."""
    tags = _load_tags()
    for tag in tags:
        if tag.id == tag_id:
            return tag
    return None

def get_tags_by_name(name):
    """Busca tags que contenham o termo no nome."""
    tags = _load_tags()
    return [tag for tag in tags if name.lower() in tag.name.lower()]

def create_tag(name, color="#3498db", description=""):
    """Cria uma nova tag."""
    tags = _load_tags()
    
    # Verificar se já existe uma tag com esse nome
    if any(tag.name.lower() == name.lower() for tag in tags):
        raise ValueError(f"Já existe uma tag com o nome '{name}'")
    
    # Criar nova tag
    new_tag = Tag(name=name, color=color, description=description)
    tags.append(new_tag)
    _save_tags(tags)
    return new_tag

def update_tag(tag_id, name=None, color=None, description=None):
    """Atualiza uma tag existente."""
    tags = _load_tags()
    
    # Encontrar a tag pelo ID
    for tag in tags:
        if tag.id == tag_id:
            if name is not None:
                # Verificar se o novo nome não conflita com outras tags
                if any(t.name.lower() == name.lower() and t.id != tag_id for t in tags):
                    raise ValueError(f"Já existe uma tag com o nome '{name}'")
                tag.name = name
            
            if color is not None:
                tag.color = color
            
            if description is not None:
                tag.description = description
            
            _save_tags(tags)
            return tag
    
    raise ValueError(f"Tag com ID '{tag_id}' não encontrada")

def delete_tag(tag_id):
    """Remove uma tag do sistema."""
    tags = _load_tags()
    tags = [tag for tag in tags if tag.id != tag_id]
    _save_tags(tags)
    
    # Remover todas as associações com documentos
    relations = _load_document_tags()
    relations = [rel for rel in relations if rel.tag_id != tag_id]
    _save_document_tags(relations)

def associate_tag_to_document(document_id, tag_id):
    """Associa uma tag a um documento."""
    relations = _load_document_tags()
    
    # Verificar se a relação já existe
    if any(rel.document_id == document_id and rel.tag_id == tag_id for rel in relations):
        return False  # Relação já existe
    
    # Criar nova relação
    new_relation = DocumentTag(document_id=document_id, tag_id=tag_id)
    relations.append(new_relation)
    _save_document_tags(relations)
    return True

def dissociate_tag_from_document(document_id, tag_id):
    """Remove a associação entre uma tag e um documento."""
    relations = _load_document_tags()
    relations = [rel for rel in relations if not (rel.document_id == document_id and rel.tag_id == tag_id)]
    _save_document_tags(relations)

def get_document_tags(document_id):
    """Retorna todas as tags associadas a um documento."""
    relations = _load_document_tags()
    tags = _load_tags()
    
    # Encontrar os IDs das tags associadas ao documento
    tag_ids = [rel.tag_id for rel in relations if rel.document_id == document_id]
    
    # Retornar as tags completas
    return [tag for tag in tags if tag.id in tag_ids]

def get_documents_by_tag(tag_id):
    """Retorna todos os documentos associados a uma tag."""
    relations = _load_document_tags()
    return [rel.document_id for rel in relations if rel.tag_id == tag_id]