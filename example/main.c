#include "neslib.h"

void create_text();
void fill_nametable();

void main(void)
{
  // All white palette.
  pal_col(1, 0x30);
  pal_col(2, 0x30);
  pal_col(3, 0x30);

  // Display text.
  create_text();
  fill_nametable();

  // Turn on rendering.
  ppu_on_all();

  // Loop forever.
  while(1);
}
