# Contrato de integração — CPA Manager / LTV Manager / Projeto principal

**Versão:** 1.0  
**Estado:** API de leitura implementada com sessão Django ou token Bearer por conta. Sincronização automática com LTV Manager/ROI Manager ainda não implementada.

## 1. Princípios

- CPA Manager, LTV Manager e o projeto principal (por exemplo, ROI Manager/Skallora) mantêm bancos e ciclos de implantação independentes. O projeto principal pode atuar como hub de integração.
- Nenhum módulo importa models Django de outro módulo.
- Não compartilhar o arquivo SQLite entre projetos.
- Comunicação futura deve ocorrer por API HTTPS versionada, com autenticação serviço-a-serviço, escopo por conta, IDs externos estáveis, idempotência e logs sem segredos.
- Os dois lados devem preservar a origem e o horário de atualização dos dados.
- Valores monetários devem carregar moeda explícita no contrato de produção. Nesta versão local, a interface assume BRL (R$); não misture moedas no mesmo conjunto de métricas.

## 2. Chaves e correspondência

`Campaign.integration_key` é uma chave estável definida pelo usuário, única por conta quando preenchida. `Campaign.external_id` guarda o identificador da campanha no provedor de anúncios. Use esses campos para mapear campanhas entre CPA, LTV e o projeto principal.

O LTV Manager possui dimensões próprias de campanha, canal e marketplace. A integração deve manter uma tabela de mapeamento no serviço integrador com, no mínimo:

- `source_system`: `cpa_manager`, `ltv_manager` ou sistema de origem;
- `source_account_id`: identificador não sensível da conta no serviço de origem;
- `source_object_type`: por exemplo `campaign`;
- `source_object_id`: ID externo estável;
- `target_object_type` e `target_object_id`;
- `mapping_status`, `created_at`, `updated_at`.

Não usar o nome textual da campanha como chave primária de integração. Nomes podem mudar ou se repetir.

## 3. API implementada nesta versão

### `GET /api/v1/metrics/`

Requer sessão Django válida ou cabeçalho `Authorization: Bearer <token>` criado na tela **Integrações**. Para consumo pelo projeto principal, prefira o token Bearer por conta. Parâmetros opcionais:

- `start=YYYY-MM-DD`
- `end=YYYY-MM-DD`

Sem parâmetros, retorna os últimos 30 dias incluindo hoje. Intervalo máximo aceito: 10 anos.

Exemplo de resposta (valores ilustrativos):

```json
{
  "schema_version": "1.0",
  "currency": "BRL",
  "period": {"start": "2026-11-01", "end": "2026-11-30"},
  "totals": {
    "spend": "1000.00",
    "clicks": 5000,
    "conversions": 40,
    "impressions": 90000,
    "cpc": "0.20",
    "cpa": "25.00",
    "conversion_rate_percent": "0.80"
  },
  "daily": [],
  "campaigns": [{"name": "Campanha A", "integration_key": "campanha-a", "external_id": "ads-123", "platform": "Meta Ads", "channel": "Instagram", "objective": "purchase", "conversion_label": "Compras", "spend": "1000.00", "clicks": 5000, "conversions": 40, "cpc": "0.20", "cpa": "25.00"}]
}
```

`cpc` e `cpa` são `null` quando o denominador é zero. Cada item de `campaigns` inclui `integration_key`, `external_id`, plataforma, canal e métricas para facilitar o mapeamento. O contrato não expõe a chave primária local do banco; não dependa de IDs internos entre serviços. A API é restrita à conta associada ao token e não aceita `user_id` como parâmetro para trocar de conta.

**Limite operacional:** para integração entre serviços, crie uma chave em **Integrações**. O token é exibido uma única vez e armazenado somente como hash; a tela permite revogá-lo. Envie `Authorization: Bearer <token>`. Cada token pertence a uma conta, possui acesso somente de leitura a métricas daquela conta e não permite escolher outro `user_id`. Use HTTPS, armazene o token em um gestor de segredos, limite o acesso de rede e revogue/regenere a chave quando necessário. Rate limiting e auditoria avançada de chamadas ainda são pontos de evolução.

