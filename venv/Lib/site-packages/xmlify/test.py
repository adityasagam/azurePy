# -*- coding: utf-8 -*-
'''
@author: saaj
'''


import unittest
import decimal
import datetime
import xml.etree.ElementTree as etree

import xmlify


class TestCase(unittest.TestCase):
  
  def testScalar(self):
    self.assertEqual('<data />',             xmlify.dumps({}))
    self.assertEqual('<data>123</data>',     xmlify.dumps(123))
    self.assertEqual('<data>123.123</data>', xmlify.dumps(123.123))
    
    self.assertEqual('<data>foo</data>',                          xmlify.dumps('foo'))
    self.assertEqual('<data>foo&gt;</data>',                      xmlify.dumps('foo>'))
    self.assertEqual('<data>&lt;foo&gt;&amp;&lt;/foo&gt;</data>', xmlify.dumps('<foo>&</foo>'))
    self.assertEqual('<data>foo</data>',                          xmlify.dumps(b'foo'))
    self.assertEqual('<data>foo&gt;</data>',                      xmlify.dumps(b'foo>'))
    self.assertEqual('<data>&lt;foo&gt;&amp;&lt;/foo&gt;</data>', xmlify.dumps(b'<foo>&</foo>'))
    self.assertEqual(u'<data>бар</data>',                         xmlify.dumps(u'бар'))
    self.assertEqual(u'<data>бар&lt;</data>',                     xmlify.dumps(u'бар<'))
    self.assertEqual(u'<data>бар&lt;&amp;baz;&gt;</data>',        xmlify.dumps(u'бар<&baz;>'))
    
    self.assertEqual('<data>True</data>', xmlify.dumps(True))
    self.assertEqual('<data>None</data>', xmlify.dumps(None))
    
    self.assertEqual('<data>123.123</data>', xmlify.dumps(decimal.Decimal('123.123')))
    self.assertEqual('<data>2012-11-10 09:08:07</data>', xmlify.dumps(datetime.datetime(2012, 11, 10, 9, 8, 7)))
  
  def testIterable(self):
    expected = u'<data><data-item>бар</data-item><data-item>foo</data-item><data-item>123</data-item></data>'
    self.assertEqual(expected, xmlify.dumps((u'бар', b'foo', 123)))
    self.assertEqual(expected, xmlify.dumps([u'бар', b'foo', 123]))
    self.assertEqual(expected, xmlify.dumps(v for v in (u'бар', b'foo', 123)))
    
    actual = etree.fromstring(xmlify.dumps({u'бар', b'foo', 123}).encode('utf-8'))
    self.assertTrue(all(n.text in (u'бар', 'foo', '123') for n in actual.iterfind('data')))
  
  def testMapping(self):
    d = {
      u'бар'                    : b'foo', 
      b'foo'                    : u'бар', 
      123                       : 234.345,
      234.345                   : 123,
      False                     : None, 
      None                      : False, 
      datetime.date(2008, 8, 8) : decimal.Decimal('2.2'),
      decimal.Decimal('2.2')    : datetime.date(2008, 8, 8) 
    }
    
    actual = etree.fromstring(xmlify.dumps(d).encode('utf-8'))
    self.assertEqual('foo',        actual.find('xd0b1d0b0d180').text)
    self.assertEqual(u'бар',       actual.find('foo').text)
    self.assertEqual('234.345',    actual.find('n123').text)
    self.assertEqual('123',        actual.find('n234.345').text)
    self.assertEqual('None',       actual.find('False').text)
    self.assertEqual('False',      actual.find('None').text)
    self.assertEqual('2.2',        actual.find('n2008-08-08').text)
    self.assertEqual('2008-08-08', actual.find('n2.2').text)
    
    self.assertEqual('<data><x>21</x></data>',   xmlify.dumps({''   : 21}))
    self.assertEqual('<data><__>22</__></data>', xmlify.dumps({'!#' : 22}))
  
  def testXmlUnfriendly(self):
    d = {b'\x00\x80\x01': b'\xde\xad\xbe\xef'}
    self.assertEqual('<data><x008001>xdeadbeef</x008001></data>', xmlify.dumps(d))
    
  def testNested(self):
    data = {
      'request' : {
        'url'     : 'http://planetpython.org/rss20.xml',
        'method'  : 'GET',
        'headers' : {
          'host'            : 'planetpython.org',
          'user-agent'      : 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0',
          'accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'accept-language' : 'en,en-gb;q=0.7,ru;q=0.3',
          'accept-encoding' : 'gzip, deflate',
          'referer'         : 'http://planetpython.org/',
          'connection'      : 'keep-alive'            
        }
      },
      'response' : {
        'status'  : '200',
        'headers' : {
          'server'         : 'nginx',
          'date'           : 'Mon, 01 Jun 2015 18:42:30 GMT',
          'content-type'   : 'text/xml',
          'content-length' : '123690',
          'last-modified'  : 'Mon, 01 Jun 2015 16:48:44 GMT',
          'connection'     : 'keep-alive',
          'etag'           : '"556c8cec-1e32a"',
          'accept-ranges'  : 'bytes'
        },
        'body' : '''<?xml version="1.0"?>
          <rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
            <channel>
              <title>Planet Python</title>
              <link>http://planetpython.org/</link>
              <language>en</language>
              <description>Planet Python - http://planetpython.org/</description>
              <item>
                <title>PyPy Development: PyPy 2.6.0 release</title>
                <guid>http://feedproxy.google.com/~r/PyPyStatusBlog/~3/LP9tp3TPXOY/pypy-260-release.html</guid>
                <link>http://feedproxy.google.com/~r/PyPyStatusBlog/~3/LP9tp3TPXOY/pypy-260-release.html</link>
                <description>&lt;div dir=&quot;ltr&quot;&gt;
                  &lt;div class=&quot;document&quot;&gt;
                  &lt;div class=&quot;section&quot; id=&quot;pypy-2-6-0-cameo-charm&quot;&gt;
                  &lt;h2&gt;PyPy 2.6.0 - Cameo Charm&lt;/h2&gt;
                </description>
                <pubDate>Mon, 01 Jun 2015 16:41:36 +0000</pubDate>
              </item>
            </channel>
          </rss>
        '''
      }        
    }
    
    actual = etree.fromstring(xmlify.dumps(data).encode('utf-8'))
    def match(path, obj):
      if isinstance(obj, dict):
        for k, v in obj.items():
          match(path + [k], v)
      elif path:
        self.assertEqual(obj, actual.find('/'.join(path)).text)
    match([], data)
  
