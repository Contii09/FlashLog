import random
import string
import sql
from flask import Flask, jsonify, request
from sqlalchemy import select
from main import app
from models import Usuario, Encomenda, Entregador, CentroDeTranporcacao, Cliente, SessionLocal, ListarEncomendas, \
    BuscarEncomenda, Movimentacao
# Gerar o token
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
# Gerir papeis
from functools import wraps
from flask_login import LoginManager, login_required, login_user, logout_user, current_user


# Cadastro de entrega
@app.route('/cadastro_encomendas', methods=['POST'])
def cadastro_encomendas():
    """
    **API para Cadastro de Encomendas**
    ### Endpoint:
    POST /cadastro_encomendas

    ### Parâmetros de Entrada (JSON):
    ```json
    {
        "codigo_rastreio": "string (obrigatório) - Código único gerado para a encomenda",
        "nome": "string (obrigatório) - Nome ou descrição do item",
        "fragilidade": "string (obrigatório) - Nível de fragilidade (Ex: Alta, Baixa)",
        "tipo": "string (obrigatório) - Categoria do produto"
    }
    ```

    ### Respostas (JSON):
    * **201 Created:** Encomenda registrada com sucesso.
      ```json
      {
          "msg": "Encomenda criada com sucesso",
          "encomenda_id": 1,
          "codigo_rastreio": "FLASH123456"
      }
      ```
    * **400 Bad Request:** Ausência de campos obrigatórios ou código já existente.
      ```json
      {
          "msg": "Os campos codigo_rastreio, nome, fragilidade e tipo são obrigatórios"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar encomenda.: [Descrição do Erro]"
      }
      ```
    """
    dados = request.get_json()

    codigo_rastreio = dados.get('codigo_rastreio')
    nome = dados.get('nome')
    fragilidade = dados.get('fragilidade')
    tipo = dados.get('tipo')

    if not codigo_rastreio or not nome or not fragilidade or not tipo:
        return jsonify({"msg": "Os campos codigo_rastreio, nome, fragilidade e tipo são obrigatórios"}), 400

    banco = SessionLocal()
    try:
        existe = banco.query(Encomenda).filter(Encomenda.codigo_rastreio == codigo_rastreio).first()
        if existe:
            return jsonify({"msg": f"O código de rastreio {codigo_rastreio} já está em uso"}), 400

        nova_encomenda = Encomenda(
            codigo_rastreio=codigo_rastreio,
            nome=nome,
            fragilidade=fragilidade,
            tipo=tipo
        )
        banco.add(nova_encomenda)
        banco.commit()

        return jsonify({
            "msg": "Encomenda criada com sucesso",
            "encomenda_id": nova_encomenda.id,
            "codigo_rastreio": nova_encomenda.codigo_rastreio
        }), 201

    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar encomenda.: {str(e)}"}), 500
    finally:
        banco.close()


@app.route('/cadastro_usuario', methods=['POST'])
def cadastro_usuario():
    """
    **API para Cadastro de Usuário**

    ### Endpoint:
    POST /cadastro_usuario

    ### Parâmetros de Entrada (JSON):
    ```json
    {
        "nome": "string (obrigatório) - Nome completo do usuário",
        "email": "string (obrigatório) - Endereço de e-mail único",
        "senha": "string (obrigatório) - Senha em texto limpo para criptografia"
    }
    ```

    ### Respostas (JSON):
    * **201 Created:** Usuário registrado com sucesso.
      ```json
      {
          "msg": "Usuário criado com sucesso",
          "usuario_id": 1
      }
      ```
    * **400 Bad Request:** Ausência de campos obrigatórios.
      ```json
      {
          "msg": "Os campos Nome, Email e Senha são obrigatórios"
      }
      ```
    * **409 Conflict:** E-mail já cadastrado no sistema.
      ```json
      {
          "msg": "Este e-mail já está cadastrado"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar usuário.: [Descrição do Erro]"
      }
      ```
    """
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({"msg": "Os campos Nome, Email e Senha são obrigatórios"}), 400
    banco = SessionLocal()

    try:
        # verificar se o email esta no banco
        usuario_existente = banco.query(Usuario).filter(Usuario.email == email).first()
        if usuario_existente:
            return jsonify({"msg": "Este e-mail já está cadastrado"}), 409

        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.setar_senha_hash(senha)
        banco.add(novo_usuario)
        banco.commit()

        usuario_id = novo_usuario.id
        return jsonify({"msg": "Usuário criado com sucesso", "usuario_id": usuario_id}), 201
    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar usuário.: {str(e)}"}), 500
    finally:
        banco.close()


