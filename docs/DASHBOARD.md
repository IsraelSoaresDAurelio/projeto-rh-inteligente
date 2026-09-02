# Dashboard

O dashboard apresenta os resultados já processados pelo motor de matching. Ele não chama a IA automaticamente, evitando custo inesperado durante uma demonstração.

## Executar

```powershell
streamlit run dashboard/app.py
```

Antes, gere o ranking com `python -m services.matching --top 30`. Para exibir pareceres de IA, gere-os com `python -m services.analise --vaga VAG-0001 --top 10`.

Como alternativa, o painel **Executar ações** no topo do dashboard tem um botão que processa a pasta `curriculos/` e atualiza o ranking. A geração de pareceres fica em uma ação separada porque pode usar a API paga da OpenAI ou, se `IA_PROVIDER=ollama`, um modelo local.

## Roteiro de demonstração

1. Selecione uma vaga na barra lateral.
2. Mostre o ranking, o score e as lacunas principais.
3. Abra um candidato e explique a composição do score.
4. Mostre o parecer de IA, deixando claro que ele apoia a decisão humana e não substitui a avaliação do recrutador.
