#!/usr/bin/env python3
import sys
import re
from cached_property import cached_property
import string
import tempfile
import subprocess
import os.path
import glob

import genanki
from note import AnatomyTrueFalseNote, AnatomyMultipleChoiceNote


class MultipleChoice:
  def __init__(self, prompt, options, answer, learning_outcome=None):
    self.prompt = prompt
    self.options = options
    self.answer = answer
    self.learning_outcome = learning_outcome

  @classmethod
  def parse(cls, q):
    lines = q.splitlines()

    promptlines = []
    idx = 0
    while True:
      if re.search(r'^[A-Z]\) ', lines[idx]):
        break
      promptlines.append(lines[idx])
      idx += 1

    promptlines[0] = promptlines[0].split(') ', 1)[1]
    prompt = '\n'.join(promptlines)

    options = []
    while True:
      if not re.search(r'^[A-Z]\) ', lines[idx]):
        break

      options.append(lines[idx].split(') ', 1)[1])
      idx += 1

    answer = lines[idx].split(': ')[1]
    idx += 1
    learning_outcome = lines[idx].split(': ')[1].strip()

    return cls(prompt, options, answer, learning_outcome)

  def to_note(self):
    tags = [f'chapter_{self.learning_outcome.split(".")[0]}', f'learning_outcome_{self.learning_outcome}']
    prompt_html = self.prompt.replace('\n', '<br>')
    options_html = ''.join('<li>' + opt + '</li>' for opt in self.options)
    return AnatomyMultipleChoiceNote(fields=[prompt_html, options_html, self.answer], tags=tags)

  def __str__(self):
    options_str = '\n'.join(string.ascii_uppercase[i] + ') ' + opt for i, opt in enumerate(self.options))
    return f'{self.prompt}\n{options_str}\nAnswer: {self.answer}\nLearning Outcome: {self.learning_outcome}'


class TrueFalse:
  def __init__(self, prompt, answer, learning_outcome=None):
    self.prompt = prompt
    self.answer = answer
    self.learning_outcome = learning_outcome

  @classmethod
  def parse(cls, q):
    lines = q.splitlines()

    prompt = lines[0].split(') ', 1)[1]
    answer = lines[1].split(': ')[1]
    learning_outcome = lines[2].split(': ')[1].strip()

    return cls(prompt, answer, learning_outcome)

  def to_note(self):
    tags = [f'chapter_{self.learning_outcome.split(".")[0]}', f'learning_outcome_{self.learning_outcome}']
    return AnatomyTrueFalseNote(fields=[self.prompt, self.answer], tags=tags)

  def __str__(self):
    return f'{self.prompt}\nAnswer: {self.answer}\nLearning Outcome: {self.learning_outcome}'


class Processor:
  def __init__(self, doc_path):
    self.doc_path = doc_path

  @cached_property
  def doc_as_text(self):
    tmpdir = tempfile.mkdtemp()
    subprocess.check_call([
      'libreoffice',
      '--headless',
      '--convert-to',
      'txt:Text (encoded):UTF8',
      '--outdir',
      tmpdir,
      self.doc_path])

    # libreoffice is so dumb
    while not glob.glob(os.path.join(tmpdir, '*.txt')):
      pass

    txt_file_path = glob.glob(os.path.join(tmpdir, '*.txt'))[0]

    with open(txt_file_path) as f:
      rv = f.read()

    return rv

  @cached_property
  def raw_questions(self):
    rv = []
    qlines = []
    for line in self.doc_as_text.splitlines():
      # skip section headings
      if re.match(r'^[0-9]+\.[1-9].*\bQuestions\b.*$',  line):
        continue

      if re.match(r'^[0-9]+\)', line):
        rv.append('\n'.join(qlines).strip())
        qlines = [line]
        continue

      qlines.append(line)

    rv.append('\n'.join(qlines).strip())

    return rv

  @cached_property
  def raw_multiple_choice_questions(self):
    rv = []
    for q in self.raw_questions:
      if 'indicated by Label' in q:
        continue

      if 'specified by Label' in q:
        continue

      if not ('\nA)' in q and '\nB)' in q):
        continue

      rv.append(q)

    return rv

  @cached_property
  def raw_true_false_questions(self):
    rv = []
    for q in self.raw_questions:
      if re.search(r'Answer:\s+(TRUE|FALSE)', q):
        rv.append(q)

    return rv

  @cached_property
  def multiple_choice_questions(self):
    return [MultipleChoice.parse(q) for q in self.raw_multiple_choice_questions]

  @cached_property
  def true_false_questions(self):
    return [TrueFalse.parse(q) for q in self.raw_true_false_questions]


def sort_docs(paths):
  def extract_chapter(path):
    fname = os.path.basename(path)
    m = re.search(' ([0-9]+) ', fname)
    if m:
      return int(m.group(1))
    return 0

  return sorted(paths, key=extract_chapter)


def main(doc_paths):
  deck = genanki.Deck(2141944527, 'Anatomy (generated)')

  doc_paths = sort_docs(doc_paths)

  for doc_path in doc_paths:
    p = Processor(doc_path)

    for q in p.multiple_choice_questions + p.true_false_questions:
      deck.add_note(q.to_note())

  deck.write_to_file('output.apkg')


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
  main(sys.argv[1:])
