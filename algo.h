#ifndef __ALGO_H__
#define __ALGO_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

#ifdef _WIN32
#  define _EXPORT __declspec( dllexport )
#else
#  define _EXPORT __attribute__((__visibility__("default")))
#endif

#define PU32_LENGTH (32)

typedef struct {
    uint8_t    u8;
    uint16_t   u16;
    uint16_t * pu16;
    uint32_t   length_of_pu16;
    uint32_t   pu32[PU32_LENGTH];
} MyStruct;


_EXPORT uint32_t MyFunction(MyStruct * mystruct, uint8_t  * array, uint32_t   array_size);

_EXPORT void tablefunction(uint32_t * arrayin, uint32_t  * arrayout, int width, int height);

#ifdef __cplusplus
}
#endif

#endif /* __ALGO_H__ */
