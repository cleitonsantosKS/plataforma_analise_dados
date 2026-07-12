# Guia de Configuração - Plataforma de Análise de Dados

## ⚙️ Parametrização e Configurações

O comportamento do sistema pode ser configurado por variáveis de ambiente ou arquivos de configuração local.

### Variáveis de Ambiente (.env)
Crie um arquivo `.env` na raiz do projeto contendo:
```env
PORT=8000
DEBUG=True
SECRET_KEY=segredo_super_secreto_do_projeto
```

### Segurança de Credenciais
**IMPORTANTE:** Nunca envie o arquivo `.env` ou qualquer chave criptográfica ao repositório Git. O arquivo `.gitignore` do projeto já está pré-configurado para bloquear o envio desses arquivos por segurança.
