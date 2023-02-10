#include <stdio.h>

int main(void)
{
    int arr[] = { 10, 22, 35, 40, 45, 50, 80, 82, 85, 90, 100,235};
    int n = sizeof(arr) / sizeof(arr[0]);
    int x = 235;
    int y = n + x % arr[5];
    char a[] = "                     ";
    a[0] = 'r';
    a[1] = 'e';
    a[2] = 'v';
    a[3] = 'e';
    a[4] = 'r';
    a[5] = 's';
    a[6] = 'e';
    a[7] = '-';
    a[8] = 'm';
    a[9] = 'e';
    a[10] = '-';
    a[11] = 'b';
    a[12] = 'a';
    a[13] = 'b';
    a[14] = 'y';
    
    char *FLAG = &a[0];
    return 0;
}
