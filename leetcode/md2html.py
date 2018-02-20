#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 18:36:17 2018



@author: wuxiaobai24
"""

import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html


mdpath = './md'
htmlpath = './html'


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code><pre>\n' % mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formater = html.HtmlFormatter()
        return highlight(code, lexer, formater)


def md2html(mdfilename, html_name):
    print(mdfilename, '->', html_name)
    with open(mdpath + '/' + mdfilename, 'r') as f:
        md_text = f.read()
    with open('autumn.css', 'r') as f:
        css_text = f.read()
    renderer = HighlightRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    html_text = markdown(md_text)

    with open(html_name, 'w') as f:
        f.write(css_text + html_text)


if __name__ == '__main__':
    pass
