import os
import re
import subprocess
import sys


def run_cmd(bin, cmd):
  p = subprocess.Popen(' '.join([bin] + cmd), shell=True,
                       stderr=subprocess.PIPE)
  out, err = p.communicate()
  if p.returncode == 0:
    return
  if not ('command not found' in err or 'not recognized as an' in err):
    sys.stderr.write(err)
    sys.exit(p.returncode)
  # Check if the binary is in the same directory as this script.
  orig_err = err
  dir = os.path.dirname(__file__)
  bin = os.path.join(dir, bin)
  # Run command again.
  p = subprocess.Popen(' '.join([bin] + cmd), shell=True,
                       stderr=subprocess.PIPE)
  out, err = p.communicate()
  if p.returncode == 0:
    return
  if not ('command not found' in err or 'not recognized as an' in err):
    sys.stderr.write(err)
  else:
    sys.stderr.write(orig_err)
  sys.exit(p.returncode)


def read_file(name):
  fp = open(name, 'r')
  content = fp.read()
  fp.close()
  return content


def annotate_intermediary(source_basename, content, fout, fmap):
  """Insert meta-labels into the compiled source while building map file."""
  is_code = n = 0
  for line in content.split('\n'):
    if not line:
      continue
    # cc65 outputs source code as three commented lines.
    if line[0] == ';':
      is_code += 1
    else:
      is_code = 0
    # cc65 disables debuginfo, turn it back on.
    if re.match(r'\W*.debuginfo.*off', line):
      fout.write('.debuginfo on\n')
      continue
    if re.match(r'\W*.debuginfo.*-', line):
      fout.write('.debuginfo +\n')
      continue
    fout.write(line + '\n')
    # The source code appears on the middle commented line.
    if is_code == 2:
      code_text = line[1:]
    elif is_code == 3:
      # Don't output source code for raw assembly, because it's not needed.
      if '__asm__' in code_text:
        continue
      if n:
        fout.write('_Rsource_map__%s__%04d:\n' % (source_basename, n))
        fmap.write('%s__%04d %s\n' % (source_basename, n, code_text))
      n += 1


def compile_file(args, filename):
  args.append('-o')
  args.append(filename)
  run_cmd('cc65', args)


def manipulate_args(args):
  output_file = None
  filtered_args = []
  i = 0
  while i < len(args):
    if args[i] == '-o':
      output_file = args[i + 1]
      i += 2
      continue
    filtered_args.append(args[i])
    i += 1
  return (output_file, filtered_args)


def process():
  args = sys.argv[1:]
  (output_file, args) = manipulate_args(args)
  if '--add-source' not in args:
    args.append('--add-source')
  final_dir = os.path.dirname(output_file)
  final_name = os.path.basename(output_file)
  final_base, final_ext = os.path.splitext(final_name)
  inter_file = os.path.join(final_dir, '.annotate.' + final_base + '.s')
  outmap_file = os.path.join(final_dir, '.annotate.' + final_base + '.map')
  compile_file(args, inter_file)
  fout = open(output_file, 'w')
  fmap = open(outmap_file, 'w')
  annotate_intermediary(final_base, read_file(inter_file), fout, fmap)
  fout.close()
  fmap.close()


if __name__ == '__main__':
  process()
