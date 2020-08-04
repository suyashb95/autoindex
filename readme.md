### autoindex

A Python project that automatically adds an index/bookmarks/outlines to a PDF

```
Usage: main.py [OPTIONS]

Options:
  -i, --input TEXT                input file name
  -o, --output TEXT               output file name
  --toc-page-numbers, --toc INTEGER...
                                  range of pages (from, to) having the table 
                                  of contents

  --nest-using-fontsize BOOLEAN   flag to try and figure out nested bookmarks
                                  using font sizes

  --nest-using-indents BOOLEAN    flag to try and figure out nested bookmarks
                                  using indents

  --offset INTEGER                offset to add to the page numbers from the
                                  table of contents

  --char-margin FLOAT             spacing between characters to be considered
                                  as a part of the same line

  --line-margin FLOAT             spacing between lines to be considered as a
                                  part of the same text box

  --header-fontsize-threshold FLOAT
                                  minimum difference between font sizes for a
                                  line to be considered as header

  --topic-fontsize-threshold FLOAT
                                  font size delta for lines to be considered
                                  as a part of the same parent header

  --header-indent-threshold FLOAT
                                  indent difference for a line to be
                                  considered as header

  --topic-indent-threshold FLOAT  indent difference for lines to be considered
                                  as a part of the same parent header

  --help                          Show this message and exit.
  ```

### To Do
- [x] Detect nesting using indents
- [ ] Output an intermediate YAML containing bookmarks
that can be fixed before being added to the file
- [ ] Add support for EPUB/DjVu
- [ ] Expose as a web app
- [ ] Add GUI/diagnostics to help choose configuration params
