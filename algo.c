#include <stdio.h>
#include "algo.h"

/**
 * Function that prints content of input structures/arrays
 */
uint32_t MyFunction(
    MyStruct * mystruct,
    uint8_t  * array,
    uint32_t   array_size
){
    printf("***************\nHELLO from C Code!!\n***************\n\n");
    printf("mystruct = {\n");
    printf("\tu8 = %d\n", mystruct->u8);
    printf("\tu16 = %d\n", mystruct->u16);
    printf("\tpu16 = {");
    for (int i = 0; i < mystruct->length_of_pu16; ++i) {
        printf("%d, ", mystruct->pu16[i]);
    }
    printf("}\n");
    printf("\tpu32 = {");
    for (int i = 0; i < PU32_LENGTH; ++i) {
        printf("%d, ", mystruct->pu32[i]);
    }
    printf("}\n\n");

    printf("array = {");
    for (int i = 0; i < array_size; ++i) {
        printf("%d, ", array[i]);
    }
    printf("}\n");
    return array_size + 2;
}

void tablefunction(
    uint32_t * arrayin,
    uint32_t  * arrayout,
    int width,
    int height
){
    printf("\nTable modification from C code \n\n");
    for (int i = 0 ; i<height ; i++) {
        int offset = i*width;
        for (int j = 0 ; j<width ; j++) {
            arrayout[offset+j] = arrayin[offset+j] + 1;
        }
    }
}