## 4. Fórmulas e semântica

- `CPC = gasto total / cliques totais`.
- `CPA = gasto total / conversões totais`.
- `taxa_de_conversao = conversões / cliques × 100`.
- `CTR = cliques / impressões × 100`, quando impressões estiverem disponíveis.

Os indicadores do período são calculados sobre totais agregados, não pela média simples de CPC/CPA de cada linha. Assim, linhas com volumes diferentes são ponderadas corretamente.

Uma conversão é a ação definida para aquela campanha (compra, lead, cadastro, clique qualificado ou outra ação). O CPA consolidado da conta combina os tipos de ação e pode não ser uma comparação homogênea quando os objetivos diferem; prefira comparar campanhas com o mesmo objetivo. CPA Manager não presume que toda conversão seja uma venda aprovada ou uma aquisição individual do LTV.

## 5. Relação com o LTV Manager

O LTV Manager mede comissões aprovadas e atribuídas ao longo do tempo; CPA Manager mede gasto, cliques e quantidade de conversões informadas nos relatórios de anúncios. São métricas complementares, mas seus denominadores não são automaticamente equivalentes.

- Comparação agregada: pode relacionar investimento por campanha no CPA com comissões atribuídas à campanha no LTV após mapear as campanhas e alinhar o período/moeda.
- Correspondência individual: um registro agregado diário com `conversions=8` não revela quais oito aquisições são essas. Não é correto distribuir esse número entre aquisições do LTV por data ou proximidade.
- Para correspondência individual futura, a origem deve fornecer um evento de conversão por ação, com `conversion_id` externo estável, data-hora, campanha mapeada, identificador de tracking não pessoal e evidência de atribuição. O integrador poderá então relacionar o evento a `Acquisition.external_reference` somente quando houver correspondência exata e permitida.
- Não enviar nome, telefone, CPF, e-mail ou outros dados pessoais de consumidores ao CPA Manager ou em exportações de integração.

## 6. Eventos e idempotência para evolução futura

Um contrato futuro de eventos pode adotar:

```json
{
  "schema_version": "1.0",
  "event_type": "conversion.recorded",
  "source_system": "ads_provider",
  "source_account_id": "account-external-id",
  "conversion_id": "provider-conversion-id",
  "occurred_at": "2026-11-17T12:30:00-03:00",
  "campaign_external_id": "campaign-123",
  "tracking_reference": "opaque-non-personal-reference",
  "conversion_type": "purchase",
  "currency": "BRL"
}
```

O evento acima é uma proposta documental, não um endpoint implementado nesta versão. Eventos repetidos devem ser deduplicados por `source_system + source_account_id + conversion_id`. Eventos sem identificador confiável não devem ser tratados como duplicados por aproximação de horário/valor.

## 7. Recomendações para o projeto principal

1. Consumir a API pelo adaptador/gateway autenticado do projeto principal (ROI Manager/Skallora); não conectar ao SQLite do CPA Manager.
2. Criar adaptador próprio no projeto principal, preservando a versão do contrato.
3. Manter `integration_key` e IDs externos em tabela de mapeamento, sem assumir que IDs PK locais coincidem.
4. Registrar `synced_at`, cursor ou janela temporal e resultado de cada sincronização.
5. Tratar `null` de CPC/CPA como ausência de denominador, não como zero.
6. Recalcular totais agregados a partir de gasto/cliques/conversões, sem tirar média de índices diários.
7. Não contabilizar conversão publicitária como comissão ou venda aprovada sem confirmação da origem comercial.

## 8. O que não está implementado

- OAuth ou conectores oficiais de Meta Ads, Google Ads, TikTok Ads ou afiliados.
- Importação automática por API, webhook ou pasta monitorada.
- Sincronização automática entre CPA Manager, LTV Manager e projeto principal.
- Push de aquisições ou comissões para LTV Manager.
- Mapeamento automático de campanhas entre bancos.
- Atribuição individual de conversões a aquisições.
- ROAS, ROI ou lucro líquido como indicador certificado.
