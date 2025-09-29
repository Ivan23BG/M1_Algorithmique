/* on reprend le squelette de l'exo 4 en modifiant les fonctions appropriées */
#include "EvalPerf.hpp"
#include <string>
#include <stdlib.h> /* necessaire dans cet exercice pour creer des tableaux aleatoires */
#include <stdio.h> /* necessaire dans cet exercice pour lire des entrees */
#include <iostream> /* lecture et ecriture de fichiers */
#include <fstream> 

void ma_fonction(int *, int);
int flops_ma_fonction(int);


int main(int argc, char **argv) {
    if (argc < 2) {
        printf("You must enter the following details:\nmin max array_size number_of_loops output_file\n");
        return -1;
    }
    /* declaration des variables*/
    int min, max, array_size, number_of_loops, N;
    EvalPerf PE;

    /* initialisation des valeurs */
    srand(time(NULL));
    min = atoi(argv[1]);
    max = atoi(argv[2]);
    array_size = atoi(argv[3]);
    number_of_loops = atoi(argv[4]);
    int A[array_size], B[array_size];

    int nbctot;
    double nbstot, nbcpitot, nbmstot, nbipctot;
    /* on ouvre le fichier de sortie */
    std::ofstream fichier {argv[5]};
    /* boucle sur le nombre de resultats */
    for (int k=0; k < number_of_loops; k++) {
        /* boucle sur la taille du tableau */
        for (int i = 0; i < array_size; i++) {
            A[i] = rand() % (max + 1 - min) + min;
            B[i] = A[i];
        }
        PE.start();
        ma_fonction(B, array_size);
        PE.stop();
        N = flops_ma_fonction(array_size);
        
        nbctot += PE.nb_c();
        nbstot += PE.nb_s();
        nbmstot += PE.nb_ms();
        nbcpitot += PE.cpi(N);
        nbipctot += PE.ipc(N);
        /*  Si on veut tester le bon fonctionnement de notre programme on
            peut decommenter les lignes suivantes */
        /*
        printf("Voici A:\n[");
        for (int i = 0; i < array_size; i++) {
            printf("%d, ", A[i]);
        }
        printf("]\n");
        printf("Et voici B:\n[");
        for (int i = 0; i < array_size; i++) {
            printf("%d, ", B[i]);
        }
        printf("]\n");
        */
    }
    std::cout << "nbc:" << PE.nb_c() << std::endl;
    std::cout << "nbs:" << PE.nb_s() << std::endl;
    std::cout << "nbms:" << PE.nb_ms() << std::endl;
    std::cout << "CPI=" << PE.cpi(N) << std::endl;
    std::cout << "IPC=" << PE.ipc(N) << std::endl;

    fichier << "nbc:" << (double) nbctot / number_of_loops << "\n";
    fichier << "nbs:" << (double) nbstot / number_of_loops << "\n";
    fichier << "nbms:" << (double) nbmstot / number_of_loops << "\n";
    fichier << "CPI=" << (double) nbcpitot / number_of_loops << "\n";
    fichier << "IPC=" << (double) nbipctot / number_of_loops << "\n";

    /* on ferme le fichier de sortie */
    fichier.close();
    
    return 0;
}



void ma_fonction(int* B, int n) {
    /* somme prefixe */
    for (int i=1; i < n; i++) {
        B[i] = B[i] + B[i-1];
    }
}

int flops_ma_fonction(int n) {
    return n;
}

/*  commandes d'execution:
    ./execs/tp2 0 1000 50000 10000 exo5_out.txt
    ./execs/tp2_O1 0 1000 50000 10000 exo5_out_O1.txt
    ./execs/tp2_O2 0 1000 50000 10000 exo5_out_O2.txt
    ./execs/tp2_O3 0 1000 50000 10000 exo5_out_O3.txt
*/
/* commandes de compilation:
    g++ tp2_exo5.cpp -o execs/tp2
    g++ -O0 tp2_exo5.cpp -o execs/tp2_O0
    g++ -O1 tp2_exo5.cpp -o execs/tp2_O1
    g++ -O2 tp2_exo5.cpp -o execs/tp2_O2
    g++ -O3 tp2_exo5.cpp -o execs/tp2_O3
*/