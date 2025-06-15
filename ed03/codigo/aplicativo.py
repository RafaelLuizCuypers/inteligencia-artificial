import random
import time
import csv
import glob
import os
import re

def carregar_csv(caminho_pasta="."):
   
    instancias_mochila = {}
    padrao_arquivos = os.path.join(caminho_pasta, 'knapsack_*.csv')

    def chave_natural(s):
       
        return [int(texto) if texto.isdigit() else texto.lower() for texto in re.split('([0-9]+)', s)]

    arquivos_ordenados = sorted(glob.glob(padrao_arquivos), key=chave_natural)

    if not arquivos_ordenados:
        print("Nenhum arquivo no formato 'knapsack_*.csv' foi encontrado.")
        return None

    print("Carregando Instâncias do Problema da Mochila")
    for caminho_arquivo in arquivos_ordenados:
        try:
            with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
                linhas_arquivo = f.readlines()
                linha_capacidade_str = linhas_arquivo[-1].strip()
                capacidade_mochila = int(linha_capacidade_str.split(',')[1])
                itens_mochila = []
                for linha in linhas_arquivo[1:-1]:
                    partes_linha = linha.strip().split(',')
                    peso_item = int(partes_linha[1])
                    valor_item = int(partes_linha[2])
                    itens_mochila.append((peso_item, valor_item))

                nome_base_arquivo = os.path.basename(caminho_arquivo)
                match_numero_instancia = re.search(r'\d+', nome_base_arquivo)
                numero_instancia = match_numero_instancia.group() if match_numero_instancia else 'Desconhecido'
                nome_instancia = f"Mochila {numero_instancia}"
                
                instancias_mochila[nome_instancia] = {'capacidade': capacidade_mochila, 'itens': itens_mochila}
        except Exception as e:
            print(f"ERRO ao processar o arquivo {caminho_arquivo}: {e}")

    print(f"\nCarga concluída. {len(instancias_mochila)} instâncias prontas para o teste:")
    for nome in instancias_mochila.keys():
        print(f"  - {nome}")
    print("-" * 45)
    time.sleep(1)
    
    return instancias_mochila

def calcular_fitness_individuo(solucao_individuo, todos_os_itens, capacidade_mochila):
   
    peso_total, valor_total = 0, 0
    for i, valor_gene in enumerate(solucao_individuo):
        if valor_gene == 1:
            peso_total += todos_os_itens[i][0]
            valor_total += todos_os_itens[i][1]
            
    return valor_total if peso_total <= capacidade_mochila else 0

def inicializar_populacao(tamanho_populacao, numero_de_itens, modo_inicializacao='aleatoria', todos_os_itens=None, capacidade_mochila=None):
   
    if modo_inicializacao == 'heuristica' and todos_os_itens and capacidade_mochila:
        populacao_inicial = []
        densidade_itens = sorted([(i, valor_item / peso_item if peso_item > 0 else 0) 
                                  for i, (peso_item, valor_item) in enumerate(todos_os_itens)], 
                                 key=lambda x: x[1], reverse=True)
        
        for _ in range(tamanho_populacao):
            solucao_individuo = [0] * numero_de_itens
            peso_atual = 0
            for i, _ in densidade_itens:
                if random.random() > 0.3 and peso_atual + todos_os_itens[i][0] <= capacidade_mochila:
                    solucao_individuo[i] = 1
                    peso_atual += todos_os_itens[i][0]
           
            for _ in range(int(numero_de_itens * 0.1)):
                idx = random.randint(0, numero_de_itens - 1)
                if solucao_individuo[idx] == 0 and peso_atual + todos_os_itens[idx][0] <= capacidade_mochila:
                    solucao_individuo[idx] = 1
                    peso_atual += todos_os_itens[idx][0]
            populacao_inicial.append(solucao_individuo)
        return populacao_inicial

    return [[random.randint(0, 1) for _ in range(numero_de_itens)] for _ in range(tamanho_populacao)]

