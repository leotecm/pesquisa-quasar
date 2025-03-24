import os
import time
from elasticsearch import Elasticsearch
import docx
import textract
from datetime import datetime
import hashlib

# Configuração do Elasticsearch
ES_HOST = "http://localhost:9200"
INDEX_NAME = "documents"

# Diretório com os documentos (ajuste conforme sua necessidade)
DOCUMENTS_DIR = "file"  # Use o mesmo diretório que sua API Flask usa

def connect_elasticsearch():
    """Conecta-se à instância do Elasticsearch."""
    es = Elasticsearch([ES_HOST])
    if es.ping():
        print("Conectado ao Elasticsearch")
    else:
        print("Não foi possível conectar ao Elasticsearch")
        return None
    return es

def create_index(es, recreate=False):
    """Cria o índice para os documentos se não existir."""
    # Definição de como os documentos serão indexados
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "filename": {"type": "keyword"},
                "path": {"type": "keyword"},
                "content": {"type": "text", "analyzer": "standard"},
                "extension": {"type": "keyword"},
                "last_modified": {"type": "date"},
                "indexed_at": {"type": "date"},
                "file_size": {"type": "long"},
                "file_hash": {"type": "keyword"}
            }
        }
    }
    
    # Se recreate=True ou o índice não existe, criamos um novo
    if recreate and es.indices.exists(index=INDEX_NAME):
        print(f"Removendo índice existente '{INDEX_NAME}'...")
        es.indices.delete(index=INDEX_NAME)
        print(f"Índice '{INDEX_NAME}' removido")
    
    if not es.indices.exists(index=INDEX_NAME):
        # Cria o índice com as configurações definidas
        es.indices.create(index=INDEX_NAME, body=settings)
        print(f"Índice '{INDEX_NAME}' criado")
    else:
        print(f"Índice '{INDEX_NAME}' já existe")

def extract_text_from_document(file_path):
    """Extrai texto de um documento .doc ou .docx."""
    try:
        if file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():  # Evitar parágrafos vazios
                    full_text.append(para.text)
            return "\n".join(full_text)
        elif file_path.endswith('.doc'):
            text = textract.process(file_path).decode('utf-8')
            return text
        else:
            print(f"Formato não suportado: {file_path}")
            return ""
    except Exception as e:
        print(f"Erro ao extrair texto de {file_path}: {e}")
        return ""

def calculate_file_hash(file_path):
    """Calcula o hash MD5 do arquivo para verificar mudanças."""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_existing_documents(es):
    """Obtém uma lista de todos os documentos já indexados."""
    query = {
        "query": {"match_all": {}},
        "size": 10000,  # Limite de 10000 documentos
        "_source": ["filename", "file_hash"]
    }
    
    result = es.search(index=INDEX_NAME, body=query)
    
    # Criar um dicionário com filename como chave e id/hash como valores
    existing_docs = {}
    for hit in result['hits']['hits']:
        filename = hit['_source']['filename']
        existing_docs[filename] = {
            'id': hit['_id'],
            'hash': hit['_source'].get('file_hash', '')
        }
    
    return existing_docs

def index_documents(es):
    """Indexa todos os documentos do diretório configurado."""
    # Verifica se o diretório existe
    if not os.path.exists(DOCUMENTS_DIR):
        print(f"Diretório '{DOCUMENTS_DIR}' não encontrado")
        return
    
    # Obter documentos existentes
    existing_docs = get_existing_documents(es)
    print(f"Encontrados {len(existing_docs)} documentos já indexados")
    
    # Estatísticas
    new_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    # Lista de todos os arquivos processados nesta execução
    processed_files = []
    
    # Processar todos os arquivos .doc e .docx no diretório
    for filename in os.listdir(DOCUMENTS_DIR):
        if filename.endswith(('.doc', '.docx')):
            file_path = os.path.join(DOCUMENTS_DIR, filename)
            processed_files.append(filename)
            
            try:
                # Calcular hash do arquivo
                file_hash = calculate_file_hash(file_path)
                
                # Verificar se o arquivo já existe e se o hash é o mesmo
                if filename in existing_docs and existing_docs[filename]['hash'] == file_hash:
                    print(f"Documento não modificado, ignorando: {filename}")
                    skipped_count += 1
                    continue
                
                # Extrair informações do arquivo
                stat_info = os.stat(file_path)
                last_modified = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                file_size = stat_info.st_size
                extension = os.path.splitext(filename)[1].lower().replace('.', '')
                
                # Extrair o texto do documento
                content = extract_text_from_document(file_path)
                
                # Preparar o documento para indexação
                doc = {
                    'filename': filename,
                    'path': file_path,
                    'content': content,
                    'extension': extension,
                    'last_modified': last_modified,
                    'indexed_at': datetime.now().isoformat(),
                    'file_size': file_size,
                    'file_hash': file_hash
                }
                
                # Indexar o documento (atualizar se existir, criar se não)
                if filename in existing_docs:
                    doc_id = existing_docs[filename]['id']
                    es.index(index=INDEX_NAME, id=doc_id, body=doc)
                    print(f"Documento atualizado: {filename}")
                    updated_count += 1
                else:
                    es.index(index=INDEX_NAME, body=doc)
                    print(f"Novo documento indexado: {filename}")
                    new_count += 1
                
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")
                error_count += 1
    
    # Verificar arquivos que não existem mais no diretório
    for filename in list(existing_docs.keys()):
        if filename not in processed_files:
            print(f"Documento não encontrado no diretório, removendo do índice: {filename}")
            try:
                es.delete(index=INDEX_NAME, id=existing_docs[filename]['id'])
            except Exception as e:
                print(f"Erro ao remover documento {filename}: {e}")
    
    # Forçar um refresh do índice
    es.indices.refresh(index=INDEX_NAME)
    
    print(f"\nResumo da indexação:")
    print(f"Novos documentos: {new_count}")
    print(f"Documentos atualizados: {updated_count}")
    print(f"Documentos ignorados (não modificados): {skipped_count}")
    print(f"Erros de processamento: {error_count}")

def main():
    """Função principal."""
    print("Iniciando processo de indexação...")
    start_time = time.time()
    
    # Conecta ao Elasticsearch
    es = connect_elasticsearch()
    if not es:
        return
    
    # Pergunta se o usuário deseja recriar o índice
    choice = input("Deseja recriar o índice (remover todos os documentos existentes)? (s/N): ")
    recreate = choice.lower() in ('s', 'sim', 'y', 'yes')
    
    # Cria ou recria o índice conforme escolha do usuário
    create_index(es, recreate)
    
    # Indexa os documentos
    index_documents(es)
    
    # Exibe o tempo total de processamento
    elapsed_time = time.time() - start_time
    print(f"Processo concluído em {elapsed_time:.2f} segundos")

if __name__ == "__main__":
    main()