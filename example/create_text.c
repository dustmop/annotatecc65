#include "common.h"

// Compressed "HELLO THERE"
static byte compressed_data[] = {
  0x03,0xc6,0xfe,0x03,0xc6,0x80,0xfe,0x02,
  0xc0,0xfc,0x02,0xc0,0xfe,0x80,0x06,0x60,
  0x01,0x7e,0x80,0x06,0x60,0x01,0x7e,0x80,
  0x01,0x7c,0x05,0xc6,0x01,0x7c,0x19,0x00,
  0x01,0x7e,0x06,0x18,0x80,0x03,0xc6,0xfe,
  0x03,0xc6,0x80,0xfe,0x02,0xc0,0xfc,0x02,
  0xc0,0xfe,0x80,0xfc,0x02,0xc6,0xce,0xf8,
  0xdc,0xce,0x80,0xfe,0x02,0xc0,0xfc,0x02,
  0xc0,0xfe,0x0a,0x00,0x00,
};

void create_text() {
  static byte* load_pointer;
  static byte val, count;

  load_pointer = compressed_data;

  val = PPU_STATUS;
  PPU_ADDR = 0x00;
  PPU_ADDR = 0x00;

  while (1) {
    count = *(load_pointer++);
    if (count == 0) {
      // Exit the loop.
      break;
    } else if (count < 0x80) {
      // Repeated bytes.
      val = *(load_pointer++);
      while (count--) {
        PPU_DATA = val;
      }
    } else if (count == 0x80) {
      // 0x80 means 9 repeated null bytes.
      val = 0x00;
      count = 9;
      while (count--) {
        PPU_DATA = val;
      }
    } else {
      // Literal value.
      val = count;
      PPU_DATA = val;
    }
  }
}
