#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "utils.h"

int M;
int L;
int N = 16;
int INITIAL_SIZE;
int NUM_LEVELS;
int ROOT_ADDR;
int NUMS[16] = {
    5, 81, 85, 16, 80, 97, 23, 13, 21, 42, 87, 14, 8, 52, 54, 31
};

void calc_metadata(int m, int l, int n);
int parse_args(int len_args, char *argsv[]);

int main(int argc, char *argv[]) {
    int go;
    go = parse_args(argc, argv);
    if (go == 1) {
        return 1;
    }
    calc_metadata(M, L, N);
    int B[INITIAL_SIZE];

    printf("Memory allocated on the stack for:\n");
    printf("M:\t\t%d\n", M);
    printf("L:\t\t%d\n", L);
    printf("Num Levels:\t%d\n", NUM_LEVELS);
    printf("Initial size:\t%d\n", INITIAL_SIZE);
    printf("Root Addr:\t%d\n\n", ROOT_ADDR);
    print_arr(NUMS, 16);
    return 0;
}

void calc_metadata(int m, int l, int n) {
    NUM_LEVELS = ceil(log(n) / log(m));
    for (int i = 0; i < NUM_LEVELS; i++) {
        INITIAL_SIZE += (m - 1) * pow(m, i);
    }
    INITIAL_SIZE += l * pow(m, NUM_LEVELS);
    ROOT_ADDR = INITIAL_SIZE - (l - 1);
}

int parse_args(int len_args, char *argsv[]) {
    if (len_args < 2 || len_args != 5) {
        printf("m/l args not passed\n");
        return 1;
    } else {
        int i = 1;
        while (i < len_args) {
            if (strcmp(argsv[i], "-m") == 0) {
                M = atoi(argsv[i + 1]);
            } else if (strcmp(argsv[i], "-l") == 0) {
                L = atoi(argsv[i + 1]);
            } 
            i++;
        }
    }
    if (M == 0 || L == 0) {
        printf("unable to parse M, L args\n");
        printf("must be formatted like '-m 5 -l 4'\n");
        return 1;
    } else {
        return 0;
    }
}