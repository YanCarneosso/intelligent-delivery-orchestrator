<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/cover-dark.svg">
  <img src="docs/assets/cover-light.svg" width="100%" alt="Intelligent Delivery Orchestrator — LLM dentro de um workflow determinístico. Mais de 40 testes, 7 ADRs e CI.">
</picture>

<p align="center"><strong>Orquestração serverless de pedidos de delivery com IA generativa, decisões auditáveis e segurança alimentar.</strong></p>

<p align="center">
  <a href="https://github.com/YanCarneosso/intelligent-delivery-orchestrator/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/YanCarneosso/intelligent-delivery-orchestrator/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python 3.12" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
  <img alt="AWS Serverless" src="https://img.shields.io/badge/AWS-Serverless-FF9900?logo=amazonwebservices&logoColor=white">
  <img alt="Amazon Bedrock" src="https://img.shields.io/badge/Amazon-Bedrock-8A2BE2">
  <a href="LICENSE"><img alt="Licença MIT" src="https://img.shields.io/badge/licen%C3%A7a-MIT-green.svg"></a>
</p>

## Em 30 segundos

- **Problema:** pedidos chegam em linguagem natural, com intenção, sentimento e restrições alimentares implícitas. Delegar decisões críticas a um LLM traz riscos como alergias ignoradas, pagamentos duplicados e *prompt injection*.
- **Solução:** workflow serverless em AWS Step Functions no qual o Amazon Nova Lite, via Bedrock, apenas interpreta o pedido, com saída validada por JSON Schema. Pagamento, idempotência, retries, despacho e auditoria permanecem determinísticos.
- **Resultado:** uma resposta inválida do modelo ou uma tentativa de *prompt injection* não remove um risco de alergia já identificado. Mais de 40 testes (unitários, de contrato, de segurança e de workflow), CI, 7 ADRs, runbook operacional e demo local sem conta AWS.
- **Stack:** Python 3.12 · AWS SAM · Step Functions · Amazon Bedrock (Nova Lite) · Lambda · DynamoDB · CloudWatch
- **Por onde começar:** [guia para recrutadores](docs/recruiter-guide.md) (cerca de 5 minutos) · [arquitetura](docs/architecture.md) · [decisões de arquitetura](docs/adr/)

## Sobre o projeto

Este projeto demonstra como combinar **Amazon Bedrock e Amazon Nova Lite** com **AWS Step Functions** para interpretar pedidos em linguagem natural sem entregar decisões críticas ao modelo de IA.

O princípio central é simples:

```text
IA interpreta  •  Schema estabelece o contrato  •  Workflow decide
IAM delimita a confiança  •  Testes produzem evidências
```

O modelo identifica intenção, sentimento e restrições alimentares. Pagamento, idempotência, segurança, retries, despacho e auditoria permanecem determinísticos.

## Visão geral da arquitetura

```mermaid
flowchart LR
    A["Pedido"] --> B["Validação"]
    B --> C[("Idempotência")]
    C --> D["Bedrock · Nova Lite"]
    D --> E["Contrato JSON + proteção de alergias"]
    E --> F{"Decisão auditável"}
    F --> G["Pagamento"]
    G --> H["Despacho"]
    G --> I["Notificação"]
    H --> J["Pedido processado"]
    I --> J
```

A chamada ao Bedrock é feita diretamente pela integração otimizada do Step Functions. Uma camada determinística impede que uma resposta inválida ou uma tentativa de prompt injection remova um risco de alergia identificado.

## O que você encontrará aqui

- Infraestrutura reproduzível com AWS SAM.
- State machine Standard com `Choice`, `Parallel`, retries seletivos e tratamento de falhas.
- Contratos JSON Schema para entrada e saída do modelo.
- Defesa em profundidade para alergias e prompt injection.
- Idempotência com escrita condicional no DynamoDB.
- Observabilidade com CloudWatch, métricas, alarmes e dashboard.
- Testes unitários, de contrato, segurança e workflow, além de CI no GitHub Actions.
- Demo local que não exige conta AWS.

## Experimente localmente

### Windows PowerShell

```powershell
.\scripts\dev.ps1 setup
.\scripts\dev.ps1 test
.\scripts\dev.ps1 demo
```

### Linux e macOS

```bash
make setup
make test
make demo
```

O demo é identificado como `LOCAL_DETERMINISTIC_MOCK`: ele exercita o fluxo real do projeto, mas não chama AWS, LLM ou provedores externos.

## Documentação completa

| Tema | Documento |
|---|---|
| Arquitetura e fluxo de execução | [Arquitetura](docs/architecture.md) |
| Decisões e trade-offs | [Architecture Decision Records](docs/adr/) |
| Segurança e ameaças | [Threat model](docs/threat-model.md) |
| Privacidade e tratamento de dados | [Privacidade](docs/privacy.md) |
| Operação, incidentes e rollback | [Runbook operacional](docs/operations.md) |
| Custos e cenários de volume | [Modelo de custos](docs/cost-model.md) |
| Métricas técnicas e de negócio | [Métricas](docs/business-metrics.md) |
| Avaliação rápida do repositório | [Guia para recrutadores](docs/recruiter-guide.md) |
| Proteção da branch principal | [Branch protection](docs/branch-protection.md) |

> Para uma avaliação técnica em aproximadamente cinco minutos, comece pelo [guia para recrutadores](docs/recruiter-guide.md).

## Transparência

Os adaptadores de pagamento, despacho e notificação são referências sem efeitos externos. Resultados locais não são apresentados como medições de produção, e nenhum benefício de negócio é tratado como resultado comprovado sem uma integração real.

## Autor

<img src="docs/assets/agentes-de-ia-em-campo.png" width="160" alt="Selo Agentes de IA em Campo — AWS" align="right">

Implementação independente desenvolvida por **Yan Costa Carneosso**.

Distribuído sob a [Licença MIT](LICENSE).
