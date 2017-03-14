import os
import subprocess
import sys


def run_cmd(cmd):
  p = subprocess.Popen(' '.join(cmd), shell=True)
  p.communicate()
  if p.returncode != 0:
    sys.exit(p.returncode)


def read_file(name):
  fp = open(name, 'r')
  content = fp.read()
  fp.close()
  return content


def annotate_intermediary(source_basename, content, fout, fmap):
  is_code = n = 0
  for line in content.split('\n'):
    if not line:
      continue
    if line[0] == ';':
      is_code += 1
    else:
      is_code = 0
    if line == '\t.debuginfo\toff':
      fout.write('.debuginfo on\n')
      continue
    fout.write(line + '\n')
    if is_code == 2:
      code_text = line[1:]
    elif is_code == 3:
      if '__asm__' in code_text:
        continue
      if n:
        fout.write('_Rsource_map__%s__%04d:\n' % (source_basename, n))
        fmap.write('%s__%04d %s\n' % (source_basename, n, code_text))
      n += 1


def compile_file(args, filename):
  args.append('-o')
  args.append(filename)
  run_cmd(['cc65'] + args)


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
