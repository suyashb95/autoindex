### autoindex 📑

A Python project that automatically adds an index/bookmarks/outlines to a PDF

### Installation

#### Using Pip
* Run `pip install autoindex`

#### From Source
* Clone the repo or download the zip
* `cd` to the folder
* Run `pip install -r "requirements.txt"`
* Run `python autoindex.py [OPTIONS]`

### Usage

autoindex works well with PDFs that have clearly outlined bookmarks with numerical page numbers and no images. 
Nesting can be detected by differences in font sizes or the indents in bookmarks. In both cases, the thresholds
to detect child bookmarks have to be configured. The `-d/--diagnose` option can be useful for this. It prints the 
most common font sizes, line starting coordinates which can be used to figure out the threshold values

Most PDFs have an offset between the actual page number and what's shown in the reader. That can be specified
using the `--offset` option 

Scanned PDFs are not supported yet

### Limitations

 - Multi line bookmarks might not be extracted completely. 
 - PDFs meant for printing have different offsets for text on odd/even pages which can cause problems while detecting nesting

### Options

```
Usage: autoindex.py [OPTIONS]

Options:
  -i, --input TEXT                input file name  [required]
  -o, --output TEXT               output file name. If not provided, defaults
                                  to the input file name suffixed with
                                  "-bookmarked"

  --toc-page-numbers, --toc INTEGER...
                                  range of pages (from, to) having the table
                                  of contents

  -d, --diagnose                  print the most common font sizes and line
                                  starting points to help choose values for
                                  fontsize/indent thresholds

  --nest-using-fontsize           flag to try and figure out nested bookmarks
                                  using font sizes

  --nest-using-indents            flag to try and figure out nested bookmarks
                                  using indents

  --offset INTEGER                offset to add to the page numbers from the
                                  table of contents

  --char-margin FLOAT             spacing between characters to be considered
                                  as a part of the same line

  --line-margin FLOAT             spacing between lines to be considered as a
                                  part of the same text box

  --header-fontsize-threshold FLOAT
                                  font size difference for a line to be
                                  considered as header

  --topic-fontsize-threshold FLOAT
                                  font size difference for lines to be
                                  considered as a part of the same parent
                                  header

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
