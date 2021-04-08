/*__________________________________________________________________________________
|       Trabalho 1 - Segurança de Redes e Sistemas
|       
|		Descrição: Implementação de uma ferramenta para análise de frequências
|       Aluno: Lucas da Silva Nolasco
| __________________________________________________________________________________
*/

#include <iostream>
#include <vector>

/*------------------------------------------------------------------------------
 *  Nome: decifrar
 *      Método para decifrar um caractere de entrada com base em um determinado 
 *      k fornecido.
 *
 *      original - Caractere original;
 *      k - Valor de K a ser utilizado na Cifra de César;
 *
 *  descrição do retorno: retorna char decifrado, caso o dado original esteja em [A-Z, a-z, 0-9];
 *                        retorn a letra fornecida, caso o dado esteja fora de [A-Z, a-z, 0-9].
 *---------------------------------------------------------------------------*/
char decifrar(char original, int k) {
    char convertido = original;

    if(original >= 0x30 && original <= 0x39) { /* Números */
        original = original - 0x30 + 52;
    }
    else if(original >= 0x41 && original <= 0x5A) { /* Caracteres maiúsculos */
        original = original - 0x41;
    }
    else if(original >= 0x61 && original <= 0x7A) { /* Caracteres minúsculos */
        original = original - 0x61 + 26;
    }
    else { /* Se não for letra nem número, nem modifica */
        return original;
    }

    /* Decifra */
    k = k % 62;
    convertido = original - k;
    if(convertido < 0) {
        convertido += 62;
    }

    /* Converte de volta para um valor válido de ASCII */
    if(convertido < 26) {
        convertido = convertido + 0x41;
    }
    else if(convertido >= 26 && convertido < 52) {
        convertido = convertido - 26 + 0x61;
    }
    else if(convertido >= 52) {
        convertido = convertido - 52 + 0x30;
    }

    return convertido;
}

/*------------------------------------------------------------------------------
 *  Nome: atualizaFreq
 *      Método para atualizar o vetor de frequências com um novo dado;
 *
 *      palavra - String contendo uma nova palavra com caracteres para contabilizar;
 *      freq - Vetor de frequências;
 *---------------------------------------------------------------------------*/
void atualizaFreq(std::string palavra, float* freq) {
    for(unsigned int i = 0; i < palavra.length(); i++) { /* Itera sobre cara caractere */
        int original = palavra[i];
        /* Converte do valor ASCII para um intervalo de 0-61 considerando a seguinte ordem: [A-Z, a-z, 0-9] */
        if(original >= 0x30 && original <= 0x39) { /* Números */
            original = original - 0x30 + 26;
        }
        else if(original >= 0x41 && original <= 0x5A) { /* Caracteres maiúsculos */
            original = original - 0x41;
        }
        else if(original >= 0x61 && original <= 0x7A) { /* Caracteres minúsculos */
            original = original - 0x61;
        }
        else{ /* Caso esteja fora da lista [A-Z, a-z, 0-9] não é contabilizado */
            continue;
        }

        freq[original] += 1;
    }
}

int main(int argc, char *argv[]) {
    float* freq = new float[36]; /* Cria o vetor de frequências */
    for(int i = 0; i < 36; i++) {
        freq[i] = 0;
    }

    std::vector<std::string> texto_completo;
    std::string texto_entrada; 
    do {
        std::string entrada;
        std::cin >> entrada; /* Faz a leitura do arquivo de entrada */
        if(entrada.length() > 0) { /* Verifica se havia informações no buffer */
            texto_entrada = entrada;
            atualizaFreq(texto_entrada, freq); /* Atualiza a frequência */
            texto_completo.push_back(texto_entrada); /* Armazena os dados da entrada para decifrar com o k encontrado */
        }
    } while(!std::cin.eof());

    /* Calcula a frequência para cada caractere */
    float sum = 0;
    for(int i = 0; i < 36; i++) {
        sum += freq[i];
    }

    /* Escreve as frequências encontradas na saída */
    std::cout << "Frequencias: " << std::endl;
    int max_freq_index = 0;
    for(int i = 0; i < 36; i++) {
        freq[i] /= sum;

        if(freq[i] > freq[max_freq_index]) {
            max_freq_index = i;
        }

        char convertido = i;
        if(convertido < 26) {
            convertido = convertido + 0x61;
        }
        else if(convertido >= 26) {
            convertido = convertido - 26 + 0x30;
        }

        std::cout << i << ", " << convertido << ": " << freq[i] * 100 << " %" << std::endl;
    }

    /* Utiliza como k a maior frequência no vetor, já que a maior frequência da tabela é 'a' que equivale a 0 dentro do vetor de frequências */
    int k = max_freq_index; 

    /* Itera sobre o texto de entrada mais uma vez e decifra com base no k encontrado */
    std::cout << "\nTexto decifrado com k = " << k << ":" << std::endl;
    for(std::string palavra : texto_completo) {
        for(unsigned int i = 0; i < palavra.length(); i++) {
            palavra[i] = decifrar(palavra[i], k);
        }

        std::cout << palavra << " ";
    }

    delete freq;

    return 0;
}