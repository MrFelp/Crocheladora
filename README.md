# Plataforma de Precificação — Streamlit

Este repositório contém uma **aplicação Streamlit** pronta para subir no **Streamlit Cloud** (ou rodar localmente) para gerenciar sua planilha de precificação.

## Conteúdo
- `app.py` — aplicação principal (Streamlit)
- `requirements.txt` — dependências
- `sample_planilha_precificacao.xlsx` — (opcional) se você tiver fornecido uma amostra

## Como publicar no Streamlit Cloud (passo-a-passo para leigos)
1. Crie uma conta no GitHub: https://github.com/ (se ainda não tiver).
2. Faça um novo repositório (por exemplo `precificacao-streamlit`) e envie os arquivos deste pacote.
   - Se preferir, clique em **Add file -> Upload files** e faça upload de todos os arquivos deste ZIP.
3. Crie uma conta no Streamlit Cloud (https://streamlit.io/cloud) com sua conta GitHub.
4. No Streamlit Cloud clique em **New app** -> escolha seu repositório -> Branch `main` -> `app.py` -> **Deploy**.
5. Em alguns segundos sua aplicação estará disponível em uma URL do tipo `https://<seu-app>.streamlit.app`.

## Como rodar localmente (Windows/PC) sem GitHub
1. Instale Python 3.8+: https://www.python.org/downloads/
2. Abra o Prompt de Comando (ou PowerShell) na pasta do projeto.
3. Crie e ative um ambiente virtual (opcional, recomendado):
   - `python -m venv venv`
   - Windows PowerShell: `.env\Scripts\Activate.ps1`
   - Windows cmd: `venv\Scripts\activate`
4. Instale dependências:
   - `pip install -r requirements.txt`
5. Rode a aplicação:
   - `streamlit run app.py`
6. O Streamlit abrirá automaticamente o navegador com o app (ou use o link mostrado no terminal).

## Observações
- O app lê arquivos `.xlsx` e `.csv`, detecta colunas e permite mapeamento.
- Você pode editar células na tabela e aplicar imposto (%) e frete por item.
- Se quiser, eu posso fazer o upload direto para o seu GitHub (se você me der acesso temporário) ou guiar você passo a passo enquanto faz.

Boa — após extrair o ZIP, siga o README acima. Se quiser, posso te guiar com prints passo-a-passo em cada etapa.
