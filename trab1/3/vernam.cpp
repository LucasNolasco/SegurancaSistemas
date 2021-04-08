/*__________________________________________________________________________________
|       Trabalho 1 - Segurança de Redes e Sistemas
|       
|		Descrição: Implementação da Cifra de Vernam
|       Aluno: Lucas da Silva Nolasco
| __________________________________________________________________________________
*/

#include <iostream>
#include <time.h>
#include <fstream>

/*------------------------------------------------------------------------------
 *  Nome: Operacao
 *      Enum com os tipos de operações possíveis para o programa, sendo elas:
 * 
 *      IDLE: Operação padrão do programa onde nada é feito
 *      CIFRAR: Faz a cifragem dos dados de entrada
 *      DECIFRAR: Decifra os dados de entrada
 *      GERAR: Operação de gerar uma nova chave
 *---------------------------------------------------------------------------*/
enum Operacao {
    IDLE,
    CIFRAR,
    DECIFRAR,
    GERAR
};

/*------------------------------------------------------------------------------
 *  Nome: parseComandos
 *      Método para processar as opções passadas pela linha de comando.
 *      Opções possíveis:
 *          -c : Cifrar os dados fornecidos na entrada
 *          -d : Decifrar os dados fornecidos na entrada
 *          -k : Para fornecer o caminho do arquivo contendo a chave a ser utilizada
 *
 *      argc - Número de strings passadas em argv;
 *      argv - Vetor com os dados passados pela linha de comando;
 *      operacao - Variável para armazenar a opção passada para o programa
 *                 pela linha de comando;
 *      tamanho_chave - Variável para armazenar o tamanho da chave, caso o usuário
 *                      deseje gerar uma chave;
 *
 *  descrição do retorno: retorna uma string com o caminho para o arquivo da chave *
 *---------------------------------------------------------------------------*/
std::string parseComandos(int argc, char* argv[], Operacao* operacao, int* tamanho_chave) {
    std::string opcao_decifrar = "-d";
    std::string opcao_cifrar = "-c";
    std::string opcao_chave = "-k";
    std::string opcao_gerar_chave = "-g";

    std::string arquivo_chave;
    for(int i = 1; i < argc; i++) {
        if(argv[i] == opcao_chave) {
            if(i + 1 < argc) {
                arquivo_chave = argv[i + 1];
            }
            else { /* Flag -k usada mas caminho da chave não informado */
                exit(-1);
            }
        }
        else if(argv[i] == opcao_cifrar) { /* Cifrar */
            *operacao = CIFRAR;
        }
        else if(argv[i] == opcao_decifrar) { /* Decifrar */
            *operacao = DECIFRAR;
        }
        else if(argv[i] == opcao_gerar_chave) { /* Gerar */
            if(i + 1 < argc) {
                sscanf(argv[i + 1], "%d", tamanho_chave);
                *operacao = GERAR;
            }
            else {
                exit(-1);
            }
        }
    }

    return arquivo_chave;
}

/*------------------------------------------------------------------------------
 *  Nome: carregarChave
 *      Método para carregar de um arquivo a chave para ser utilizada na Cifra
 *      de Vernam.
 *
 *      caminho_chave - String com o caminho do arquivo que contém a chave.
 *
 *  descrição do retorno: retorna uma string contendo a chave lida *
 *---------------------------------------------------------------------------*/
std::string carregarChave(std::string caminho_chave) {
    std::ifstream arquivo_chave;
    std::string chave;
    arquivo_chave.open(caminho_chave);
    arquivo_chave >> chave;
    arquivo_chave.close();

    return chave;
}

/*------------------------------------------------------------------------------
 *  Nome: ASCIIparaLocal
 *      Método para converter de ASCII para um intervalo local de 0 até 61 seguindo
 *      a seguinte ordem: [A-Z, a-z, 0-9]. Caso o caractere esteja fora desse intervalo,
 *      ele é retornado sem ser convertido.
 *
 *      original - Caractere original no ASCII;
 *
 *  descrição do retorno: retorna o caractere convertido para o intervalo local.
 *---------------------------------------------------------------------------*/
char ASCIIparaLocal(char original) {
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

    return original;
}

