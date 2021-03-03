#include <iostream>
#include <vector>

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

    k = k % 62;
    convertido = original - k;
    if(convertido < 0) {
        convertido += 62;
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

void atualizaFreq(std::string palavra, float* freq) {
    for(unsigned int i = 0; i < palavra.length(); i++) {
        int original = palavra[i];
        if(original >= 0x30 && original <= 0x39) { /* Números */
            original = original - 0x30 + 52;
        }
        else if(original >= 0x41 && original <= 0x5A) { /* Caracteres maiúsculos */
            original = original - 0x41;
        }
        else if(original >= 0x61 && original <= 0x7A) { /* Caracteres minúsculos */
            original = original - 0x61 + 26;
        }
        else{
            continue;
        }

        freq[original] += 1;
    }
}

int main(int argc, char *argv[]) {
    float* freq = new float[62]; /* Cria o vetor de frequências */
    for(int i = 0; i < 62; i++) {
        freq[i] = 0;
    }

    std::vector<std::string> texto_completo;
    std::string texto_entrada;
    do {
        std::cin >> texto_entrada;
        atualizaFreq(texto_entrada, freq);
        texto_completo.push_back(texto_entrada);
    } while(!std::cin.eof());

    float sum = 0;
    for(int i = 0; i < 62; i++) {
        sum += freq[i];
    }

    std::cout << "Frequencias: " << std::endl;

    int max_freq_index = 0;
    for(int i = 0; i < 62; i++) {
        freq[i] /= sum;

        if(freq[i] > freq[max_freq_index]) {
            max_freq_index = i;
        }

        char convertido = i;
        if(convertido < 26) {
            convertido = convertido + 0x41;
        }
        else if(convertido >= 26 && convertido < 52) {
            convertido = convertido - 26 + 0x61;
        }
        else if(convertido >= 52) {
            convertido = convertido - 52 + 0x30;
        }

        std::cout << i << ", " << convertido << ": " << freq[i] * 100 << " %" << std::endl;
    }

    int k = max_freq_index - 26;

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