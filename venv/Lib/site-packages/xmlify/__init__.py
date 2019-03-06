# -*- coding: utf-8 -*-
'''
@author: saaj
'''


import re
import collections
import binascii
from io import BytesIO

try:
  import xml.etree.cElementTree as etree
except ImportError: # pragma: no cover
  import xml.etree.ElementTree as etree


__all__ = 'dump', 'dumps'


try: # pragma: no cover
  __basestr = basestring
  __bytes   = str
  __unicode = unicode
except NameError: # pragma: no cover
  __basestr = bytes, str
  __bytes   = bytes 
  __unicode = str
'''Python 2/3 compatible string types'''


_notFirstCharRe  = re.compile(r'[^a-z_]{1}', re.IGNORECASE)
_notOtherCharsRe = re.compile(r'[^a-z0-9_\-\.]', re.IGNORECASE)

def _key(obj):
  try:
    if isinstance(obj, __bytes):
      key = obj.decode('ascii')
    else:
      key = __unicode(obj).encode('ascii').decode('ascii')
      
    key = _notOtherCharsRe.sub('_', key)
    if not key:
      raise ValueError
    
    if _notFirstCharRe.match(key):
      key = 'n' + key
  except (UnicodeEncodeError, ValueError):
    bytes = obj if isinstance(obj, __bytes) else __unicode(obj).encode('utf-8')
    key   = (b'x' + binascii.hexlify(bytes)).decode('ascii')
  
  return key   

def _build(obj, name, node):
  if isinstance(obj, collections.Mapping):
    for key, value in obj.items():
      key = _key(key)
      _build(value, key, etree.SubElement(node, key))
  elif not isinstance(obj, collections.Iterable) or isinstance(obj, __basestr):
    try:
      node.text = obj.decode('utf-8') if isinstance(obj, __bytes) else __unicode(obj)
    except UnicodeDecodeError:
      node.text = (b'x' + binascii.hexlify(obj)).decode('ascii')
  elif isinstance(obj, collections.Iterable):
    key = _key(name) + '-item'
    for value in obj:
      _build(value, key, etree.SubElement(node, key))

  return node


def dump(obj, fp, root = 'data', declaration = False):
  root = _build(obj, root, etree.Element(_key(root)))
  etree.ElementTree(root).write(fp, encoding = 'utf-8', xml_declaration = declaration)

def dumps(obj, root = 'data', declaration = False):
  # io.StringIO is unicode only on py2
  with BytesIO() as fp:
    dump(obj, fp, root, declaration) 
    fp.seek(0)
    return fp.read().decode('utf-8')

