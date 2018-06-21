import genanki
import functools
import os

MODEL_ID = 1803127777
@functools.lru_cache()
def load_model():
  data = {}
  for fname in ['fields.json', 'templates.yaml', 'cards.css']:
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        fname)
    with open(fname) as f:
      data[fname] = f.read()

  return genanki.Model(
      MODEL_ID,
      'Anatomy',
      fields=data['fields.json'],
      templates=data['templates.yaml'],
      css=data['cards.css'],
  )

class AnatomyNote(genanki.Note):
  def __init__(self, *args, **kwargs):
    super().__init__(load_model(), *args, **kwargs)