/*------------------------------------------------------------------------------
 *  Nome: LocalParaASCII
 *      Método para converter do intervalo local para ASCII. Caso o caractere
 *      informado esteja fora do intervalo local (0 até 61), ele é retornado
 *      sem ser convertido.
 *
 *      caractere - Caractere original no ASCII;
 *
 *  descrição do retorno: retorna o caractere convertido para ASCII.
 *---------------------------------------------------------------------------*/
char localParaASCII(char convertido) {
    if(convertido < 26) { /* Maiúsculos */
        convertido = convertido + 0x41;
    }
    else if(convertido >= 26 && convertido < 52) { /* Minúsculo */
        convertido = convertido - 26 + 0x61;
    }
    else if(convertido >= 52) { /* Números */
        convertido = convertido - 52 + 0x30;
    }

    return convertido;
}

/*------------------------------------------------------------------------------
 *  Nome: converter
 *      Método para aplicar a cifra de Vernam em um determinado caractere.
 *
 *      original - Caractere original do texto de entrada;
 *      k - Valor da chave na mesma posição do caractere de entrada;
 *      operacao - Operação a ser executada (CIFRAR ou DECIFRAR).
 *
 *  descrição do retorno: retorna o caractere cifrado/decifrado.
 *---------------------------------------------------------------------------*/
char converter(char original, char k, Operacao operacao) {
    char convertido = original;

    original = ASCIIparaLocal(original);
    k = ASCIIparaLocal(k);

    if (original == convertido) {
        return original;
    }

    if (operacao == CIFRAR) {
        convertido = (original + k) % 62;
    }
    else {
        convertido = original - k;
        if (convertido < 0) {
            convertido += 62;
        }
    }

    convertido = localParaASCII(convertido);
    return convertido;
}

/*------------------------------------------------------------------------------
 *  Nome: gerarChave
 *      Método para gerar uma chave para ser utilizada pela cifra de Vernam.
 *      Simplesmente gera caracteres aleatórios que estejam dentro de [A-Z, a-z, 0-9]
 *      utilizando como semente o timestamp atual.
 *
 *      tamanho - Número de caracteres que a chave deve ter;
 *---------------------------------------------------------------------------*/
void gerarChave(int tamanho) {
    char chave;

    srand(time(NULL));
    for(int i = 0; i < tamanho; i++) {
        chave = rand() % 62;
        chave = localParaASCII(chave);

        std::cout << chave;
    }
}

int main(int argc, char *argv[]) {
    Operacao operacao = IDLE;

    int tamanho_chave = 0;
    std::string arquivo_chave = parseComandos(argc, argv, &operacao, &tamanho_chave); /* Obtém os comandos passados no momento da execução */
    if(operacao == Operacao::IDLE) { /* Caso a operação não tenha sido informada */
        std::cout << "Operação não informada. Informe -d para decifrar e -c para cifrar" << std::endl;
        exit(-1);
    }
    else if(operacao == Operacao::GERAR){ /* Gera a chave */
        gerarChave(tamanho_chave);
    }
    else if(operacao == Operacao::CIFRAR || operacao == Operacao::DECIFRAR) {
        std::string chave = carregarChave(arquivo_chave); /* Carrega a chave */

        std::string texto_entrada;
        unsigned int j = 0;
        do {
            std::string entrada;
            std::cin >> entrada; /* Faz a leitura do arquivo de entrada */
            if(entrada.length() > 0) { /* Verifica se havia informações no buffer */
                texto_entrada = entrada;
                for(unsigned int i = 0; i < texto_entrada.length(); i++) {
                    if(j < chave.length()) { /* Verifica se a chave possui tamanho suficiente */
                        texto_entrada[i] = converter(texto_entrada[i], chave[j], operacao);
                        j++;
                    }
                    else { /* Caso a chave tenha estourado, exibe o erro */
                        std::cout << " Erro! Tamanho da chave menor que a quantidade de caracteres do texto a ser convertido";
                        exit(-1);
                    }
                }
                j++; /* Pula o espaço */

                std::cout << texto_entrada << " ";
            }
        } while(!std::cin.eof());
    }

    return 0;
}