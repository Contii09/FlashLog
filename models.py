from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, func, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, Session
from werkzeug.security import generate_password_hash, check_password_hash


engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/flashlog')
Base = declarative_base()


SessionLocal = scoped_session(sessionmaker(bind=engine))
Base.query = SessionLocal.query_property()


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
    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "nome": self.nome,
            "codigo_rastreio": self.codigo_rastreio,
            "fragilidade": self.fragilidade,
            "tipo": self.tipo,
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
    produto = Column(String(250), nullable=False)
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
            "produto": self.produto,
            "criado_em": self.criado_em
        }
        return dados


class BuscarEncomenda:
    def por_id(self, encomenda_id: int):
        db: Session = SessionLocal()
        try:
            encomenda = db.query(Encomenda).filter(Encomenda.id == encomenda_id).first()
            if encomenda:
                return encomenda.serialize()
            return None
        finally:
            db.close()

    def por_codigo(self, codigo_rastreio: str):
        db: Session = SessionLocal()
        try:
            encomenda = db.query(Encomenda).filter(Encomenda.codigo_rastreio == codigo_rastreio).first()
            if encomenda:
                return encomenda.serialize()
            return None
        finally:
            db.close()


class ListarEncomendas:
    def todas(self):
        db: Session = SessionLocal()
        try:
            encomendas = db.query(Encomenda).all()
            return [encomenda.serialize() for encomenda in encomendas]
        finally:
            db.close()




class Movimentacao(Base):
    __tablename__ = 'movimentacoes'
    id = Column(Integer, primary_key=True)
    status = Column(String(100), nullable=False) #Em trânsito/Entregue
    localizacao = Column(String(255), nullable=False)
    data_hora = Column(DateTime, nullable=False, server_default=func.now())

    encomenda_id = Column(Integer, ForeignKey('encomendas.id'), nullable=False)
    entregador_id = Column(Integer, ForeignKey('entregadores.id'), nullable=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "status": self.status,
            "localizacao": self.localizacao,
            "data_hora": self.data_hora,
            "encomenda_id": self.encomenda_id,
            "entregador_id": self.entregador_id,
            "usuario_id": self.usuario_id
        }

Base.metadata.create_all(engine)  #Cria as tabelas