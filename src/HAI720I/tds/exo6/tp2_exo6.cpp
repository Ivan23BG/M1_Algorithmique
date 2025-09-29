#include "EvalPerf.hpp"
#include <string>
#include <stdlib.h> /* necessaire dans cet exercice pour creer des tableaux aleatoires */
#include <stdio.h> /* necessaire dans cet exercice pour lire des entrees */
#include <iostream> /* lecture et ecriture de fichiers */
#include <fstream> 
#include <math.h> /* pour la fonction puissance */

int ma_fonction_naive(int*, int, int);
int flops_ma_fonction_naive(int);
int ma_fonction_horner(int*, int, int);
int flops_ma_fonction_horner(int);


int main(int argc, char **argv) {
    if (argc < 2) {
        printf("You must enter the following details:\nmin max array_size number_of_loops alpha output_file\n");
        return -1;
    }
    /* declaration des variables*/
    int min, max, array_size, number_of_loops, N, alpha;
    EvalPerf PE;

    /* variables statistiques moyennes */
    int nbctot1=0;
    double nbstot1=0, nbcpitot1=0, nbmstot1=0, nbipctot1=0;
    int nbctot2=0;
    double nbstot2=0, nbcpitot2=0, nbmstot2=0, nbipctot2=0;

    /* initialisation des valeurs */
    srand(time(NULL));
    min = atoi(argv[1]);
    max = atoi(argv[2]);
    array_size = atoi(argv[3]);
    number_of_loops = atoi(argv[4]);
    alpha = atoi(argv[5]);
    int A[array_size];

    int acc1=0, acc2=0;
    
    /* on ouvre le fichier de sortie */
    std::ofstream fichier {argv[6]};
    
    for (int k=0; k < number_of_loops; k++) {
        for (int i = 0; i < array_size; i++) {
            A[i] = rand() % (max + 1 - min) + min;
        }
        acc1 = 0;
        acc2 = 0;
        // printf("acc1: %d, acc2: %d\n", acc1, acc2);
        /* premier programme */
        PE.start();
        acc1 = ma_fonction_naive(A, array_size, alpha);
        PE.stop();

        N = flops_ma_fonction_naive(array_size);
        nbctot1 += PE.nb_c();
        nbstot1 += PE.nb_s();
        nbmstot1 += PE.nb_ms();
        nbcpitot1 += PE.cpi(N);
        nbipctot1 += PE.ipc(N);

        /* deuxieme programme */
        PE.start();
        acc2 = ma_fonction_horner(A, array_size, alpha);
        PE.stop();

        N = flops_ma_fonction_horner(array_size);
        nbctot2 += PE.nb_c();
        nbstot2 += PE.nb_s();
        nbmstot2 += PE.nb_ms();
        nbcpitot2 += PE.cpi(N);
        nbipctot2 += PE.ipc(N);
        printf("acc1: %d, acc2: %d\n", acc1, acc2);
    }

    fichier << "nbc:" << ((double) nbctot1 / number_of_loops) << //
            "   |" << ((double) nbctot2 / number_of_loops) << //
    "\n";
    fichier << "nbs:" << ((double) nbstot1 / number_of_loops) << //
            "   |" << ((double) nbstot2 / number_of_loops) << //
    "\n";
    fichier << "nbms:" << ((double) nbmstot1 / number_of_loops) <<
            "   |" << ((double) nbmstot2 / number_of_loops) << //
    "\n";
    fichier << "CPI=" << ((double) nbcpitot1 / number_of_loops) <<
            "   |" << ((double) nbcpitot2 / number_of_loops) << //
    "\n";
    fichier << "IPC=" << ((double) nbipctot1 / number_of_loops) <<
            "   |" << ((double) nbipctot2 / number_of_loops) << //
    "\n";
    
    /* on ferme le fichier de sortie */
    fichier.close();
    
    return 0;
}



int ma_fonction_naive(int* p, int n, int alpha) {
    /* methode naive */
    int res = 0;
    for (int i=0; i<n; i++) {
        res += p[i] * pow(alpha, i);
    }
    return res;
}

int flops_ma_fonction_naive(int n) {
    return 3*n;
}


int ma_fonction_horner(int* p, int n, int alpha) {
    /* methode horner */
    int res = 0;
    for (int i=1; i<=n; i++) {
        res += res * alpha + p[n-i];
    }
    return res;
}

int flops_ma_fonction_horner(int n) {
    return 2*n;
}

/*  commandes d'execution:
    ./execs/tp2 1 30 20 10 6 exo6_out.txt
    ./execs/tp2_O0 1 30 20 10 6 exo6_out_O0.txt
    ./execs/tp2_O1 1 30 20 10 6 exo6_out_O1.txt
    ./execs/tp2_O2 1 30 20 10 6 exo6_out_O2.txt
    ./execs/tp2_O3 1 30 20 10 6 exo6_out_O3.txt
*/
/* commandes de compilation:
    g++ tp2_exo6.cpp -o execs/tp2
    g++ -O0 tp2_exo6.cpp -o execs/tp2_O0
    g++ -O1 tp2_exo6.cpp -o execs/tp2_O1
    g++ -O2 tp2_exo6.cpp -o execs/tp2_O2
    g++ -O3 tp2_exo6.cpp -o execs/tp2_O3
*/