def selecionar_pais(populacao_atual, valores_fitness_populacao):
    
    indices_participantes = random.sample(range(len(populacao_atual)), k=3)
    indice_melhor_pai = max(indices_participantes, key=lambda i: valores_fitness_populacao[i])
    
    indices_participantes.remove(indice_melhor_pai)
    indice_segundo_melhor_pai = max(indices_participantes, key=lambda i: valores_fitness_populacao[i])
    
    return populacao_atual[indice_melhor_pai], populacao_atual[indice_segundo_melhor_pai]

def realizar_cruzamento(genoma_pai1, genoma_pai2, tipo_cruzamento='ponto_unico'):
   
    comprimento_genoma = len(genoma_pai1)
    if comprimento_genoma < 2: return genoma_pai1[:], genoma_pai2[:] 

    genoma_descendente1, genoma_descendente2 = genoma_pai1[:], genoma_pai2[:]
    
    if tipo_cruzamento == 'ponto_unico':
        ponto_cruzamento = random.randint(1, comprimento_genoma - 1)
        genoma_descendente1 = genoma_pai1[:ponto_cruzamento] + genoma_pai2[ponto_cruzamento:]
        genoma_descendente2 = genoma_pai2[:ponto_cruzamento] + genoma_pai1[ponto_cruzamento:]
    elif tipo_cruzamento == 'dois_pontos' and comprimento_genoma > 2:
        ponto1, ponto2 = sorted(random.sample(range(1, comprimento_genoma), 2))
        genoma_descendente1 = genoma_pai1[:ponto1] + genoma_pai2[ponto1:ponto2] + genoma_pai1[ponto2:]
        genoma_descendente2 = genoma_pai2[:ponto1] + genoma_pai1[ponto1:ponto2] + genoma_pai2[ponto2:]
    elif tipo_cruzamento == 'uniforme':
        for i in range(comprimento_genoma):
            if random.random() < 0.5:
                genoma_descendente1[i], genoma_descendente2[i] = genoma_pai2[i], genoma_pai1[i]
            
    return genoma_descendente1, genoma_descendente2

def mutar_individuo(genoma_individuo, taxa_mutacao):
  
    for i in range(len(genoma_individuo)):
        if random.random() < taxa_mutacao:
            genoma_individuo[i] = 1 - genoma_individuo[i]
    return genoma_individuo

def executar_algoritmo_genetico(itens_mochila, capacidade_mochila, configuracao_algoritmo):
   
    tempo_inicio = time.time()
    tamanho_populacao = configuracao_algoritmo['tamanho_populacao']
    numero_de_itens = len(itens_mochila)
    populacao_atual = inicializar_populacao(tamanho_populacao, numero_de_itens, configuracao_algoritmo['metodo_inicializacao'], itens_mochila, capacidade_mochila)
    
    melhor_solucao_geral = None
    melhor_fitness_geral = 0
    contador_convergencia = 0
    
    for numero_geracao in range(configuracao_algoritmo['num_geracoes']):
        valores_fitness = [calcular_fitness_individuo(ind, itens_mochila, capacidade_mochila) for ind in populacao_atual]
        populacao_nova_geracao = []
        
        indice_melhor_individuo_na_geracao = max(range(len(valores_fitness)), key=valores_fitness.__getitem__)
        melhor_individuo_na_geracao = populacao_atual[indice_melhor_individuo_na_geracao]
        fitness_do_melhor_na_geracao = valores_fitness[indice_melhor_individuo_na_geracao]
        populacao_nova_geracao.append(melhor_individuo_na_geracao)
        
        if fitness_do_melhor_na_geracao > melhor_fitness_geral:
            melhor_fitness_geral = fitness_do_melhor_na_geracao
            melhor_solucao_geral = melhor_individuo_na_geracao
            contador_convergencia = 0
        else:
            contador_convergencia += 1
            
        if configuracao_algoritmo['criterio_parada'] == 'convergencia' and contador_convergencia >= configuracao_algoritmo['geracoes_paciencia']:
            break

        while len(populacao_nova_geracao) < tamanho_populacao:
            pai_1, pai_2 = selecionar_pais(populacao_atual, valores_fitness)
            filho_1, filho_2 = realizar_cruzamento(pai_1, pai_2, configuracao_algoritmo['tipo_cruzamento'])
            populacao_nova_geracao.append(mutar_individuo(filho_1, configuracao_algoritmo['taxa_mutacao']))
            if len(populacao_nova_geracao) < tamanho_populacao:
                populacao_nova_geracao.append(mutar_individuo(filho_2, configuracao_algoritmo['taxa_mutacao']))
            
        populacao_atual = populacao_nova_geracao
        
    tempo_fim = time.time()
    
    return {
        "melhor_valor": melhor_fitness_geral,
        "tempo_execucao_segundos": tempo_fim - tempo_inicio,
    }

