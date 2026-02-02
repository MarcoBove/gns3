#include <stdio.h>
#include <string.h>
#include <ctype.h>

// Simple program to check for palindromes
// University Lab - Lesson1

int main() {
    char str[100];
    int l = 0;
    int h;

    printf("\n=== PALINDROME CHECKER v1.0 ===\n");
    printf("Enter a word to check: ");
    scanf("%s", str);

    h = strlen(str) - 1;

    while (h > l) {
        if (str[l++] != str[h--]) {
            printf("Result: %s is NOT a palindrome.\n\n", str);
            return 0;
        }
    }

    printf("Result: %s is a PALINDROME!\n\n", str);
    return 0;
}
