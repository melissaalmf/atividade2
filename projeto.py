import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import random
from datetime import datetime, timedelta


PASTA_SAIDA = Path("resultados")
PASTA_SAIDA.mkdir(exist_ok=True)


def gerar_dados_exemplo(qtd_clientes=300):
    random.seed(42)

    dados = []

    for cliente_id in range(1, qtd_clientes + 1):
        idade = random.randint(18, 65)
        meses_como_cliente = random.randint(1, 60)
        valor_mensal = round(random.uniform(29.90, 299.90), 2)
        tickets_suporte = random.randint(0, 12)
        dias_desde_ultimo_acesso = random.randint(0, 90)
        uso_mensal_horas = round(random.uniform(1, 80), 1)

        prob_cancelamento = 0

        if dias_desde_ultimo_acesso > 45:
            prob_cancelamento += 0.35

        if tickets_suporte > 6:
            prob_cancelamento += 0.25

        if uso_mensal_horas < 10:
            prob_cancelamento += 0.25

        if meses_como_cliente < 6:
            prob_cancelamento += 0.10

        cancelou = random.random() < prob_cancelamento

        dados.append({
            "cliente_id": cliente_id,
            "idade": idade,
            "meses_como_cliente": meses_como_cliente,
            "valor_mensal": valor_mensal,
            "tickets_suporte": tickets_suporte,
            "dias_desde_ultimo_acesso": dias_desde_ultimo_acesso,
            "uso_mensal_horas": uso_mensal_horas,
            "cancelou": int(cancelou)
        })

    df = pd.DataFrame(dados)
    return df


def analisar_dados(df):
    total_clientes = len(df)
    clientes_cancelados = df["cancelou"].sum()
    taxa_cancelamento = clientes_cancelados / total_clientes * 100

    receita_total = df["valor_mensal"].sum()
    receita_perdida = df[df["cancelou"] == 1]["valor_mensal"].sum()

    print("\n========== RESUMO GERAL ==========")
    print(f"Total de clientes: {total_clientes}")
    print(f"Clientes cancelados: {clientes_cancelados}")
    print(f"Taxa de cancelamento: {taxa_cancelamento:.2f}%")
    print(f"Receita mensal total: R$ {receita_total:.2f}")
    print(f"Receita mensal perdida com cancelamentos: R$ {receita_perdida:.2f}")

    print("\n========== MÉDIAS POR GRUPO ==========")
    print(df.groupby("cancelou")[[
        "idade",
        "meses_como_cliente",
        "valor_mensal",
        "tickets_suporte",
        "dias_desde_ultimo_acesso",
        "uso_mensal_horas"
    ]].mean().round(2))

    return {
        "total_clientes": total_clientes,
        "clientes_cancelados": clientes_cancelados,
        "taxa_cancelamento": taxa_cancelamento,
        "receita_total": receita_total,
        "receita_perdida": receita_perdida
    }


def criar_score_risco(df):
    df = df.copy()

    df["score_risco"] = 0

    df.loc[df["dias_desde_ultimo_acesso"] > 45, "score_risco"] += 35
    df.loc[df["tickets_suporte"] > 6, "score_risco"] += 25
    df.loc[df["uso_mensal_horas"] < 10, "score_risco"] += 25
    df.loc[df["meses_como_cliente"] < 6, "score_risco"] += 15

    def classificar(score):
        if score >= 60:
            return "Alto risco"
        elif score >= 30:
            return "Médio risco"
        else:
            return "Baixo risco"

    df["classificacao_risco"] = df["score_risco"].apply(classificar)

    return df


