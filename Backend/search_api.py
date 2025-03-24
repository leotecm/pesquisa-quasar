from flask import Flask, jsonify, request
from flask_cors import CORS
from elasticsearch import Elasticsearch
from flask import send_file
import os
import docx
import textract
import tag_service
import json
from models import Tag

app = Flask(__name__)
CORS(app)  # Permitir requisições cross-origin

# Configuração do Elasticsearch
ES_HOST = "http://localhost:9200"
INDEX_NAME = "documents"

# Diretório com os documentos
DOCUMENTS_DIR = "file"

# Conectar ao Elasticsearch
es = Elasticsearch([ES_HOST])

@app.route('/api/search', methods=['GET'])
def search():
    """Endpoint para buscar documentos."""
    # Obter parâmetro de consulta da URL
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    
    # Calcular o offset para paginação
    from_val = (page - 1) * size
    
    if not query:
        return jsonify({'error': 'Nenhum termo de busca fornecido'}), 400
    
    try:
        # Construir a consulta para o Elasticsearch
        search_query = {
            "from": from_val,
            "size": size,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "filename^2"],  # ^2 dá mais peso ao nome do arquivo
                    "fuzziness": "AUTO"  # Tolera erros de digitação
                }
            },
            "highlight": {
                "fields": {
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3,
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"]
                    }
                }
            }
        }
        
        # Executar a busca
        response = es.search(index=INDEX_NAME, body=search_query)
        
        # Formatar os resultados
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            result = {
                'id': hit['_id'],
                'filename': source['filename'],
                'path': source['path'],
                'extension': source.get('extension', ''),
                'last_modified': source.get('last_modified', ''),
                'file_size': source.get('file_size', 0),
                'score': hit['_score']
            }
            
            # Adicionar trechos destacados se disponíveis
            if 'highlight' in hit and 'content' in hit['highlight']:
                result['highlights'] = hit['highlight']['content']
                
            # Obter tags associadas ao documento
            doc_tags = tag_service.get_document_tags(hit['_id'])
            if doc_tags:
                result['tags'] = [tag.to_dict() for tag in doc_tags]
            
            results.append(result)
        
        # Buscar tags que correspondem ao termo de busca
        matching_tags = tag_service.get_tags_by_name(query)
        tag_results = []
        
        for tag in matching_tags:
            # Obter todos os documentos associados à tag
            doc_ids = tag_service.get_documents_by_tag(tag.id)
            # Buscar informações dos documentos
            docs = []
            for doc_id in doc_ids[:5]:  # Limitar a 5 documentos por tag nos resultados
                try:
                    doc_query = {
                        "query": {
                            "term": {
                                "_id": doc_id
                            }
                        }
                    }
                    doc_response = es.search(index=INDEX_NAME, body=doc_query)
                    if doc_response['hits']['hits']:
                        source = doc_response['hits']['hits'][0]['_source']
                        docs.append({
                            'id': doc_id,
                            'filename': source['filename']
                        })
                except Exception as e:
                    print(f"Erro ao buscar documento {doc_id}: {e}")
            
            tag_results.append({
                'tag': tag.to_dict(),
                'document_count': len(doc_ids),
                'sample_documents': docs
            })
        
        # Adicionar informações de paginação e metadados
        return jsonify({
            'results': results,
            'total': response['hits']['total']['value'],
            'page': page,
            'size': size,
            'pages': (response['hits']['total']['value'] + size - 1) // size,
            'query': query,
            'tag_results': tag_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """Lista os arquivos indexados."""
    try:
        # Buscar todos os documentos, ordenados por última modificação
        search_query = {
            "size": 100,  # Limitado a 100 documentos para evitar problemas de performance
            "sort": [
                {"last_modified": {"order": "desc"}}
            ],
            "_source": ["filename", "path", "extension", "last_modified", "file_size"]
        }
        
        response = es.search(index=INDEX_NAME, body=search_query)
        
        files = []
        for hit in response['hits']['hits']:
            file_data = hit['_source']
            # Adicionar tags ao resultado
            doc_tags = tag_service.get_document_tags(hit['_id'])
            if doc_tags:
                file_data['tags'] = [tag.to_dict() for tag in doc_tags]
            files.append(file_data)
            
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file-content/<filename>', methods=['GET'])
def get_file_content(filename):
    """Retorna o conteúdo de um arquivo específico."""
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
            
        # Extrair o conteúdo do arquivo
        if filename.endswith('.docx'):
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            content = '\n'.join(full_text)
        elif filename.endswith('.doc'):
            try:
                content = textract.process(file_path).decode('utf-8')
            except Exception as e:
                return jsonify({'error': f'Erro ao processar .doc: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Formato de arquivo não suportado'}), 400

        # Buscar o ID do documento no Elasticsearch
        search_query = {
            "query": {
                "term": {
                    "filename.keyword": filename
                }
            }
        }
        response = es.search(index=INDEX_NAME, body=search_query)
        
        if response['hits']['hits']:
            doc_id = response['hits']['hits'][0]['_id']
            # Obter tags do documento
            doc_tags = tag_service.get_document_tags(doc_id)
            return jsonify({
                'content': content,
                'tags': [tag.to_dict() for tag in doc_tags] if doc_tags else []
            })
        else:
            return jsonify({'content': content, 'tags': []})

    except Exception as e:
        return jsonify({'error': f'Erro ao ler arquivo: {str(e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Permite o download do arquivo original."""
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
            
        # Enviar o arquivo original para download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'  # Tipo genérico para forçar download
        )
    except Exception as e:
        return jsonify({'error': f'Erro ao fazer download do arquivo: {str(e)}'}), 500

# Endpoints para gerenciar tags
@app.route('/api/tags', methods=['GET'])
def get_tags():
    """Retorna todas as tags."""
    try:
        tags = tag_service.get_all_tags()
        return jsonify([tag.to_dict() for tag in tags])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags', methods=['POST'])
def create_tag():
    """Cria uma nova tag."""
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({'error': 'Nome da tag é obrigatório'}), 400
        
        new_tag = tag_service.create_tag(
            name=data['name'],
            color=data.get('color', '#3498db'),
            description=data.get('description', '')
        )
        return jsonify(new_tag.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags/<tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """Atualiza uma tag existente."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400
        
        updated_tag = tag_service.update_tag(
            tag_id=tag_id,
            name=data.get('name'),
            color=data.get('color'),
            description=data.get('description')
        )
        return jsonify(updated_tag.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags/<tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """Remove uma tag."""
    try:
        tag_service.delete_tag(tag_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags/<tag_id>/documents', methods=['GET'])
def get_documents_by_tag(tag_id):
    """Retorna todos os documentos associados a uma tag."""
    try:
        doc_ids = tag_service.get_documents_by_tag(tag_id)
        
        if not doc_ids:
            return jsonify([])
        
        # Buscar informações dos documentos no Elasticsearch
        docs = []
        for doc_id in doc_ids:
            try:
                doc_query = {
                    "query": {
                        "term": {
                            "_id": doc_id
                        }
                    }
                }
                doc_response = es.search(index=INDEX_NAME, body=doc_query)
                if doc_response['hits']['hits']:
                    source = doc_response['hits']['hits'][0]['_source']
                    docs.append({
                        'id': doc_id,
                        'filename': source['filename'],
                        'path': source['path'],
                        'extension': source.get('extension', ''),
                        'last_modified': source.get('last_modified', '')
                    })
            except Exception as e:
                print(f"Erro ao buscar documento {doc_id}: {e}")
        
        return jsonify(docs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<document_id>/tags', methods=['GET'])
def get_document_tags(document_id):
    """Retorna todas as tags associadas a um documento."""
    try:
        tags = tag_service.get_document_tags(document_id)
        return jsonify([tag.to_dict() for tag in tags])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<document_id>/tags/<tag_id>', methods=['POST'])
def associate_tag(document_id, tag_id):
    """Associa uma tag a um documento."""
    try:
        success = tag_service.associate_tag_to_document(document_id, tag_id)
        if success:
            return jsonify({'success': True}), 201
        else:
            return jsonify({'message': 'Tag já associada ao documento'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<document_id>/tags/<tag_id>', methods=['DELETE'])
def dissociate_tag(document_id, tag_id):
    """Remove a associação entre uma tag e um documento."""
    try:
        tag_service.dissociate_tag_from_document(document_id, tag_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota principal para testar se a API está funcionando
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'online',
        'message': 'API de busca de documentos está funcionando',
        'endpoints': {
            '/api/search': 'Buscar documentos (parâmetros: q, page, size)',
            '/api/files': 'Listar todos os documentos indexados',
            '/api/file-content/<filename>': 'Obter conteúdo de um documento específico',
            '/download/<filename>': 'Baixar o arquivo original',
            '/api/tags': 'Gerenciar tags (GET, POST)',
            '/api/tags/<tag_id>': 'Gerenciar tag específica (PUT, DELETE)',
            '/api/tags/<tag_id>/documents': 'Listar documentos de uma tag (GET)',
            '/api/documents/<document_id>/tags': 'Listar tags de um documento (GET)',
            '/api/documents/<document_id>/tags/<tag_id>': 'Associar/desassociar tag (POST, DELETE)'
        }
    })

if __name__ == '__main__':
    # Verificar se o Elasticsearch está rodando
    if not es.ping():
        print("ERRO: Não foi possível conectar ao Elasticsearch. Verifique se o serviço está em execução.")
        exit(1)
    
    # Verificar se o índice existe
    if not es.indices.exists(index=INDEX_NAME):
        print(f"AVISO: O índice '{INDEX_NAME}' não existe no Elasticsearch. Execute o indexador primeiro.")
    
    print("Iniciando servidor de API de busca...")
    app.run(host='0.0.0.0', port=5000, debug=True)