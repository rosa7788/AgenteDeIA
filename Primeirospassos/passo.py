import re

class TradutorCPC:
    def __init__(self):
        self.variaveis_proposicionais = {}
        self.proxima_variavel = 'A'
        
        # Mapeamento de conectivos
        self.conectivos_nl_para_cpc = {
            'e': '∧',
            'ou': '∨',
            'não': '¬',
            'se': '→',
            'se e somente se': '↔',
            'então': '→',
            'implica': '→',
            'equivale': '↔'
        }
        
        self.conectivos_cpc_para_nl = {
            '∧': 'e',
            '∨': 'ou',
            '¬': 'não',
            '→': 'implica',
            '↔': 'se e somente se'
        }
        
        # Padrões para reconhecimento de sentenças
        self.padroes_nl = [
            (r'não\s+(\w+)', self._processar_negacao),
            (r'se\s+(.+)\s+então\s+(.+)', self._processar_implicacao),
            (r'(.+)\s+e\s+(.+)', self._processar_conjuncao),
            (r'(.+)\s+ou\s+(.+)', self._processar_disjuncao),
            (r'(.+)\s+se e somente se\s+(.+)', self._processar_bicondicional)
        ]

    def obter_variavel(self, proposicao):
        """Obtém uma variável proposicional para uma proposição"""
        proposicao_limpa = proposicao.strip().lower()
        
        if proposicao_limpa not in self.variaveis_proposicionais:
            self.variaveis_proposicionais[proposicao_limpa] = self.proxima_variavel
            self.proxima_variavel = chr(ord(self.proxima_variavel) + 1)
        
        return self.variaveis_proposicionais[proposicao_limpa]

    def nl_para_cpc(self, sentenca):
        """Traduz sentença em linguagem natural para fórmula do CPC"""
        try:
            sentenca = sentenca.lower().strip()
            
            # Remove pontuação final
            sentenca = re.sub(r'[.!?]$', '', sentenca)
            
            # Processa padrões complexos primeiro
            for padrao, processador in self.padroes_nl:
                match = re.search(padrao, sentenca, re.IGNORECASE)
                if match:
                    return processador(match.groups())
            
            # Se não encontrou padrão complexo, trata como proposição atômica
            return self.obter_variavel(sentenca)
            
        except Exception as e:
            return f"Erro na tradução: {str(e)}"

    def cpc_para_nl(self, formula):
        """Traduz fórmula do CPC para linguagem natural"""
        try:
            formula = formula.replace(' ', '')  # Remove espaços
            
            # Processa parênteses primeiro
            while '(' in formula:
                formula = self._processar_parenteses(formula)
            
            # Processa operadores por ordem de precedência
            formula = self._processar_operadores(formula, ['↔'])
            formula = self._processar_operadores(formula, ['→'])
            formula = self._processar_operadores(formula, ['∨'])
            formula = self._processar_operadores(formula, ['∧'])
            formula = self._processar_operadores(formula, ['¬'])
            
            return self._traduzir_variaveis(formula)
            
        except Exception as e:
            return f"Erro na tradução: {str(e)}"

    def _processar_negacao(self, grupos):
        proposicao = grupos[0]
        var = self.obter_variavel(proposicao)
        return f"¬{var}"

    def _processar_implicacao(self, grupos):
        antecedente = grupos[0]
        consequente = grupos[1]
        return f"({self.nl_para_cpc(antecedente)} → {self.nl_para_cpc(consequente)})"

    def _processar_conjuncao(self, grupos):
        esquerda = grupos[0]
        direita = grupos[1]
        return f"({self.nl_para_cpc(esquerda)} ∧ {self.nl_para_cpc(direita)})"

    def _processar_disjuncao(self, grupos):
        esquerda = grupos[0]
        direita = grupos[1]
        return f"({self.nl_para_cpc(esquerda)} ∨ {self.nl_para_cpc(direita)})"

    def _processar_bicondicional(self, grupos):
        esquerda = grupos[0]
        direita = grupos[1]
        return f"({self.nl_para_cpc(esquerda)} ↔ {self.nl_para_cpc(direita)})"

    def _processar_parenteses(self, formula):
        """Processa expressões entre parênteses"""
        padrao = r'\(([^()]+)\)'
        match = re.search(padrao, formula)
        
        if match:
            expressao_interna = match.group(1)
            traducao_interna = self._processar_operadores(expressao_interna, ['↔', '→', '∨', '∧', '¬'])
            traducao_interna = self._traduzir_variaveis(traducao_interna)
            formula = formula.replace(match.group(0), traducao_interna)
        
        return formula

    def _processar_operadores(self, formula, operadores):
        """Processa operadores específicos na fórmula"""
        for operador in operadores:
            padrao = rf'([^¬→↔∧∨]+){re.escape(operador)}([^¬→↔∧∨]+)'
            
            while True:
                match = re.search(padrao, formula)
                if not match:
                    break
                
                esquerda = match.group(1).strip()
                direita = match.group(2).strip()
                
                if operador == '¬':
                    traducao = f"não {self._obter_proposicao(direita)}"
                else:
                    traducao_esq = self._obter_proposicao(esquerda)
                    traducao_dir = self._obter_proposicao(direita)
                    conectivo_nl = self.conectivos_cpc_para_nl[operador]
                    traducao = f"{traducao_esq} {conectivo_nl} {traducao_dir}"
                
                formula = formula.replace(match.group(0), traducao)
        
        return formula

    def _traduzir_variaveis(self, formula):
        """Traduz variáveis proposicionais de volta para linguagem natural"""
        for proposicao, var in self.variaveis_proposicionais.items():
            formula = formula.replace(var, proposicao)
        return formula

    def _obter_proposicao(self, variavel):
        """Obtém a proposição original a partir da variável"""
        for proposicao, var in self.variaveis_proposicionais.items():
            if var == variavel.strip():
                return proposicao
        return variavel.strip()

    def mostrar_mapeamento(self):
        """Mostra o mapeamento entre proposições e variáveis"""
        print("\n=== Mapeamento de Variáveis Proposicionais ===")
        for proposicao, var in self.variaveis_proposicionais.items():
            print(f"'{proposicao}' → {var}")
        print("=============================================\n")

