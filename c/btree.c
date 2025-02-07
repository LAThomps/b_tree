#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int M;
int L;

int parse_args(int len_args, char *argsv[]);

int main(int argc, char *argv[]) {
    int go;
    go = parse_args(argc, argv);
    if (go == 1) {
        return 1;
    }
    printf("M:\t%d\n", M);
    printf("L:\t%d\n", L);
    return 0;
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