def rodar_experimentos(instancias_carregadas):
    """
    Executa uma série de experimentos para avaliar diferentes configurações do algoritmo genético.
    """
    configuracoes_experimento = {
        'Tipo de Cruzamento': {
            'Ponto Único': {'tipo_cruzamento': 'ponto_unico'},
            'Dois Pontos': {'tipo_cruzamento': 'dois_pontos'},
            'Uniforme': {'tipo_cruzamento': 'uniforme'}
        },
        'Taxa de Mutação': {
            'Baixa (1%)': {'taxa_mutacao': 0.01},
            'Média (5%)': {'taxa_mutacao': 0.05},
            'Alta (10%)': {'taxa_mutacao': 0.10}
        },
        'Método de Inicialização': {
            'Aleatória': {'metodo_inicializacao': 'aleatoria'},
            'Heurística': {'metodo_inicializacao': 'heuristica'}
        },
        'Critério de Parada': {
            'Gerações Fixas': {'criterio_parada': 'geracoes_fixas'},
            'Convergência': {'criterio_parada': 'convergencia'}
        }
    }
    
    configuracao_algoritmo = {
        'tamanho_populacao': 100,
        'num_geracoes': 200,
        'taxa_mutacao': 0.05,
        'tipo_cruzamento': 'ponto_unico',
        'metodo_inicializacao': 'aleatoria',
        'criterio_parada': 'geracoes_fixas',
        'geracoes_paciencia': 20 
    }
    
    print("\n\nIniciando Testes\n")
    
    for nome_grupo, configuracoes_grupo in configuracoes_experimento.items():
        print(f"\n{'='*60}")
        print(f"    AVALIANDO O IMPACTO DE: {nome_grupo.upper()}")
        print(f"{'='*60}")
        
        for nome_config, atualizacao_config_parcial in configuracoes_grupo.items():
            configuracao_atual_algoritmo = configuracao_algoritmo.copy()
            configuracao_atual_algoritmo.update(atualizacao_config_parcial)
            
            print(f"\n    [*] Configuração em Teste: '{nome_config}'")
            
            for nome_instancia, dados_instancia in instancias_carregadas.items():
                resultado_experimento = executar_algoritmo_genetico(
                    dados_instancia['itens'], 
                    dados_instancia['capacidade'], 
                    configuracao_atual_algoritmo
                )
                print(f"          - {nome_instancia}: \tValor = {resultado_experimento['melhor_valor']}, \tTempo = {resultado_experimento['tempo_execucao_segundos']:.4f}s")
        
        time.sleep(1)

if __name__ == '__main__':
    random.seed(42) 
    
    instancias_mochila_carregadas = carregar_csv()
    
    if instancias_mochila_carregadas:
        rodar_experimentos(instancias_mochila_carregadas)
        print("\n\n testes finalizados!")