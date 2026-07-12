# Plataforma de Análise de Dados

## 📝 Descrição e Objetivo
Infraestrutura avançada de análise de dados com suporte para pipelines ETL, controle de qualidade de código (Ruff), e scripts de implantação automatizada em VPS.
O principal objetivo deste projeto é fornecer uma ferramenta estável, de alta performance e fácil usabilidade, consolidando uma arquitetura escalável e segura.

## 🚀 Tecnologias Utilizadas
Este projeto foi construído utilizando as seguintes tecnologias:
- **Tecnologias Principais:** Python, FastAPI, Ruff, Pytest, Bash Scripting
- **Gerenciamento de Versão:** Git & GitHub
- **Hospedagem/Infraestrutura:** VPS Linux

## 🏗️ Arquitetura do Projeto
O projeto utiliza um padrão de organização limpo, visando a separação de responsabilidades (Separation of Concerns). 

### Estrutura de Pastas
A estrutura geral de arquivos e diretórios do projeto é apresentada abaixo:
```text
├── DEV/\n│   ├── agentes/\n│   │   └── AGENTE_1_CARGA.md\n│   │   └── AGENTE_2_BASCULAMENTO.md\n│   │   └── README.md\n│   │   └── TAREFAS_PROGRESSO.md\n│   └── app.py\n│   ├── assets/\n│   │   └── loguin_fundo.png\n│   │   ├── powerbi/\n│   │   │   ... (conteúdo adicional)\n│   ├── dados/\n│   │   └── movimentacao_detalhada.csv\n│   │   └── movimentacao_detalhada.xlsx\n│   └── deploy_vps_dev.py\n│   └── requirements.txt\n│   └── setup_vps_dev.sh\n│   ├── src/\n│   │   └── __init__.py\n│   │   └── chart_engine.py\n│   │   └── column_profiler.py\n│   │   └── data_cleaner.py\n│   │   └── data_loader.py\n│   │   └── export_service.py\n│   │   └── fleet_analyzer.py\n│   ├── tests/\n│   │   └── __init__.py\n│   │   └── test_basic.py\n└── README.md\n└── app.py\n├── assets/\n│   └── loguin_fundo.png\n│   ├── powerbi/\n│   │   └── COMO_IMPORTAR_POWERBI.txt\n│   │   └── LEIA-ME_TEMPLATE.txt\n├── dados/\n│   └── movimentacao_detalhada.csv\n│   └── movimentacao_detalhada.xlsx\n└── deploy.zip\n└── deploy_vps.ps1\n└── deploy_vps.py\n└── login-redesign.md\n├── pipes.sh/\n│   └── CONTRIBUTING.rst\n│   └── LICENSE\n│   └── Makefile\n│   └── README.rst\n│   ├── i/\n│   │   └── pipes.png\n│   │   └── pipes.t0.png\n│   │   └── pipes.t1.png\n│   │   └── pipes.t2.png\n│   │   └── pipes.t3.png\n│   │   └── pipes.t4.png\n│   │   └── pipes.t5.png\n│   │   └── pipes.t6.png\n│   │   └── pipes.t7.png\n│   │   └── pipes.t8.png\n│   │   └── pipes.t9.png\n│   │   └── pipes.tc.png\n│   └── pipes.sh\n│   └── pipes.sh.6\n│   ├── scripts/\n│   │   └── README\n│   │   └── benchmark.sh\n│   │   └── gen-man-html.sh\n│   │   └── travis-script.sh\n│   ├── test/\n│   │   └── README\n│   │   └── helper.sh\n│   │   └── run_tests.sh\n│   │   └── test_command.sh\n│   │   └── test_init.sh\n│   │   └── test_main.sh\n│   │   └── test_parse.sh\n└── requirements.txt\n└── run.bat\n└── setup_vps.sh\n├── src/\n│   └── __init__.py\n│   └── chart_engine.py\n│   └── column_profiler.py\n│   └── data_cleaner.py\n│   └── data_loader.py\n│   └── export_service.py\n│   └── fleet_analyzer.py\n├── tests/\n│   └── __init__.py\n│   └── test_basic.py\n
```

## ⚙️ Pré-requisitos
Para instalar e executar este projeto localmente, você precisará de:
- **Python 3.8+**\n- **pip** (instalador de pacotes do Python)\n- **virtualenv** (opcional, mas altamente recomendado)

## 📥 Como Instalar e Configurar o Ambiente
1. Clone este repositório privado em sua máquina:
   ```bash
   git clone git@github.com:cleitonsantosKS/plataforma_analise_dados.git
   cd plataforma_analise_dados
   ```
2. Configure as dependências do ambiente:
1. Crie um ambiente virtual Python:\n   ```bash\n   python -m venv venv\n   source venv/bin/activate  # No Linux\n   # ou venv\\Scripts\\activate na sua máquina Windows\n   ```\n2. Instale as dependências do projeto:\n   ```bash\n   pip install -r requirements.txt\n   ```

## 🏃 Como Executar
### Modo Desenvolvimento
Para iniciar o servidor local de desenvolvimento, execute:
```bash
python app.py
```
O servidor estará acessível em: `http://localhost:8000`

### Como Executar Testes (quando aplicável)
Para validar o funcionamento do código com testes automatizados:
```bash
pytest
```

## 🔒 Variáveis de Ambiente Necessárias
Caso o projeto necessite de variáveis sensíveis, configure um arquivo `.env` na raiz com os seguintes parâmetros básicos de exemplo (nunca envie o arquivo `.env` real ao GitHub!):
```env
PORT=8000
DEBUG=True
SECRET_KEY=sua_chave_secreta_aqui
```

## 🌐 Links Importantes
- **Repositório GitHub:** [https://github.com/cleitonsantosKS/plataforma_analise_dados](https://github.com/cleitonsantosKS/plataforma_analise_dados)
- **Documentação Adicional:** [docs/](docs/)
- **Ambiente de Desenvolvimento:** `http://localhost:8000`

## 🤝 Como Contribuir
Por favor, leia as diretrizes detalhadas de contribuição e convenção de branches no documento [docs/contribuicao.md](docs/contribuicao.md).

## 📄 Licença
Este projeto está sob a licença MIT. Para mais detalhes, consulte o arquivo de licença.

## 🕒 Histórico de Versões
Veja o histórico detalhado de atualizações e lançamentos no arquivo [docs/changelog.md](docs/changelog.md).
