# Crea-MS · DFI — Folha de Atividades de Viagem 2027

Aplicação Streamlit para planejar viagens de fiscalização e gerar a Folha de Atividades em PDF.

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Arquivos

- `app.py` — painel web (Etapas 1, 2 e 3)
- `dados_fiscalizacao.py` — microrregiões/agentes 2027, 79 municípios de MS e atividades
- `pdf_generator.py` — geração do PDF (ReportLab)
- `logo_crea_ms.png` (ou `.jpg`/`.jpeg`/`.webp`) — **coloque aqui o logotipo oficial**; é detectado automaticamente no painel e no PDF. Sem ele, o app e o PDF usam um cabeçalho tipográfico "CREA-MS | Departamento de Fiscalização".
