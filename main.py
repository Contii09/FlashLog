from flask import Flask, jsonify, request
from sqlalchemy import select
from models import Usuario, Encomenda, Entregador, CentroDeTranporcacao, Cliente, ListarEncomendas, BuscarEncomenda

app = Flask(__name__)
