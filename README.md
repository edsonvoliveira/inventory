# 📦 Inventário — Sistema de Gestão de Estoque

Projeto desenvolvido com **Python**, **FastAPI**, **SQLite** e **Flet**.

## 🧭 Estrutura Geral
inventario/
├── backend/ # API e banco de dados
├── desktop/ # Aplicativo desktop (Flet)
├── mobile/ # Aplicativo móvel (scanner de códigos)
├── components/ # Componentes reutilizáveis

## ⚙️ Tecnologias
- **Backend:** FastAPI, SQLAlchemy, SQLite
- **Frontend Desktop:** Flet
- **Mobile:** Flet (planejado)
- **Linguagem:** Python 3.13+

## 🚀 Objetivos
1. CRUD de empresas, estoques e produtos  
2. Importar dados de CSV  
3. Visualizar e editar informações  
4. Sincronizar com API (FastAPI)

## 📚 Como rodar (prévia)
**Backend**
```bash
cd backend/app
uvicorn app.main:app --reload
cd desktop
python app.py

📄 Licença

Projeto de uso educacional — base para estudos e práticas de desenvolvimento Python + Flet.

