#ifndef EVAL_PERF_H
#define EVAL_PERF_H

#include <iostream>
#include <chrono>
#include <x86intrin.h>


uint64_t rdtsc(void);

struct EvalPerf {
    std::chrono::_V2::steady_clock::time_point init;
    std::chrono::_V2::steady_clock::time_point end;
    double elapsed_s;
    double elapsed_ms;
    double nb_c0, nb_c1, nb_tot;
    void start(){
        EvalPerf::init = std::chrono::steady_clock::now();
        nb_c0 = rdtsc();
    }; /* lance le chrono */

    void stop() {
        nb_c1 = rdtsc();
        end = std::chrono::steady_clock::now();
    }; /* arrete le chrono*/

    int nb_c() {
        nb_tot = nb_c1 - nb_c0;
        return nb_tot;
    }; /* renvoie le nombre de cycles */

    double nb_s() {
        elapsed_s = 
        std::chrono::duration_cast<std::chrono::duration<double>>(end - init).count();
        return elapsed_s;
    }; /* renvoie le nombre de secondes*/

    double nb_ms() {
        return (elapsed_s * 1000);
    }; /* renvoie le nombre de secondes*/

    double cpi(int N) {
        return N / nb_tot;
    }; /* renvoie le CPI*/

    double ipc(int N) {
        return nb_tot / N;
    }; /* renvoie l'IPC*/
};


uint64_t rdtsc(void) {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc": "=a" (lo), "=d" (hi));
    return ((uint64_t) hi << 32) | lo;
}
#endif // EVAL_PERF_H
