import random, datetime
import string
from flask import jsonify, request
from sqlalchemy import select
from main import app
from models import Usuario, Encomenda, Entregador, CentroDeTranporcacao, Cliente, SessionLocal, ListarEncomendas, \
    BuscarEncomenda, Movimentacao, BuscarCentroDeTransporte, BuscarCliente, BuscarEntregador, BuscarUsuario


@app.route('/cadastro_encomendas', methods=['POST'])
def cadastro_encomendas():
    """
    **API para Cadastro de Encomendas**
    ### Endpoint:
    POST /cadastro_encomendas

    ### Parametros de Entrada (JSON):
    ```json
    {
        "nome": "string (obrigatorio) - Nome ou descricao do item",
        "fragilidade": "string (obrigatorio) - Nivel de fragilidade (Ex: Alta, Baixa)",
        "tipo": "string (obrigatorio) - Categoria do produto"
    }
    ```

    ### Respostas (JSON):
    * **201 Created:** Encomenda registrada com sucesso (com codigo gerado automaticamente).
      ```json
      {
          "msg": "Encomenda criada com sucesso",
          "encomenda_id": 1,
          "codigo_rastreio": "FLASH123456"
      }
      ```
    * **400 Bad Request:** Ausencia de campos obrigatorios.
      ```json
      {
          "msg": "Os campos nome, fragilidade e tipo sao obrigatorios"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar encomenda.: [Descricao do Erro]"
        }
        ```
      """
    dados = request.get_json()
    nome = dados.get('nome')
    fragilidade = dados.get('fragilidade')
    tipo = dados.get('tipo')

    if not nome or not fragilidade or not tipo:
        return jsonify({"msg": "Os campos nome, fragilidade e tipo sao obrigatorios"}), 400

    banco = SessionLocal()
    try:
        # chamei a função do codigo em uma variavel
        codigo_gerado = gerar_codigo_unico(banco)

        nova_encomenda = Encomenda(
            codigo_rastreio=codigo_gerado,
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
       **API para Cadastro de Usuario**

       ### Endpoint:
       POST /cadastro_usuario

       ### Parametros de Entrada (JSON):
       ```json
       {
           "nome": "string (obrigatorio) - Nome completo do usuario",
           "email": "string (obrigatorio) - Endereco de e-mail unico",
           "senha": "string (obrigatorio) - Senha em texto limpo para criptografia"
       }
       ```

       ### Respostas (JSON):
       * **201 Created:** Usuario registrado com sucesso.
         ```json
         {
             "msg": "Usuario criado com sucesso",
             "usuario_id": 1
         }
         ```
       * **400 Bad Request:** Ausencia de campos obrigatorios.
         ```json
         {
             "msg": "Os campos Nome, Email e Senha sao obrigatorios"
         }
         ```
       * **409 Conflict:** E-mail ja cadastrado no sistema.
         ```json
         {
             "msg": "Este e-mail ja esta cadastrado"
         }
         ```
       * **500 Internal Server Error:** Falha operacional no banco de dados.
         ```json
         {
             "msg": "Erro ao registrar usuario.: [Descricao do Erro]"
         }
         ```
       """
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({"msg": "Os campos Nome, Email e Senha sao obrigatorios"}), 400

    banco = SessionLocal()
    try:
        # Busca utilizando select e .where para verificar e-mail duplicado
        consulta = select(Usuario).where(Usuario.email == email)
        usuario_existente = banco.execute(consulta).scalar_one_or_none()

        if usuario_existente:
            return jsonify({"msg": "Este e-mail ja esta cadastrado"}), 409

        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.setar_senha_hash(senha)
        banco.add(novo_usuario)
        banco.commit()
        return jsonify({"msg": "Usuario criado com sucesso", "usuario_id": novo_usuario.id}), 201
    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar usuario.: {str(e)}"}), 500
    finally:
        banco.close()

@app.route('/cadastro_cliente', methods=['POST'])
def cadastro_cliente():
    """
    **API para Cadastro de Cliente**
    ### Endpoint:
    POST /cadastro_cliente

    ### ParAmetros de Entrada (JSON):
    ```json
    {
        "nome": "string (obrigatorio) - Nome ou descricao da cliente",
        "email": "string (obrigatorio) - Endereco de e-mail unico",
        "senha": "string (obrigatorio) - Senha em texto limpo para criptografia",
        "endereco": "boolean/string (obrigatorio) - Indicador de endereco",
        "produto": "string (obrigatorio) - Tipo de produto/encomenda"
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
    * **400 Bad Request:** Ausencia de campos obrigatorios.
      ```json
      {
          "msg": "Os campos Nome, Email, Senha, Endereco e Produto sao obrigatorios"
      }
      ```
    * **409 Conflict:** E-mail ja cadastrado.
      ```json
      {
          "msg": "Este e-mail ja esta cadastrado"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar cliente.: [Descricao do Erro]"
      }
      ```
    """
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    endereco = dados.get('endereco')
    produto = dados.get('produto')

    if not nome or not email or not senha or not endereco or not produto:
        return jsonify({"msg": "Os campos Nome, Email, Senha, Endereco e Produto sao obrigatorios"}), 400

    banco = SessionLocal()
    try:
        # Busca utilizando select e .where para verificar e-mail duplicado
        consulta = select(Cliente).where(Cliente.email == email)
        cliente_existente = banco.execute(consulta).scalar_one_or_none()

        if cliente_existente:
            return jsonify({"msg": "Este e-mail ja esta cadastrado"}), 409

        novo_cliente = Cliente(nome=nome, email=email, endereco=endereco, produto=produto)
        if hasattr(novo_cliente, 'setar_senha_hash'):
            novo_cliente.setar_senha_hash(senha)

        banco.add(novo_cliente)
        banco.commit()
        return jsonify({"msg": "Cliente criado com sucesso", "cliente_id": novo_cliente.id}), 201
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

      ### ParAmetros de Entrada (JSON):
      ```json
      {
          "nome": "string (obrigatorio) - Nome ou descricao da encomenda",
          "veiculo": "boolean/string (obrigatOrio) - Indicador o veiculo do entregador",

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
      * **400 Bad Request:** Ausencia de campos obrigatorios.
        ```json
        {
            "msg": "Os campos Nome e veiculo sao obrigatorios"
        }
        ```
      * **500 Internal Server Error:** Falha operacional no banco de dados.
        ```json
        {
            "msg": "Erro ao registrar usuario.: [Descricao do Erro]"
        }
        ```
      """
    dados = request.get_json()
    nome = dados.get('nome')
    veiculo = dados.get('veiculo')

    if not nome or not veiculo:
        return jsonify({"msg": "Os campos Nome e veiculo sao obrigatorios"}), 400

    banco = SessionLocal()
    try:
        novo_entregador = Entregador(nome=nome, veiculo=veiculo)
        banco.add(novo_entregador)
        banco.commit()
        return jsonify({"msg": "Entregador criado com sucesso", "entregador_id": novo_entregador.id}), 201
    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar entregador.: {str(e)}"}), 500
    finally:
        banco.close()

@app.route('/cadastro_centro_transporte', methods=['POST'])
def cadastro_centro_transporte():
    """
    **API para Cadastro do centro de transporte

    ### Endpoint:
    POST /cadastro_centro_transporte

    ### ParAmetros de Entrada (JSON):
    ```json
    {
        "nome": "string (obrigatorio) - Nome ou descricao da encomenda",
        "localizacao": "boolean/string (obrigatorio) - Indicador de localizacao da transportadora",

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
    * **400 Bad Request:** Ausencia de campos obrigatorios.
      ```json
      {
          "msg": "Os campos Nome, localizacao sao obrigatorios"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao registrar a transportadora.: [Descricao do Erro]"
      }
      ```
    """
    dados = request.get_json()
    nome = dados.get('nome')
    localizacao = dados.get('localizacao')

    if not nome or not localizacao:
        return jsonify({"msg": "Os campos Nome e localizacao sao obrigatorios"}), 400

    banco = SessionLocal()
    try:
        novo_centro = CentroDeTranporcacao(nome=nome, localizacao=localizacao)
        banco.add(novo_centro)
        banco.commit()
        return jsonify({"msg": "Centro criado com sucesso", "centro_id": novo_centro.id}), 201
    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar centro.: {str(e)}"}), 500
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
                 "tipo": "Eletronicos",
                 "criado_em": "Mon, 18 May 2026 15:42:00 GMT"
             }
         ]
         ```
       * **500 Internal Server Error:** Falha operacional no banco de dados.
         ```json
         {
             "msg": "Erro ao listar encomendas.: [Descricao do Erro]"
         }
         ```
       """
    try:
        listador = ListarEncomendas()
        return jsonify(listador.todas()), 200
    except Exception as e:
        return jsonify({"msg": f"Erro ao listar encomendas.: {str(e)}"}), 500

@app.route('/buscar_encomenda/<string:codigo_rastreio>', methods=['GET'])
def buscar_encomenda(codigo_rastreio):
    """
        **API para Busca de Encomenda por Codigo de Rastreio**

        ### Endpoint:
        GET /buscar_encomenda/<codigo_rastreio>

        ### Respostas (JSON):
        * **200 OK:** Encomenda encontrada com sucesso (inclui historico de movimentacoes).
          ```json
          {
              "id": 1,
              "codigo_rastreio": "FLASH987654",
              "nome": "Smartphone",
              "fragilidade": "Alta",
              "tipo": "Eletronicos",
              "criado_em": "Mon, 18 May 2026 15:42:00 GMT",
              "historico": [
                  {
                      "id": 5,
                      "status": "Em transito",
                      "localizacao": "Sao Paulo - SP",
                      "data_hora": "Tue, 19 May 2026 10:30:00 GMT",
                      "encomenda_id": 1,
                      "entregador_id": 2,
                      "usuario_id": 1
                  }
              ]
          }
          ```
        * **404 Not Found:** Encomenda nao encontrada no banco de dados.
          ```json
          {
              "msg": "Encomenda nao encontrada"
          }
          ```
        * **500 Internal Server Error:** Falha operacional no banco de dados.
          ```json
          {
              "msg": "Erro ao buscar encomenda.: [Descricao do Erro]"
          }
          ```
        """
    banco = SessionLocal()
    try:
        buscador = BuscarEncomenda()
        resultado = buscador.por_codigo(codigo_rastreio)

        if resultado:
            # Busca utilizando select e .where, ordenando de forma decrescente
            consulta = (
                select(Movimentacao)
                .where(Movimentacao.encomenda_id == resultado["id"])
                .order_by(Movimentacao.data_hora.desc())
            )
            movimentacoes = banco.execute(consulta).scalars().all()

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
    **API para Cadastro de Movimentacoes por Codigo de Rastreio**

    ### Endpoint:
    POST /cadastro_movimentacao

    ### ParAmetros de Entrada (JSON):
    ```json
    {
        "situacao": "string (obrigatorio) - Ex: Em transito, Entregue, Aguardando",
        "localizacao": "string (obrigatorio) - Cidade, filial ou coordenadas atuais",
        "codigo_rastreio": "string (obrigatorio) - Codigo unico de rastreio da encomenda",
        "usuario_id": "integer (obrigatorio) - ID do usuario que registrou",
        "entregador_id": "integer (opcional) - ID do entregador responsavel"
    }
    ```
    ### Respostas (JSON):
    * **201 Created:** Movimentacao registrada com sucesso.
      ```json
      {
          "msg": "Movimentacao registrada com sucesso",
          "movimentacao_id": 1
      }
      ```
    * **400 Bad Request:** Ausencia de campos obrigatorios.
      ```json
      {
          "msg": "Os campos situacao, localizacao, codigo_rastreio e usuario_id sao obrigatorios"
      }
      ```
    * **404 Not Found:** Codigo de rastreio nao cadastrado no sistema.
      ```json
      {
          "msg": "Encomenda com o codigo [CoDIGO] nao foi encontrada"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {1
          "msg": "Erro ao registrar movimentacao.: [Descricao do Erro]"
      }
      ```
    """
    dados = request.get_json()

    print("DADOS RECEBIDOS:", dados)
    situacao = dados.get('situacao')
    localizacao = dados.get('localizacao')
    codigo_rastreio = dados.get('codigo_rastreio')
    usuario_id = dados.get('usuario_id')
    entregador_id = dados.get('entregador_id')

    if not situacao or not localizacao or not codigo_rastreio or not usuario_id:
        return jsonify({"msg": "Os campos situacao, localizacao, codigo_rastreio e usuario_id sao obrigatorios"}), 400

    banco = SessionLocal()
    try:
        # Busca a encomenda utilizando select e .where
        consulta = select(Encomenda).where(Encomenda.codigo_rastreio == codigo_rastreio)
        encomenda = banco.execute(consulta).scalar_one_or_none()

        if not encomenda:
            return jsonify({"msg": f"Encomenda com o codigo {codigo_rastreio} nao foi encontrada"}), 404

        # Busca a ultima movimentacao utilizando select, .where e order_by
        consulta_ultima = (
            select(Movimentacao)
            .where(Movimentacao.encomenda_id == encomenda.id)
            .order_by(Movimentacao.data_hora.desc())
        )
        ultima = banco.execute(consulta_ultima).scalars().first()

        if ultima and ultima.situacao.lower() == "entregue":
            return jsonify({"msg": "Esta encomenda ja foi entregue e nao pode ser movimentada"}), 400

        nova_movimentacao = Movimentacao(
            situacao=situacao,
            localizacao=localizacao,
            encomenda_id=encomenda.id,
            usuario_id=usuario_id,
            entregador_id=entregador_id
        )
        banco.add(nova_movimentacao)
        banco.commit()
        return jsonify({"msg": "Movimentacao registrada com sucesso", "movimentacao_id": nova_movimentacao.id}), 201
    except Exception as e:
        banco.rollback()
        return jsonify({"msg": f"Erro ao registrar movimentacao.: {str(e)}"}), 500
    finally:
        banco.close()

def gerar_codigo_unico(banco):
    data = datetime.datetime.now()
    alfabeto = [
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
        "k", "l", "m","n", "o", "p", "q", "r", "s", "t", "u", "v",
        "w", "x", "y", "z"
    ]
    codigo = random.choice(alfabeto).upper()
    codigo1 = random.choice(alfabeto).upper()
    codigo2 = random.choice(alfabeto).upper()
    codigo_unico = str(data.timestamp()). replace(".", "")
    codigo_final = str(codigo+codigo1+codigo2)+codigo_unico

    conslta = select(Encomenda).where(Encomenda.codigo_rastreio == codigo_final)
    resultado = banco.execute(conslta).scalars().first()

    return codigo_final


@app.route('/buscar_centro_transporte/<int:centro_id>', methods=['GET'])
def buscar_centro_transporte(centro_id):
    """
    **API para Busca de Centro de Transporte por ID**

    ### Endpoint:
    GET /buscar_centro_transporte/<int:centro_id>

    ### Respostas (JSON):
    * **200 OK:** Centro de transporte encontrado com sucesso.
      ```json
      {
          "id": 1,
          "nome": "qqqq",
          "localizacao": "São Paulo"
      }
      ```
    * **404 Not Found:** Centro de transporte não encontrado.
      ```json
      {
          "msg": "Centro de transporte não encontrado"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao buscar centro de transporte.: [Descrição do Erro]"
      }
      ```
    """
    banco = SessionLocal()
    try:
        buscador = BuscarCentroDeTransporte()
        resultado = buscador.por_id(centro_id)

        if resultado:
            return jsonify(resultado), 200

        return jsonify({"msg": "Centro de transporte não encontrado"}), 404
    except Exception as e:
        return jsonify({"msg": f"Erro ao buscar centro de transporte.: {str(e)}"}), 500
    finally:
        banco.close()

@app.route('/buscar_cliente/<int:cliente_id>', methods=['GET'])
def buscar_cliente(cliente_id):
    """
    **API para Busca de Cliente por ID**

    ### Endpoint:
    GET /buscar_cliente/<int:cliente_id>

    ### Respostas (JSON):
    * **200 OK:** Cliente encontrado com sucesso.
      ```json
      {
        "nome": "selma",
        "email": "selma@gmail.com",
        "senha": "123",
        "endereco": "rua brasil 123",
        "produto": "tabua"
      }
      ```
    * **404 Not Found:** Cliente não encontrado.
      ```json
      {
          "msg": "Cliente não encontrado"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao buscar cliente.: [Descrição do Erro]"
      }
      ```
    """
    banco = SessionLocal()
    try:
        buscador = BuscarCliente()
        resultado = buscador.por_id(cliente_id)

        if resultado:
            return jsonify(resultado), 200

        return jsonify({"msg": "Centro de transporte não encontrado"}), 404
    except Exception as e:
        return jsonify({"msg": f"Erro ao buscar centro de transporte.: {str(e)}"}), 500
    finally:
        banco.close()

@app.route("/buscar_entregador/<int:entregador_id>", methods=['GET'])
def buscar_entregador(entregador_id):
    """
       **API para Busca de Entregador por ID**

       ### Endpoint:
       GET /buscar_entregador/<int:entregador_id>

       ### Respostas (JSON):
       * **200 OK:** Cliente encontrado com sucesso.
         ```json
         {
            "nome": "sm",
            "veiculo": "sm"
         }
         ```
       * **404 Not Found:** Entregador não encontrado.
         ```json
         {
             "msg": "Entregador não encontrado"
         }
         ```
       * **500 Internal Server Error:** Falha operacional no banco de dados.
         ```json
         {
             "msg": "Erro ao buscar entregador.: [Descrição do Erro]"
         }
         ```
       """
    banco = SessionLocal()
    try:
        buscador = BuscarEntregador()
        resultado = buscador.por_id(entregador_id)

        if resultado:
            return jsonify(resultado), 200
        return jsonify({"msg": "Entregador nao encontrada"}), 404
    except Exception as e:
        return jsonify({"msg":"Erro ao buscar entregador.:{str(e)}"}), 500
    finally:
        banco.close()

@app.route('/buscar_usuario/<int:usuario_id>', methods=['GET'])
def buscar_usuario(usuario_id):
    """
    **API para Busca de Usuario por ID**

    ### Endpoint:
    GET /buscar_usuario/<int:usuario_id>

    ### Respostas (JSON):
    * **200 OK:** Usuario encontrado com sucesso.
      ```json
      {
        "nome": "selma",
        "email": "asc@gmail.com",
        "senha": "123"
      }
      ```
    * **404 Not Found:** Usuario não encontrado.
      ```json
      {
          "msg": "Usuario não encontrado"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "Erro ao buscar usuario.: [Descrição do Erro]"
      }
      ```
    """
    banco = SessionLocal()
    try:
        buscador = BuscarUsuario()
        resultado = buscador.por_id(usuario_id)

        if resultado:
            return jsonify(resultado), 200

        return jsonify({"msg": "Usuario não encontrado"}), 404
    except Exception as e:
        return jsonify({"msg": f"Erro ao buscar usuarioi.: {str(e)}"}), 500
    finally:
        banco.close()


if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")

