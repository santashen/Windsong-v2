import { marked } from 'marked'
import katex from 'katex'

function renderLatex(latex, displayMode, fallback) {
  try {
    return katex.renderToString(latex.trim(), { displayMode })
  } catch (error) {
    console.error('KaTeX rendering error:', error)
    return fallback
  }
}

marked.use({
  extensions: [
    {
      name: 'blockLatex',
      level: 'block',
      tokenizer(src) {
        const multiline = /^\$\$[ \t]*\r?\n([\s\S]*?)\r?\n\$\$[ \t]*(?:\r?\n|$)/.exec(src)
        const singleLine = /^\$\$([^\r\n]+?)\$\$[ \t]*(?:\r?\n|$)/.exec(src)
        const match = multiline || singleLine

        if (!match) return undefined

        return {
          type: 'blockLatex',
          raw: match[0],
          text: match[1]
        }
      },
      renderer(token) {
        return `${renderLatex(token.text, true, token.raw)}\n`
      }
    },
    {
      name: 'inlineLatex',
      level: 'inline',
      tokenizer(src) {
        const match = /^\$(?!\$)((?:\\.|[^$\\\r\n])+?)\$(?!\$)/.exec(src)

        if (!match) return undefined

        return {
          type: 'inlineLatex',
          raw: match[0],
          text: match[1]
        }
      },
      renderer(token) {
        return renderLatex(token.text, false, token.raw)
      }
    }
  ]
})

marked.setOptions({
  breaks: true,
  gfm: true
})

export function renderMarkdown(content) {
  return marked(content)
}