@app.route('/cadastro_cliente', methods=['POST'])
def cadastro_cliente():
    """
    **API para Cadastro de Cliente**
    ### Endpoint:
    POST /cadastro_cliente

    ### Parâmetros de Entrada (JSON):
    ```json
    {
        "nome": "string (obrigatório) - Nome ou descrição da cliente",
        "email": "string (obrigatório) - Endereço de e-mail único",
        "senha": "string (obrigatório) - Senha em texto limpo para criptografia",
        "endereco": "boolean/string (obrigatório) - Indicador de endereco",
        "produto": "string (obrigatório) - Tipo de produto/encomenda"
    }
    ```

    ### Respostas (JSON):
    * **201 Created:** Cliente registrado com sucesso.
      ```json
      {
          "msg": "Cliente criado com sucesso",
          "cliente_id": 1
      }
      ```
    * **400 Bad Request:** Ausência de campos obrigatórios.
      ```json
      {
          "msg": "Os campos Nome, Email, Senha, Endereço e Produto são obrigatórios"
      }
      ```
    * **409 Conflict:** E-mail já cadastrado.
      ```json
      {
          "msg": "Este e-mail já está cadastrado"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar cliente.: [Descrição do Erro]"
      }
      ```
    """
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    endereco = dados.get('endereco')
    produto = dados.get('produto')

    #checar se tds os campos estao preenchidos
    if not nome or not email or not senha or not endereco or not produto:
        return jsonify({"msg": "Os campos Nome, Email, Senha, Endereço e Produto são obrigatórios"}), 400

    banco = SessionLocal()

    try:
        #verificar se o email esta no banco
        cliente_existente = banco.query(Cliente).filter(Cliente.email == email).first()
        if cliente_existente:
            return jsonify({"msg": "Este e-mail já está cadastrado"}), 409

        novo_cliente = Cliente(nome=nome, email=email, endereco=endereco, produto=produto)
        if hasattr(novo_cliente, 'setar_senha_hash'):
            novo_cliente.setar_senha_hash(senha)

        banco.add(novo_cliente)
        banco.commit()

        cliente_id = novo_cliente.id
        return jsonify({"msg": "Cliente criado com sucesso", "cliente_id": cliente_id}), 201
    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar cliente.: {str(e)}"}), 500
    finally:
        banco.close()


@app.route('/cadastro_entregador', methods=['POST'])
def cadastro_entregador():
    """
    **API para Cadastro de Entregador**

    ### Endpoint:
    POST /cadastro_entregador

    ### Parâmetros de Entrada (JSON):
    ```json
    {
        "nome": "string (obrigatório) - Nome ou descrição da encomenda",
        "veiculo": "boolean/string (obrigatório) - Indicador o veiculo do entregador",

    }
    ```

    ### Respostas (JSON):
    * **201 Created:** Entregador registrado com sucesso.
      ```json
      {
          "msg": "Entregador cadastrado com sucesso",
          "enconmenda_id": 1
      }
      ```
    * **400 Bad Request:** Ausência de campos obrigatórios.
      ```json
      {
          "msg": "Os campos Nome e veiculo são obrigatórios"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar usuário.: [Descrição do Erro]"
      }
      ```
    """

    dados = request.get_json()
    nome = dados['nome']
    veiculo = dados['veiculo']

    if not nome or not veiculo:
        return jsonify({"msg": "Os campos Nome e veiculo."})
    banco = SessionLocal()

    try:
        novo_entregador = Entregador(nome=nome, veiculo=veiculo)
        banco.add(novo_entregador)
        banco.commit()

        entregador_id = novo_entregador.id
        return jsonify({"msg": "Usuário criado com sucesso", "entregador_id": entregador_id}), 201
    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar usuário.: {str(e)}"}), 500
    finally:
        banco.close()


