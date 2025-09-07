import argparse
import logging
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("srcdir")
args = parser.parse_args()

def process_line(line: str) -> (str, bool):
	changed = False
	if 'Tidal' in line:
		line = line.replace('Tidal', 'Tidallp')
		changed = True
	chunks = line.split("tidal")
	if len(chunks) == 1:
		return line, changed
	new_line = ''
	for i in range(len(chunks)):
		new_line = new_line + chunks[i]
		if i+1 < len(chunks):
			if chunks[i+1].startswith('api'):
				new_line = new_line + "tidal"
			else:
				changed = True
				new_line = new_line + "tidallp"
	return new_line, changed


def process_files(dir_path: Path) -> None:
	logger.info("file processing: {}".format(str(dir_path)))
	for child in dir_path.iterdir():
		if child.name.startswith('.'):
			continue
		if child.is_dir():
			process_files(child)
			continue
		if child.is_file():
			changed = False
			new_child = Path(str(child.absolute()) + ".new")
			with child.open() as f:
				with new_child.open(mode='w') as new_f:
					try:
						for line in f.readlines():
							new_line, line_changed = process_line(line)
							if line_changed:
								changed = True
							new_f.write(new_line)
					except UnicodeDecodeError:
						changed = False

		if not changed:
			new_child.unlink()
		elif 'tidal' not in child.name:
			new_child.rename(str(child))
		else:
			new_name = child.parent / child.name.replace('tidal', 'tidallp')
			child.unlink()
			new_child.rename(new_name)


def process_dirs(dir_path: Path) -> None:
	logger.info("dir processing: {}".format(str(dir_path)))
	for child in dir_path.iterdir():
		if child.name.startswith('.'):
			continue
		if child.is_file():
			continue
		if child.is_dir():
			process_dirs(child)
			if 'tidal' in child.name and 'tidallp' not in child.name:
				new_name = child.parent / child.name.replace('tidal', 'tidallp')
				child.rename(new_name)


if __name__ == "__main__":
	path = Path(args.srcdir)
	if not path.exists():
		raise FileNotFoundError(args.srcdir)
	if not path.is_dir():
		raise TypeError("{} not a directory".format(args.srcdir))

	process_dirs(path)
	process_files(path)
