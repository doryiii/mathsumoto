import sys
import scribus

def get_prop(prop):
    """ Returns whether an object whose name is given in prop exists."""
    scribus.deselectAll()
    try:
        scribus.selectObject(prop)
    except NoValidObjectError:
        return False
    return scribus.selectionCount() > 0
    

output = sys.argv[2]
text = sys.argv[1].upper() if get_prop("Uppercase") else sys.argv[1]
TXTBOX = "MainText"

if text:
    size = scribus.getFontSize(TXTBOX)
    pstyle = scribus.getParagraphStyle(TXTBOX)

    scribus.setText(text, TXTBOX)

    scribus.setFontSize(size, TXTBOX)
    scribus.setParagraphStyle(pstyle, TXTBOX)
    scribus.setFirstLineOffset(scribus.FLOP_LINESPACING, TXTBOX)

i = ImageExport()
i.type = "PNG"
i.dpi = 100
i.scale = 100
i.transparentBkgnd = get_prop("TransparentExport")
i.saveAs(output)

# https://impagina.org/scribus-scripter-api/image-export/