@app.route('/cadastro_centro_transporte', methods=['POST'])
def cadastro_centro_transporte():
    """
    **API para Cadastro do centro de transporte

    ### Endpoint:
    POST /cadastro_centro_transporte

    ### Parâmetros de Entrada (JSON):
    ```json
    {
        "nome": "string (obrigatório) - Nome ou descrição da encomenda",
        "localizacao": "boolean/string (obrigatório) - Indicador de localizacao da transportadora",

    }
    ```

    ### Respostas (JSON):
    * **201 Created:** Transportadora registrada com sucesso.
      ```json
      {
          "msg": "Transportadora criado com sucesso",
          "enconmenda_id": 1
      }
      ```
    * **400 Bad Request:** Ausência de campos obrigatórios.
      ```json
      {
          "msg": "Os campos Nome, localizacao são obrigatórios"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar a transportadora.: [Descrição do Erro]"
      }
      ```
    """
    dados = request.get_json()
    nome = dados['nome']
    localizacao = dados['localizacao']

    if not nome or not localizacao:
        return jsonify({"msg": "Os campos Nome e localizacao."})
    banco = SessionLocal()

    try:
        novo_centro = CentroDeTranporcacao(nome=nome, localizacao=localizacao)
        banco.add(novo_centro)
        banco.commit()

        centro_id = novo_centro.id
        return jsonify({"msg": "Usuário criado com sucesso", "centro_id": centro_id}), 201
    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar usuário.: {str(e)}"}), 500
    finally:
        banco.close()


@app.route('/listar_encomendas', methods=['GET'])
def listar_encomendas():
    """
    **API para Listagem de Encomendas**

    ### Endpoint:
    GET /listar_encomendas

    ### Respostas (JSON):
    * **200 OK:** Lista de encomendas retornada com sucesso.
      ```json
      [
          {
              "id": 1,
              "codigo_rastreio": "FLASH987654",
              "nome": "Smartphone",
              "fragilidade": "Alta",
              "tipo": "Eletrônicos",
              "criado_em": "Mon, 18 May 2026 15:42:00 GMT"
          }
      ]
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao listar encomendas.: [Descrição do Erro]"
      }
      ```
    """
    try:
        listador = ListarEncomendas()
        resultado = listador.todas()
        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"msg": f"Erro ao listar encomendas.: {str(e)}"}), 500


@app.route('/buscar_encomenda/<string:codigo_rastreio>', methods=['GET'])
def buscar_encomenda(codigo_rastreio):
    """
    **API para Busca de Encomenda por Código de Rastreio**

    ### Endpoint:
    GET /buscar_encomenda/<codigo_rastreio>

    ### Respostas (JSON):
    * **200 OK:** Encomenda encontrada com sucesso (inclui histórico de movimentações).
      ```json
      {
          "id": 1,
          "codigo_rastreio": "FLASH987654",
          "nome": "Smartphone",
          "fragilidade": "Alta",
          "tipo": "Eletrônicos",
          "criado_em": "Mon, 18 May 2026 15:42:00 GMT",
          "historico": [
              {
                  "id": 5,
                  "status": "Em trânsito",
                  "localizacao": "São Paulo - SP",
                  "data_hora": "Tue, 19 May 2026 10:30:00 GMT",
                  "encomenda_id": 1,
                  "entregador_id": 2,
                  "usuario_id": 1
              }
          ]
      }
      ```
    * **404 Not Found:** Encomenda não encontrada no banco de dados.
      ```json
      {
          "msg": "Encomenda não encontrada"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao buscar encomenda.: [Descrição do Erro]"
      }
      ```
    """
    banco = SessionLocal()
    try:
        buscador = BuscarEncomenda()
        resultado = buscador.por_codigo(codigo_rastreio)

        if resultado:
            movimentacoes = banco.query(Movimentacao).filter(
                Movimentacao.encomenda_id == resultado["id"]
            ).order_by(Movimentacao.data_hora.desc()).all()

            resultado["historico"] = [m.serialize() for m in movimentacoes]

            return jsonify(resultado), 200

        return jsonify({"msg": "Encomenda não encontrada"}), 404

    except Exception as e:
        return jsonify({"msg": f"Erro ao buscar encomenda.: {str(e)}"}), 500
    finally:
        banco.close()


