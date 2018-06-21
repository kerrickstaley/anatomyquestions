#!/usr/bin/env python3
import sys
import re
from cached_property import cached_property
import string

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
  def __init__(self, txt_path):
    self.txt_path = txt_path

  @cached_property
  def raw_questions(self):
    rv = []
    qlines = []
    with open(self.txt_path) as f:
      for line in f:
        # skip section headings
        if re.match(r'^[0-9]+\.[1-9].*\bQuestions\b.*$',  line):
          continue

        if re.match(r'^[0-9]+\)', line):
          rv.append(''.join(qlines).strip())
          qlines = [line]
          continue

        qlines.append(line)

    rv.append(''.join(qlines).strip())

    return rv

  @cached_property
  def multiple_choice_questions_raw(self):
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
  def true_false_questions_raw(self):
    rv = []
    for q in self.raw_questions:
      if re.search(r'Answer:\s+(TRUE|FALSE)', q):
        rv.append(q)

    return rv

  @cached_property
  def multiple_choice_questions(self):
    return [MultipleChoice.parse(q) for q in self.multiple_choice_questions_raw]

  @cached_property
  def true_false_questions(self):
    return [TrueFalse.parse(q) for q in self.true_false_questions_raw]

def main():
  p = Processor('in.txt')
  for q in p.multiple_choice_questions + p.true_false_questions:
    print(q)
    print()


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
  main()
