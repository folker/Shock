package index

import (
	"encoding/binary"
	"fmt"
	"github.com/MG-RAST/Shock/shock-server/conf"
	"github.com/MG-RAST/Shock/shock-server/node/file/format/multi"
	"github.com/MG-RAST/Shock/shock-server/node/file/format/seq"
	"io"
	"math/rand"
	"os"
)

type chunkRecord struct {
	f     *os.File
	r     seq.Reader
	Index *Idx
	size  int64
}

func NewChunkRecordIndexer(f *os.File) Indexer {
	fi, _ := f.Stat()
	return &chunkRecord{
		f:     f,
		size:  fi.Size(),
		r:     multi.NewReader(f),
		Index: New(),
	}
}

func (i *chunkRecord) Create(file string) (count int64, format string, err error) {
	tmpFilePath := fmt.Sprintf("%s/temp/%d%d.idx", conf.Conf["data-path"], rand.Int(), rand.Int())

	f, err := os.Create(tmpFilePath)
	if err != nil {
		return
	}
	defer f.Close()

	format = "array"
	curr := int64(0)
	count = 0
	buffer_pos := 0 // used to track the location in our byte array

	// Writing index file in 16MB chunks
	var b [16777216]byte
	for {
		n, er := i.r.SeekChunk(curr)
		if er != nil {
			if er != io.EOF {
				err = er
				return
			}
		}
		// Calculating position in byte array
		x := (buffer_pos * 16)
		if x == 16777216 {
			f.Write(b[:])
			buffer_pos = 0
			x = 0
		}
		binary.LittleEndian.PutUint64(b[x:x+8], uint64(curr))
		if er == io.EOF {
			binary.LittleEndian.PutUint64(b[x+8:x+16], uint64(i.size-curr))
		} else {
			binary.LittleEndian.PutUint64(b[x+8:x+16], uint64(n))
		}

		curr += int64(n)
		count += 1
		buffer_pos += 1
		if er == io.EOF {
			break
		}
	}
	if buffer_pos != 0 {
		f.Write(b[:buffer_pos*16])
	}
	err = os.Rename(tmpFilePath, file)

	return
}

func (i *chunkRecord) Close() (err error) {
	i.f.Close()
	return
}
