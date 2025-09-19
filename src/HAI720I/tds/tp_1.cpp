#include "EvalPerf.hpp"
#include <string>

int ma_fonction(int);
int flops_ma_fonction(int);


int main() {
    int n, N;
    EvalPerf PE;
    n = 100000000;
    PE.start();
    ma_fonction(n);
    PE.stop();
    N = flops_ma_fonction(n);
    std::cout << "nbc:" << PE.nb_c() << std::endl;
    std::cout << "nbs:" << PE.nb_s() << std::endl;
    std::cout << "nbms:" << PE.nb_ms() << std::endl;
    std::cout << "CPI=" << PE.cpi(N) << std::endl;;
    std::cout << "IPC=" << PE.ipc(N) << std::endl;;
    
    return 0;
}



int ma_fonction(int n) {
    int t=0;
    for (int i=0; i<n; i++) {
        t += i;
        t *= i;
    }
    return t;
}

int flops_ma_fonction(int n) {
    return 2*n;
}