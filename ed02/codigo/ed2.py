import time
import tracemalloc
from collections import deque
import heapq

# Objetivo final
fim = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# 10 estados iniciais
inicios = [
    [1, 2, 0, 4, 5, 3, 7, 8, 6],
    [1, 3, 0, 4, 2, 6, 7, 5, 8],
    [1, 3, 5, 4, 0, 2, 7, 8, 6],
    [1, 3, 6, 4, 5, 2, 0, 7, 8],
    [0, 2, 3, 1, 8, 5, 4, 7, 6],
    [1, 2, 3, 4, 0, 8, 7, 6, 5],
    [0, 2, 3, 1, 4, 8, 7, 6, 5],
    [1, 0, 3, 4, 2, 5, 7, 8, 6],
    [7, 3, 6, 2, 1, 0, 5, 4, 8],
    [7, 1, 3, 0, 5, 6, 4, 2, 8],
]

def pegar_vizinhos(estado):
    lista = []
    pos = estado.index(0)
    lin = pos // 3
    col = pos % 3
    direcoes = [(-1,0),(1,0),(0,-1),(0,1)]
    for dx, dy in direcoes:
        nova_lin = lin + dx
        nova_col = col + dy
        if 0 <= nova_lin < 3 and 0 <= nova_col < 3:
            nova_pos = nova_lin * 3 + nova_col
            novo = estado[:]
            novo[pos], novo[nova_pos] = novo[nova_pos], novo[pos]
            lista.append(novo)
    return lista

def calcular_distancia(estado):
    total = 0
    for i in range(9):
        if estado[i] == 0:
            continue
        certo = estado[i] - 1
        total += abs(i // 3 - certo // 3) + abs(i % 3 - certo % 3)
    return total

# Implementações das buscas
def largura(inicio):
    fila = deque()
    fila.append((inicio, []))
    vistos = set()
    cont = 0
    while fila:
        atual, caminho = fila.popleft()
        cont += 1
        if atual == fim:
            return caminho + [atual], cont
        vistos.add(tuple(atual))
        for viz in pegar_vizinhos(atual):
            if tuple(viz) not in vistos:
                fila.append((viz, caminho + [atual]))
    return None, cont

def profundidade(inicio):
    pilha = [(inicio, [])]
    vistos = set()
    cont = 0
    while pilha:
        atual, caminho = pilha.pop()
        cont += 1
        if atual == fim:
            return caminho + [atual], cont
        vistos.add(tuple(atual))
        if len(caminho) < 50:
            for viz in pegar_vizinhos(atual):
                if tuple(viz) not in vistos:
                    pilha.append((viz, caminho + [atual]))
    return None, cont

def gulosa(inicio):
    fila = [(calcular_distancia(inicio), inicio, [])]
    vistos = set()
    cont = 0
    while fila:
        _, atual, caminho = heapq.heappop(fila)
        cont += 1
        if atual == fim:
            return caminho + [atual], cont
        vistos.add(tuple(atual))
        for viz in pegar_vizinhos(atual):
            if tuple(viz) not in vistos:
                heapq.heappush(fila, (calcular_distancia(viz), viz, caminho + [atual]))
    return None, cont

def a_estrela(inicio):
    fila = [(calcular_distancia(inicio), 0, inicio, [])]
    vistos = set()
    cont = 0
    while fila:
        _, custo, atual, caminho = heapq.heappop(fila)
        cont += 1
        if atual == fim:
            return caminho + [atual], cont
        vistos.add(tuple(atual))
        for viz in pegar_vizinhos(atual):
            if tuple(viz) not in vistos:
                novo_custo = custo + 1
                total = novo_custo + calcular_distancia(viz)
                heapq.heappush(fila, (total, novo_custo, viz, caminho + [atual]))
    return None, cont

metodos = {
    "Largura": largura,
    "Profundidade": profundidade,
    "Gulosa": gulosa,
    "A*": a_estrela,
}

# Cabeçalho
print(f"{'Método':<13} | {'Nº':<3} | {'Passos':<6} | {'Nós':<6} | {'Tempo(s)':<9} | {'Memória(KB)':<13}")
print("-" * 75)

# Loop de testes
for n, estado in enumerate(inicios):
    for nome, func in metodos.items():
        tracemalloc.start()
        ini = time.time()
        resp, total_nos = func(estado)
        fim_tempo = time.time()
        mem_atual, mem_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        passos = len(resp) - 1 if resp else -1
        tempo = fim_tempo - ini
        memoria_kb = mem_pico / 1024
        print(f"{nome:<13} | {n+1:<3} | {passos:<6} | {total_nos:<6} | {tempo:.4f}   | {memoria_kb:>10.2f}")
    print("-" * 75)
