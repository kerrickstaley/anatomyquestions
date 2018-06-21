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
from note import AnatomyTrueFalseNote


class MultipleChoice:
  def __init__(self, prompt, options, answer, learning_outcome=None):
    self.prompt = prompt
    self.options = options
    self.answer = answer
    self.learning_outcome = learning_outcome

  @classmethod
  def parse(cls, q):
    lines = q.splitlines()

    prompt = lines[0].split(') ', 1)[1]

    options = []
    idx = 1
    while True:
      if not re.search(r'^[A-Z]\) ', lines[idx]):
        break

      options.append(lines[idx].split(') ', 1)[1])
      idx += 1

    answer = lines[idx].split(': ')[1]
    idx += 1
    learning_outcome = lines[idx].split(': ')[1]

    return cls(prompt, options, answer, learning_outcome)

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
    learning_outcome = lines[2].split(': ')[1]

    return cls(prompt, answer, learning_outcome)

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

    print(txt_file_path)

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

def main():
  p = Processor('in.doc')
  deck = genanki.Deck(2141944527, 'Anatomy (generated)')

  for q in p.true_false_questions:
    note = AnatomyTrueFalseNote(fields=[q.prompt + ' (True/False)', q.answer])
    deck.add_note(note)

  deck.write_to_file('output.apkg')


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
  main()
