#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>



static int sigint_called = 0;
static const char red[] = "\033[1;31m";
static const char blue[] = "\033[1;34m";
static const char green[] = "\033[1;32m";
static const char yellow[] = "\033[1;33m";
static const char reset[] = "\033[0m";

void signal_handler(int sig) {
    switch(sig) {
        case SIGINT:
            printf("%sReceived SIGINT%s\n", red, reset);
            sigint_called++;
            if (sigint_called == 3) {
                printf("%sReceived SIGINT 3 times. Exiting...%s\n", red, reset);
                exit(EXIT_SUCCESS);
            }
            break;
        case SIGALRM:
            printf("%sReceived SIGALRM%s\n", blue, reset);
            break;
        case SIGHUP:
            printf("%sReceived SIGHUP%s\n", green, reset);
            break;
        case SIGTERM:
            printf("%sReceived SIGTERM%s\n", yellow, reset);
            break;
    }
}

int main() {

    signal(SIGINT, signal_handler);
    signal(SIGALRM, signal_handler);
    signal(SIGHUP, signal_handler);
    signal(SIGTERM, signal_handler);


    printf("Worker process[PID: %s%d%s] is running...\n",red, getpid(), reset);
    while(1) {
        sleep(1);
    }

    return 0;
}
