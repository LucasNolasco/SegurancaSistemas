/*__________________________________________________________________________________
|       Trabalho 1 - Segurança de Redes e Sistemas
|       
|		Descrição: Implementação da Cifra de César
|       Aluno: Lucas da Silva Nolasco
| __________________________________________________________________________________
*/

#include <iostream>

/*------------------------------------------------------------------------------
 *  Nome: Operacao
 *      Enum com os tipos de operações possíveis para o programa, sendo elas:
 * 
 *      IDLE: Operação padrão do programa onde nada é feito
 *      CIFRAR: Faz a cifragem dos dados de entrada
 *      DECIFRAR: Decifra os dados de entrada
 *---------------------------------------------------------------------------*/
enum Operacao {
    IDLE,
    CIFRAR,
    DECIFRAR
};

/*------------------------------------------------------------------------------
 *  Nome: parseComandos
 *      Método para processar as opções passadas pela linha de comando.
 *      Opções possíveis:
 *          -c : Cifrar os dados fornecidos na entrada
 *          -d : Decifrar os dados fornecidos na entrada
 *          -k : Para fornecer o k a ser usado com a cifra de César
 *
 *      argc - Número de strings passadas em argv;
 *      argv - Vetor com os dados passados pela linha de comando;
 *      operacao - Variável para armazenar a opção passada para o programa
 *                 pela linha de comando;
 *
 *  descrição do retorno: retorna k, caso este tenha sido informado pela linha de comando.
 *                        retorna 0, caso o usuário não tenha informado k. *
 *---------------------------------------------------------------------------*/
int parseComandos(int argc, char* argv[], Operacao* operacao) {
    std::string opcao_cifrar = "-c";
    std::string opcao_decifrar = "-d";
    std::string opcao_k = "-k";

    int k = 0;

    for(int i = 1; i < argc; i++) { /* Verifica todos os argumentos passados */
        if(argv[i] == opcao_cifrar) { /* Flag -c informada pela linha de comando */
            *operacao = CIFRAR;
        }
        else if(argv[i] == opcao_decifrar) { /* Flag -d informada pela linha de comando */
            *operacao = DECIFRAR;
        }
        else if(argv[i] == opcao_k) { /* Flag -k informada pela linha de comando */
            if(i + 1 < argc) {
                sscanf(argv[i + 1], "%d", &k);
            }
        }
    }

    return k;
}

/*------------------------------------------------------------------------------
 *  Nome: converter
 *      Método para cifrar ou decifrar um caractere de entrada com base em um
 *      determinado k fornecido.
 *
 *      original - Caractere original;
 *      k - Valor de K a ser utilizado na Cifra de César;
 *      operacao - Tipo de operação a ser performada (CIFRAR ou DECIFRAR).
 *
 *  descrição do retorno: retorna char convertido, caso o dado original esteja em [A-Z, a-z, 0-9];
 *                        retorn a letra fornecida, caso o dado esteja fora de [A-Z, a-z, 0-9].
 *---------------------------------------------------------------------------*/
char converter(char original, int k, Operacao operacao) {
    char convertido = original;

    /* Converte do valor ASCII para um intervalo de 0-61 considerando a seguinte ordem: [A-Z, a-z, 0-9] */
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

    if(operacao == Operacao::CIFRAR) { /* Cifra */
        convertido = (original + k) % 62;
    }
    else if(operacao == Operacao::DECIFRAR) { /* Decifra */
        k = k % 62;
        convertido = original - k;
        if(convertido < 0) {
            convertido += 62;
        }
    }

    if(convertido < 26) { /* Converte de volta para um valor válido de ASCII */
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

int main(int argc, char *argv[]) {
    Operacao operacao = IDLE;

    int k = parseComandos(argc, argv, &operacao); /* Obtém os comandos passados no momento da execução */

    if(operacao == Operacao::IDLE) { /* Caso a operação não tenha sido informada */
        std::cout << "Operação não informada. Informe -d para decifrar e -c para cifrar" << std::endl;
        exit(-1);
    }

    std::string texto_entrada;
    do {
        std::string entrada;
        std::cin >> entrada; /* Faz a leitura do arquivo de entrada */
        if(entrada.length() > 0) { /* Verifica se havia informações no buffer */
            texto_entrada = entrada;
            for(unsigned int i = 0; i < texto_entrada.length(); i++) {
                if(k < 0) { /* Em caso de k negativo só inverte o valor de k e também a operação */
                    k *= -1;
                    if(operacao == Operacao::CIFRAR) {
                        operacao = DECIFRAR;
                    }
                    else if(operacao == Operacao::DECIFRAR) {
                        operacao = CIFRAR;
                    }
                }

                texto_entrada[i] = converter(texto_entrada[i], k, operacao); /* Aplica a cifragem/decifragem */
            }

            std::cout << texto_entrada << " "; /* Escreve na saída */
        }
    } while(!std::cin.eof());

    return 0;
}