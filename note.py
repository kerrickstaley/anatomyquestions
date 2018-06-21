import genanki
import functools
import os

TRUE_FALSE_MODEL_ID = 1803127777
@functools.lru_cache()
def load_true_false_model():
  data = {}
  for fname in ['fields.json', 'templates.yaml', 'cards.css']:
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'true_false_model',
        fname)
    with open(path) as f:
      data[fname] = f.read()

  return genanki.Model(
      TRUE_FALSE_MODEL_ID,
      'Anatomy True False',
      fields=data['fields.json'],
      templates=data['templates.yaml'],
      css=data['cards.css'],
  )

class AnatomyTrueFalseNote(genanki.Note):
  def __init__(self, *args, **kwargs):
    super().__init__(load_true_false_model(), *args, **kwargs)


MULTIPLE_CHOICE_MODEL_ID = 1803127778
@functools.lru_cache()
def load_multiple_choice_model():
  data = {}
  for fname in ['fields.json', 'templates.yaml', 'cards.css']:
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'multiple_choice_model',
        fname)
    with open(path) as f:
      data[fname] = f.read()

  return genanki.Model(
      MULTIPLE_CHOICE_MODEL_ID,
      'Anatomy Multiple Choice',
      fields=data['fields.json'],
      templates=data['templates.yaml'],
      css=data['cards.css'],
  )

class AnatomyMultipleChoiceNote(genanki.Note):
  def __init__(self, *args, **kwargs):
    super().__init__(load_multiple_choice_model(), *args, **kwargs)
