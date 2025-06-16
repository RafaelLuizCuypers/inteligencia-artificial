import random
import pandas as pd
import os
import itertools


TAMANHO_POPULACAO = 50
TAMANHO_CROMOSSOMO = 10
NUMERO_GERACOES = 100

TAXAS_MUTACAO = {
    'baixa': 0.01,
    'media': 0.05,
    'alta': 0.1
}


def carregar_dados_csv(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo, header=None)
        dados = df.values.flatten().tolist()
        return [float(str(item).replace(',', '.')) for item in dados if str(item).replace(',', '.').replace('.', '', 1).isdigit()]
    except:
        return []


def avaliar_fitness(cromossomo, dados_fitness):
    return sum(g * f for g, f in zip(cromossomo, dados_fitness))


def inicializar_populacao(tamanho, tipo='aleatoria'):
    populacao = []
    for _ in range(tamanho):
        if tipo == 'aleatoria':
            cromossomo = [random.randint(0, 1) for _ in range(TAMANHO_CROMOSSOMO)]
        else:
            cromossomo = [1]*(TAMANHO_CROMOSSOMO//2) + [0]*(TAMANHO_CROMOSSOMO//2)
            random.shuffle(cromossomo)
        populacao.append(cromossomo)
    return populacao


def crossover(p1, p2, tipo='um_ponto'):
    if tipo == 'um_ponto':
        ponto = random.randint(1, TAMANHO_CROMOSSOMO-1)
        return p1[:ponto]+p2[ponto:], p2[:ponto]+p1[ponto:]
    elif tipo == 'dois_pontos':
        a, b = sorted(random.sample(range(1, TAMANHO_CROMOSSOMO), 2))
        return p1[:a]+p2[a:b]+p1[b:], p2[:a]+p1[a:b]+p2[b:]
    elif tipo == 'uniforme':
        f1, f2 = [], []
        for g1, g2 in zip(p1, p2):
            if random.random() < 0.5:
                f1.append(g1)
                f2.append(g2)
            else:
                f1.append(g2)
                f2.append(g1)
        return f1, f2


def mutar(c, taxa):
    return [1-g if random.random() < taxa else g for g in c]


def selecao_torneio(pop, fits, k=3):
    competidores = random.sample(list(zip(pop, fits)), k)
    competidores.sort(key=lambda x: x[1], reverse=True)
    return competidores[0][0]


def populacao_convergiu(fits):
    return len(set(fits)) == 1


def algoritmo_genetico(caminho_csv, tipo_crossover, taxa_mutacao, tipo_inicializacao, criterio_parada):
    dados_fitness = carregar_dados_csv(caminho_csv)
    if not dados_fitness:
        return None, None

    populacao = inicializar_populacao(TAMANHO_POPULACAO, tipo_inicializacao)

    for geracao in range(NUMERO_GERACOES):
        fitnesses = [avaliar_fitness(ind, dados_fitness) for ind in populacao]

        if criterio_parada == 'convergencia' and populacao_convergiu(fitnesses):
            break

        nova_populacao = []
        while len(nova_populacao) < TAMANHO_POPULACAO:
            pai1 = selecao_torneio(populacao, fitnesses)
            pai2 = selecao_torneio(populacao, fitnesses)
            f1, f2 = crossover(pai1, pai2, tipo=tipo_crossover)
            nova_populacao.append(mutar(f1, taxa_mutacao))
            if len(nova_populacao) < TAMANHO_POPULACAO:
                nova_populacao.append(mutar(f2, taxa_mutacao))

        populacao = nova_populacao

    fitnesses = [avaliar_fitness(ind, dados_fitness) for ind in populacao]
    melhor_indice = fitnesses.index(max(fitnesses))
    return populacao[melhor_indice], fitnesses[melhor_indice]


if __name__ == "__main__":
    pasta_csv = "C:\\Users\\pc\\Downloads\\ed03\\ed03-funcoes"
    arquivos = [f"function_opt_{i}.csv" for i in range(1, 11)]

    crossovers = ['um_ponto', 'dois_pontos', 'uniforme']
    inicializacoes = ['aleatoria', 'heuristica']
    paradas = ['geracoes', 'convergencia']
    taxas = ['baixa', 'media', 'alta']

    print("ARQUIVO\t\tCROSSOVER\tMUTACAO\t\tINICIALIZACAO\tPARADA\t\tFITNESS")

    for arquivo in arquivos:
        caminho = os.path.join(pasta_csv, arquivo)
        if not os.path.exists(caminho):
            continue

        for c in crossovers:
            for m in taxas:
                for i in inicializacoes:
                    for p in paradas:
                        taxa_real = TAXAS_MUTACAO[m]
                        sol, fit = algoritmo_genetico(
                            caminho_csv=caminho,
                            tipo_crossover=c,
                            taxa_mutacao=taxa_real,
                            tipo_inicializacao=i,
                            criterio_parada=p
                        )
                        nome_limpo = arquivo.replace("function_opt_", "").replace(".csv", "")
                        print(f"{nome_limpo:<8}\t{c:<12}\t{m:<8}\t{i:<12}\t{p:<10}\t{round(fit,2) if fit else 'Erro'}")
