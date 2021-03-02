#include <iostream>

enum Operacao {
    IDLE,
    CIFRAR,
    DECIFRAR
};

int parseComandos(int argc, char* argv[], Operacao* operacao) {
    std::string opcao_cifrar = "-c";
    std::string opcao_decifrar = "-d";
    std::string opcao_k = "-k";

    int k = 0;

    for(int i = 1; i < argc; i++) {
        if(argv[i] == opcao_cifrar) {
            *operacao = CIFRAR;
        }
        else if(argv[i] == opcao_decifrar) {
            *operacao = DECIFRAR;
        }
        else if(argv[i] == opcao_k) {
            if(i + 1 < argc) {
                sscanf(argv[i + 1], "%d", &k);
            }
        }
    }

    return k;
}

char converter(char original, int k, Operacao operacao) {
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

    if(operacao == Operacao::CIFRAR) {
        convertido = (original + k) % 62;
    }
    else if(operacao == Operacao::DECIFRAR) {
        k = k % 62;
        convertido = original - k;
        if(convertido < 0) {
            convertido += 62;
        }
    }

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

int main(int argc, char *argv[]) {
    Operacao operacao = IDLE;

    int k = parseComandos(argc, argv, &operacao);

    if(operacao == Operacao::IDLE) {
        std::cout << "Operação não informada. Informe -d para decifrar e -c para cifrar" << std::endl;
        exit(-1);
    }

    std::string texto_entrada;
    std::cin >> texto_entrada;
    while(!std::cin.eof()) {
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

            texto_entrada[i] = converter(texto_entrada[i], k, operacao);
        }

        std::cout << texto_entrada << " ";
        std::cin >> texto_entrada;
    }

    return 0;
}