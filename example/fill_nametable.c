#include "common.h"

#define BLANK_TILE 0x05

void fill_nametable() {
  static word count;
  static byte num;

  num = PPU_STATUS;

  PPU_ADDR = 0x20;
  PPU_ADDR = 0x00;
  // Clear nametable.
  for (count = 0; count < 0x3c0; count++) {
    PPU_DATA = BLANK_TILE;
  }
  // Clear attribute.
  for (count = 0; count < 0x40; count++) {
    PPU_DATA = 0;
  }

  PPU_ADDR = 0x21;
  PPU_ADDR = 0x8a;
  for (num = 0; num < 11; num++) {
    PPU_DATA = num;
  }
}
