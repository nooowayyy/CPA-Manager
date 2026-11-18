# CPA Manager

Aplicação Django independente para registrar, importar e analisar investimento em campanhas, cliques e conversões, com foco em **CPC (custo por clique)** e **CPA (custo por aquisição/conversão)**. Foi construída para manter a identidade visual e a arquitetura modular do LTV Manager e permitir integração futura com ele e com um projeto principal Django.

> **Limite importante:** esta versão é funcional para cadastro manual, importação CSV/XLSX, dashboard, gráficos e exportação. Não possui conectores de Meta Ads, Google Ads, TikTok Ads ou marketplaces; não faz OAuth nem sincronização automática. A API de métricas possui autenticação Bearer por conta, com chaves armazenadas como hash e revogáveis pela interface.

## 1. O que o sistema faz

- Registra campanhas com plataforma, canal, objetivo e identificadores de integração; permite arquivar sem apagar o histórico de desempenho.
- Registra desempenho diário com gasto, cliques, conversões e impressões opcionais.
- Calcula CPC, CPA, taxa de conversão e CTR quando há denominador disponível.
- Mostra KPIs, evolução diária de CPC e CPA e comparação entre campanhas.
- Filtra o dashboard por período.
- Importa CSV/XLSX com pré-visualização, validação por linha e confirmação.
- Atualiza reimportações quando a combinação de origem e ID externo é estável; não deduplica linhas sem ID por heurística fraca.
- Exporta registros de desempenho em CSV.
- Disponibiliza endpoint de leitura `/api/v1/metrics/` com `schema_version` e autenticação Bearer por conta.
- Permite gerar e revogar chaves de integração; cada chave é exibida uma única vez e dá acesso somente às métricas da conta emissora.
- Isola todos os dados por usuário e mantém banco próprio.

## 2. Requisitos

- Windows 10/11.
- Python 3.12 ou 3.13 (recomendado: 3.12).
- Navegador moderno.
- Internet na primeira instalação para baixar dependências e carregar Chart.js/Inter por CDN.

Dependências: Django 5.2, dj-database-url, python-dotenv, openpyxl, WhiteNoise e psycopg.

## 3. Instalação pelo CMD

Extraia o ZIP em uma pasta, por exemplo `C:\Projetos\cpa_manager`. Abra o CMD nessa pasta e execute:

```bat
scripts\preparar_ambiente.bat
```

O script cria `.env`, cria o ambiente virtual, instala dependências, aplica migrações e executa `manage.py check`.

Para iniciar:

```bat
scripts\iniciar_servidor.bat
```

