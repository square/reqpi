if __name__ != '__main__':
    raise ImportError('module cannot be imported')

import sys
import mainland

mainland.main(
    root='reqpi',
    marker='REQPI_MAIN_OK',
    argv=sys.argv,
)