# Exemplo de uso e demonstração
def demonstrar_agente():
    agente = TradutorCPC()
    
    print("=== AGENTE DE TRADUÇÃO NL ↔ CPC ===\n")
    
    # Exemplos de tradução NL → CPC
    exemplos_nl_para_cpc = [
        "chove",
        "não chove",
        "chove e faz frio",
        "chove ou faz sol",
        "se chove então a rua fica molhada",
        "chove se e somente se há nuvens"
    ]
    
    print("1. TRADUÇÃO: Linguagem Natural → Cálculo Proposicional")
    print("-" * 50)
    
    for exemplo in exemplos_nl_para_cpc:
        traducao = agente.nl_para_cpc(exemplo)
        print(f"NL: '{exemplo}'")
        print(f"CPC: {traducao}\n")
    
    agente.mostrar_mapeamento()
    
    # Exemplos de tradução CPC → NL
    print("2. TRADUÇÃO: Cálculo Proposicional → Linguagem Natural")
    print("-" * 50)
    
    # Usando as mesmas variáveis do mapeamento anterior
    exemplos_cpc_para_nl = [
        "A",
        "¬A",
        "(A ∧ B)",
        "(A ∨ C)",
        "(A → D)",
        "(A ↔ E)"
    ]
    
    for exemplo in exemplos_cpc_para_nl:
        traducao = agente.cpc_para_nl(exemplo)
        print(f"CPC: {exemplo}")
        print(f"NL: '{traducao}'\n")

    # Demonstração interativa
    print("3. MODO INTERATIVO")
    print("-" * 50)
    print("Digite 'sair' para encerrar\n")
    
    while True:
        entrada = input("Digite uma sentença em português ou fórmula do CPC: ")
        
        if entrada.lower() == 'sair':
            break
        
        if any(op in entrada for op in ['∧', '∨', '¬', '→', '↔', '(', ')']):
            # É uma fórmula do CPC
            traducao = agente.cpc_para_nl(entrada)
            print(f"Tradução para NL: {traducao}")
        else:
            # É linguagem natural
            traducao = agente.nl_para_cpc(entrada)
            print(f"Tradução para CPC: {traducao}")
        
        print()

if __name__ == "__main__":
    demonstrar_agente()