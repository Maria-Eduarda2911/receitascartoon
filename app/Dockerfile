FROM python:3.12-slim

# Usuário sem privilégios (boa prática de segurança)
RUN useradd -r -u 1001 appuser

WORKDIR /app

# Instala as dependências (incluindo pytest para os testes)
COPY requirements.txt requirements_2.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytest

# Copia o código da aplicação e os testes
COPY app.py seed_data.py ./
COPY templates/ templates/
COPY static/ static/
COPY tests/ tests/

# Executa os testes automatizados durante o build da imagem
RUN export USE_SQLITE=1 && python -m pytest tests/

USER 1001
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]