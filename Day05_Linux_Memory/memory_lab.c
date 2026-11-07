
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int global_init = 100;
int global_uninit;
static int static_var = 200;

int main(void)
{
    int local_var = 10;
    int *heap_var = malloc(sizeof(int));

    if (heap_var == NULL) {
        perror("malloc");
        return 1;
    }

    *heap_var = 30;

    printf("===== PROCESS =====\n");
    printf("PID             : %ld\n", (long)getpid());

    printf("\n===== GLOBAL / STATIC =====\n");
    printf("global_init     : %p\n", (void *)&global_init);
    printf("global_uninit   : %p\n", (void *)&global_uninit);
    printf("static_var      : %p\n", (void *)&static_var);

    printf("\n===== STACK =====\n");
    printf("local_var       : %p\n", (void *)&local_var);
    printf("heap_var itself : %p\n", (void *)&heap_var);

    printf("\n===== HEAP =====\n");
    printf("malloc address  : %p\n", (void *)heap_var);
    printf("malloc value    : %d\n", *heap_var);

    printf("\nPress ENTER to exit...\n");
    fflush(stdout);
    getchar();

    free(heap_var);
    return 0;
}
