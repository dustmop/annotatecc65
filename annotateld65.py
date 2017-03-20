import collections
import os
import re
import shutil
import subprocess
import sys


def run_cmd(bin, cmd):
  p = subprocess.Popen(' '.join([bin] + cmd), shell=True,
                       stderr=subprocess.PIPE)
  _, err = p.communicate()
  if p.returncode != 0:
    if 'command not found' not in err:
      sys.stderr.write(err)
      sys.exit(p.returncode)
  # Check if the binary is in the same directory as this script.
  orig_err = err
  dir = os.path.dirname(__file__)
  bin = os.path.join(dir, bin)
  # Run command again.
  p = subprocess.Popen(' '.join([bin] + cmd), shell=True,
                       stderr=subprocess.PIPE)
  _, err = p.communicate()
  if p.returncode != 0:
    sys.stderr.write(orig_err)
    sys.exit(p.returncode)


class Pair(object):
  def __init__(self):
    self.first = self.second = None


def read_file(filename):
  """Get the contents of the file."""
  fp = open(filename, 'r')
  content = fp.read()
  fp.close()
  return content


def parse_ln_file(filename):
  """Read .ln file, convert it to a sorted list of address and labels."""
  content = read_file(filename)
  accum = []
  for line in content.split('\n'):
    if not line:
      continue
    if line[0] == ';':
      continue
    (oper, address, label) = line.split()
    address = address[2:]
    label = label[1:]
    accum.append([address, label])
  accum.sort(key=lambda x: x[0])
  return accum


def parse_map_file(filename):
  """Read .map file, convert it to a dict from meta-labels to source code."""
  content = read_file(filename)
  map = {}
  for line in content.split('\n'):
    if not line:
      continue
    pos = line.find(' ')
    num = line[0:pos]
    code_text = line[pos+2:]
    map[num] = code_text
  return map


def combine_ln_and_map(items, source_map):
  """Merge .ln and .map files, making a list of addresses and source code."""
  combined = collections.defaultdict(Pair)
  for address, label in items:
    if label.startswith('_Rsource_map__'):
      key = label[14:]
      code_text = source_map[key]
      if code_text.startswith('void '):
        continue
      combined[address].second = code_text
    else:
      combined[address].first = label
  accum = []
  for address in sorted(combined.keys()):
    elem = combined[address]
    accum.append([address, elem.first, elem.second])
  return accum


def link_file(args):
  run_cmd('ld65', args)


def read_num_prg_banks(rom_file):
  """Get the number of prg banks from the ROM header."""
  fp = open(rom_file, 'r')
  bytes = fp.read(5)
  fp.close()
  return ord(bytes[4])


def extract_args(args):
  """Manipulate the command-line args to the linker."""
  link_objects = []
  build_target = None
  listing_file = None
  i = 0
  while i < len(args):
    if args[i] == '-o':
      build_target = args[i + 1]
      i += 2
      continue
    elif args[i] == '-Ln':
      listing_file = args[i + 1]
      i += 2
      continue
    elif args[i].endswith('.o'):
      link_objects.append(args[i])
    i += 1
  if not listing_file:
    build_dir = os.path.dirname(link_objects[0])
    listing_file = os.path.join(build_dir, '.annotate.ln')
  return (link_objects, build_target, listing_file)


def write_build_listing(items, outfile):
  """Write contents of a single listing file."""
  fout = open(outfile, 'w')
  for address,label,comment in items:
    if label and label[0:6] == '__BSS_':
      continue
    elif label and re.match(r'L[1-9A-F]{4}', label):
      continue
    else:
      rom_start = ('%04x' % ((int(address,16) / 0x4000) * 0x4000)).upper()
      fout.write('$%s#%s#%s\n' % (address,label or '',comment or ''))
  fout.close()


def copy_build_listing(orig_file, prg_banks):
  """Copy the listing for each PRG bank."""
  for n in xrange(prg_banks):
    replace_suffix = '.nes.%d.nl' % n
    dest_file = orig_file.replace('.nes.ram.nl', replace_suffix)
    shutil.copy2(orig_file, dest_file)


def process():
  # Process command line args.
  args = sys.argv[1:]
  (link_objects, build_target, listing_file) = extract_args(args)
  if '-Ln' not in args:
    args.append('-Ln')
    args.append(listing_file)

  # Call the linker.
  link_file(args)

  # Get number of prg banks.
  prg_banks = read_num_prg_banks(build_target)

  # Parse source map for each object.
  source_map = {}
  for obj in link_objects:
    obj_dir = os.path.dirname(obj)
    obj_name = os.path.basename(obj)
    obj_base, obj_ext = os.path.splitext(obj_name)
    map_file = os.path.join(obj_dir, '.annotate.' + obj_base + '.map')
    if os.path.isfile(map_file):
      source_map.update(parse_map_file(map_file))

  # Read listing and merge with source map.
  ln_data = parse_ln_file(listing_file)
  items = combine_ln_and_map(ln_data, source_map)

  # Create listings.
  build_dir = os.path.dirname(build_target)
  build_name = os.path.basename(build_target)
  build_base, build_ext = os.path.splitext(build_name)
  build_listing = os.path.join(build_dir, build_base + '.nes.ram.nl')
  write_build_listing(items, build_listing)
  copy_build_listing(build_listing, prg_banks)


if __name__ == '__main__':
  process()
