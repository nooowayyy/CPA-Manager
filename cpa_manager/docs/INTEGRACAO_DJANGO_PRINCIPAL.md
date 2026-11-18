# Integração do CPA Manager a um projeto Django principal

O CPA Manager foi organizado para dois cenários. Escolha um deles; não copie o banco SQLite entre projetos.

## Opção A — serviços independentes (mais desacoplamento)

Mantenha CPA Manager e LTV Manager como aplicações separadas, cada uma com seu próprio banco. O projeto principal (ROI Manager/Skallora) atua como hub e consome a API versionada de cada serviço.

1. Instale e execute CPA Manager como descrito no `README.md`.
2. Crie uma chave em **Integrações** e guarde-a em um gestor de segredos no projeto principal.
3. Faça chamadas HTTPS a `GET /api/v1/metrics/`, enviando `Authorization: Bearer <token>`.
4. No projeto principal, implemente um adaptador que conheça `schema_version=1.0` e mantenha o mapeamento das campanhas por `integration_key` e `external_id`.
5. Faça o mesmo para a API futura/contrato do LTV Manager. Não conecte diretamente um banco ao outro.

Se o CPA Manager estiver publicado sob um prefixo de proxy, inclua esse prefixo na URL-base. A chave pertence a uma única conta e só lê as métricas dessa conta.

## Opção B — incorporar o app dentro do projeto principal

O pacote Django `cpa/` pode ser instalado como um app no projeto existente. Neste modo, o banco do projeto principal passa a conter as tabelas `cpa_*`; não instale uma segunda cópia do `config/` do CPA Manager.

1. Copie o diretório `cpa/` inteiro, incluindo `migrations/`, para a raiz do projeto principal.
2. Garanta que as dependências do `requirements.txt` estejam instaladas, especialmente Django compatível e `openpyxl`.
3. Adicione a aplicação:

```python
INSTALLED_APPS = [
    # ... apps do projeto principal
    "cpa.apps.CpaConfig",
]
```

4. Inclua as rotas com namespace próprio. Por exemplo, no `urls.py` principal:

```python
from django.urls import include, path

urlpatterns = [
    # ... rotas existentes
    path("cpa/", include(("cpa.urls", "cpa"), namespace="cpa")),
]
```

5. Copie `templates/cpa/` para o diretório de templates reconhecido pelo projeto e `static/cpa/` para uma pasta localizada pelos staticfiles finders. Os caminhos já usam o prefixo `cpa/` para evitar colisões com CSS, JavaScript e templates do sistema principal. Com a inclusão em `path("cpa/", ...)`, o endpoint fica em `/cpa/api/v1/metrics/`.
6. A aplicação usa `settings.AUTH_USER_MODEL`; mantenha o mesmo sistema de autenticação do projeto principal. Não crie outro modelo de usuário para o CPA.
7. Execute:

```bash
python manage.py migrate cpa
python manage.py seed_cpa_defaults
python manage.py check
```

O comando `seed_cpa_defaults` cria plataformas e canais padrão para usuários já existentes. O sinal de criação de usuário cobre novos cadastros posteriores.
8. Mantenha `LOGIN_URL` apontando para a tela de login do projeto principal. Não defina `CPA_ENABLE_REGISTRATION=True` no projeto principal: por padrão, a rota de cadastro local fica desativada. A rota de cadastro do CPA Manager no projeto independente é apenas um ponto de entrada demonstrativo; em um sistema integrado, use a autenticação e o cadastro centrais.

### O que permanece isolado

- Models e tabelas do CPA ficam dentro do app `cpa`.
- As URLs usam o namespace `cpa:` (por exemplo, `cpa:dashboard`), evitando colisões com o `dashboard` do sistema principal.
- CSS, JS e modelos têm prefixo `cpa/`.
- Os registros continuam limitados ao `request.user`.
- Os tokens de integração continuam associados a uma conta e podem ser revogados.

## Compatibilidade com LTV Manager e ROI Manager/Skallora

`Campaign.integration_key` deve ser preenchida com uma chave estável e compartilhada pelo integrador. `Campaign.external_id` guarda o ID do provedor de anúncios. A API entrega os dois campos, além de plataforma, canal e métricas agregadas.

O integrador deve manter uma tabela de correspondência entre os IDs de campanhas do CPA, campanhas do LTV e dimensões do projeto principal. Não dependa do `id` de banco de dados de outro serviço, nem do nome textual da campanha.

CPA registra investimento, cliques e conversões. LTV registra comissões aprovadas atribuídas a aquisições. Um total agregado de conversões não identifica individualmente as aquisições correspondentes. Para uma ligação individual, a origem precisa enviar IDs de conversão/tracking estáveis, sem dados pessoais, e a correspondência deve ser exata e sustentada por evidência.

## Cuidados antes de produção

- Publicar somente em HTTPS.
- Armazenar tokens fora do código e do banco de dados do consumidor.
- Revogar tokens quando um integrador for removido ou comprometido.
- Configurar `DEBUG=False`, hosts e CSRF corretos, backups e PostgreSQL no serviço independente.
- Implementar rate limiting e auditoria avançada das chamadas API.
- Não enviar CPF, telefone, e-mail ou outros dados pessoais de consumidores.
