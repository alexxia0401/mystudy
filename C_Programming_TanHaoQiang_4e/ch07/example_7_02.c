#include <stdio.h>

int main()
{
    int max(int, int);
    int a, b, c;
    printf("Please enter two integer numbers: ");
    scanf("%d,%d", &a, &b);
    c = max(a, b);
    printf("max is %d\n", c);
    return 0;
}

int max(int x, int y) {
    int z;
    z = x > y? x: y;
    return z;
}