Acesse [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Crie sua conta em **Criar conta**. O painel administrativo fica em `/admin/` e pode ser habilitado com `venv\Scripts\python.exe manage.py createsuperuser`. O cadastro próprio fica ativado somente no `config/settings.py` deste pacote (`CPA_ENABLE_REGISTRATION=True`); ao incorporar o app a outro projeto, mantenha essa opção desativada e use o cadastro central.

### Comandos equivalentes

```bat
python -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py check
python manage.py runserver
```

## 4. Configuração

Ajuste `.env` quando necessário:

```ini
SECRET_KEY=troque-por-uma-chave-longa-e-aleatoria
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
DATABASE_URL=sqlite:///db.sqlite3
TIME_ZONE=America/Sao_Paulo
```

SQLite é suficiente para uso local. Para hospedagem, configure PostgreSQL e `DEBUG=False`, segredo exclusivo, HTTPS, hosts restritos, backups e credenciais fora do repositório. Execute também `python manage.py collectstatic --noinput` na implantação.

## 5. Como usar

1. Crie uma campanha em **Campanhas**. Defina o objetivo (compra, lead, cadastro ou outra conversão), plataforma, canal e, quando disponíveis, ID externo e chave estável de integração.
2. Registre dados diários em **Desempenho** ou importe um CSV/XLSX em **Importações**.
3. No dashboard, escolha o período. CPC é gasto total dividido por cliques totais; CPA é gasto total dividido por conversões totais.
4. Use **Exportar CSV** para extrair a base registrada.

A taxa de conversão é conversões divididas por cliques. CTR é cliques divididos por impressões quando impressões foram fornecidas. Se o denominador for zero, a interface mostra `—` e a API retorna `null`, nunca um zero artificial. Campanhas criadas automaticamente pela importação começam com objetivo **Outra conversão** para não presumir que todo resultado seja compra; revise o objetivo na tela de campanhas quando souber o tipo da ação.

### Importação

Campos mínimos: `data`, `campanha`, `gasto`, `cliques` e `conversoes`. Cabeçalhos em português/inglês são reconhecidos. O campo opcional `objetivo` aceita `purchase`, `lead`, `signup`, `click` ou `other` (também reconhece alguns rótulos em português). O modelo está em `docs/modelo_importacao_desempenho.csv`. Limites: 10 MB e 2.000 linhas por arquivo; a tela mostra até 30 linhas de prévia e a confirmação processa todas as linhas válidas. Use `external_id` estável para atualização idempotente na reimportação.

Uma linha representa o desempenho diário agregado de uma campanha. Não misture moedas no mesmo conjunto de métricas; a interface desta versão assume BRL.

## 6. Entender CPA e CPC

- **CPC:** investimento dividido pelo número de cliques.
- **CPA:** investimento dividido pela quantidade de conversões definida no objetivo da campanha.
- **Taxa de conversão:** conversões divididas por cliques.

Os indicadores de um período são calculados pela soma dos numeradores e denominadores. Não se faz média simples de CPC/CPA diários, pois isso distorceria o resultado quando os volumes variam.

Uma conversão pode ser lead, cadastro ou compra. O CPA consolidado combina as ações registradas; quando os objetivos são diferentes, compare campanhas com o mesmo objetivo. Uma conversão não é automaticamente uma comissão aprovada nem uma aquisição individual no LTV Manager.

## 7. Integração futura com LTV Manager / projeto principal

Consulte `docs/CONTRATO_INTEGRACAO_V1.md` e `docs/INTEGRACAO_DJANGO_PRINCIPAL.md`. No modo de serviços independentes, CPA Manager, LTV Manager e o projeto principal (como ROI Manager/Skallora) mantêm bancos separados e conversam por API HTTPS versionada. No modo de incorporação, as tabelas CPA passam a pertencer ao banco do projeto principal, usando o app namespaced `cpa`. O CPA oferece tokens Bearer por conta, somente leitura. `Campaign.integration_key` e `Campaign.external_id` são pontos de mapeamento.

O endpoint `/api/v1/metrics/` aceita sessão autenticada ou token Bearer por conta, criado na tela **Integrações**. Ainda não há sincronização automática, webhooks ou rate limiting avançado. Dados agregados não permitem identificar quais aquisições individuais geraram as conversões; para isso será necessário receber eventos com ID de conversão e tracking comprovados.

## 8. Testes

Execute:

```bat
scripts\verificar_projeto.bat
```

Ou diretamente:

```bat
venv\Scripts\python.exe manage.py test cpa.tests
```

## 9. Estrutura

- `config/`: configurações Django.
- `cpa/`: models, forms, views, analytics, importador, testes e API.
- `templates/cpa/`: interface Django com namespace visual próprio.
- `static/cpa/css/`: design system modular sem colisão com o app principal.
- `static/cpa/js/`: navegação e gráficos.
- `scripts/`: atalhos CMD.
- `docs/`: modelo CSV, contrato de integração, guia de incorporação no Django principal e bíblia de reconstrução.

## 10. Limitações conhecidas

- Sem conectores ou OAuth de plataformas de anúncio.
- Sem coleta automática, webhooks ou sincronização automática entre serviços.
- Sem atribuição individual de conversões.
- Sem suporte a múltiplas moedas, ROAS ou lucro líquido.
- Chart.js e Inter são carregados por CDN; uso totalmente offline exige vendorização local com licenças/versionamento.

**Documentação técnica:** `docs/BIBLIA_RECONSTRUCAO.md`.