@app.route('/cadastro_movimentacao', methods=['POST'])
def cadastro_movimentacao():
    """
    **API para Cadastro de Movimentações por Código de Rastreio**

    ### Endpoint:
    POST /cadastro_movimentacao

    ### Parâmetros de Entrada (JSON):
    ```json
    {
        "status": "string (obrigatório) - Ex: Em trânsito, Entregue, Aguardando",
        "localizacao": "string (obrigatório) - Cidade, filial ou coordenadas atuais",
        "codigo_rastreio": "string (obrigatório) - Código único de rastreio da encomenda",
        "usuario_id": "integer (obrigatório) - ID do usuário que registrou",
        "entregador_id": "integer (opcional) - ID do entregador responsável"
    }
    ```

    ### Respostas (JSON):
    * **201 Created:** Movimentação registrada com sucesso.
      ```json
      {
          "msg": "Movimentação registrada com sucesso",
          "movimentacao_id": 1
      }
      ```
    * **400 Bad Request:** Ausência de campos obrigatórios.
      ```json
      {
          "msg": "Os campos status, localizacao, codigo_rastreio e usuario_id são obrigatórios"
      }
      ```
    * **404 Not Found:** Código de rastreio não cadastrado no sistema.
      ```json
      {
          "msg": "Encomenda com o código [CÓDIGO] não foi encontrada"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar movimentação.: [Descrição do Erro]"
      }
      ```
    """
    dados = request.get_json()

    status = dados.get('status')
    localizacao = dados.get('localizacao')
    codigo_rastreio = dados.get('codigo_rastreio')
    usuario_id = dados.get('usuario_id')
    entregador_id = dados.get('entregador_id')

    if not status or not localizacao or not codigo_rastreio or not usuario_id:
        return jsonify({"msg": "Os campos status, localizacao, codigo_rastreio e usuario_id são obrigatórios"}), 400

    banco = SessionLocal()
    try:
        # buscar encomenda pelo codigo
        encomenda = banco.query(Encomenda).filter(Encomenda.codigo_rastreio == codigo_rastreio).first()

        if not encomenda:
            return jsonify({"msg": f"Encomenda com o código {codigo_rastreio} não foi encontrada"}), 404

        nova_movimentacao = Movimentacao(
            status=status, localizacao=localizacao,
            encomenda_id=encomenda.id,
            usuario_id=usuario_id,
            entregador_id=entregador_id
        )

        banco.add(nova_movimentacao)
        banco.commit()

        return jsonify({
            "msg": "Movimentação registrada com sucesso",
            "movimentacao_id": nova_movimentacao.id
        }), 201

    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar movimentação.: {str(e)}"}), 500
    finally:
        banco.close()


def gerar_codigo_unico(banco):
    # gerar codigo
    while True:
        numeros = ''.join(random.choices(string.digits, k=6))
        codigo = f"FLASH{numeros}"

        # verifica se o código já existe na tabela Encomenda
        existe = banco.query(Encomenda).filter(Encomenda.codigo_rastreio == codigo).first()
        if not existe:
            return codigo


@app.route('/gerar_codigo_rastreio', methods=['GET'])
def obter_codigo_rastreio():
    """
    **API para Geração de Código de Rastreio Único**

    ### Endpoint:
    GET /gerar_codigo_rastreio

    ### Respostas (JSON):
    * **200 OK:** Código de rastreio gerado e validado com sucesso.
      ```json
      {
          "codigo_rastreio": "FLASH381947"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao gerar código de rastreio.: [Descrição do Erro]"
      }
      ```
    """
    banco = SessionLocal()
    try:
        codigo_unico = gerar_codigo_unico(banco)
        return jsonify({"codigo_rastreio": codigo_unico}), 200

    except Exception as e:
        return jsonify({"msg": f"Erro ao gerar código de rastreio.: {str(e)}"}), 500
    finally:
        banco.close()


# Mostrar entrega
if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")  # Rodar em uma porta diferente da API principal