def gerar_insights(df):
    print("\n========== INSIGHTS ==========")

    cancelados = df[df["cancelou"] == 1]
    ativos = df[df["cancelou"] == 0]

    media_acesso_cancelados = cancelados["dias_desde_ultimo_acesso"].mean()
    media_acesso_ativos = ativos["dias_desde_ultimo_acesso"].mean()

    media_uso_cancelados = cancelados["uso_mensal_horas"].mean()
    media_uso_ativos = ativos["uso_mensal_horas"].mean()

    media_tickets_cancelados = cancelados["tickets_suporte"].mean()
    media_tickets_ativos = ativos["tickets_suporte"].mean()

    print(f"Clientes que cancelaram ficaram, em média, {media_acesso_cancelados:.1f} dias sem acessar.")
    print(f"Clientes ativos ficaram, em média, {media_acesso_ativos:.1f} dias sem acessar.")
    print(f"Clientes que cancelaram usavam, em média, {media_uso_cancelados:.1f} horas por mês.")
    print(f"Clientes ativos usavam, em média, {media_uso_ativos:.1f} horas por mês.")
    print(f"Clientes que cancelaram abriram, em média, {media_tickets_cancelados:.1f} tickets de suporte.")
    print(f"Clientes ativos abriram, em média, {media_tickets_ativos:.1f} tickets de suporte.")

    print("\nConclusão automática:")
    print(
        "O cancelamento parece estar mais associado a baixo uso da plataforma, "
        "muitos dias sem acesso e maior quantidade de tickets de suporte."
    )


def grafico_cancelamento(df):
    contagem = df["cancelou"].value_counts().sort_index()
    labels = ["Ativos", "Cancelados"]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, contagem)
    plt.title("Quantidade de Clientes Ativos vs Cancelados")
    plt.ylabel("Quantidade de clientes")
    plt.tight_layout()
    plt.savefig(PASTA_SAIDA / "clientes_ativos_vs_cancelados.png")
    plt.close()


def grafico_risco(df):
    contagem = df["classificacao_risco"].value_counts()

    plt.figure(figsize=(8, 5))
    plt.bar(contagem.index, contagem.values)
    plt.title("Distribuição de Clientes por Nível de Risco")
    plt.ylabel("Quantidade de clientes")
    plt.tight_layout()
    plt.savefig(PASTA_SAIDA / "clientes_por_risco.png")
    plt.close()


def grafico_uso_vs_cancelamento(df):
    media_uso = df.groupby("cancelou")["uso_mensal_horas"].mean()
    labels = ["Ativos", "Cancelados"]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, media_uso)
    plt.title("Uso Médio Mensal: Ativos vs Cancelados")
    plt.ylabel("Horas de uso por mês")
    plt.tight_layout()
    plt.savefig(PASTA_SAIDA / "uso_medio_ativos_vs_cancelados.png")
    plt.close()


def grafico_acesso_vs_cancelamento(df):
    media_acesso = df.groupby("cancelou")["dias_desde_ultimo_acesso"].mean()
    labels = ["Ativos", "Cancelados"]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, media_acesso)
    plt.title("Dias Desde o Último Acesso: Ativos vs Cancelados")
    plt.ylabel("Dias")
    plt.tight_layout()
    plt.savefig(PASTA_SAIDA / "dias_sem_acesso_ativos_vs_cancelados.png")
    plt.close()


def exportar_relatorios(df, resumo):
    df.to_csv(PASTA_SAIDA / "base_clientes_analisada.csv", index=False, encoding="utf-8")

    clientes_risco = df[df["classificacao_risco"] == "Alto risco"].sort_values(
        by="score_risco",
        ascending=False
    )

    clientes_risco.to_csv(PASTA_SAIDA / "clientes_alto_risco.csv", index=False, encoding="utf-8")

    resumo_df = pd.DataFrame([resumo])
    resumo_df.to_csv(PASTA_SAIDA / "resumo_geral.csv", index=False, encoding="utf-8")


def main():
    print("Projeto: Análise de Cancelamento de Clientes")
    print("Gerando base de dados fictícia...")

    df = gerar_dados_exemplo(qtd_clientes=300)

    df = criar_score_risco(df)

    resumo = analisar_dados(df)

    gerar_insights(df)

    grafico_cancelamento(df)
    grafico_risco(df)
    grafico_uso_vs_cancelamento(df)
    grafico_acesso_vs_cancelamento(df)

    exportar_relatorios(df, resumo)

    print("\n========== ARQUIVOS GERADOS ==========")
    print("Pasta: resultados/")
    print("- base_clientes_analisada.csv")
    print("- clientes_alto_risco.csv")
    print("- resumo_geral.csv")
    print("- clientes_ativos_vs_cancelados.png")
    print("- clientes_por_risco.png")
    print("- uso_medio_ativos_vs_cancelados.png")
    print("- dias_sem_acesso_ativos_vs_cancelados.png")

    print("\nProjeto finalizado com sucesso.")


if __name__ == "__main__":
    main()