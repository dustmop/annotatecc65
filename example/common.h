typedef unsigned char byte;
typedef unsigned int word;

#define PPU_STATUS *((volatile byte*)(0x2002))
#define PPU_ADDR   *((volatile byte*)(0x2006))
#define PPU_DATA   *((volatile byte*)(0x2007))
