from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    endereco = Column(String, nullable=True)

    # Relationship with stockrooms
    estoques = relationship("Estoque", back_populates="empresa")

class Estoque(Base):
    __tablename__ = "estoques"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    # Relationship with empresa
    empresa = relationship("Empresa", back_populates="estoques")
    # Relationship with products
    produtos = relationship("Produto", back_populates="estoque")

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    codigo_barra = Column(String, unique=True, index=True, nullable=False)
    preco = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False)
    estoque_id = Column(Integer, ForeignKey("estoques.id"), nullable=False)

    # Relationship with stockroom
    estoque = relationship("Estoque", back_populates="produtos")