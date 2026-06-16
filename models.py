from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, func, ForeignKey, select
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, Session
from werkzeug.security import generate_password_hash, check_password_hash


engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/flashlog')
Base = declarative_base()

SessionLocal = scoped_session(sessionmaker(bind=engine))


class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    def setar_senha_hash(self,senha):
        self.senha = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha, senha)

    def serialize(self):
        dados = {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "criado_em": self.criado_em,
        }
        return dados

class Encomenda(Base):
    __tablename__ = 'encomendas'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    codigo_rastreio = Column(String(50), unique=True, nullable=False)
    fragilidade = Column(String(255), nullable=False)
    tipo = Column(String(255), nullable=False)
    remetente = Column(String(255), nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "nome": self.nome,
            "codigo_rastreio": self.codigo_rastreio,
            "fragilidade": self.fragilidade,
            "tipo": self.tipo,
            "remetente": self.remetente,
            "criado_em": self.criado_em
        }
        return dados

class Entregador(Base):
    __tablename__ = 'entregadores'

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    veiculo = Column(String(255), nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())


    def serialize(self):

        dados = {
            "id": self.id,
            "nome": self.nome,
            "veiculo": self.veiculo,
            "criado_em": self.criado_em
        }
        return dados



class Veiculo(Base):
    __tablename__ = 'veiculos'
    id = Column(Integer, primary_key=True)
    modelo = Column(String(255), nullable=False)

    def serialize(self):

        dados = {
            "id": self.id,
            "modelo": self.modelo

        }
        return dados

class BuscarVeiculo:
    def por_id(self,id):

        db: Session = SessionLocal()
        try:
            consulta = select(Veiculo).filter(Veiculo.id == id)
            veiculo = db.scalar(consulta)
            if veiculo:
                return veiculo.serialize()
            return None
        finally:
            db.close()


class CentroDeTranporcacao(Base):
    __tablename__ = 'centro_de_transporcacoes'
    id = Column(Integer, primary_key=True)
    localizacao = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "localizacao": self.localizacao,
            "nome": self.nome,
            "criado_em": self.criado_em
        }
        return dados


class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250), nullable=False)
    email = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    endereco = Column(String(250), nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    def setar_senha_hash(self,senha):
        self.senha = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha, senha)


    def serialize(self):
        dados = {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "endereco": self.endereco,
            "criado_em": self.criado_em
        }
        return dados


class BuscarEncomenda:
    def por_codigo(self, codigo_rastreio: str):
        db: Session = SessionLocal()
        try:
            consulta = select(Encomenda).filter(Encomenda.codigo_rastreio == codigo_rastreio)
            encomenda = db.scalar(consulta)

            if encomenda:
                return encomenda.serialize()
            return None
        finally:
            db.close()


class BuscarCentroDeTransporte:
    def por_id(self, centro_id: int):
        db: Session = SessionLocal()
        try:
            consulta = select(CentroDeTranporcacao).filter(CentroDeTranporcacao.id == centro_id)
            centro = db.scalar(consulta)

            if centro:
                return centro.serialize()
            return None
        finally:
            db.close()

class BuscarGalpoes:
    def por_id(self, galpoes_id: int):
        db: Session = SessionLocal()
        try:
            consulta = select(Galpao).filter(Galpao.id == galpoes_id)
            galpao = db.scalar(consulta)

            if galpao:
                return galpao.serialize()
            return None
        finally:
            db.close()


class BuscarCliente:
    def por_id(self, cliente_id: int):
        db: Session = SessionLocal()
        try:
            consulta = select(Cliente).filter(Cliente.id == cliente_id)
            cliente = db.scalar(consulta)

            if cliente:
                return cliente.serialize()
            return None
        finally:
            db.close()


class BuscarUsuario:
    def por_id(self, id):
        db: Session = SessionLocal()
        try:
            consulta = select(Usuario).filter(Usuario.id == id)
            usuario  = db.scalar(consulta)

            if usuario:
                return usuario.serialize()
            return None

        finally:
            db.close()


class BuscarEntregador:
    def por_id(self,id):

        db: Session = SessionLocal()
        try:
            consulta = select(Entregador).filter(Entregador.id == id)
            entregador = db.scalar(consulta)
            if entregador:
                return entregador.serialize()
            return None
        finally:
            db.close()


class ListarEncomendas:
    def todas(self):
        db: Session = SessionLocal()
        try:
            consulta = select(Encomenda)
            encomendas = db.scalars(consulta).all()

            return [encomenda.serialize() for encomenda in encomendas]
        finally:
            db.close()

class ListarVeiculos:
    def todas(self):
        db: Session = SessionLocal()
        try:
            consulta = select(Veiculo)
            veiculos = db.scalars(consulta).all()

            return [veiculo.serialize() for veiculo in veiculos]
        finally:
            db.close()

class ListarClientes:
    def todas(self):
        db: Session = SessionLocal()
        try:
            consulta = select(Cliente)
            clientes = db.scalars(consulta).all()

            return [cliente.serialize() for cliente in clientes]
        finally:
            db.close()


class ListarGalpoes:
    def todas(self):
        db: Session = SessionLocal()
        try:
            consulta = select(Galpao)
            galpoes = db.scalars(consulta).all()

            return [galpao.serialize() for galpao in galpoes]
        finally:
            db.close()


class ListarMovimentacoes:
    def todas(self):
        db: Session = SessionLocal()
        try:
            consulta = select(Movimentacao)
            movimentacoes = db.scalars(consulta).all()

            return [movimentacao.serialize() for movimentacao in movimentacoes]
        finally:
            db.close()


class Movimentacao(Base):
    __tablename__ = 'movimentacoes'
    id = Column(Integer, primary_key=True)
    situacao = Column(String(100), nullable=False) #Em trânsito/Entregue
    data_hora = Column(DateTime, nullable=False, server_default=func.now())

    encomenda_id = Column(Integer, ForeignKey('encomendas.id'), nullable=False)
    galpao_id = Column(Integer, ForeignKey('galpoes.id'), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "situacao": self.situacao,
            "data_hora": self.data_hora,
            "encomenda_id": self.encomenda_id,
            "galpoes_id": self.galpao_id

        }

class Galpao(Base):
    __tablename__ = "galpoes"

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    localizacao = Column(String(255), nullable=False)
    capacidade = Column(String(255), nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "localizacao": self.localizacao,
            "nome": self.nome,
            "capacidade": self.capacidade,
            "criado_em": self.criado_em
        }
        return dados


Base.metadata.create_all(engine) #Cria as tabelas